""" 
Joins the municipal tree dataset (stem points) with the 
segmented laser tree crowns (tree crown polygons) 
result: urban_trees (fc) 
"""
# -*- coding: utf-8 -*-
import os
import arcpy
from arcpy import env
from arcpy.sa import *

# local modules
from src import (SPATIAL_REFERENCE, URBAN_TREES_GDB)
from src import logger

# set console logger
logger.setup_logger(logfile=False)

# --------------------------------------------------------------------------- #
# RUN make_gdb and make_fc before running this file
# --------------------------------------------------------------------------- #

# set path variables
ds_urban_trees = os.path.join(URBAN_TREES_GDB, "urban_trees")

fc_stem_in_situ = os.path.join(URBAN_TREES_GDB, "urban_trees", "stem_in_situ") # join
fc_crown_laser = os.path.join(URBAN_TREES_GDB, "urban_trees", "crown_laser") # target
fc_urban_trees = os.path.join(URBAN_TREES_GDB, "urban_trees", "urban_trees") # putput

# env settings
env.overwriteOutput = True
env.outputCoordinateSystem = arcpy.SpatialReference(SPATIAL_REFERENCE)
env.workspace = ds_urban_trees

#------------------------------------------------------ #
# SPATIAL JOIN - TREE CROWN POLYGON CONTAINS STEM POINT
# ----------------------------------------------------- #
arcpy.AddMessage(f"\tCreating a joined feature class {os.path.basename(fc_urban_trees)} by joining\
    the in situ stem points to the crown polygons that they intersect ... ")

# define field mapping
fm_crown_id = str(f'crown_id_laser "crown_id_laser" true true false 4 Long 0 0,First,#,{fc_crown_laser},crown_id_laser,-1,-1')
fm_crown_diam = str(f'crown_diam "crown_diam" true true false 4 Float 0 0,First,#,{fc_crown_laser},crown_diam,-1,-1')
fm_crown_area = str(f'crown_area "crown_area" true true false 4 Float 0 0,First,#,{fc_crown_laser},crown_area,-1,-1')
fm_tree_height = str(f'tree_height "tree_height" true true false 4 Float 0 0,First,#,{fc_crown_laser},tree_height,-1,-1')
fm_tree_id = str(f'tree_id "tree_id" true true false 4 Long 0 0,First,#,{fc_stem_in_situ},tree_id,-1,-1')
fm_dbh = str(f'dbh "dbh" true true false 4 Long 0 0,First,#,{fc_stem_in_situ},dbh,-1,-1')
fm_crown_radius = str(f'crown_radius "crown_radius" true true false 4 Long 0 0,First,#,{fc_stem_in_situ},crown_radius,-1,-1')
fm_norwegian_name = str(f'norwegian_name "norwegian_name" true true false 255 Text 0 0,First,#,{fc_stem_in_situ},norwegian_name,0,255')

fm_list = [fm_crown_id,fm_crown_diam,fm_crown_area,fm_tree_height,fm_tree_id,fm_dbh,fm_crown_radius,fm_norwegian_name]

# generate field mapping string
fieldmapping= ""
for string in fm_list:
    fieldmapping += string + ";"
fieldmapping = fieldmapping[:-1] # remove the last semicolon

arcpy.AddMessage(f'fieldmapping:+n{fieldmapping}')

# join 
if arcpy.Exists(fc_urban_trees):
    arcpy.AddMessage(f"\tFeature {os.path.basename(fc_urban_trees)} already exists. Continue...")
else:
    arcpy.analysis.SpatialJoin(
        target_features=fc_crown_laser,
        join_features=fc_stem_in_situ,
        out_feature_class=fc_urban_trees,
        join_operation="JOIN_ONE_TO_MANY",
        join_type="KEEP_ALL",
        field_mapping = fieldmapping,
        match_option="CONTAINS",
        search_radius=None,
        distance_field_name=""
    )
    
    
