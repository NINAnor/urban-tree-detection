# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# perform_tree_detection_v1.py
# Description: Translation of Hanssen et al. (2021) tree detection algorithm
# from ArcMap model builder to ArcPy script - Version 1
# Author: Zofie Cimburova, Willeke A'Campo
# Dependencies: ArcGIS Pro 3.0, 3D analyst, image analyst, spatial analyst
# ---------------------------------------------------------------------------

# ------------------------------------------------------ #
# TODO - buildt in good practices
# top = treetop (vector pnt)
# crown = treecrown (vector polygon)
# stem = treestem (vector pnt)
# create (_temp) temprorary files in functions  
# organise modules by use 
# ------------------------------------------------------ #

import os
import time
import arcpy
from arcpy import env

# TODO use config 
import dotenv
from dotenv import dotenv_values
import datetime

# TODO use logger instead
#from utils.control import Log

# local sub-package modules
import tree
import select_area
from compute_attribute import LaserAttributes

# local sub-package utils
from src import arcpy_utils as au

# set the municipality (kommune) to be analyzed
kommune = "bodo"
# TODO move to time_config file
current_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
# ------------------------------------------------------ #
# Municipality Dependent Parameters  
# TODO move to config.py
# ------------------------------------------------------ #

if kommune == "oslo" or "baerum" :
    spatial_reference = "ETRS 1989 UTM Zone 32N"
    rgb_is_available = True       # Baerum = True, Kristiandsand and Bodø = False 
    veg_is_available = True        # Baerum = True, Kristiandsand and Bodø = False 
    point_density = 10              # pkt/m2
    min_heigth = 2               # TO DO check municipalities specific min_height
    radius = 1.5                # radius can vary locally, dependent on species

if kommune == "bodo" :
    spatial_reference = "ETRS 1989 UTM Zone 33N"
    rgb_is_available = False        # Baerum = True, Kristiandsand and Bodø = False 
    veg_is_available = False        # Baerum = True, Kristiandsand and Bodø = False 
    point_density = 2 
    min_heigth = 2               # TO DO check municipalities specific min_height
    radius = 1.5                # radius can vary locally, dependent on species

if kommune == "kristiansand" :
    spatial_reference = "ETRS 1989 UTM Zone 32N"
    rgb_is_available = False        # Baerum = True, Kristiandsand and Bodø = False 
    veg_is_available = False        # Baerum = True, Kristiandsand and Bodø = False 
    point_density = 5 
    min_heigth = 2               # min_height can vary locally, dependent on species
    radius = 1.5                # radius can vary locally, dependent on species and can be tuned with gtd 


# define the spatial resolution of the DSM/DTM/CHM grid based on lidar point density 
if point_density >= 4:
    spatial_resolution = 0.25 
elif point_density < 4 and point_density >= 2: 
    spatial_resolution =  0.5
else: 
    spatial_resolution = 1

# start timer
start_time0 = time.time()

# ------------------------------------------------------ #
# Path Variables  
# Protected Variables are stored in .env file 
# ------------------------------------------------------ #

# search for .env file in USER directory 
# user_dir = C:\\USERS\\<<firstname.lastname>>
user_dir = os.path.join(os.path.expanduser("~"))
dotenv_path = os.path.join(user_dir, 'trekroner.env')

dotenv.load_dotenv(dotenv_path)
config = dotenv_values(dotenv_path)

# set secure variables
# source dataset path variables
FKB_BUILDING_PATH = os.getenv('FKB_BUILDING_PATH')
#FKB_WATER_PATH = os.getenv('FKB_WATER_PATH')
FKB_WATER_PATH = r"R:\\GeoSpatialData\\Topography\\Norway_FKB\\Original\\FKB-Vann FGDB-format\\Basisdata_0000_Norge_5973_FKB-Vann_FGDB.gdb"

FKB_WATER_PATH = os.path.join(FKB_WATER_PATH, "fkb_vann_omrade")


# project data path variables 
DATA_PATH = os.getenv('DATA_PATH')
raw_data_path = os.path.join(DATA_PATH, kommune, "raw")
interim_data_path = os.path.join(DATA_PATH, kommune, "interim")
processed_data_path = os.path.join(DATA_PATH, kommune, "processed")

# specific file paths
lidar_path = os.path.join(interim_data_path, "lidar")

