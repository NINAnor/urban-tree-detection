# ------------------------------------------------------ #
# 4. Compute additional attributes
# ------------------------------------------------------ #
import arcpy
import os

# Join "source_table" to "destination table" and copy attributes from "source table" to attributes in "destination table"
def join_and_copy(t_dest, join_a_dest, t_src, join_a_src, a_src, a_dest):
     
    name_dest = arcpy.Describe(t_dest).name
    name_src = arcpy.Describe(t_src).name
     
    # Create layer from "destination table"
    l_dest = "dest_lyr"
    arcpy.MakeFeatureLayer_management(t_dest, l_dest)
     
    # Join
    arcpy.AddJoin_management(l_dest, join_a_dest, t_src, join_a_src)
     
    # Copy attributes   
    i = 0
    for i in a_src: #a
        arcpy.AddMessage(
            "Copying values from " + name_src +  "." + a_src[i] + " to " + name_dest + "." + a_dest[i]
        )
        arcpy.CalculateField_management(
            l_dest, 
            name_dest + "." + a_dest[i], 
            "[" + name_src + "." + a_src[i] + "]"
        )
        i = i+1  

# ------------------------------------------------------ #
# Add attributes related to bykrest/bedel in "cal attr. "
# ------------------------------------------------------ #


# Add LiDAR information
def attr_lidarTile(layer, tile_code):
    format_tile_code = tile_code[:3] + "-" + tile_code[4:]

    arcpy.AddMessage(f"\t\tAdding the attribute <<lidar_tile>> with the corresponding tile code: {format_tile_code}... ")
    # Store information on neighbourhood code
    arcpy.AddField_management(layer, "lidar_tile", "TEXT")
    arcpy.CalculateField_management(layer, "lidar_tile", str(format_tile_code))
    
    # Delete useless attributes
    arcpy.DeleteField_management(
        layer, 
        ["Id", "gridcode", "ORIG_FID"]
    )
    

# Assign a unique ID to each tree polygon
def attr_crownID(v_treecrown_result):
    arcpy.AddMessage(f"\t\tAdding the attribute <<crown_id>> using the unique ObjectID number... ")

    arcpy.AddField_management(v_treecrown_result, "crown_id", "LONG")
    
    with arcpy.da.UpdateCursor(v_treecrown_result, ["OBJECTID", "crown_id"]) as cursor:
        for row in cursor:
            row[1] = row[0]
            cursor.updateRow(row)
    #arcpy.CalculateField_management(v_treecrown_result, "crown_id", "SHAPE@OID")

# Compute crown diameter for each tree polygon using Minimum Bounding Geometry
def attr_crownArea(v_treecrown_result, output_path):

    arcpy.AddMessage(f"\t\tComputing the crown diameter by using the Minimum Bounding Geometry... ")
    v_mbg = os.path.join(output_path, "mbg_temp")
    arcpy.MinimumBoundingGeometry_management(
        v_treecrown_result,
        v_mbg,
        "CIRCLE", # TODO - adjust geometry here if necessary
        "NONE", 
        "", 
        "MBG_FIELDS"
    )
    
    arcpy.AddMessage(f"\t\tAdding the attribute <<crown_diam>>... ")
    arcpy.AddField_management(v_treecrown_result, "crown_diam", "FLOAT")
    join_and_copy(v_treecrown_result, "crown_id", v_mbg, "crown_id", ["MBG_Diameter"], ["crown_diam"])
    arcpy.Delete_management(v_mbg)

    # Compute crown area 
    arcpy.AddMessage(f"\t\tComputing the crown area by using the polygon shape area... ")
    arcpy.AddMessage(f"\t\tAdding the attribute <<crown_area>>... ")
    arcpy.AddField_management(v_treecrown_result, "crown_area", "FLOAT")
    arcpy.CalculateField_management(v_treecrown_result, "crown_area", '[Shape_Area]')

    # Compute crown perimeter
    arcpy.AddMessage(f"\t\tComputing the crown perimeter by using the shape length... ")
    arcpy.AddMessage(f"\t\tAdding the attribute <<crown_peri>>... ")
    arcpy.AddField_management(v_treecrown_result, "crown_peri", "FLOAT")
    arcpy.CalculateField_management(v_treecrown_result, "crown_peri", '[Shape_Length]')



