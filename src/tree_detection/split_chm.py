import os
import arcpy
from arcpy import env
import logging
from src import arcpy_utils as au
from src import (
    SPATIAL_REFERENCE,
    MUNICIPALITY,
    DATA_PATH,
    INTERIM_PATH,
    POINT_DENSITY,
)


# define the spatial resolution of the DSM/DTM/CHM grid based on lidar point density
# move to config
def get_spatial_resolution():
    if POINT_DENSITY >= 4:
        spatial_resolution = 0.25
    elif POINT_DENSITY < 4 and POINT_DENSITY >= 2:
        spatial_resolution = 0.5
    else:
        spatial_resolution = 1
    return spatial_resolution


def split_chm_nb(
    neighbourhood_list, split_neighbourhoods_gdb, r_chm, split_chm_gdb
):
    logger = logging.getLogger(__name__)
    logger.info("Splitting neighbourhoods...")
    logger.info("-" * 100)
    logger.info("Processing neighbourhoods...")
    logger.info(neighbourhood_list)

    # split chm by neighbourhood
    for n_code in neighbourhood_list:
        logger.info("\t---------------------".format(n_code))
        logger.info("\tPROCESSING NEIGHBOURHOOD <<{}>>".format(n_code))
        logger.info("\t---------------------".format(n_code))

        # workspace settings
        env.overwriteOutput = True
        env.outputCoordinateSystem = arcpy.SpatialReference(SPATIAL_REFERENCE)

        # ------------------------------------------------------ #
        # Dynamic Path Variables
        # ------------------------------------------------------ #

        # neighbourhood specific file paths
        v_neighb = os.path.join(split_neighbourhoods_gdb, "b_" + n_code)
        v_neighb_buffer = os.path.join(
            split_neighbourhoods_gdb, "b_" + n_code + "_buffer200"
        )

        # chm clipped by neighbourhood
        r_chm_neighb = os.path.join(
            split_chm_gdb, "chm_" + "b_" + n_code + "_buffer200"
        )

        # ------------------------------------------------------ #
        # 1.1 Clip CHM to neighbourhood + 200m buffer to avoid edge effects
        # ------------------------------------------------------ #
        try:
            logger.info(
                "\t1.1 Clip CHM to {} + 200m buffer to avoid edge effects".format(
                    n_code
                )
            )
            if arcpy.Exists(r_chm_neighb):
                logger.info(
                    "\t\tThe clipped CHM for neighbourhood <<{}>> exists in database. Continue ...".format(
                        n_code
                    )
                )
            else:
                arcpy.Buffer_analysis(
                    in_features=v_neighb,
                    out_feature_class=v_neighb_buffer,
                    buffer_distance_or_field=200,
                )

                arcpy.Clip_management(
                    in_raster=r_chm,
                    out_raster=r_chm_neighb,
                    in_template_dataset=v_neighb_buffer,
                    clipping_geometry="ClippingGeometry",
                )

        except Exception as e:
            # catch any exception and print error message.
            logger.info(f"\t\tERROR: {e}. \nContinue...")


if __name__ == "__main__":
    # set up logger
    from src.logger import setup_custom_logging  # noqa

    setup_custom_logging()
    logger = logging.getLogger(__name__)

    kommune = MUNICIPALITY

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
    keep_temp = True

    # split neighbourhoods
    split_neighbourhoods_gdb = os.path.join(INTERIM_PATH, "bydeler_split.gdb")
    if not arcpy.Exists(split_neighbourhoods_gdb):
        logger.info("Splitting neighbourhoods...")
        au.split_neighbourhoods(
            neighbourhood_path, n_field_name, split_neighbourhoods_gdb
        )

    # terrain data
    gdb_elevation_data = os.path.join(
        DATA_PATH, kommune, "general", kommune + "_hoydedata.gdb"
    )

    if not arcpy.Exists(gdb_elevation_data):
        logger.error(
            f"The elevation and canopy height model data for {kommune} kommune is not available.\
                     \nPlease run the script 'model_chm.py' first."
        )
        exit()

    # chm data
    spatial_resolution = get_spatial_resolution()
    str_resolution = str(spatial_resolution).replace(".", "")
    r_chm = os.path.join(
        gdb_elevation_data, "chm_" + str(str_resolution) + "m_int_100x"
    )

    # split neighbourhoods
    split_chm_gdb = os.path.join(INTERIM_PATH, "chm_split.gdb")
    au.createGDB_ifNotExists(split_chm_gdb)
    split_chm_nb(
        neighbourhood_list, split_neighbourhoods_gdb, r_chm, split_chm_gdb
    )