# admin GDB
admin_data_path = os.path.join(interim_data_path, kommune + "_admin.gdb")
study_area_path = os.path.join(admin_data_path, "analyseomrade")

# laser segmented trees GDB
laser_trees_path = os.path.join(interim_data_path, kommune + "_laser_trees.gdb")
au.createGDB_ifNotExists(laser_trees_path)
v_crown_merge = os.path.join(laser_trees_path, "crown_merge")
v_top_merge = os.path.join(laser_trees_path, "top_merge")


#------------------------------------------------------ #
# Workspace settings
# ------------------------------------------------------ #
#log_file = Log(processed_data_path,"tree_dectection_v1_log.txt")
env.overwriteOutput = True
env.outputCoordinateSystem = arcpy.SpatialReference(spatial_reference)
env.workspace = interim_data_path

arcpy.AddMessage("\n")
arcpy.AddMessage(f"Script started at: {current_datetime}")
arcpy.AddMessage("-"*100)
arcpy.AddMessage("municipality:\t\t\t" + kommune)
arcpy.AddMessage("spatial reference:\t\t"+ spatial_reference)
arcpy.AddMessage("RGB image available:\t\t"+ str(rgb_is_available))
arcpy.AddMessage("Vegetation Classes available:\t"+ str(veg_is_available))
arcpy.AddMessage("Output FileGDB:\t\t\t"+ str(os.path.basename(laser_trees_path)))
arcpy.AddMessage("-"*100)

#------------------------------------------------------ #
# Functions 
# ------------------------------------------------------ #

def end_time1(start_time1):
    end_time1 = time.time()
    execution_time1 = end_time1 - start_time1
    arcpy.AddMessage("\tTIME:\t {:.2f} sec".format(execution_time1))

# ------------------------------------------------------ #
# 1. Detect tree polygons (crowns) and tree points (tops) per tile
# ------------------------------------------------------ #

arcpy.AddMessage("Step 1: Detecting tree polygons and points per las tile")
arcpy.AddMessage("-"*100)


