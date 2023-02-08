# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# perform_tree_detection_v2.py
# Description: Translation of Hanssen et al. (2021) tree detection algorithm
# from ArcMap model builder to ArcPy script - Version 2
# Author: Zofie Cimburova
# ---------------------------------------------------------------------------

# Import arcpy module
import arcpy
import os
from arcpy import env

# ------------------------------------------------------ #
# Functions
# ------------------------------------------------------ #
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
    for a in a_src:
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
# Workspace settings
# ------------------------------------------------------ #
env.overwriteOutput = True
env.outputCoordinateSystem = arcpy.SpatialReference("ETRS 1989 UTM Zone 32N")
env.workspace = r"P:\15220700_gis_samordning_2022_(marea_spare_ecogaps)\Zofie\synergi_3_tree_accounts\DATA" # IF NECESSARY, CHANGE PATH TO DATA DIRECTORY


# ------------------------------------------------------ #
# Inputs
# ------------------------------------------------------ #
path_bydel = "neighbourhoods.gdb\\" # IF NECESSARY, CHANGE PATH TO GEODATABASE STORING NEIGHBOURHOOD POLYGONS
path_output = "trees_v2.gdb\\" # IF NECESSARY, CHANGE PATH TO GEODATABASE STORING OUTPUT DATA
r_chm = r"pbe_chm_2021.gdb\Trehoyde_over2m" # IF NECESSARY, CHANGE PATH TO DATASET STORING CANOPY HEIGHT MODEL
v_water = r"R:\GeoSpatialData\Topography\Norway_FKB\Original\FKB-Vann FGDB-format\Basisdata_0000_Norge_5973_FKB-Vann_FGDB\Basisdata_0000_Norge_5973_FKB-Vann_FGDB.gdb\fkb_vann_omrade" # IF NECESSARY, CHANGE PATH TO DATASET STORING WATER POLYGONS


# ------------------------------------------------------ #
# 1. Detect tree polygons (crowns) and tree points (tops) per neighbourhood
# ------------------------------------------------------ #
arcpy.AddMessage("Step 1: Detecting tree polygons and points per neighbourhood...")

# Iterate over bydel (here adjusted for Oslo - 16 bydel numbered 01-16 with prefix 0301)
list_tree_pnt_names = []
list_tree_poly_names = []  