# join tree crown attr. to tree points
def polygonAttr_toPoint(v_treetop_result, v_treecrown_result, output_path):
    
    
    # temporary ID for tree points to avoid issues with join_and_copy()
    arcpy.AddMessage(f"\t\tAdding a temporary treetop id using ObjectID... ")

    arcpy.AddField_management(v_treetop_result, "tmp_id", "LONG") 
    
    with arcpy.da.UpdateCursor(v_treetop_result, ["OBJECTID", "tmp_id"]) as cursor:
        for row in cursor:
            row[1] = row[0]
            cursor.updateRow(row)    
    
    
    #arcpy.CalculateField_management(v_treetop_result, "tmp_id", '[OBJECTID]')

    arcpy.AddMessage(f"\t\tJoining the tree crown attributes: crown_id, crown_diam, crown_area, crown_peri to the treetop points... ")
    v_join = os.path.join(output_path, "join_tmp")
    arcpy.SpatialJoin_analysis(
        v_treetop_result,
        v_treecrown_result, 
        v_join,
        "JOIN_ONE_TO_ONE", 
        "KEEP_ALL", 
        match_option="INTERSECT"
    )
    
    # Assign tree crown ID to tree points
    arcpy.AddField_management(v_treetop_result, "crown_id", "LONG")
    join_and_copy(
        v_treetop_result, 
        "tmp_id", 
        v_join, 
        "tmp_id", 
        ["crown_id"], 
        ["crown_id"]
    )

    arcpy.Delete_management(v_join)
    arcpy.DeleteField_management(v_treetop_result, "tmp_id")

    # Copy crown_diam, crown_area, crown_peri from tree polygons to tree points
    arcpy.AddField_management(v_treetop_result, "crown_diam", "FLOAT")
    arcpy.AddField_management(v_treetop_result, "crown_area", "FLOAT")
    arcpy.AddField_management(v_treetop_result, "crown_peri", "FLOAT")

    join_and_copy(
        v_treetop_result, 
        "crown_id", 
        v_treecrown_result, 
        "crown_id", 
        ["crown_diam", "crown_area", "crown_peri"], 
        ["crown_diam", "crown_area", "crown_peri"]
    )


# Copy tree_heigh, tree_altit from tree points to tree polygons
def pointAttr_toPolygon(v_treecrown_result,v_treetop_result):
    
    arcpy.AddMessage(f"\t\tJoining the tree top attributes: tree_height and tree_altit to the treecrown polygons... ")
    arcpy.AddField_management(v_treecrown_result, "tree_height", "SHORT")
    arcpy.AddField_management(v_treecrown_result, "tree_altit", "LONG")

    join_and_copy(
    v_treecrown_result, 
    "crown_id", 
    v_treetop_result, 
    "crown_id", 
    ["tree_height", "tree_altit"], 
    ["tree_height", "tree_altit"]
)


# Compute tree volume for each tree crown using the formula 
# tree volume =(1/3)π * (crown diameter/2)^2 * tree height

def attr_crownVolume(layer):
    # Calculate tree volume
    
    formula = str("tree volume =(1/3)π * (crown diameter/2)^2 * tree height")
    arcpy.AddMessage(f"\t\tComputing the crown volume by using the formula: \n\t\t{formula}")
    
    arcpy.AddField_management(layer, "tree_volum", "FLOAT")
    arcpy.CalculateField_management(
    in_table=layer,
    field="tree_volum", 
    expression="(1.0/3.0) * math.pi * ( !crown_diam! /2.0 ) * ( !crown_diam! /2.0) * float(!tree_heigh!)",
    expression_type="PYTHON_9.3", 
    code_block=""
)