if not arcpy.Exists(v_top_merge) or not arcpy.Exists(v_crown_merge):

    # Iterate over tile (here the 5000 maplist is used for the tilecode, each las dataset contains all .las files within the tilecode)
    list_tree_top_names = []
    list_tree_crown_names = []  

    # List the subdirectories in the folder
    tile_list = [f.name for f in os.scandir(lidar_path) if f.is_dir() and not f.name.endswith('.gdb')]
    n_tiles = len([f for f in os.listdir(lidar_path) if os.path.isdir(os.path.join(lidar_path, f))])

    arcpy.AddMessage("In {} kommune {} tiles (5000 maplist) are processed:\n".format(kommune,n_tiles))
    arcpy.AddMessage(tile_list)
    print(tile_list)

    
    # Detect trees per tile in tile_list
    for tile_code in tile_list: 

        arcpy.AddMessage("\n\tPROCESSING TILE <<{}>>".format(tile_code))
        arcpy.AddMessage("\t---------------------".format(tile_code))

        # layer paths 
        l_las_folder = r"lidar\{}".format(tile_code) # IF NECESSARY, CHANGE PATH TO .las FILES
        d_las = os.path.join(lidar_path, "tile_" + tile_code + ".lasd")

        filegdb_path = os.path.join(lidar_path, "tree_segmentation_" + tile_code + ".gdb")     
        au.createGDB_ifNotExists(filegdb_path)

        prefix = os.path.join(filegdb_path, "tile_" + tile_code)

        # ------------------------------------------------------ #
        # Dynamic Path Variables  
        # MOVE TEMPORARY FILES TO tree.py
        # ------------------------------------------------------ #  

        # canopy height model
        r_dtm = os.path.join(prefix + "_012_dtm") 
        r_dsm = os.path.join(prefix + "_012_dsm") 
        r_chm = os.path.join(prefix + "_012_chm") 
        # vegetation mask 
        r_rgb = os.path.join(prefix + "_013_rgb_temp") # temporary file
        r_tgi = os.path.join(prefix + "_013_tgi_temp") # temporary file
        v_tgi = os.path.join(prefix + "_013_tgi")
        # smoothed vegetation mask 
        r_chm_tgi = os.path.join(prefix + "_014_chm_tgi_temp") # temporary file (input_chm)
        r_chm_h = os.path.join(prefix + "_014_chm_h") # canopy heigth (tree height)
        r_chm_smooth = os.path.join(prefix + "_014_chm_smooth") # canopy smooth (tree segmenatation)

        # watershed segmentation
        r_chm_flip = os.path.join(prefix + "_015_chm_flip_temp") # temporary file 
        r_flowdir = os.path.join(prefix + "_015_flowdir_temp") # temporary file 
        r_sinks = os.path.join(prefix + "_015_sinks") 
        r_watersheds = os.path.join(prefix + "_015_watersheds")

        # identify tree tops 
        r_focflow = os.path.join(prefix + "_016_focflow_temp") # temporary file
        r_focflow_01 = os.path.join(prefix + "_016_focflow_01_temp") # temporary file
        v_top_poly = os.path.join(prefix + "_016_top_poly_temp") # temporary file
        v_top_singlepoly = os.path.join(prefix + "_016_top_singlepoly_temp") # temporary file
        v_top_pnt = os.path.join(prefix + "_016_all_tops_temp") # temporary file containing all points 
        v_top_1to1 = os.path.join(prefix + "_016_top_1to1") # contains ONLY points that intersect with tree crowns 

        # identify tree crowns 
        v_crown_poly = os.path.join(prefix + "_017_all_crowns_temp") # old name v_watersheds (temporary file containing all points )
        v_crown_1to1 = os.path.join(prefix + "_017_crown_1to1") # contains ONLY crowns that intersect with a treetop

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
        #     Create CHM for the study area (TODO add +200m buffer to avoid edge effect?)
        # ------------------------------------------------------ #
        arcpy.AddMessage("\t1.2 Create Canopy Height Model (CHM)")

        if arcpy.Exists(r_chm):
            arcpy.AddMessage("\t\tCHM for tile <<{}>> exists in database. Continue ...".format(tile_code))
        else:
            start_time1 = time.time()
                        
            # create DTM
            tree.create_DTM(d_las, r_dtm, spatial_resolution, study_area_path)
            
            # create DSM 
            if veg_is_available:
                arcpy.AddMessage("\t\tLiDAR point clouds are classified for vegetation in {} kommune. \n\t\tThe classes unclassified (1), low- (3), medium- (4), and, high (5) vegetation are used to create the DSM.".format(kommune))
                class_code=["1", "3", "4", "5"]
                return_values=["1", "3", "4", "5"]
                tree.create_DSM(d_las, r_dsm, spatial_resolution, class_code, return_values, study_area_path)
            else:
                arcpy.AddMessage("\t\tLiDAR point clouds are not classified for vegetation in {} kommune. \n\t\tSolely the class unclassified (1) is used to create the DSM.".format(kommune))
                class_code=["1"]
                return_values=["1"]
                tree.create_DSM(d_las, r_dsm, spatial_resolution, class_code, return_values, study_area_path)
                
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
                tree.create_RGB(d_las, r_rgb, study_area_path)
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

        try:
            arcpy.AddMessage("\t1.5 The Watershed Segmentation Method")
            start_time1 = time.time()
            if arcpy.Exists(r_watersheds):
                arcpy.AddMessage("\t\t The watershed raster for tile <<{}>> exists in database. Continue ...".format(tile_code))
            else: 
                # nested function for watershed segmentation method
                tree.watershed_segmentation(r_chm_smooth,r_chm_flip,r_flowdir,r_sinks,r_watersheds)
                end_time1(start_time1)
        except Exception as e:
            # catch any exception and print error message. 
            arcpy.AddMessage(f"\t\tERROR: {e}. \nContinue...")


        # ------------------------------------------------------ #
        # 1.6 IDENTIFY TREE TOPS 
        #     Identify tree tops (I) by identifying focal flow (old 1.15)
        #     Identify tree tops (II) by converting focal flow values from 0 to 1 (old 1.16)
        #     Vectorize tree tops to polygons (old 1.17)
        #     Convert tree top polygons to points (old 1.18)
        # ------------------------------------------------------ #        

        # TODO use version 2 instead! 
        # r_focflow_01 can be deleted
        try:        
            arcpy.AddMessage("\t1.6 Identify Tree Tops  ")
            start_time1 = time.time()
            if arcpy.Exists(v_top_pnt):
                arcpy.AddMessage("\t\tThe treetop vector for tile <<{}>> exists in database. Continue ...".format(tile_code))
            else: 
                # nested function to identify treeTops
                tree.identify_treeTops(r_sinks, r_focflow, v_top_poly,v_top_singlepoly, r_chm_h, r_dsm, v_top_pnt)
                end_time1(start_time1)
        except Exception as e:
            # catch any exception and print error message. 
            arcpy.AddMessage(f"\t\tERROR: {e}. \nContinue...")
        
        #list_tree_top_names.append(v_top_pnt)

        # ------------------------------------------------------ #
        #  1.7 IDENTIFY TREE CROWNS
        #      Identify tree crowns by vectorizing watersheds (old 1.19)
        # ------------------------------------------------------ #  

        arcpy.AddMessage("\t1.7 Identify Tree Crowns ")
        start_time1 = time.time()
        if arcpy.Exists(v_crown_poly):
                arcpy.AddMessage("\t\tThe tree crown vector for tile <<{}>> exists in database. Continue ...".format(tile_code))
        else: 
            tree.identify_treeCrowns(r_watersheds,v_crown_poly)
            end_time1(start_time1)


        
        # adding lidar info to attr. 
        #computeAttribute.attr_lidarTile(v_top_pnt, tile_code)
        laser_tile = LaserAttributes(filegdb_path, v_crown_poly, v_top_pnt)
        laser_tile.attr_lidarTile(tile_code)

        # ------------------------------------------------------ #
        # 1.8 TOPOLOGY CHECK - ONLY ONE POINT WITHIN A POLYGON 
        #     Select only tree points within neighbourhood (old 1.20)
        #     Select only tree polygons within neighbourhood (i.e., the ones that intersect with tree tops) (old 1.21)
        #     STEP 1.8 NOT NECESSARY already selected by study area by using Extract by Mask in CHM and vegetation mask     
        # ------------------------------------------------------ #
        arcpy.AddMessage("\t1.8 Topology check - one pnt within a polygon")
        arcpy.AddMessage("\t\tSelecting only treecrown polygons that intersect with treetop point ...")
        tree.topology_crownTop(v_crown_poly,v_top_pnt,v_crown_1to1)
        
        arcpy.AddMessage("\t\tSelecting only treetop points that intersect with treecrown polygons ...")
        tree.topology_crownTop(v_top_pnt,v_crown_1to1,v_top_1to1)
        
        # ------------------------------------------------------ #
        #  1.9 LIST ALL TOP PNTS AND CROWN POLYGONS 
        # ------------------------------------------------------ #
        arcpy.AddMessage("\t1.9 List all top pnts and crown polygons")
        arcpy.AddMessage("\t\tAppending all treecrowns to list_tree_crown_names ...")
        list_tree_crown_names.append(v_crown_1to1)
        arcpy.AddMessage("\t\tAppending all treetops to list_tree_top_names ...")
        list_tree_top_names.append(v_top_1to1)

        arcpy.AddMessage("\t---------------------")
        #break 