for i in range (1, 17): # IF NECESSARY, CHANGE NUMBER OF BYDEL

    bydel_code = "0301" + str(i).zfill(2) # IF NECESSARY, CHANGE CODE PREFIX OF BYDEL
    arcpy.AddMessage("  PROCESSING BYDEL {}".format(bydel_code))
    arcpy.AddMessage("  ---------------------".format(bydel_code))
   
    v_bydel = path_bydel + "\\b_" + bydel_code
    
    # names of output tree points and polygons
    v_tree_pnt = path_output + "data_" + bydel_code + "_tree_pnt"
    v_tree_poly = path_output + "data_" + bydel_code + "_tree_poly"

    list_tree_pnt_names.append(v_tree_pnt)
    list_tree_poly_names.append(v_tree_poly)
    
        
    # ------------------------------------------------------ #
    # 0. Select part of CHM within neighbourhood + 200m buffer to avoid edge effect
    # ------------------------------------------------------ # 
    arcpy.AddMessage("  0: Clipping CHM by neighbourhood...")

    v_bydel_buffer = path_output + "data_" + bydel_code + "_00_bydel_buffer"
    arcpy.Buffer_analysis(
        v_bydel,
        v_bydel_buffer,
        200,
    )
    
    r_chm_clip = path_output + "data_" + bydel_code + "_00_chm_clip"
    arcpy.Clip_management(
        in_raster = r_chm,
        out_raster = r_chm_clip,
        in_template_dataset = v_bydel_buffer,
        clipping_geometry="ClippingGeometry",
    )
    
    arcpy.Delete_management(v_bydel_buffer)


    # ------------------------------------------------------ #
    # 1. Filter CHM by minimum height
    # ------------------------------------------------------ #
    arcpy.AddMessage("  1: Filtering CHM by minimum height...")
    
    r_chm_h = path_output + "data_" + bydel_code + "_01_chm_h"
    h = 2.0
    arcpy.gp.ExtractByAttributes_sa(
        r_chm_clip, 
        "Value >= {}".format(h), 
        r_chm_h
    )
    arcpy.Delete_management(r_chm_clip)


    # ------------------------------------------------------ #
    # 2. Refine CHM by focal maximum filter
    # ------------------------------------------------------ #
    arcpy.AddMessage("  2: Refining CHM by focal maximum filter...")
    
    r_chm_smooth = path_output + "data_" + bydel_code + "_02_chm_smooth"
    arcpy.gp.FocalStatistics_sa(
        r_chm_h, 
        r_chm_smooth, 
        "Circle 1,5 MAP", 
        "MAXIMUM", 
        "DATA", 
        "90"
    )


    # ------------------------------------------------------ #
    # 3. Flip CHM
    # ------------------------------------------------------ #
    arcpy.AddMessage("  3: Flipping CHM...")
    
    r_chm_flip = path_output + "data_" + bydel_code + "_03_chm_flip"
    arcpy.gp.RasterCalculator_sa(
        '"{}"*(-1)'.format(r_chm_smooth), 
        r_chm_flip
    )
    arcpy.Delete_management(r_chm_smooth)


    # ------------------------------------------------------ #
    # 4. Compute flow direction
    # ------------------------------------------------------ #
    arcpy.AddMessage("  4: Computing flow direction...")
    
    r_flowdir = arcpy.sa.FlowDirection(
        r_chm_flip
    )
    arcpy.Delete_management(r_chm_flip)


    # ------------------------------------------------------ #
    # 5. Identify sinks
    # ------------------------------------------------------ #
    arcpy.AddMessage("  5: Identifying sinks...")
    
    r_sinks = arcpy.sa.Sink(
        r_flowdir
    )


    # ------------------------------------------------------ #
    # 6. Identify watersheds 
    # ------------------------------------------------------ #
    arcpy.AddMessage("  6: Identifying watersheds...")
    
    r_watersheds = arcpy.sa.Watershed(
        r_flowdir,
        r_sinks,
        "Value"
    ) 
    

    # ------------------------------------------------------ #
    # 7. Identify tree tops by focal flow
    # ------------------------------------------------------ #
    arcpy.AddMessage("  7: Identifying tree tops by focal flow...")
    
    r_focflow = arcpy.sa.FocalFlow(
        r_sinks, 
        "0,5"
    )


    # ------------------------------------------------------ #
    # 8. Vectorize tree tops to polygons
    # ------------------------------------------------------ #
    arcpy.AddMessage("  8: Vectorizing tree tops to polygons...")
    
    v_treetop_poly = path_output + "data_" + bydel_code + "_08_treetop_poly"
    arcpy.RasterToPolygon_conversion(
        in_raster = r_focflow,
        out_polygon_features = v_treetop_poly, 
        simplify = "NO_SIMPLIFY", 
        raster_field = "Value", 
        create_multipart_features = "SINGLE_OUTER_PART", 
        max_vertices_per_feature = ""
    )


    # ------------------------------------------------------ #
    # 9. Convert tree top polygons to points
    # ------------------------------------------------------ #
    arcpy.AddMessage("  9: Converting tree top polygons to points...")
    
    v_treetop_pnt = path_output + "data_" + bydel_code + "_09_treetop_pnt"
    arcpy.FeatureToPoint_management(
        in_features = v_treetop_poly,
        out_feature_class = v_treetop_pnt, 
        point_location = "INSIDE"
    )
    arcpy.Delete_management(v_treetop_poly)

    # Extract tree height (from CHM) to tree points   
    arcpy.gp.ExtractMultiValuesToPoints_sa(
        v_treetop_pnt,
        "'{}' tree_heigh".format(r_chm_h),
        "NONE"
        )
    arcpy.Delete_management(r_chm_h)


    # ------------------------------------------------------ #
    # 10. Identify tree crowns by vectorizing watersheds
    # ------------------------------------------------------ #
    arcpy.AddMessage("  10: Identifying tree crowns by vectorizing watersheds...")
    
    v_watersheds = path_output + "data_" + bydel_code + "_10_watersheds"
    arcpy.RasterToPolygon_conversion(
        in_raster = r_watersheds,
        out_polygon_features = v_watersheds, 
        simplify = "NO_SIMPLIFY", 
        raster_field = "Value", 
        create_multipart_features = "SINGLE_OUTER_PART", 
        max_vertices_per_feature = ""
    )
    
    
    # ------------------------------------------------------ #
    # 11. Select only tree points within neighbourhood
    # ------------------------------------------------------ #
    arcpy.AddMessage("  11: Selecting only tree points within neighbourhood...")
    
    l_tree_pnt = arcpy.MakeFeatureLayer_management(
        v_treetop_pnt, 
        "tree_pnt_lyr"
    )
    
    arcpy.SelectLayerByLocation_management(
        l_tree_pnt, 
        "INTERSECT",
        v_bydel,
        "",
        "NEW_SELECTION"
    )
    
    arcpy.CopyFeatures_management(
        in_features = l_tree_pnt,
        out_feature_class = v_tree_pnt
    )    
    arcpy.Delete_management(v_treetop_pnt)

    # Store information on neighbourhood code
    arcpy.AddField_management(v_tree_pnt, "bydel_code", "TEXT")
    arcpy.CalculateField_management(v_tree_pnt, "bydel_code", bydel_code)
    
    # Delete useless attributes
    arcpy.DeleteField_management(
        v_tree_pnt, 
        ["Id", "gridcode", "ORIG_FID"]
    )
    

    # ------------------------------------------------------ #
    # 12 Select only tree polygons within neighbourhood (i.e., the ones that intersect with tree tops)
    # ------------------------------------------------------ #
    arcpy.AddMessage("  12: Selecting only tree polygons within neighbourhood...")
    
    l_tree_poly = arcpy.MakeFeatureLayer_management(
        v_watersheds, 
        "tree_poly_lyr"
    )
    
    arcpy.SelectLayerByLocation_management(
        l_tree_poly, 
        "INTERSECT",
        v_tree_pnt,
        "",
        "NEW_SELECTION"
    )

    arcpy.CopyFeatures_management(
        in_features = l_tree_poly,
        out_feature_class = v_tree_poly
    )
    arcpy.Delete_management(v_watersheds)
    
    # Store information on neighbourhood code
    arcpy.AddField_management(v_tree_poly, "bydel_code", "TEXT")
    arcpy.CalculateField_management(v_tree_poly, "bydel_code", bydel_code)

    # Delete useless attributes
    arcpy.DeleteField_management(
        v_tree_poly, 
        ["Id", "gridcode"]
    )
   

    arcpy.AddMessage("  ---------------------")


