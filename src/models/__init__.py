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

# set the municipality (kommune) to be analyzed
kommune = "oslo"
spatial_reference = "ETRS 1989 UTM Zone 32N"
tile = "XXX-YYY"

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
env.overwriteOutput = True
env.outputCoordinateSystem = arcpy.SpatialReference(spatial_reference)
env.workspace = interim_data_path


arcpy.AddMessage("-"*100)
arcpy.AddMessage("arcpy worksapce:\t" + env.workspace)
arcpy.AddMessage("neighbourhood_path:\t" + neighbourhood_path + "\n")
end_time0 = time.time()
execution_time0 = end_time0 - start_time0
arcpy.AddMessage("Processing time model set-up:\t {:.2f} sec".format(execution_time0))
arcpy.AddMessage("-"*100)


#------------------------------------------------------ #
# Functions (move to separate module)
# ------------------------------------------------------ #


def end_time1(start_time1):
    end_time1 = time.time()
    execution_time1 = end_time1 - start_time1
    arcpy.AddMessage("  TIME:\t {:.2f} sec".format(execution_time1))

def create_lasDataset(l_las_folder: str, d_las: str):
    """
    Creates a LAS dataset using the arcpy module.

    Parameters:
    - l_las_folder (str): The folder path where the LAS files are located.
    - d_las (str): The output LAS dataset path and name.

    Returns:
    - None

    Example Usage:
    create_lasDataset("C:/data/las_files", "C:/data/las_datasets/tile_001.lasd")
    """
    
    arcpy.AddMessage("  1.1: Creating LAS Dataset...")

    arcpy.CreateLasDataset_management(
        input=l_las_folder,
        out_las_dataset=d_las,
        relative_paths="RELATIVE_PATHS"
    )

def create_RGB(d_las, r_rgb):
    arcpy.AddMessage("  1.2: Creating RGB image...")
    
    arcpy.LasDatasetToRaster_conversion(
        in_las_dataset = d_las, 
        out_raster = r_rgb, 
        value_field = "RGB", 
        interpolation_type = "BINNING NEAREST NATURAL_NEIGHBOR", 
        data_type = "INT", 
        sampling_type = "CELLSIZE", 
        sampling_value = "1", 
        z_factor = "1"
    )


def create_vegMask(r_rgb, r_tgi):
    arcpy.AddMessage("  1.3: Creating vegetation mask...")

    band_1 = arcpy.sa.Raster(r_rgb + "\\Band_1")
    band_2 = arcpy.sa.Raster(r_rgb + "\\Band_2")
    band_3 = arcpy.sa.Raster(r_rgb + "\\Band_3")

    output = arcpy.sa.Con(((band_2 - (0.39 * band_1) - (0.61 * band_3)) >= 0), 1)
    output.save(os.path.join(env.workspace, r_tgi))
    arcpy.Delete_management(r_rgb)



# ------------------------------------------------------ #
# 1. Detect tree polygons (crowns) and tree points (tops) per neighbourhood
# ------------------------------------------------------ #

arcpy.AddMessage("Step 1: Detecting tree polygons and points per las tile")


# Iterate over bydel (here adjusted for Oslo - 16 bydel numbered 01-16 with prefix 0301)
#list_tree_pnt_names = []
#list_tree_poly_names = []  

n_tiles = len([f for f in os.listdir(lidar_path) if os.path.isdir(os.path.join(lidar_path, f))])

arcpy.AddMessage("{} tiles are processed for {} kommune... {}".format(n_tiles, kommune))

for i in range (1, n_tiles): # IF NECESSARY, CHANGE NUMBER OF TILES

    tile_code= "test"

    arcpy.AddMessage("  PROCESSING TILE <<{}>>".format(tile_code))
    arcpy.AddMessage("  ---------------------".format(tile_code))
   
    # temporary file paths 
    l_las_folder = r"lidar\{}".format(tile_code) # IF NECESSARY, CHANGE PATH TO .las FILES
    d_las = "data_" + tile_code + "_001_lasdataset.lasd"
    r_rgb = os.path.join(output_path, "data_" + tile_code + "_002_rgb")
    r_tgi = os.path.join(output_path, "data_" + tile_code + "_003_tgi")
    
    # ------------------------------------------------------ #
    # 1.1 Create LAS Dataset
    # ------------------------------------------------------ #
    
    start_time1 = time.time()
    create_lasDataset(l_las_folder,d_las)
    end_time1(start_time1)

    # ------------------------------------------------------ #
    # 1.2 Create RGB image
    # ------------------------------------------------------ #
    start_time1 = time.time()
    if arcpy.Exists(r_rgb):
        arcpy.AddMessage("  RGB image for tile <<{}>> exists in database. Continue to 1.3.".format(tile_code))
    else:
        create_RGB(d_las, r_rgb)
        end_time1(start_time1)

    # ------------------------------------------------------ #
    # 1.3 Create vegetation mask
    # ------------------------------------------------------ #
    start_time1 = time.time()
    if arcpy.Exists(r_tgi):
        arcpy.AddMessage("  Vegetation mask for tile <<{}>> exists in database. Continue to 1.3.".format(tile_code))
    else:
        create_vegMask(r_rgb, r_tgi)
        end_time1(start_time1) 

    arcpy.AddMessage("  ---------------------")
    break 