# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# perform_tree_detection_v1.py
# Description: Translation of Hanssen et al. (2021) tree detection algorithm
# from ArcMap model builder to ArcPy script - Version 1
# Author: Zofie Cimburova, Willeke A'Campo
# Dependencies: ArcGIS Pro 3.0, 3D analyst, image analyst, spatial analyst
# ---------------------------------------------------------------------------

# ------------------------------------------------------ #
# TO DO
# ------------------------------------------------------ #
# test code for Oslo (one tile) 
# test code for Bodø 
# init user-parameters in batch (see lakseskart PROCEDURE)
# object-based coding instead of function-based 
# use __init__.py
# ------------------------------------------------------ #

# Import modules
import arcpy
from arcpy import env
import os
import time
import dotenv
from dotenv import dotenv_values
import control
import tree

# set the municipality (kommune) to be analyzed
kommune = "oslo"


if kommune == "oslo" or "baerum" :
    spatial_reference = "ETRS 1989 UTM Zone 32N"
    tile = "XXX-YYY"

    rgb_is_available = True       # Baerum = True, Kristiandsand and Bodø = False 
    veg_is_available = True        # Baerum = True, Kristiandsand and Bodø = False 
    point_density = 10 
    min_heigth = 2.5               # TO DO check municipalities specific min_height
    
if kommune == "bodo" :
    spatial_reference = "ETRS 1989 UTM Zone 33N"
    tile = "XXX-YYY"

    rgb_is_available = False        # Baerum = True, Kristiandsand and Bodø = False 
    veg_is_available = False        # Baerum = True, Kristiandsand and Bodø = False 
    point_density = 10 
    min_heigth = 2.5               # TO DO check municipalities specific min_height

if kommune == "kristiansand" :
    spatial_reference = "ETRS 1989 UTM Zone 32N"
    tile = "XXX-YYY"

    rgb_is_available = False        # Baerum = True, Kristiandsand and Bodø = False 
    veg_is_available = False        # Baerum = True, Kristiandsand and Bodø = False 
    point_density = 10 
    min_heigth = 2.5               # TO DO check municipalities specific min_height

    
# start timer
start_time0 = time.time()

# ------------------------------------------------------ #
# Variables  
# ------------------------------------------------------ #

# search for .env file in USER directory 
# user_dir = C:\\USERS\\<<firstname.lastname>>
user_dir = os.path.join(os.path.expanduser("~"))
dotenv_path = os.path.join(user_dir, '.env')

dotenv.load_dotenv(dotenv_path)
config = dotenv_values(dotenv_path)

# set secure variables
# source dataset path variables
FKB_BUILDING_PATH = os.getenv('FKB_BUILDING_PATH')
FKB_WATER_PATH = os.getenv('FKB_WATER_PATH')

# project data path variables 
DATA_PATH = os.getenv('DATA_PATH')
raw_data_path = os.path.join(DATA_PATH, kommune, "raw")
interim_data_path = os.path.join(DATA_PATH, kommune, "interim")
processed_data_path = os.path.join(DATA_PATH, kommune, "processed")

# specific file paths
lidar_path = os.path.join(interim_data_path, "lidar")
neighbourhood_path = os.path.join(interim_data_path, "neighbourhoods.gdb\\")
output_path = os.path.join(processed_data_path,"data.gdb")

#------------------------------------------------------ #
# Workspace settings
# ------------------------------------------------------ #
Log = control.Log(processed_data_path,"tree_dectection_v1_log.txt")
env.overwriteOutput = True
env.outputCoordinateSystem = arcpy.SpatialReference(spatial_reference)
env.workspace = interim_data_path

arcpy.AddMessage("-"*100)
arcpy.AddMessage("municipality:\t\t\t" + kommune)
arcpy.AddMessage("spatial reference:\t\t"+ spatial_reference)
arcpy.AddMessage("LiDAR-tile:\t\t\t"+ tile)
arcpy.AddMessage("RGB image available:\t\t"+ str(rgb_is_available))
arcpy.AddMessage("Vegetation Classes available:\t"+ str(veg_is_available))
arcpy.AddMessage("Output FileGDB:\t\t\t"+ output_path)
arcpy.AddMessage("-"*100)

