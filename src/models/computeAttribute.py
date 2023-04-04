import arcpy
import os 

# project pacakge read the readme file on how to install it properly
from src import join_and_copy

print("test")

def fieldExist(featureclass:str, fieldname:str):
    """
    Check if an attribute field exists

    Args:
        featureclass (str): The path to the feature class.
        fieldname (str): The name of the field to check.

    Returns:
        bool: True if the field exists, False otherwise. 
    """  
    fieldList = arcpy.ListFields(featureclass, fieldname)
    fieldCount = len(fieldList)
 
    if (fieldCount == 1):
        return True
    else:
        return False
 
         

def addField_ifNotExists(featureclass:str, fieldname:str, type:str):
    """
    Adds a field to a feature class if the field does not already exist.

    Args:
        featureclass (str): The path to the feature class.
        fieldname (str): The name of the field to add.
        type (str): The data type of the field to add.
    """    
    if (not fieldExist(featureclass, fieldname)):
        arcpy.AddField_management(featureclass, fieldname, type)
        
# ------------------------------------------------------ #
# Class "LaserAttributes"
# ------------------------------------------------------ #

class LaserAttributes:
    """ 
    A class for computing attributes for laser segmented trees. 
    
    Attributes:
    -----------
    path : str
        path to filegdb containing the treecrown polygon and treetop pnt files 
        (output_path)
    crown_filename : str
        (v_treecrown_result) 
    top_filename : str
        (v_treetop_result)
     
    Methods:
    --------
    attr_lidarTile(self, tile_code):
        Adds the attribute 'lidar_tile' (TEXT) to the crown feature class.     
    attr_crownID(self):
        Adds the attribute 'crown_id_laser' (LONG) to the crown feature class.                
    attr_crownDiam(self):
        Adds the attribtue 'crown_diam' (FLOAT) to the crown feature class.  
    attr_crownArea(self):
        Adds the attribtue 'crown_area' (FLOAT) and 'crown_peri' (FLOAT) to the crown feature class. 
    join_crownID_toTop(self):
        Joins the attribtue 'crown_id_laser' (LONG) to the top feature class. 
    join_topAttr_toCrown(self):
        Joins the attribute 'tree_height' (SHORT) and 'tree_altit' (LONG) to the crown feature class. 
    attr_crownVolume(self):
        Adds the attribute 'tree_volume' (FlOAT) to the crown feature class. 
    """
    
    def __init__(self, path:str, crown_filename:str, top_filename:str):
        self.path = path
        self.crown_filename = crown_filename 
        self.top_filename = top_filename
    
    def attr_lidarTile(self, tile_code:str):
        """  
        Adds the attribute 'lidar_tile' (TEXT) to the crown feature class. 
            > Contains the <xxx_yyy> substring of the lidar tile name.
        """     
        
        format_tile_code = str(tile_code[:3] + "_" + tile_code[4:])
        arcpy.AddMessage(f"\t\tAdding the attribute <<lidar_tile>> with the corresponding tile code: {format_tile_code}... ")
        
        # Store information on neighbourhood code
        arcpy.AddField_management(self.crown_filename, "lidar_tile", "TEXT")
        arcpy.CalculateField_management(self.crown_filename, "lidar_tile", format_tile_code)
        #arcpy.AddField_management(self.top_filename, "lidar_tile", "TEXT")
        #arcpy.CalculateField_management(self.top_filename, "lidar_tile", format_tile_code)
        
        # Delete useless attributes
        arcpy.DeleteField_management(
            self.crown_filename, 
            ["Id", "gridcode", "ORIG_FID"]
        )
        
        # Delete useless attributes
        arcpy.DeleteField_management(
            self.top_filename, 
            ["Id", "gridcode", "ORIG_FID"]
        )
        
    def attr_crownID(self):
        """  
        Adds the attribute 'crown_id_laser' (LONG) to the crown feature class.
            > Computes crown id from OBJECTID.
        """ 
        arcpy.AddMessage(f"\tAdding the attribute <<crown_id_laser>> using the unique ObjectID number... ")
    
        arcpy.AddField_management(self.crown_filename, "crown_id_laser", "LONG")
        
        with arcpy.da.UpdateCursor(self.crown_filename, ["OBJECTID", "crown_id_laser"]) as cursor:
            for row in cursor:
                row[1] = row[0]
                cursor.updateRow(row)


    def attr_crownDiam(self):
        """
        Adds the attribtue 'crown_diam' (FLOAT) to the crown feature class. 
            > Computes the crown diameter as maximum length of the convex hull. 
        """
        arcpy.AddMessage(f"\tComputing the crown diameter as maximum length of the convex hull... ")
        v_mbg = os.path.join(self.path, "mbg_temp")
        arcpy.MinimumBoundingGeometry_management(
            self.crown_filename,
            v_mbg,
            "CONVEX_HULL", # tree_detection_v1 uses "CIRCLE"
            "NONE", 
            "", 
            "MBG_FIELDS"
        )
            
        arcpy.AddMessage(f"\tAdding the attribute <<crown_diam>>... ")
        arcpy.AddField_management(self.crown_filename, "crown_diam", "FLOAT")
        self.join_and_copy(
            t_dest=self.crown_filename,
            join_a_dest= "crown_id_laser", 
            t_src= v_mbg, 
            join_a_src= "crown_id_laser", 
            a_src=["MBG_Length"],
            a_dest=["crown_diam"]
        )
        arcpy.Delete_management(v_mbg)
        

    def attr_crownArea(self):
        """
        Adds the attribtue 'crown_area' (FLOAT) to the crown feature class. 
            > Computes the crown area by using the polygon shape area.
        Adds the attribute 'crown_peri' (FLOAT) to the crown feature class. 
            > Computes the crown perimeter by using the polygon shape length.
        """
        arcpy.AddMessage(f"\tComputing the crown area by using the polygon shape area... ")
        
        # Get the linear units of the feature layer's spatial reference
        linear_units = arcpy.Describe(self.crown_filename).spatialReference.linearUnitName

        # Calculate the area of each feature based on its geometry and write the result to the crown_area field
        if linear_units == "Meter":
            arcpy.AddMessage("\tThe linear unit to calculate the area is Meter")
            expression_area = "float(!SHAPE.area@squaremeters!)"
            expression_perimeter = "float(!SHAPE.length@meters!)"
        else:
            conversion_factor = arcpy.Describe(self.crown_filename).spatialReference.metersPerUnit
            expression_area = "float(!SHAPE.area@squaremeters!) * {}".format(conversion_factor)
            expression_perimeter = "float(!SHAPE.length@meters!) * {}".format(conversion_factor)

        arcpy.AddField_management(self.crown_filename, "crown_area", "FLOAT")
        arcpy.CalculateField_management(self.crown_filename, "crown_area", expression_area)

        # Compute crown perimeter
        arcpy.AddMessage(f"\tComputing the crown perimeter by using the shape length... ")
        arcpy.AddMessage(f"\tAdding the attribute <<crown_peri>>... ")
        arcpy.AddField_management(self.crown_filename, "crown_peri", "FLOAT")
        arcpy.CalculateField_management(self.crown_filename, "crown_peri", expression_perimeter)

    # join tree crown id. to tree points
    def join_crownID_toTop(self):
        """
        Joins the attribtue 'crown_id_laser' (LONG) to the top feature class. 
        """
        
        # temporary ID for tree points to avoid issues with join_and_copy()
        arcpy.AddMessage(f"\tAdding a temporary id 'top_id_laser' using ObjectID to tree top feature class... ")
        arcpy.AddField_management(self.top_filename, "top_id_laser", "LONG") 
        with arcpy.da.UpdateCursor(self.top_filename, ["OBJECTID", "tmp_id"]) as cursor:
            for row in cursor:
                row[1] = row[0]
                cursor.updateRow(row)    
        

        arcpy.AddMessage(f"\tJoining the tree crown id 'crown_id_laser' to the tree top feature class... ")
        v_join = os.path.join(self.path, "join_tmp")
        arcpy.SpatialJoin_analysis(
            self.top_filename,
            self.crown_filename, 
            v_join,
            "JOIN_ONE_TO_ONE", 
            "KEEP_ALL", 
            match_option="INTERSECT"
        )
        
        # Assign tree crown ID to tree points
        arcpy.AddField_management(self.top_filename, "crown_id_laser", "LONG")
        join_and_copy(
            self.top_filename, 
            "tmp_id", 
            v_join, 
            "tmp_id", 
            ["crown_id_laser"], 
            ["crown_id_laser"]
        )

        arcpy.Delete_management(v_join)
        #arcpy.DeleteField_management(self.top_filename, "tmp_id")
        
        # Copy tree_heigh, tree_altit from tree points to tree polygons
    def join_topAttr_toCrown(self):
        """
        Joins the attribute 'tree_height' (SHORT) to the crown feature class. 
        Joins the attribute 'tree_altit' (LONG) to the crown feature class. 
        """
        
        arcpy.AddMessage(f"\tJoining the tree top attributes: tree_height and tree_altit to the treecrown polygons... ")
        arcpy.AddField_management(self.crown_filename, "tree_height", "SHORT")
        arcpy.AddField_management(self.crown_filename, "tree_altit", "LONG")

        join_and_copy(
            self.crown_filename, 
            "crown_id_laser", 
            self.top_filename, 
            "crown_id_laser", 
            ["tree_height", "tree_altit"], 
            ["tree_height", "tree_altit"]
        )


    def attr_crownVolume(self):
        """
        Adds the attribute 'tree_volume' (FlOAT) to the crown feature class. 
        """
        # Calculate tree volume
        formula = str("tree volume =(1/3)π * (crown diameter/2)^2 * tree height")
        arcpy.AddMessage(f"\tComputing the crown volume by using the formula: \n\t{formula}")
        
        arcpy.AddField_management(self.crown_filename, "tree_volume", "FLOAT")
        arcpy.CalculateField_management(
        in_table=self.crown_filename,
        field="tree_volume", 
        expression="(1.0/3.0) * math.pi * ( !crown_diam! /2.0 ) * ( !crown_diam! /2.0) * float(!tree_height!)",
        expression_type="PYTHON_9.3", 
        code_block=""
    )
# ------------------------------------------------------ #
# Class "LaserAttributes"
# ------------------------------------------------------ #


# ------------------------------------------------------ #
# Class "LaserAttributes"
# ------------------------------------------------------ #