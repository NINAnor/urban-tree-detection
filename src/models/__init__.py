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
# variables to .env 
# test code for Oslo (one tile) 
# test code for Bodø 
# init user-parameters in batch (see lakseskart PROCEDURE)
# time script 
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
spatial_reference = "ETRS 1989 UTM Zone 32N"
tile = "XXX-YYY"

rgb_is_available = True        # Baerum = True, Kristiandsand and Bodø = False 
veg_is_available = True        # Baerum = True, Kristiandsand and Bodø = False 

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
arcpy.AddMessage("spatial reference:\t\t\t"+ spatial_reference)
arcpy.AddMessage("LiDAR-tile:\t\t\t"+ tile)
arcpy.AddMessage("RGB image available:\t\t\t"+ str(rgb_is_available))
arcpy.AddMessage("Vegetation Classes available:\t\t\t"+ str(veg_is_available))
arcpy.AddMessage("Output FileGDB:\t\t\t"+ output_path)
arcpy.AddMessage("-"*100)


#------------------------------------------------------ #
# Functions (move to separate module)
# ------------------------------------------------------ #


def end_time1(start_time1):
    end_time1 = time.time()
    execution_time1 = end_time1 - start_time1
    arcpy.AddMessage("  TIME:\t {:.2f} sec".format(execution_time1))


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
   
    # temporary file paths 
    l_las_folder = r"lidar\{}".format(tile_code) # IF NECESSARY, CHANGE PATH TO .las FILES
    d_las = os.path.join(lidar_path, "data_" + tile_code + "_001.lasd")
    r_rgb = os.path.join(output_path, "data_" + tile_code + "_002_rgb")
    r_tgi = os.path.join(output_path, "data_" + tile_code + "_003_tgi")
    
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
    # 1.2 Create RGB image 
    # 1.3 Create TGI vegetation mask
    # not possible if RGB-colour is not available 
    # ------------------------------------------------------ #
    arcpy.AddMessage("\t1.2 Create RGB image and 1.3 Create TGI vegetation mask")
    # check if rgb-image is available 
    if rgb_is_available:
        # check if file exists 
        if arcpy.Exists(r_tgi):
            arcpy.AddMessage("\t\tVegetation mask for tile <<{}>> exists in database. Continue ...".format(tile_code))
        else:
            start_time1 = time.time()
            # create RGB-image
            tree.create_RGB(d_las, r_rgb)
            # create vegation mask     
            tree.create_vegMask(r_rgb, r_tgi)
            end_time1(start_time1)    
    else:
        arcpy.AddMessage("\t\tRGB image for {} kommune does not exits. TGI mask cannot be created. Continue... ".format(kommune))

    arcpy.AddMessage("\t---------------------")
    break 


end_time0 = time.time()
execution_time0 = end_time0 - start_time0
arcpy.AddMessage("TOTAL TIME:\t {:.2f} sec".format(execution_time0))