# ------------------------------------------------------ #
# 2. Merge detected trees into one file
# ------------------------------------------------------ #
    arcpy.AddMessage("-"*100)
    arcpy.AddMessage("Step 2: Merging detected trees into one file...")
    arcpy.AddMessage("-"*100)
    
    start_time1 = time.time()
    if arcpy.Exists(v_top_merge):
        arcpy.AddMessage(f"\t\tThe thee top layers for the different tiles are already merged. \n\t\tThe merged file is located in {kommune}_Laser_ByTre.gdb. Continue ...")
    else:
        arcpy.AddMessage("\t\tMerge tree tops for all tiles into one polygon file.")
        arcpy.Merge_management(
            inputs = list_tree_top_names,
            output = v_top_merge
        )
        end_time1(start_time1) 

    start_time1 = time.time()
    if arcpy.Exists(v_crown_merge):
        arcpy.AddMessage(f"\t\tThe thee crown layers for the different tiles are already merged. \n\t\tThe merged file is located in {kommune}_Laser_ByTre.gdb. Continue ...")
    else:
        arcpy.AddMessage("\t\tMerge tree crowns for all tiles into one polygon file.")
        arcpy.Merge_management(
            inputs = list_tree_crown_names,
            output = v_crown_merge
        )
        end_time1(start_time1)  
    
    ## contine to else statement 

