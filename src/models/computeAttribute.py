import arcpy
import os 

# project pacakge read the readme file on how to install it properly
from src import join_and_copy
from src import addField_ifNotExists
from src import calculateField_ifEmpty
from src import check_isNull

#print("test local import")

        
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
        arcpy.AddMessage("\n\tATTRIBUTE | lidar_tile:")
        arcpy.AddMessage(f"\t\tAdding the attribute <<lidar_tile>> with the corresponding tile code: {format_tile_code}... ")
        
        # Store information on neighbourhood code

        addField_ifNotExists(self.crown_filename, "lidar_tile", "TEXT")
        calculateField_ifEmpty(self.crown_filename, "lidar_tile", format_tile_code)
        
        # TODO delete calcField if fucntion works
        #arcpy.CalculateField_management(self.crown_filename, "lidar_tile", format_tile_code)
        #addField_ifNotExists(self.top_filename, "lidar_tile", "TEXT")
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
            > Only populates the field if it contains any null or empty values 
        """ 
        arcpy.AddMessage("\n\tATTRIBUTE | crown_id_laser:")
        arcpy.AddMessage(f"\tAdding the attribute <<crown_id_laser>> using the unique ObjectID number... ")
        in_table = self.crown_filename      
        field = "crown_id_laser"
        addField_ifNotExists(in_table, field, "LONG")
        
        # Check if the crown_id_laser field contains any null or empty values
        if check_isNull(in_table, field) == True:
            with arcpy.da.UpdateCursor(in_table, ["OBJECTID", field]) as cursor:
                for row in cursor:
                    row[1] = row[0]
                    cursor.updateRow(row)
        else:      
            arcpy.AddMessage(f"\tAll rows in field are already populated. Exiting function.")

        


    def attr_crownDiam(self):
        """
        Adds the attribtue 'crown_diam' (FLOAT) to the crown feature class. 
            > Computes the crown diameter as maximum length of the convex hull. 
        """
        arcpy.AddMessage("\n\tATTRIBUTE | crown_diam:")
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
        
        in_table = self.crown_filename
        field = "crown_diam"
            
        arcpy.AddMessage(f"\tAdding the attribute <<crown_diam>>... ")
        addField_ifNotExists(in_table, field, "FLOAT")
        
        if check_isNull(in_table, field) == True:
            join_and_copy(
                t_dest=self.crown_filename,
                join_a_dest= "crown_id_laser", 
                t_src= v_mbg, 
                join_a_src= "crown_id_laser", 
                a_src=["MBG_Length"],
                a_dest=["crown_diam"]
            )
            arcpy.Delete_management(v_mbg)
        else:
            arcpy.AddMessage(f"\tAll rows in field are already populated. Exiting function.")

        

    def attr_crownArea(self):
        """
        Adds the attribtue 'crown_area' (FLOAT) to the crown feature class. 
            > Computes the crown area by using the polygon shape area.
        Adds the attribute 'crown_peri' (FLOAT) to the crown feature class. 
            > Computes the crown perimeter by using the polygon shape length.
        """
        arcpy.AddMessage("\n\tATTRIBUTE | crown_area:")
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

        addField_ifNotExists(self.crown_filename, "crown_area", "FLOAT")
        calculateField_ifEmpty(self.crown_filename, "crown_area", expression_area)
        #arcpy.CalculateField_management(self.crown_filename, "crown_area", expression_area)

        # Compute crown perimeter
        arcpy.AddMessage("\n\tATTRIBUTE | crown_peri:")
        arcpy.AddMessage(f"\tComputing the crown perimeter by using the shape length... ")
        arcpy.AddMessage(f"\tAdding the attribute <<crown_peri>>... ")
        addField_ifNotExists(self.crown_filename, "crown_peri", "FLOAT")
        calculateField_ifEmpty(self.crown_filename, "crown_peri", expression_perimeter)
        #arcpy.CalculateField_management(self.crown_filename, "crown_peri", expression_perimeter)

    # join tree crown id. to tree points
    def join_crownID_toTop(self):
        """
        Joins the attribtue 'crown_id_laser' (LONG) to the top feature class. 
        """
        
        # temporary ID for tree points to avoid issues with join_and_copy()
        arcpy.AddMessage(f"\tAdding a temporary id 'top_id_laser' using ObjectID to tree top feature class... ")
        arcpy.AddField_management(self.top_filename, "tmp_id", "LONG") 
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
            
        
    # join tree_heigh, tree_altit from tree points to tree polygons
    def join_topAttr_toCrown(self):
        """
        Joins the attribute 'tree_height' (SHORT) to the crown feature class. 
        Joins the attribute 'tree_altit' (LONG) to the crown feature class. 
        """
        
        arcpy.AddMessage("\t\tJOIN ATTRIBUTE | tree_heigth and tree_altit to crown feature class:")
        arcpy.AddMessage(f"\tJoining the tree top attributes: tree_height and tree_altit to the treecrown polygons... ")
        addField_ifNotExists(self.crown_filename, "tree_height", "FLOAT")
        addField_ifNotExists(self.crown_filename, "tree_altit", "FLOAT")
        
        # Check if the  field contains any null or empty values
        if check_isNull(self.crown_filename, "tree_height") or check_isNull(self.crown_filename, "tree_altit") == True:
            # populate field with join
            join_and_copy(
                self.crown_filename, 
                "crown_id_laser", 
                self.top_filename, 
                "crown_id_laser", 
                ["tree_height", "tree_altit"], 
                ["tree_height", "tree_altit"]
            )
        else:
            arcpy.AddMessage(f"\tAll rows in field are already populated. Exiting function.")
            

    def attr_crownVolume(self):
        """
        Adds the attribute 'tree_volume' (FlOAT) to the crown feature class. 
        """
        
        addField_ifNotExists(self.crown_filename, "tree_volume", "FLOAT")
        # Calculate tree volume
        formula = str("tree volume =(1/3)π * (crown diameter/2)^2 * tree height")
        arcpy.AddMessage(f"\tComputing the crown volume by using the formula: \n\t{formula}")

        
        expression = "(1.0/3.0) * math.pi * ( !crown_diam! /2.0 ) * ( !crown_diam! /2.0) * float(!tree_height!)"
        calculateField_ifEmpty(
            in_table=self.crown_filename,
            field="tree_volume", 
            expression=expression,
        )
        
      
        
# ------------------------------------------------------ #
# Class "LaserAttributes"
# ------------------------------------------------------ #


# ------------------------------------------------------ #
# Class "LaserAttributes"
# ------------------------------------------------------ #