# ------------------------------------------------------ #
# 2. Merge detected trees into one file
# ------------------------------------------------------ #
arcpy.AddMessage("Step 2: Merging detected trees into one file...")

v_tree_poly_result = path_output + "tree_poly_OB_2021"
arcpy.Merge_management(
    inputs = list_tree_poly_names,
    output = v_tree_poly_result
)

v_tree_pnt_result = path_output + "tree_pnt_OB_2021"
arcpy.Merge_management(
    inputs = list_tree_pnt_names,
    output = v_tree_pnt_result
)


# ------------------------------------------------------ #
# 3. Compute additional attributes
# ------------------------------------------------------ #
arcpy.AddMessage("Step 4: Computing additional attributes...")

# Tree polygons - assign a unique ID
arcpy.AddField_management(v_tree_poly_result, "crown_id", "LONG")
arcpy.CalculateField_management(v_tree_poly_result, "crown_id", '[OBJECTID]')

# Tree polygons - compute crown diameter
v_mbg = path_output + "tmp_mbg"
arcpy.MinimumBoundingGeometry_management(
    v_tree_poly_result,
    v_mbg,
    "CONVEX_HULL",
    "NONE", 
    "", 
    "MBG_FIELDS"
)

arcpy.AddField_management(v_tree_poly_result, "crown_diam", "FLOAT")
join_and_copy(v_tree_poly_result, "crown_id", v_mbg, "crown_id", ["MBG_Length"], ["crown_diam"])
arcpy.Delete_management(v_mbg)

