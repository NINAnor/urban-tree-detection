import arcpy
import os
import logging

from src import arcpy_utils as au
from src import logger

logger.setup_logger(logfile=False)
logger = logging.getLogger(__name__)

# ------------------------------------------------------ #
# FLOAT: up to 6 decimal places
# DOUBLE: up to 15 decimal places
# LONG: up to 10 digits
# SHORT: up to 5 digits
# GUID: 38 characters
# TEXT: 255 characters
# ------------------------------------------------------ #

class AdminAttributes:
    """
    A class for computing administrative attributes.

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
    - attr_GlobalID(self)
    - attr_crownID(self, nb_code)
    - join_crownID_toTop(self)
    - attr_neighbCode(self, n_code)
    - delete_adminAttr(self)
  
    """
    
    def attr_GlobalID(self):
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
            join_a_dest="crown_id",
            t_src=self.crown_filename,
            join_a_src="crown_id",
            a_src=["GlobalID"],
            a_dest=["FKID_crown"],
        )

    def attr_crownID(self, nb_code: str):
        """
        Adds the attribute 'crown_id' (TEXT) to the crown feature class.
            > Computes crown id from OBJECTID.Gl
            > Only populates the field if it contains any null or empty values
        """
        logger.info("\tATTRIBUTE | crown_id:")
        au.addField_ifNotExists(self.crown_filename, "crown_id", "TEXT")

        # Check if the crown_id field contains any null or empty values
        if au.check_isNull(self.crown_filename, "crown_id") == True:
            with arcpy.da.UpdateCursor(
                self.crown_filename, ["OBJECTID", "crown_id"]
            ) as cursor:
                for row in cursor:
                    # format id to <bydelcode>_<OBJECTID>
                    row[1] = "b_" + str(nb_code) + "_" + str(row[0])
                    # row[1] = row[0]
                    cursor.updateRow(row)
        else:
            logger.info(
                f"\tAll rows in field are already populated. Exiting function."
            )
    
    def join_crownID_toTop(self):
        """
        Joins the attribtue 'crown_id' (LONG) to the top feature class.
        """

        # temporary ID for tree points to avoid issues with au.join_and_copy()
        logger.info(
            f"\tAdding a temporary id 'top_id' using ObjectID to tree top feature class... "
        )
        arcpy.AddField_management(self.top_filename, "tmp_id", "LONG")
        with arcpy.da.UpdateCursor(
            self.top_filename, ["OBJECTID", "tmp_id"]
        ) as cursor:
            for row in cursor:
                row[1] = row[0]
                cursor.updateRow(row)

        logger.info(
            f"\tJoining the tree crown id 'crown_id' to the tree top feature class... "
        )
        v_join = os.path.join(self.path, "join_tmp")
        arcpy.SpatialJoin_analysis(
            self.top_filename,
            self.crown_filename,
            v_join,
            "JOIN_ONE_TO_ONE",
            "KEEP_ALL",
            match_option="INTERSECT",
        )

        # Assign tree crown ID to tree points
        arcpy.AddField_management(self.top_filename, "crown_id", "TEXT")
        au.join_and_copy(
            self.top_filename,
            "tmp_id",
            v_join,
            "tmp_id",
            ["crown_id"],
            ["crown_id"],
        )

        arcpy.Delete_management(v_join)
        # arcpy.DeleteField_management(self.top_filename, "tmp_id")

    def attr_neighbCode(self, n_code):
        """
        Adds the attribute 'bydelnummer' (TEXT) to the crown feature class.
        """

        logger.info("\tATTRIBUTE | bydelnummer:")
        # add bydelcode to crown feature class
        logger.info(
            f"\tAdding the attribute <<bydelnummer>> with value {n_code} to crown features... "
        )
        au.addField_ifNotExists(self.crown_filename, "bydelnummer", "TEXT")
        au.calculateField_ifEmpty(self.crown_filename, "bydelnummer", n_code)

        # add bydelcode to top feature class
        logger.info(
            f"\tAdding the attribute <<bydelnummer>> with value {n_code} to top features... "
        )
        au.addField_ifNotExists(self.top_filename, "bydelnummer", "TEXT")
        au.calculateField_ifEmpty(self.top_filename, "bydelnummer", n_code)
        
    def delete_adminAttr(self):
        """
        Deletes the attributes 'Id', 'gridcode', 'ORIG_FID' from the crown and top feature class.
        """
        # Delete useless attributes
        arcpy.DeleteField_management(
            self.crown_filename, ["Id", "gridcode", "ORIG_FID"]
        )

        # Delete useless attributes
        arcpy.DeleteField_management(
            self.top_filename, ["Id", "gridcode", "ORIG_FID"]
        )
    
