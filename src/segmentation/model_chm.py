# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# perform_tree_detection_v1.py
# Description: Translation of Hanssen et al. (2021) tree detection algorithm
# from ArcMap model builder to ArcPy script - Version 3
# Author: Zofie Cimburova, Willeke A'Campo
# Dependencies: ArcGIS Pro 3.0, 3D analyst, image analyst, spatial analyst
# ---------------------------------------------------------------------------

import os
import time
import arcpy
from arcpy import env
from arcpy.ia import *
import logging

# local modules
import tree

# local sub-package utils
from src import arcpy_utils as au
from src import (MUNICIPALITY, DATA_PATH, INTERIM_PATH, SPATIAL_REFERENCE, COORD_SYSTEM, RGB_AVAILABLE,
                 VEG_CLASSES_AVAILABLE, POINT_DENSITY, MIN_HEIGHT, FOCAL_MAX_RADIUS)
from src import logger

#------------------------------------------------------ #
# Functions
# ------------------------------------------------------ #

def end_time1(start_time1):
    end_time1 = time.time()
    execution_time1 = end_time1 - start_time1
    logger.info("\tTIME:\t {:.2f} sec".format(execution_time1))

# define the spatial resolution of the DSM/DTM/CHM grid based on lidar point density
def get_spatial_resolution():
    if POINT_DENSITY >= 4:
        spatial_resolution = 0.25
    elif POINT_DENSITY < 4 and POINT_DENSITY >= 2:
        spatial_resolution =  0.5
    else:
        spatial_resolution = 1
    return spatial_resolution

