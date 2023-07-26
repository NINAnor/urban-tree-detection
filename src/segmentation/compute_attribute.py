import arcpy
import os 
import logging

from src import arcpy_utils as au
from src import logger

logger.setup_logger(logfile=False)
logger = logging.getLogger(__name__)        

# ------------------------------------------------------ #
# Class "LaserAttributes"
# FLOAT: up to 6 decimal places
# DOUBLE: up to 15 decimal places
# LONG: up to 10 digits
# SHORT: up to 5 digits
# GUID: 38 characters
# TEXT: 255 characters
# ------------------------------------------------------ #

class LaserAttributes:
    """ 
    A class for computing attributes for laser segmented trees. 
    
    Attributes:
    -----------
    path : str
        path to the filegdb containing the crown and top feature classes
    crown_filename : str
        filename of the crown feature class
    top_filename : str
        filename of the top feature class   
              
    Methods:
    --------
    attr_lidarTile(self, tile_code):
        Adds the attribute 'lidar_tile' (TEXT) to the crown feature class.     
    attr_crownID(self):
        Adds the attribute 'crown_id' (TEXT) to the crown feature class.                
    attr_crownDiam(self):
        Adds the attribtue 'crown_diam' (FLOAT) to the crown feature class.  
    attr_crownArea(self):
        Adds the attribtue 'crown_area' (FLOAT) and 'crown_peri' (FLOAT) to the crown feature class. 
    join_crownID_toTop(self):
        Joins the attribtue 'crown_id' (TEXT) to the top feature class. 
    join_topAttr_toCrown(self):
        Joins the attribute 'tree_height_laser' (SHORT) and 'tree_altit' (LONG) to the crown feature class. 
    attr_crownVolume(self):
        Adds the attribute 'tree_volume' (FlOAT) to the crown feature class. 
    """
    
    def __init__(self, path:str, crown_filename:str, top_filename:str):
        self.path = path
        self.crown_filename = crown_filename 
        self.top_filename = top_filename
        
    def delete_adminAttr(self):
        """
        Deletes the attributes 'Id', 'gridcode', 'ORIG_FID' from the crown and top feature class. 
        """
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
    
    def attr_lidarTile(self, tile_code:str):
        """  
        Adds the attribute 'lidar_tile' (TEXT) to the crown feature class. 
            > Contains the <xxx_yyy> substring of the lidar tile name.
        """     
        
        format_tile_code = str(tile_code[:3] + "_" + tile_code[4:])
        logger.info("\tATTRIBUTE | kartblad:")
        logger.info(f"\tAdding the attribute <<kartblad>> with the corresponding tile code: {format_tile_code}... ")
        
        # Store information on lidar tile 
        au.addField_ifNotExists(self.crown_filename, "kartblad", "TEXT")
        au.calculateField_ifEmpty(self.crown_filename, "kartblad", format_tile_code)

         
    def attr_neighbCode(self, n_code):
        """
        Adds the attribute 'bydelnummer' (TEXT) to the crown feature class.
        """
        
        logger.info("\tATTRIBUTE | bydelnummer:")     
        # add bydelcode to crown feature class
        logger.info(f"\tAdding the attribute <<bydelnummer>> with value {n_code} to crown features... ")
        au.addField_ifNotExists(self.crown_filename, "bydelnummer", "TEXT")
        au.calculateField_ifEmpty(self.crown_filename, "bydelnummer", n_code)
        
        # add bydelcode to top feature class
        logger.info(f"\tAdding the attribute <<bydelnummer>> with value {n_code} to top features... ")  
        au.addField_ifNotExists(self.top_filename, "bydelnummer", "TEXT")
        au.calculateField_ifEmpty(self.top_filename, "bydelnummer", n_code)
    
    def attr_segMethod(self, segmentation_method):
        """
        Adds the attribute 'seg_method' (TEXT) to the crown feature class.

        Args:
            method (str): watershed or other
        """
        
        logger.info("\tATTRIBUTE | seg_method:")
        au.addField_ifNotExists(self.crown_filename, "seg_method", "TEXT")
        au.addField_ifNotExists(self.top_filename, "seg_method", "TEXT")
       
        au.calculateField_ifEmpty(self.crown_filename, "seg_method", segmentation_method)
        au.calculateField_ifEmpty(self.top_filename, "seg_method", segmentation_method)
            
    def attr_globalID(self):
        """ 
        Compute a GlobalID for crown polygons and add it to the crown feature class as GlobalID 
        and as Foreign Key ID (FKID_crown) to the top feature class.
        
        Prerequisite: 
        - the crown feature class must have a field 'crown_id' with unique values
        - the top feature class must have a field 'crown_id' with unique values
        """
        arcpy.AddGlobalIDs_management(self.crown_filename)
        
        # add GlobalID to top feature class if top intersects with crown polygon
        au.addField_ifNotExists(self.top_filename, "FKID_crown", "GUID")
        
        au.join_and_copy(
            t_dest=self.top_filename,
            join_a_dest= "crown_id", 
            t_src= self.crown_filename, 
            join_a_src= "crown_id", 
            a_src=["GlobalID"],
            a_dest=["FKID_crown"]
        )
        
    def attr_crownID(self, nb_code:str):
        """  
        Adds the attribute 'crown_id' (TEXT) to the crown feature class.
            > Computes crown id from OBJECTID.
            > Only populates the field if it contains any null or empty values 
        """ 
        logger.info("\tATTRIBUTE | crown_id:")
        au.addField_ifNotExists(self.crown_filename , "crown_id", "TEXT")
        
        # Check if the crown_id field contains any null or empty values
        if au.check_isNull(self.crown_filename, "crown_id") == True:
            with arcpy.da.UpdateCursor(self.crown_filename, ["OBJECTID", "crown_id"]) as cursor:
                for row in cursor:
                    # format id to <bydelcode>_<OBJECTID>
                    row[1] = "b_" + str(nb_code) + "_" + str(row[0])
                    #row[1] = row[0]
                    cursor.updateRow(row)
        else:      
            logger.info(f"\tAll rows in field are already populated. Exiting function.")
            
    def attr_crownArea(self):
        """
        Calculates the crown area and perimeter attributes and adds them to the crown feature class.
        
        -----------------------------------
        crown_area (SHAPE_Area): the area of the resulting polygon
        crown_peri (SHAPE_Length): the perimeter of the resulting polygon
        outlier_CA: classifies the tree crown in normal (0), mild outlier (1) or extreme outlier (2).
            - normal (0) if crown area <= 250 m2
            - mild outlier (1) if crown area > 250 m2
            - extreme outlier (2) if crown area > 350 m2
        -----------------------------------
        """
        logger.info("\tATTRIBUTE | crown_area:")
        logger.info(f"\tComputing the crown area by using the polygon shape area... ")
        logger.info("\tATTRIBUTE | crown_peri:")
        logger.info(f"\tComputing the crown perimeter by using the shape length... ")
               
        # Get the linear units of the feature layer's spatial reference
        linear_units = arcpy.Describe(self.crown_filename).spatialReference.linearUnitName

        # Calculate the area of each feature based on its geometry and write the result to the crown_area field
        if linear_units == "Meter":
            logger.info("\tThe linear unit to calculate the area is Meter")
            expression_area = "float(!SHAPE.area@squaremeters!)"
            expression_perimeter = "float(!SHAPE.length@meters!)"
        else:
            conversion_factor = arcpy.Describe(self.crown_filename).spatialReference.metersPerUnit
            expression_area = "float(!SHAPE.area@squaremeters!) * {}".format(conversion_factor)
            expression_perimeter = "float(!SHAPE.length@meters!) * {}".format(conversion_factor)


        field_list = ["crown_area", "crown_peri"]
        for field in field_list:
            au.addField_ifNotExists(self.crown_filename, field, "FLOAT")
            
        au.addField_ifNotExists(self.crown_filename, "outlier_CA", "SHORT")

        au.calculateField_ifEmpty(self.crown_filename, "crown_area", expression_area)
        au.calculateField_ifEmpty(self.crown_filename, "crown_peri", expression_perimeter)
        
        
        if au.check_isNull(self.crown_filename, "outlier_CA") == True:
            with arcpy.da.UpdateCursor(self.crown_filename, ["crown_area", "outlier_CA"]) as cursor:
                for row in cursor:
                    if row[0] <= 250:
                        row[1] = 0
                    elif row[0] > 250 and row[0] <= 350:
                        row[1] = 1
                    else:
                        row[1] = 2
                    cursor.updateRow(row)
        else:
            logger.info(f"\tAll rows in field are already populated. Exiting function.")
            
        au.round_fields_two_decimals(self.crown_filename, ["crown_area", "crown_peri"])
    
    def attr_enclosingCircle(self, keep_temp:bool):
        """
        Calculates the enclosing circle geometry attributes and adds them to the crown feature class.
        The ratio between Crown Area / Enclosing Cirlce Area identifies elongated polygons. 
        
        -----------------------------------
        EC_diam (MBG_Diameter): the diameter of the enclosing circle (can be used to estimate crown diameter)
        EC_area (Shape_Area): the area of the resulting circle
        ratio_CA_ECA: ratio crown area / enclosing circle area
        outlier_ratio_CA_ECA: classifies the tree crown in normal (0), mild outlier (1) or extreme outlier (2). 
            - normal (0) if ratio crown area / enclosing circle area >= 0.25
            - mild outlier (1) if ratio crown area / enclosing circle area < 0.25
            - extreme outlier (2) if ratio crown area / enclosing circle area < 0.02
        -----------------------------------
        """   
        
        logger.info("\tATTRIBUTE | EC_diam:")
        logger.info(f"\tComputing the enclosing circle diameter... ")
        logger.info("\tATTRIBUTE | EC_area:")
        logger.info(f"\tComputing the enclosing circle area... ")
        logger.info("\tATTRIBUTE | ratio_CA_ECA:")
        logger.info(f"\tComputing the ratio crown area / enclosing circle area... ")
        logger.info("\tATTRIBUTE | outlier_ratio_CA_ECA:")
        logger.info(f"\tClassifying the tree crown as:\n \
                - normal (0) if ratio crown area / enclosing circle area >= 0.25\n \
                - mild outlier (1) if ratio crown area / enclosing circle area < 0.25\n \
                - extreme outlier (2) if ratio crown area / enclosing circle area < 0.02... ")
        
        v_enclosing_circle = os.path.join(self.path, "enclosing_circle_temp")

        # calculate enclosing circle
        arcpy.MinimumBoundingGeometry_management(
            self.crown_filename,
            v_enclosing_circle,
            "CIRCLE", 
            "NONE", 
            "", 
            "MBG_FIELDS"
        )
        
        # add attribute fields
        field_list = ["EC_diam", "EC_area", "ratio_CA_ECA"]
        
        for field in field_list:
            au.addField_ifNotExists(self.crown_filename, field, "FLOAT")
            
        au.addField_ifNotExists(self.crown_filename, "outlier_ratio_CA_ECA", "SHORT")
        
        # fill attribute fields
        if au.check_isNull(self.crown_filename, "EC_diam") == True \
            or au.check_isNull(self.crown_filename, "EC_area") == True:
            # EC_diam and EC_area
            au.join_and_copy(
                t_dest=self.crown_filename,
                join_a_dest= "crown_id", 
                t_src= v_enclosing_circle, 
                join_a_src= "crown_id", 
                a_src=["MBG_Diameter", "Shape_Area"],
                a_dest=["EC_diam", "EC_area"]
            )
            
            # calculate ratio crown area / enclosing circle area
            arcpy.CalculateField_management(
                in_table=self.crown_filename, 
                field="ratio_CA_ECA", 
                expression="!crown_area! / !EC_area!",
                expression_type="PYTHON3"
                )
        else:
            logger.info(f"\tAll rows in field are already populated. Exiting function.")    
            # classify tree crown as normal, mild outlier or extreme outlier

        if au.check_isNull(self.crown_filename, "outlier_ratio_CA_ECA") == True:
            with arcpy.da.UpdateCursor(self.crown_filename, ["ratio_CA_ECA", "outlier_ratio_CA_ECA"]) as cursor:
                for row in cursor:
                    if row[0] >= 0.25:
                        row[1] = 0
                    elif row[0] < 0.25 and row[0] >= 0.02:
                        row[1] = 1
                    else:
                        row[1] = 2
                    cursor.updateRow(row)

        else:
            logger.info(f"\tAll rows in field are already populated. Exiting function.")
            
        if keep_temp == False:
            arcpy.Delete_management(v_enclosing_circle)   
        
        au.round_fields_two_decimals(self.crown_filename, ["EC_diam", "EC_area", "ratio_CA_ECA"])
    
    def attr_convexHull(self, keep_temp:bool):
        """
        Calculates the convex hull attributes and adds them to the crown feature class.

        -----------------------------------
        CH_length (MBG_Length): longest distance between any two vertices of the convex hull (crown diameter in this case)
        CH_width (MBG_Width): shortest distance between any two vertices of the convex hull
        CH_area (Shape_Area): convex hull area
        ratio_CA_CHA: ratio crown area / convex hull area
        outlier_ratio_CA_CHA: classifies the tree crown in normal (0), mild outlier (1) or extreme outlier (2). 
            - normal (0) if ratio crown area / convex hull area >= 0.7
            - mild outlier (1) if ratio crown area / convex hull area < 0.7
            - extreme outlier (2) if ratio crown area / convex hull area < 0.6
        -----------------------------------
        """
        
        logger.info("\tATTRIBUTE | CH_length:")
        logger.info(f"\tComputing the convex hull length... ")
        logger.info("\tATTRIBUTE | CH_width:")
        logger.info(f"\tComputing the convex hull width... ")
        logger.info("\tATTRIBUTE | CH_area:")
        logger.info(f"\tComputing the convex hull area... ")
        logger.info("\tATTRIBUTE | ratio_CA_CHA:")
        logger.info(f"\tComputing the ratio crown area / convex hull area... ")
        logger.info("\tATTRIBUTE | outlier_ratio_CA_CHA:")
        logger.info(f"\tClassifying the tree crown as:\n \
                - normal (0) if ratio crown area / convex hull area >= 0.7\n \
                - mild outlier (1) if ratio crown area / convex hull area < 0.7\n \
                - extreme outlier (2) if ratio crown area / convex hull area < 0.6... ")
        
        v_convex_hull = os.path.join(self.path, "convex_hull_temp")
        
        field_list = ["CH_length", "CH_width", "CH_area", "ratio_CA_CHA"]
        
        for field in field_list:
            au.addField_ifNotExists(self.crown_filename, field, "FLOAT")
        
        au.addField_ifNotExists(self.crown_filename, "outlier_ratio_CA_CHA", "SHORT")
        
        arcpy.MinimumBoundingGeometry_management(
            self.crown_filename,
            v_convex_hull,
            "CONVEX_HULL", 
            "NONE", 
            "", 
            "MBG_FIELDS"
        )
        
        # fill attribute fields
        if au.check_isNull(self.crown_filename, field) == True:
            # CH_length, CH_width and CH_area
            au.join_and_copy(
                t_dest=self.crown_filename,
                join_a_dest= "crown_id", 
                t_src= v_convex_hull, 
                join_a_src= "crown_id", 
                a_src=["MBG_Length", "MBG_Width", "Shape_Area"],
                a_dest=["CH_length", "CH_width", "CH_area"]
            )
            #arcpy.Delete_management(v_convex_hull)
        
        # calculate ratio crown area / convex hull area
            arcpy.CalculateField_management(
                in_table=self.crown_filename, 
                field="ratio_CA_CHA", 
                expression="!crown_area! / !CH_area!",
                expression_type="PYTHON3"
                )
            
            with arcpy.da.UpdateCursor(self.crown_filename, ["ratio_CA_CHA", "outlier_ratio_CA_CHA"]) as cursor:
                for row in cursor:
                    if row[0] >= 0.7:
                        row[1] = 0
                    elif row[0] < 0.7 and row[0] >= 0.6:
                        row[1] = 1
                    else:
                        row[1] = 2
                    cursor.updateRow(row)

        else:
            logger.info(f"\tAll rows in field are already populated. Exiting function.")
        
        if keep_temp == False:
            arcpy.Delete_management(v_convex_hull)   
        
        au.round_fields_two_decimals(self.crown_filename, ["CH_length", "CH_width", "CH_area", "ratio_CA_CHA"])      
        
    def attr_envelope(self, keep_temp:bool):
        """
        Calculates the envelope attributes and adds them to the crown feature class.

        -----------------------------------
        EV_length (MBG_Length): the lenght of the longer side of the resulting rectangle
        EV_width (MBG_Width): the lenght of the shorter side of the resulting rectangle
        EV_area (Shape_Area): envelope area
        EV_angle (FLOAT): the dominant angle of the envelope, in decimal degrees. 
        NS_width: the width of the crown in the north-south direction (0 deg)
        ES_width: the width of the crown in the east-west direction (90 or -90 deg)
        - if angle -90 or 90 degrees, NS_width = envelope length and ES_width = envelope width
        - elif angle 0 or 180 degrees, NS_width = envelope width and ES_width = envelope length
        - else NS_width = None and ES_width = None
        -----------------------------------
        """

        logger.info("\tATTRIBUTE | EV_length:")
        logger.info(f"\tComputing the envelope length... ")
        logger.info("\tATTRIBUTE | EV_width:")
        logger.info(f"\tComputing the envelope width... ")
        logger.info("\tATTRIBUTE | EV_area:")
        logger.info(f"\tComputing the envelope area... ")
        
        v_envelope = os.path.join(self.path, "envelope_temp")
        arcpy.MinimumBoundingGeometry_management(
            self.crown_filename,
            v_envelope,
            "ENVELOPE",
            "NONE", 
            "", 
            "MBG_FIELDS"
        )
        
        field_list_crown = ["EV_length", "EV_width", "EV_area", "EV_angle", "NS_width", "ES_width"]
        
        for field in field_list_crown:
            au.addField_ifNotExists(self.crown_filename, field, "FLOAT")
        
        field_list_envelop = ["EV_angle", "NS_width", "ES_width"]
        for field in field_list_envelop:
            au.addField_ifNotExists(v_envelope, field, "FLOAT")
        

        
        # fill attribute fields
        if au.check_isNull(self.crown_filename, "EV_length") == True \
            or au.check_isNull(self.crown_filename, "EV_width") == True \
            or au.check_isNull(self.crown_filename, "EV_area") == True:
            # CH_length, CH_width and CH_area
            au.join_and_copy(
                t_dest=self.crown_filename,
                join_a_dest= "crown_id", 
                t_src= v_envelope, 
                join_a_src= "crown_id", 
                a_src=["MBG_Length", "MBG_Width", "Shape_Area"],
                a_dest=["EV_length", "EV_width", "EV_area"]
            )
            #arcpy.Delete_management(v_convex_hull)

        else:
            logger.info(f"\tAll rows in field are already populated. Exiting function.")
            
        # Calculate angle and NS and ES width      
        codeblock = """def classify_envAngle(envelope_width, envelope_length, envelope_angle, computed_measure):
                        eps = 1e-2
                        if abs(envelope_angle+90) < eps:
                            if computed_measure == "NS":
                                return envelope_length
                            elif computed_measure == "EW":
                                return envelope_width
                            else:    
                                return None
                        elif abs(envelope_angle) < eps:
                            if computed_measure == "NS":
                                return envelope_width
                            elif computed_measure == "EW":
                                return envelope_length
                            else:    
                                return None
                        else:
                            return None
                    """  
        
        if au.check_isNull(self.crown_filename, "EV_angle") == True:
            arcpy.CalculatePolygonMainAngle_cartography(v_envelope, "EV_angle", "GEOGRAPHIC")        
            arcpy.CalculateField_management(
                in_table = v_envelope, 
                field = "NS_width", 
                expression = "classify_envAngle(!MBG_Width!, !MBG_Length!, !EV_angle!, 'NS')",
                expression_type= "PYTHON_9.3",
                code_block= codeblock
            )
            arcpy.CalculateField_management(
                in_table = v_envelope,
                field = "ES_width",
                expression = "classify_envAngle(!MBG_Width!, !MBG_Length!, !EV_angle!, 'EW')",
                expression_type= "PYTHON_9.3",
                code_block= codeblock
            )
            # join measures to corresponding crown polygon
            au.join_and_copy(
                t_dest=self.crown_filename,
                join_a_dest= "crown_id", 
                t_src= v_envelope, 
                join_a_src= "crown_id", 
                a_src=["EV_angle", "NS_width", "ES_width"],
                a_dest=["EV_angle", "NS_width", "ES_width"]
            )            
            
        else: 
            logger.info(f"\tAll rows in field are already populated. Exiting function.")
        
        if keep_temp == False:
            arcpy.Delete_management(v_envelope)
            
        au.round_fields_two_decimals(self.crown_filename, ["EV_length", "EV_width", "EV_area", "EV_angle", "NS_width", "ES_width"])
        
    def attr_crownDiam(self):
        """
        Adds the attribtue 'crown_diam' (FLOAT) to the crown feature class. 
            > Computes the crown diameter as maximum length of the convex hull. 
        """
        logger.info("\tATTRIBUTE | crown_diam:")
        logger.info(f"\tComputing the crown diameter as maximum length of the convex hull... ")
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
            
        logger.info(f"\tAdding the attribute <<crown_diam>>... ")
        au.addField_ifNotExists(in_table, field, "FLOAT")
        
        if au.check_isNull(in_table, field) == True:
            au.join_and_copy(
                t_dest=self.crown_filename,
                join_a_dest= "crown_id", 
                t_src= v_mbg, 
                join_a_src= "crown_id", 
                a_src=["MBG_Length"],
                a_dest=["crown_diam"]
            )
            arcpy.Delete_management(v_mbg)
        else:
            logger.info(f"\tAll rows in field are already populated. Exiting function.")
        
        au.round_fields_two_decimals(self.crown_filename, ["crown_diam"])

    # join tree crown id. to tree points
    def join_crownID_toTop(self):
        """
        Joins the attribtue 'crown_id' (LONG) to the top feature class. 
        """
        
        # temporary ID for tree points to avoid issues with au.join_and_copy()
        logger.info(f"\tAdding a temporary id 'top_id' using ObjectID to tree top feature class... ")
        arcpy.AddField_management(self.top_filename, "tmp_id", "LONG") 
        with arcpy.da.UpdateCursor(self.top_filename, ["OBJECTID", "tmp_id"]) as cursor:
            for row in cursor:
                row[1] = row[0]
                cursor.updateRow(row)    
        
        logger.info(f"\tJoining the tree crown id 'crown_id' to the tree top feature class... ")
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
        arcpy.AddField_management(self.top_filename, "crown_id", "TEXT")
        au.join_and_copy(
            self.top_filename, 
            "tmp_id", 
            v_join, 
            "tmp_id", 
            ["crown_id"], 
            ["crown_id"]
        )

        arcpy.Delete_management(v_join)
        #arcpy.DeleteField_management(self.top_filename, "tmp_id")
        
    
    def attr_topHeight(self, v_top, r_chm_h:str, r_dtm:str, str_multiplier: str):
        """  
        Adds the attribute 'tree_height_laser' (SHORT) and 'tree_altit' (LONG) to the top feature class.
            > Extract tree height (from CHM) and tree altitude (from DSM) to tree points
        """ 
        logger.info("\tATTRIBUTE | tree_height_laser and tree_altit:")
        logger.info(f"\tExtracting tree height (from CHM) and tree altitude (from DTM) to tree points... ")
        
        # Extract tree height (from CHM) and tree altitude (from DTM) to tree points as FLOAT values 
        arcpy.gp.ExtractMultiValuesToPoints_sa(
            v_top,
            "'{}' tree_height_laser_int;'{}' tree_altit_int".format(r_chm_h, r_dtm),
            "NONE"
            )       

        # if raster is a integer and contains 100x the value of the original raster, divide by 100
        multiplier = str_multiplier.replace("x", "")
        
        logger.info("\tCHM and DSM rasters are integer values multiplied by <{}>. \
                Canopy Height Values are extracted and divided by\
                {}... ".format(str_multiplier, multiplier))
        
        # divide tree_height_laser and tree_alittude by multiplier if raster is integer
        arcpy.management.CalculateField(
            in_table=v_top,
            field="tree_height_laser",
            expression="!tree_height_laser_int! /{}".format(multiplier),
            expression_type="PYTHON3",
            code_block="",
            field_type="FLOAT",
            enforce_domains="NO_ENFORCE_DOMAINS"
        )
        
        arcpy.management.CalculateField(
            in_table=v_top,
            field="tree_altit",
            expression="!tree_altit_int! /{}".format(multiplier),
            expression_type="PYTHON3",
            code_block="",
            field_type="FLOAT",
            enforce_domains="NO_ENFORCE_DOMAINS"
        )
        
        # detelete int fields
        arcpy.DeleteField_management(v_top, ["tree_height_laser_int", "tree_altit_int"])
        au.round_fields_two_decimals(v_top, ["tree_height_laser", "tree_altit"])  
            
    # join tree_heigh, tree_altit from tree points to tree polygons
    def join_topAttr_toCrown(self):
        """
        Joins the attribute 'tree_height_laser' (SHORT) to the crown feature class. 
        Joins the attribute 'tree_altit' (LONG) to the crown feature class. 
        """
        
        logger.info("\t\tJOIN ATTRIBUTE | tree_heigth and tree_altit to crown feature class:")
        logger.info(f"\tJoining the tree top attributes: tree_height_laser and tree_altit to the crown polygons... ")
        au.addField_ifNotExists(self.crown_filename, "tree_height_laser", "FLOAT")
        au.addField_ifNotExists(self.crown_filename, "tree_altit", "FLOAT")
        
        # Check if the  field contains any null or empty values
        if au.check_isNull(self.crown_filename, "tree_height_laser") or au.check_isNull(self.crown_filename, "tree_altit") == True:
            # populate field with join
            au.join_and_copy(
                self.crown_filename, 
                "crown_id", 
                self.top_filename, 
                "crown_id", 
                ["tree_height_laser", "tree_altit"], 
                ["tree_height_laser", "tree_altit"]
            )
        else:
            logger.info(f"\tAll rows in field are already populated. Exiting function.")
        
        au.round_fields_two_decimals(self.crown_filename, ["tree_height_laser", "tree_altit"])

    def attr_crownVolume(self):
        """
        Adds the attribute 'tree_volume' (FlOAT) to the crown feature class. 
        """
        
        au.addField_ifNotExists(self.crown_filename, "tree_volume", "FLOAT")
        # Calculate tree volume
        formula = str("tree volume =(1/3)π * (crown diameter/2)^2 * tree height")
        logger.info(f"\tComputing the crown volume by using the formula: \t{formula}")

        
        expression = "(1.0/3.0) * math.pi * ( !crown_diam! /2.0 ) * ( !crown_diam! /2.0) * float(!tree_height_laser!)"
        au.calculateField_ifEmpty(
            in_table=self.crown_filename,
            field="tree_volume", 
            expression=expression,
        )
        
        au.round_fields_two_decimals(self.crown_filename, ["tree_volume"])
        # round attribute to 2 decimals
        
        
        
        
# ------------------------------------------------------ #
# Class "LaserAttributes"
# ------------------------------------------------------ #


# ------------------------------------------------------ #
# Class "LaserAttributes"
# ------------------------------------------------------ #