else:
    arcpy.AddMessage("\tTree polygons and points are already detected. Continue to Step 3...")
    
    # ------------------------------------------------------ #
    # 3. Select trees outside buildings and sea
    # TODO move to separate file (identify false detections)
    # add more 4.5 IDENTIFY FALSE DETECTIONS (v2!)
    # ------------------------------------------------------ #
    arcpy.AddMessage("-"*100)
    arcpy.AddMessage("Step 3: Selecting trees outside buildings and sea...")
    arcpy.AddMessage("-"*100)
    
    # select tree points 
    start_time1 = time.time()
    v_top_mask = os.path.join(laser_trees_path, "top_mask") 
    v_crown_mask = os.path.join(laser_trees_path, "crown_mask") 
    v_top_mask_1to1 = os.path.join(laser_trees_path, "top_1to1")
    v_crown_mask_1to1 = os.path.join(laser_trees_path, "crown_1to1")
    
    if arcpy.Exists(v_top_mask_1to1) and arcpy.Exists(v_crown_mask_1to1):
        arcpy.AddMessage(f"\tThe treetops and treecrowns are already masked for false trees within building and water areas. Continue ...")
    else:
        
        # mask tree tops 
        arcpy.AddMessage(f"\tThe tree tops are masked for false trees within building and water areas...")
        selected_trees = v_top_mask # TODO better name masked_trees?
        
        # TODO ADD IF EXISTS to vsea and vbuilding 
        v_sea = select_area.select_sea(FKB_WATER_PATH, study_area_path, admin_data_path)
        v_building = select_area.select_building(FKB_BUILDING_PATH, study_area_path, admin_data_path)
        v_top_mask = select_area.mask_tree(v_top_merge, v_building,v_sea,selected_trees)
        
        
        # mask tree crowns
        arcpy.AddMessage(f"\tThe tree crowns are masked for false trees within building and water areas...")
        selected_trees = v_crown_mask
        v_crown_mask = select_area.mask_tree(v_crown_merge, v_building,v_sea,selected_trees)

        arcpy.AddMessage("\t\tSelecting only treetop points that intersect with treecrown polygons ...")
        tree.topology_crownTop(v_top_mask, v_crown_mask,v_top_mask_1to1) 
        arcpy.AddMessage("\tEnsuring that each treecrown polygon contains one treetop point ...")
        tree.topology_crownTop(v_crown_mask, v_top_mask_1to1,v_crown_mask_1to1)

    # TODO delete fkb sea/building to save storage space
    #arcpy.Delete_management(v_sea)
    #arcpy.Delete_management(v_building)
                                               
                                               
    # ------------------------------------------------------ #
    # 4. Compute additional laser attributes
    # TODO move this step to main.py to separate file and compute all 
    # ------------------------------------------------------ #
    arcpy.AddMessage("-"*100)
    arcpy.AddMessage("Step 4: Computing additional laser attributes...") 
    arcpy.AddMessage("-"*100)
    
    # TODO check all attributes
    
    laser_trees = LaserAttributes(laser_trees_path, v_crown_mask_1to1, v_top_mask_1to1)
    laser_trees.attr_crownID()
    laser_trees.attr_crownDiam()
    laser_trees.attr_crownArea()
    laser_trees.join_crownID_toTop()
    laser_trees.join_topAttr_toCrown()
    laser_trees.attr_crownVolume()
    
    # TODO Delete if new class LaserAttributes works 
    #computeAttribute.attr_crownID(v_crown_mask_1to1)
    #computeAttribute.attr_crownArea(v_crown_mask_1to1, laser_trees_path)
    #computeAttribute.polygonAttr_toPoint(v_top_mask_1to1, v_crown_mask_1to1, laser_trees_path)
    #computeAttribute.pointAttr_toPolygon(v_crown_mask_1to1,v_top_mask_1to1)
    #computeAttribute.attr_crownVolume(v_crown_mask_1to1)
    #computeAttribute.attr_crownVolume(v_top_mask_1to1)

end_time0 = time.time()
execution_time0 = (end_time0 - start_time0)/60
arcpy.AddMessage("TOTAL TIME:\t {:.2f} min".format(execution_time0))


