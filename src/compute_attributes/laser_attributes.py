import arcpy
import os
import logging

from src import arcpy_utils as au
from src import logger

logger.setup_logger(logfile=False)
logger = logging.getLogger(__name__)

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
    - attr_lidarTile(self, tile_code)
    - attr_segMethod(self, segmentation_method)
    - attr_topHeight(self, v_top, r_chm_h, r_dtm, str_multiplier)
    - join_topAttr_toCrown(self)
    
   """

    def __init__(self, path: str, crown_filename: str, point_filename: str):
        self.path = path
        self.crown_filename = crown_filename
        self.top_filename = point_filename

    def attr_lidarTile(self, tile_code: str):
        """
        Adds the attribute 'lidar_tile' (TEXT) to the crown feature class.
            > Contains the <xxx_yyy> substring of the lidar tile name.
        """

        format_tile_code = str(tile_code[:3] + "_" + tile_code[4:])
        logger.info("\tATTRIBUTE | kartblad:")
        logger.info(
            f"\tAdding the attribute <<kartblad>> with the corresponding tile code: {format_tile_code}... "
        )

        # Store information on lidar tile
        au.addField_ifNotExists(self.crown_filename, "kartblad", "TEXT")
        au.calculateField_ifEmpty(
            self.crown_filename, "kartblad", format_tile_code
        )

    def attr_segMethod(self, segmentation_method):
        """
        Adds the attribute 'seg_method' (TEXT) to the crown feature class.

        Args:
            method (str): watershed or other
        """

        logger.info("\tATTRIBUTE | seg_method:")
        au.addField_ifNotExists(self.crown_filename, "seg_method", "TEXT")
        au.addField_ifNotExists(self.top_filename, "seg_method", "TEXT")

        au.calculateField_ifEmpty(
            self.crown_filename, "seg_method", segmentation_method
        )
        au.calculateField_ifEmpty(
            self.top_filename, "seg_method", segmentation_method
        )


    def attr_topHeight(
        self, v_top, r_chm_h: str, r_dtm: str, str_multiplier: str
    ):
        """
        Adds the attribute 'tree_height_laser' (SHORT) and 'tree_altit' (LONG) to the top feature class.
            > Extract tree height (from CHM) and tree altitude (from DSM) to tree points
        """
        logger.info("\tATTRIBUTE | tree_height_laser and tree_altit:")
        logger.info(
            f"\tExtracting tree height (from CHM) and tree altitude (from DTM) to tree points... "
        )

        # Extract tree height (from CHM) and tree altitude (from DTM) to tree points as FLOAT values
        arcpy.gp.ExtractMultiValuesToPoints_sa(
            v_top,
            "'{}' tree_height_laser_int;'{}' tree_altit_int".format(
                r_chm_h, r_dtm
            ),
            "NONE",
        )

        # if raster is a integer and contains 100x the value of the original raster, divide by 100
        multiplier = str_multiplier.replace("x", "")

        logger.info(
            "\tCHM and DSM rasters are integer values multiplied by <{}>. \
                Canopy Height Values are extracted and divided by\
                {}... ".format(
                str_multiplier, multiplier
            )
        )

        # divide tree_height_laser and tree_alittude by multiplier if raster is integer
        arcpy.management.CalculateField(
            in_table=v_top,
            field="tree_height_laser",
            expression="!tree_height_laser_int! /{}".format(multiplier),
            expression_type="PYTHON3",
            code_block="",
            field_type="FLOAT",
            enforce_domains="NO_ENFORCE_DOMAINS",
        )

        arcpy.management.CalculateField(
            in_table=v_top,
            field="tree_altit",
            expression="!tree_altit_int! /{}".format(multiplier),
            expression_type="PYTHON3",
            code_block="",
            field_type="FLOAT",
            enforce_domains="NO_ENFORCE_DOMAINS",
        )

        # detelete int fields
        arcpy.DeleteField_management(
            v_top, ["tree_height_laser_int", "tree_altit_int"]
        )
        au.round_fields_two_decimals(v_top, ["tree_height_laser", "tree_altit"])

    # join tree_heigh, tree_altit from tree points to tree polygons
    def join_topAttr_toCrown(self):
        """
        Joins the attribute 'tree_height_laser' (SHORT) to the crown feature class.
        Joins the attribute 'tree_altit' (LONG) to the crown feature class.
        """

        logger.info(
            "\t\tJOIN ATTRIBUTE | tree_heigth and tree_altit to crown feature class:"
        )
        logger.info(
            f"\tJoining the tree top attributes: tree_height_laser and tree_altit to the crown polygons... "
        )
        au.addField_ifNotExists(
            self.crown_filename, "tree_height_laser", "FLOAT"
        )
        au.addField_ifNotExists(self.crown_filename, "tree_altit", "FLOAT")

        # Check if the  field contains any null or empty values
        if (
            au.check_isNull(self.crown_filename, "tree_height_laser")
            or au.check_isNull(self.crown_filename, "tree_altit") == True
        ):
            # populate field with join
            au.join_and_copy(
                self.crown_filename,
                "crown_id",
                self.top_filename,
                "crown_id",
                ["tree_height_laser", "tree_altit"],
                ["tree_height_laser", "tree_altit"],
            )
        else:
            logger.info(
                f"\tAll rows in field are already populated. Exiting function."
            )

        au.round_fields_two_decimals(
            self.crown_filename, ["tree_height_laser", "tree_altit"]
        )