def model_chm(lidar_path, kommune):
    """_summary_

    Args:
        lidar_path (str): path to lidar data
        kommune (str): munciaplity name
    """
    logger.info("Start modelling the DTM, DSM and CHM ...")
    logger.info("-"*100)
    
    list_dtm_files = []
    list_dsm_files = []
    list_chm_files = []

    # List the subdirectories in the folder
    tile_list = [f.name for f in os.scandir(lidar_path) if f.is_dir() and not f.name.endswith('.gdb')]
    n_tiles = len([f for f in os.listdir(lidar_path) if os.path.isdir(os.path.join(lidar_path, f))])

    logger.info("In {} kommune {} tiles (5000 maplist) are processed:\n".format(kommune,n_tiles))
    logger.info(tile_list)

    # Detect trees per tile in tile_list
    for tile_code in tile_list:
        logger.info("\t---------------------".format(tile_code))
        logger.info("\tPROCESSING TILE <<{}>>".format(tile_code))
        logger.info("\t---------------------".format(tile_code))

        # layer paths
        l_las_folder = os.path.join(lidar_path, tile_code) # IF NECESSARY, CHANGE PATH TO .las FILES
        d_las = os.path.join(lidar_path, "tile_" + tile_code + ".lasd")

        # temporary filegdb for each tile to store intermediate results
        filegdb_path = os.path.join(lidar_path, "chm_" + tile_code + ".gdb")
        au.createGDB_ifNotExists(filegdb_path)

        # workspace settings
        env.overwriteOutput = True
        env.outputCoordinateSystem = arcpy.SpatialReference(SPATIAL_REFERENCE)
        env.workspace = filegdb_path  
        
        # ------------------------------------------------------ #
        # Dynamic Path Variables
        # ------------------------------------------------------ #

        # temporary buffer of the study area to avoid edge effect
        study_area_buffer = os.path.join(filegdb_path, "analyseomrade_buffer")
        
        # height models
        r_dtm = os.path.join(filegdb_path, "dtm") # exported
        r_dsm = os.path.join(filegdb_path, "dsm") # exported 
        r_chm = os.path.join(filegdb_path, "chm") # input_chm if vegetation mask not available 
        
        # vegetation mask
        r_rgb = os.path.join(filegdb_path, "rgb") 
        r_tgi = os.path.join(filegdb_path, "tgi") 
        v_tgi = os.path.join(filegdb_path, "tgi")
        
        # refining and smoothing of chm
        r_chm_tgi = os.path.join(filegdb_path, "chm_tgi") # input chm if vegetation mask available
        r_chm_mask = os.path.join(filegdb_path, "chm_mask") # chm masked with municipality specific mask
        r_chm_h = os.path.join(filegdb_path, "chm_h") # chm filtered by min height
        r_chm_edge = os.path.join(filegdb_path, "chm_edge") # chm where building edges are removed
        r_chm_smooth = os.path.join(filegdb_path, "chm_smooth") # chm filtered by focal max filter to smooth the chm, final chm output. 


        # ------------------------------------------------------ #
        # 1.0 Create a 200m buffer around study area to avoid edge effect
        # ------------------------------------------------------ #
        
        logger.info("\t1.0 Create a 200m buffer around study area to avoid edge effect")
        arcpy.Buffer_analysis(
            in_features=study_area_path,
            out_feature_class=study_area_buffer,
            buffer_distance_or_field=200
        ) 
              
        # ------------------------------------------------------ #
        # 1.1 Create LAS Dataset
        # ------------------------------------------------------ #
        logger.info("\t1.1 Create LAS Dataset")

        if arcpy.Exists(d_las):
            logger.info("\t\tLAS Dataset for tile <<{}>> exists in database. Continue ...".format(tile_code))
        else:
            logger.info
            start_time1 = time.time()
            tree.create_lasDataset(l_las_folder,d_las)
            end_time1(start_time1)

        # ------------------------------------------------------ #
        # 1.2 CANOPY height MODEL
        #     Create DTM (old 1.5)
        #     Create DSM (old 1.6)
        #     Create CHM (old 1.7)
        #     Create CHM for the study area (TODO add +200m buffer to avoid edge effect?)
        # ------------------------------------------------------ #
        logger.info("\t1.2 Create Canopy Height Model (CHM)")

        if arcpy.Exists(r_chm):
            logger.info("\t\tCHM for tile <<{}>> exists in database. Continue ...".format(tile_code))
        else:
            start_time1 = time.time()

            # create DTM
            tree.create_DTM(d_las, r_dtm, spatial_resolution, study_area_buffer)

            # create DSM
            if VEG_CLASSES_AVAILABLE:
                logger.info("\t\tLiDAR point clouds are classified for vegetation in {} kommune. \n\t\tThe classes unclassified (1), low- (3), medium- (4), and, high (5) vegetation are used to create the DSM.".format(kommune))
                class_code=["1", "3", "4", "5"]
                return_values=["1", "3", "4", "5"]
                tree.create_DSM(d_las, r_dsm, spatial_resolution, class_code, return_values, study_area_buffer)
            else:
                logger.info("\t\tLiDAR point clouds are not classified for vegetation in {} kommune. \n\t\tSolely the class unclassified (1) is used to create the DSM.".format(kommune))
                class_code=["1"]
                return_values=["1"]
                tree.create_DSM(d_las, r_dsm, spatial_resolution, class_code, return_values, study_area_buffer)

            # create CHM
            tree.create_CHM(r_dtm, r_dsm, r_chm)
            end_time1(start_time1)

        # ------------------------------------------------------ #
        # 1.3 VEGETATION MASK and building mask
        #     Create RGB image (old 1.2)
        #     Create TGI vegetation mask (old 1.3)
        #     Vectorize vegetation mask (old 1.4)
        # ------------------------------------------------------ #
        logger.info("\t1.3 Create Vegetation Mask (TGI)")
        # check if rgb-image is available
        if RGB_AVAILABLE:
            # check if file exists
            if arcpy.Exists(v_tgi):
                logger.info("\t\tVegetation mask for tile <<{}>> exists in database. Continue ...".format(tile_code))
            else:
                start_time1 = time.time()
                # create RGB-image
                tree.create_RGB(d_las, r_rgb, study_area_buffer)
                # create vegation mask
                tree.create_vegMask(r_rgb, r_tgi)
                # vegetation mask to Vector
                tree.tgi_toVector(r_tgi, v_tgi)
                end_time1(start_time1)
        else:
            logger.info("\t\tRGB image for {} kommune does not exits. Vegetation mask cannot be created. Continue... ".format(kommune))

        start_time1 = time.time()

        # ------------------------------------------------------ #
        # 1.4 REFINING CANOPY HEIGHT MODEL
        #     Refine CHM with vegetation mask (old 1.8)
        #     Filter CHM by minimum height (old 1.9)
        #     Refine CHM by focal maximum filter (old 1.10)
        #       --> best filter size can vary locally, dependent on tree species
        # ------------------------------------------------------ #
        logger.info("\t1.3 Smoothing and Filtering the Canopy Height Model (CHM)")

        start_time1 = time.time()

        if arcpy.Exists(r_chm_smooth):
                logger.info("\t\tRefined vegetation mask for tile <<{}>> exists in database. Continue ...".format(tile_code))
        else:
            # check if vegetation mask exists
            if arcpy.Exists(v_tgi):
                # 1. refine with veg mask
                tree.extract_vegMask(v_tgi, r_chm, r_chm_tgi)
                # 2. filter by min tree height (municipality-sepcific)
                input_chm = r_chm_tgi  # vegetation masked chm
                # 3. mask with muncipality specific mask
                tree.extract_Mask(mask_path, input_chm, r_chm_mask)
                # 4. filter by min tree height
                tree.extract_minHeight(r_chm_mask, r_chm_h, MIN_HEIGHT)
                # 5. noise removal of building edges etc.
                tree.focal_meanFilter(r_chm_h,r_chm_edge)
                # 6. focal maximum filter
                tree.focal_maxFilter(r_chm_edge, r_chm_smooth, FOCAL_MAX_RADIUS)
                arcpy.Delete_management(r_chm_tgi)
                end_time1(start_time1)
            else:
                # refine with veg mask
                logger.info("\t\tVegetation maks is not generated for {} kommune. CHM cannot be refined using the vegetation mask. Continue... ".format(kommune))
                # 1. filter by min tree height (municipality-sepcific)
                input_chm = r_chm     # non-vegetation masked chm
                # 2. mask with muncipality specific mask
                tree.extract_Mask(mask_path, input_chm, r_chm_mask)
                # 3. filter by min tree height
                tree.extract_minHeight(r_chm_mask, r_chm_h, MIN_HEIGHT)
                # 4. noise removal of building edges etc.
                tree.focal_meanFilter(r_chm_h,r_chm_edge)
                # 5. focal maximum filter
                tree.focal_maxFilter(r_chm_edge, r_chm_smooth, FOCAL_MAX_RADIUS)
                end_time1(start_time1)

        # ------------------------------------------------------ #
        # 1.5 CONVERT CHM, DTM, DSM to integer rasters
        # ------------------------------------------------------ #
        
        logger.info("\t1.4 Convert CHM, DTM, DSM to integer by multiplying by 100")
        # multiply x 1000
        r_dtm_int = os.path.join(filegdb_path, "int_dtm_" + tile_code)
        r_dsm_int = os.path.join(filegdb_path, "int_dsm_" + tile_code)
        r_chm_int = os.path.join(filegdb_path, "int_chm_" + tile_code)

        au.convert_toIntRaster(r_dtm, r_dtm_int)
        au.convert_toIntRaster(r_dsm, r_dsm_int)
        au.convert_toIntRaster(r_chm_smooth, r_chm_int)

        # ------------------------------------------------------ #
        # 1.6 APPEND CHM, DTM, DSM to lists
        # ------------------------------------------------------ #

        logger.info("\t1.5 Append CHM, DTM, DSM to lists")
        list_dtm_files.append(r_dtm_int)
        list_dsm_files.append(r_dsm_int)
        list_chm_files.append(r_chm_int)

    # ------------------------------------------------------ #
    # 1.7 MOSAIC FILES IN THE CHM, DTM, DSM lists
    # ------------------------------------------------------ #
    
    logger.info("\t1.6 Mosaic CHM, DTM, DSM rasters to study area extent")
    chm_mosaic = "chm_"+str(spatial_resolution)+"m_int_100x"
    chm_mosaic = chm_mosaic.replace(".","")
    dtm_mosaic = "dtm_"+str(spatial_resolution)+"m_int_100x"
    dtm_mosaic = dtm_mosaic.replace(".","")
    dsm_mosaic = "dsm_"+str(spatial_resolution)+"m_int_100x"
    dsm_mosaic = dsm_mosaic.replace(".","")
    
    # loop over raster lists and output names to mosaic the rasters
    raster_lists = [list_chm_files, list_dtm_files, list_dsm_files]
    mosaic_names = [chm_mosaic, dtm_mosaic, dsm_mosaic]
    
    for raster_list, mosaic_name in zip(raster_lists, mosaic_names):
        au.rasterList_toMosaic(raster_list=raster_list,
                           ouput_gdb=gdb_elevation_data,
                           output_name=mosaic_name,
                           coord_system=COORD_SYSTEM,
                           spatial_resolution=spatial_resolution)
    
    logger.info("Finished modelling the DTM, DSM and CHM ...")
    logger.info("The mosaiced DTM, DSM and CHM for {} are stored in the file geodatabase:\n\t {}".format(kommune, gdb_elevation_data))
    logger.info("\t\tDTM:\t{}".format(dtm_mosaic))
    logger.info("\t\tDSM:\t{}".format(dsm_mosaic))
    logger.info("\t\tCHM:\t{}".format(chm_mosaic))
    logger.info("-"*100)
    # ------------------------------------------------------ #

