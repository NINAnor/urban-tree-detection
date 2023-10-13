import os
import time
import arcpy
from arcpy import env
import logging

# local sub-package modules

# local sub-package utils
from src import arcpy_utils as au
from src import (
    MUNICIPALITY,
    DATA_PATH,
    RAW_PATH,
    INTERIM_PATH,
    PROCESSED_PATH,
    SPATIAL_REFERENCE,
    COORD_SYSTEM,
    POINT_DENSITY,
)
from src import logger


def merge_trees(neighbourhood_list, tree_detection_path):
    logger = logging.getLogger(__name__)
    logger.info("3. Merge Trees with Other Trees...")
    logger.info("-" * 100)
    logger.info("Processing neighbourhoods...")
    logger.info(neighbourhood_list)

    # Detect trees per neighbourhood
    for n_code in neighbourhood_list:
        logger.info("\t---------------------".format(n_code))
        logger.info("\tPROCESSING NEIGHBOURHOOD <<{}>>".format(n_code))
        logger.info("\t---------------------".format(n_code))

        # temporary filegdb containing detected trees per neighbourhood
        filegdb_path = os.path.join(
            tree_detection_path, "tree_detection_b" + n_code + ".gdb"
        )

        # workspace settings
        env.overwriteOutput = True
        env.outputCoordinateSystem = arcpy.SpatialReference(SPATIAL_REFERENCE)

        # ------------------------------------------------------ #
        # Dynamic Path Variables
        # ------------------------------------------------------ #

        v_top_watershed = os.path.join(
            filegdb_path, "tops_watershed_" + n_code
        )  # RESULTING tree tops from watershed
        v_crown_watershed = os.path.join(
            filegdb_path, "crowns_watershed_" + n_code
        )  # RESULTING tree crowns from watershed
        v_other_crowns = os.path.join(
            filegdb_path, "crowns_other_" + n_code
        )  # Resulting other crowns
        v_other_tops = os.path.join(
            filegdb_path, "tops_other_" + n_code
        )  # Resulting other tops

        v_top_temp = os.path.join(filegdb_path, "tops_tmp_" + n_code)
        v_crown_temp = os.path.join(filegdb_path, "crowns_tmp_" + n_code)

        v_top = os.path.join(filegdb_path, "tops_" + n_code)
        v_crown = os.path.join(filegdb_path, "crowns_" + n_code)

        # ------------------------------------------------------ #
        # 3. Merge detected trees into one file
        # ------------------------------------------------------ #
        logger.info("-" * 100)
        logger.info("3.1 Merging detected trees into one file...")
        logger.info("-" * 100)

        if arcpy.Exists(v_top):
            logger.info("\tThe tree tops are already merged. Continue ...")
        else:
            logger.info(
                "\tMerge tree tops for all tiles into one polygon file."
            )
            arcpy.Merge_management(
                inputs=[v_top_watershed, v_other_tops], output=v_top_temp
            )

        if arcpy.Exists(v_crown):
            logger.info("\tThe tree crowns are already merged. Continue ...")
        else:
            logger.info(
                "\t\tMerge tree crowns for all tiles into one polygon file."
            )
            arcpy.Merge_management(
                inputs=[v_crown_watershed, v_other_crowns], output=v_crown_temp
            )

    logger.info("Finished merging the detected trees into one file ...")


if __name__ == "__main__":
    logger = logging.getLogger(__name__)

    kommune = MUNICIPALITY
    # ------------------------------------------------------ #
    # INPUT PATHS
    # ------------------------------------------------------ #

    # specific file paths
    tree_detection_path = os.path.join(INTERIM_PATH, "tree_detection")
    # create folder in tree_detection_path if not exits
    if not os.path.exists(tree_detection_path):
        logger.info("Creating folder {} ...".format(tree_detection_path))
        os.makedirs(tree_detection_path)

    # admin data
    admin_data_path = os.path.join(
        DATA_PATH, kommune, "general", kommune + "_admindata.gdb"
    )
    study_area_path = os.path.join(admin_data_path, "analyseomrade")

    # neighbourhood list
    neighbourhood_path = os.path.join(admin_data_path, "bydeler")
    n_field_name = "bydelnummer"

    neighbourhood_list = au.get_neighbourhood_list(
        neighbourhood_path, n_field_name
    )
    logger.info("Processing neighbourhoods: {}".format(neighbourhood_list))

    # ------------------------------------------------------ #
    # RUN FUNCTIONS
    # ------------------------------------------------------ #
    merge_trees(neighbourhood_list, tree_detection_path)