#------------------------------------------------------ #
# Functions 
# ------------------------------------------------------ #

def end_time1(start_time1):
    end_time1 = time.time()
    execution_time1 = end_time1 - start_time1
    arcpy.AddMessage("\tTIME:\t {:.2f} sec".format(execution_time1))

# ------------------------------------------------------ #
# 1. Detect tree polygons (crowns) and tree points (tops) per neighbourhood
# ------------------------------------------------------ #

arcpy.AddMessage("Step 1: Detecting tree polygons and points per las tile")
arcpy.AddMessage("-"*100)

# Iterate over bydel (here adjusted for Oslo - 16 bydel numbered 01-16 with prefix 0301)
#list_tree_pnt_names = []
#list_tree_poly_names = []  

n_tiles = len([f for f in os.listdir(lidar_path) if os.path.isdir(os.path.join(lidar_path, f))])

arcpy.AddMessage("In {} kommune {} tiles are processed... \n".format(kommune,n_tiles))

for i in range (1, n_tiles): # IF NECESSARY, CHANGE NUMBER OF TILES

    tile_code= "test"

    arcpy.AddMessage("\tPROCESSING TILE <<{}>>".format(tile_code))
    arcpy.AddMessage("\t---------------------".format(tile_code))
   
    # layer paths 
    l_las_folder = r"lidar\{}".format(tile_code) # IF NECESSARY, CHANGE PATH TO .las FILES
    d_las = os.path.join(lidar_path, "data_" + tile_code + "_011.lasd")
    # canopy height model
    r_dtm = os.path.join(output_path, "data_" + tile_code + "_012_dtm") 
    r_dsm = os.path.join(output_path, "data_" + tile_code + "_012_dsm") 
    r_chm = os.path.join(output_path, "data_" + tile_code + "_012_chm") 
    # vegetation mask 
    r_rgb = os.path.join(output_path, "data_" + tile_code + "_013_rgb_temp") # temporary file
    r_tgi = os.path.join(output_path, "data_" + tile_code + "_013_tgi_temp") # temporary file
    v_tgi = os.path.join(output_path, "v_" + tile_code + "_013_tgi")
    # smoothed vegetation mask 
    r_chm_tgi = os.path.join(output_path, "data_" + tile_code + "_014_chm_tgi_temp") # temporary file (input_chm)
    r_chm_h = os.path.join(output_path, "data_" + tile_code + "_014_chm_h") # canopy heigth (tree height)
    r_chm_smooth = os.path.join(output_path,"data_" + tile_code + "_014_chm_smooth") # canopy smooth (tree segmenatation)
    
    # watershed segmentation
    r_chm_flip = os.path.join(output_path, "data_" + tile_code + "_015_chm_flip_temp") # temporary file 
    r_flowdir = os.path.join(output_path, "data_" + tile_code + "_015_flowdir_temp") # temporary file 
    r_sinks = os.path.join(output_path, "data_" + tile_code + "_015_sinks") 
    r_watersheds = os.path.join(output_path,"data_" + tile_code + "_015_watersheds")
    
    # identify tree tops 
    r_focflow = os.path.join(output_path, "data_" + tile_code + "_016_focflow_temp") # temporary file
    r_focflow_01 = os.path.join(output_path, "data_" + tile_code + "_016_focflow_01_temp") # temporary file
    v_treetop_poly = os.path.join(output_path, "data_" + tile_code + "_016_treetop_poly_temp") # temporary file
    v_treetop_pnt = os.path.join(output_path, "data_" + tile_code + "_016_treetop_pnt")
    
    # identify tree crowns 
    v_treecrown_poly = os.path.join(output_path, "data_" + tile_code + "_017_treecrown_poly") # old name v_watersheds
    
    
    # ------------------------------------------------------ #
    # 1.1 Create LAS Dataset
    # ------------------------------------------------------ #
    arcpy.AddMessage("\t1.1 Create LAS Dataset")
    
    if arcpy.Exists(d_las):
        arcpy.AddMessage("\t\tLAS Dataset for tile <<{}>> exists in database. Continue ...".format(tile_code))  
    else:
        start_time1 = time.time()
        tree.create_lasDataset(l_las_folder,d_las)
        end_time1(start_time1)

    # ------------------------------------------------------ #
    # 1.2 CANOPY HEIGTH MODEL
    #     Create DTM (old 1.5)
    #     Create DSM (old 1.6)
    #     Create CHM (old 1.7)
    # ------------------------------------------------------ #
    arcpy.AddMessage("\t1.2 Create Canopy Height Model (CHM)")
    
    if arcpy.Exists(r_chm):
        arcpy.AddMessage("\t\tCHM for tile <<{}>> exists in database. Continue ...".format(tile_code))
    else:
        start_time1 = time.time()
        
        # create DTM
        if point_density >= 10:
            spatial_resolution = 0.5 
            tree.create_DTM(d_las, r_dtm, spatial_resolution)
        else: 
            spatial_resolution = 1 
            tree.create_DTM(d_las, r_dtm, spatial_resolution)
        
        # create DSM 
        if veg_is_available:
            arcpy.AddMessage("\t\tLiDAR point clouds are classified for vegetation in {} kommune. \n\t\tThe classes unclassified (1), low- (3), medium- (4), and, high (5) vegetation are used to create the DSM.".format(kommune))
            class_code=["1", "3", "4", "5"]
            return_values=["1", "3", "4", "5"]
            tree.create_DSM(d_las, r_dsm, spatial_resolution, class_code, return_values)
        else:
            arcpy.AddMessage("\t\tLiDAR point clouds are not classified for vegetation in {} kommune. \n\t\tSolely the class unclassified (1) is used to create the DSM.".format(kommune))
            class_code=["1"]
            return_values=["1"]
            tree.create_DSM(d_las, r_dsm, spatial_resolution, class_code, return_values)
            
        # create CHM 
        tree.create_CHM(r_dtm, r_dsm, r_chm)
        end_time1(start_time1)
        
    # ------------------------------------------------------ #
    # 1.3 VEGETATION MASK
    #     Create RGB image (old 1.2)
    #     Create TGI vegetation mask (old 1.3)
    #     Vectorize vegetation mask (old 1.4)
    # ------------------------------------------------------ #
    arcpy.AddMessage("\t1.3 Create Vegetation Mask (TGI)")
    # check if rgb-image is available 
    if rgb_is_available:
        # check if file exists 
        if arcpy.Exists(v_tgi):
            arcpy.AddMessage("\t\tVegetation mask for tile <<{}>> exists in database. Continue ...".format(tile_code))
        else:
            start_time1 = time.time()
            # create RGB-image
            tree.create_RGB(d_las, r_rgb)
            # create vegation mask     
            tree.create_vegMask(r_rgb, r_tgi)
            # vegetation mask to Vector 
            tree.tgi_toVector(r_tgi, v_tgi)
            end_time1(start_time1)    
    else:
        arcpy.AddMessage("\t\tRGB image for {} kommune does not exits. Vegetation mask cannot be created. Continue... ".format(kommune))

   
    # ------------------------------------------------------ #
    # 1.4 SMOOTHING AND FILTERING CANOPY HEIGHT MODEL
    #     Refine CHM with vegetation mask (old 1.8)
    #     Filter CHM by minimum height (old 1.9)
    #     Refine CHM by focal maximum filter (old 1.10)
    #       --> best filter size can vary locally, dependent on tree species
    # ------------------------------------------------------ #
    arcpy.AddMessage("\t1.4 Smoothing and Filtering the Canopy Height Model (CHM)")

    min_heigth = min_heigth     # min_height can vary locally, dependent on species
    radius = 1.5                # radius can vary locally, dependent on species
    
    start_time1 = time.time()
    
    if arcpy.Exists(r_chm_smooth):
            arcpy.AddMessage("\t\tRefined vegetation mask for tile <<{}>> exists in database. Continue ...".format(tile_code))
    else: 
        # check if vegetation mask exists
        if arcpy.Exists(v_tgi):
            # refine with veg mask 
            tree.extract_vegMask(v_tgi, r_chm, r_chm_tgi)
            # filter by min tree heigth (municipality-sepcific)
            input_chm=r_chm_tgi  # vegetation masked chm 
            tree.extract_minHeight(input_chm, r_chm_h, min_heigth)
            # focal maximum filter 
            tree.focal_maxFilter(r_chm_h, r_chm_smooth, radius)
            arcpy.Delete_management(r_chm_tgi)
            end_time1(start_time1)
        else:
            # refine with veg mask 
            arcpy.AddMessage("\t\tVegetation maks is not generated for {} kommune. CHM cannot be refined using the vegetation mask. Continue... ".format(kommune))
            # filter by min tree heigth (municipality-sepcific)
            input_chm=r_chm     # non-vegetation masked chm
            tree.extract_minHeight(input_chm, r_chm_h, min_heigth)
            # focal maximum filter 
            tree.focal_maxFilter(r_chm_h, r_chm_smooth, radius)
            end_time1(start_time1)

    
    # ------------------------------------------------------ #
    # 1.5 THE WATERSHED SEGMENTATION METHOD
    #     Flip CHM (old 1.11)
    #     Compute flow direction (old 1.12)
    #     Identify sinks (old 1.13)
    #     Identify watersheds (old 1.14)
    # ------------------------------------------------------ #
    arcpy.AddMessage("\t1.5 The Watershed Segmentation Method")
    start_time1 = time.time()
    if arcpy.Exists(r_watersheds):
            arcpy.AddMessage("\t\t The watershed raster for tile <<{}>> exists in database. Continue ...".format(tile_code))
    else: 
        # nested function for watershed segmentation method
        tree.watershed_segmentation(r_chm_smooth,r_chm_flip,r_flowdir,r_sinks,r_watersheds)
        end_time1(start_time1)
    
    
    # ------------------------------------------------------ #
    # 1.6 IDENTIFY TREE TOPS 
    #     Identify tree tops (I) by identifying focal flow (old 1.15)
    #     Identify tree tops (II) by converting focal flow values from 0 to 1 (old 1.16)
    #     Vectorize tree tops to polygons (old 1.17)
    #     Convert tree top polygons to points (old 1.18)
    # ------------------------------------------------------ #        
            
    arcpy.AddMessage("\t1.6 Identify Tree Tops  ")
    start_time1 = time.time()
    if arcpy.Exists(v_treetop_pnt):
            arcpy.AddMessage("\t\tThe treetop vector for tile <<{}>> exists in database. Continue ...".format(tile_code))
    else: 
        # nested function to identify treeTops
        tree.identify_treeTops(r_sinks, r_focflow, r_focflow_01, v_treetop_poly, r_chm_h, r_dsm, v_treetop_pnt)
        end_time1(start_time1)
    
    
    # ------------------------------------------------------ #
    #  1.7 IDENTIFY TREE CROWNS
    #      Identify tree crowns by vectorizing watersheds (old 1.19)
    # ------------------------------------------------------ #  
    
    arcpy.AddMessage("\t1.7 Identify Tree Crowns ")
    start_time1 = time.time()
    if arcpy.Exists(v_treecrown_poly):
            arcpy.AddMessage("\t\tThe tree crownvector for tile <<{}>> exists in database. Continue ...".format(tile_code))
    else: 
        tree.identify_treeCrowns(r_watersheds,v_treecrown_poly)
        end_time1(start_time1)
    
    
    
    arcpy.AddMessage("\t---------------------")
    break 


end_time0 = time.time()
execution_time0 = end_time0 - start_time0
arcpy.AddMessage("TOTAL TIME:\t {:.2f} sec".format(execution_time0))