if __name__ == '__main__':
    
    logger.setup_logger(logfile=True)
    logger = logging.getLogger(__name__)
    
    # start timer
    start_time0 = time.time()
    kommune = MUNICIPALITY
    # TODO move get_spatial_resolution() to config file
    spatial_resolution = get_spatial_resolution()

    # ------------------------------------------------------ #
    # Path variables Parameters
    # ------------------------------------------------------ #

    # specific file paths
    lidar_path = os.path.join(INTERIM_PATH, "lidar")

    # admin data
    admin_data_path = os.path.join(DATA_PATH, kommune, "general", kommune + "_admindata.gdb")
    study_area_path = os.path.join(admin_data_path, "analyseomrade")
    mask_path = os.path.join(admin_data_path, "analyseomrade_mask")

    # base data
    base_data_path = os.path.join(DATA_PATH, kommune, "general", kommune + "_basisdata.gdb")
    fkb_bygning_omrade = os.path.join(base_data_path, "fkb_bygning_omrade")
    fkb_vann_omrade = os.path.join(base_data_path, "fkb_vann_omrade")

    # terrain data
    gdb_elevation_data = os.path.join(DATA_PATH, kommune, "general", kommune + "_hoydedata.gdb")
    au.createGDB_ifNotExists(gdb_elevation_data)

    logger.info("\n")
    logger.info("municipality:\t\t\t" + kommune)
    logger.info("spatial reference:\t\t"+ SPATIAL_REFERENCE)
    logger.info("RGB image available:\t\t"+ str(RGB_AVAILABLE))
    logger.info("Vegetation Classes available:\t"+ str(VEG_CLASSES_AVAILABLE))
    logger.info("Point Density:\t\t\t"+ str(POINT_DENSITY))
    logger.info("Spatial Resolution:\t\t"+ str(spatial_resolution))
    logger.info("Minimum Tree Height:\t\t"+ str(MIN_HEIGHT))
    logger.info("Focal Max Radius:\t\t\t"+ str(FOCAL_MAX_RADIUS))
    logger.info("-"*100)
    
    user_input = input("Do you want to keep the interim chm filegdb's? (y/n):")
    
    if user_input == "y" or "yes" or "true" or "1" or "True":
        keep_temp = True
        logger.info("\tInterim filegdb's will be kept ...")
    else:
        keep_temp = False
        logger.info("\tInterim filegdb's will be deleted ...")
    
    # start moddelling dsm, dtm and chm
    model_chm(lidar_path, kommune)

    # delete all interim filegdb's 
    if keep_temp == False:
        logger.info("\tDeleting all interim filegdb's ...")
        for file in os.listdir(lidar_path):
            if file.startswith("chm_"):
                arcpy.Delete_management(os.path.join(lidar_path, file))
            
    end_time0 = time.time()
    execution_time1 = end_time0 - start_time0
    logger.info("\n\tEXCEUTION TIME:\t {:.2f} sec".format(execution_time1))