# Tree polygons - compute crown area and perimeter
arcpy.AddField_management(v_tree_poly_result, "crown_area", "FLOAT")
arcpy.AddField_management(v_tree_poly_result, "crown_peri", "FLOAT")

arcpy.CalculateField_management(v_tree_poly_result, "crown_area", '[Shape_Area]')
arcpy.CalculateField_management(v_tree_poly_result, "crown_peri", '[Shape_Length]')

# Assign tree polygon ID to tree points
arcpy.AddField_management(v_tree_pnt_result, "tmp_id", "LONG") # temporary ID for tree points to avoid issues with join_and_copy()
arcpy.CalculateField_management(v_tree_pnt_result, "tmp_id", '[OBJECTID]')

v_join = path_output + "tmp_join"
arcpy.SpatialJoin_analysis(
    v_tree_pnt_result,
    v_tree_poly_result, 
    v_join,
    "JOIN_ONE_TO_ONE", 
    "KEEP_ALL", 
    match_option="INTERSECT"
)

arcpy.AddField_management(v_tree_pnt_result, "crown_id", "LONG")
join_and_copy(
    v_tree_pnt_result, 
    "tmp_id", 
    v_join, 
    "tmp_id", 
    ["crown_id"], 
    ["crown_id"]
)

arcpy.Delete_management(v_join)
arcpy.DeleteField_management(v_tree_pnt_result, "tmp_id")

# Copy crown_diam, crown_area, crown_peri from tree polygons to tree points
arcpy.AddField_management(v_tree_pnt_result, "crown_diam", "FLOAT")
arcpy.AddField_management(v_tree_pnt_result, "crown_area", "FLOAT")
arcpy.AddField_management(v_tree_pnt_result, "crown_peri", "FLOAT")

join_and_copy(
    v_tree_pnt_result, 
    "crown_id", 
    v_tree_poly_result, 
    "crown_id", 
    ["crown_diam", "crown_area", "crown_peri"], 
    ["crown_diam", "crown_area", "crown_peri"]
)

# Copy tree_heigh from tree points to tree polygons
arcpy.AddField_management(v_tree_poly_result, "tree_heigh", "FLOAT")

join_and_copy(
    v_tree_poly_result, 
    "crown_id", 
    v_tree_pnt_result, 
    "crown_id", 
    ["tree_heigh"], 
    ["tree_heigh"]
)

# Calculate tree volume
arcpy.AddField_management(v_tree_poly_result, "tree_volum", "FLOAT")
arcpy.CalculateField_management(
    in_table=v_tree_poly_result,
    field="tree_volum", 
    expression="(1.0/3.0) * math.pi * ( !crown_diam! /2.0 ) * ( !crown_diam! /2.0) * float(!tree_heigh!)",
    expression_type="PYTHON_9.3", 
    code_block=""
)

arcpy.AddField_management(v_tree_pnt_result, "tree_volum", "FLOAT")
arcpy.CalculateField_management(
    in_table=v_tree_pnt_result,
    field="tree_volum", 
    expression="(1.0/3.0) * math.pi * ( !crown_diam! /2.0 ) * ( !crown_diam! /2.0) * float(!tree_heigh!)",
    expression_type="PYTHON_9.3", 
    code_block=""
)
