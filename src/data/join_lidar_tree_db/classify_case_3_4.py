""" 
Classify the geometric relation between the stem points (in situ) and the crown polygons (laser)
Case 1: one polygon contains one point (1:1), simple join.  
Case 2: one polygon contains more than one point (1:n), split crown with voronoi tesselation.
Case 3: a point is not overlapped by any polygon (0:1), model tree crown using oslo formula.
Case 4: a polygon does not contain any point (1:0), not used to train i-tree eco/dataset for extrapolation.

result: geo_relation (attr. field in urban_trees feature class) 

Bodo:
Case 1 and 2: 4583
Case 1:  (unique JOIN_FID and unique TARGET_FID)
Case 2: (multiple JOIN_FID and unique TARGET FID)
Case 3: 0
Case 4: 76 399 (join_count (0))

stem in situ # join (JOIN_FID)
crown laser # target (TARGET_FID)
"""

# -*- coding: utf-8 -*-
import os
import csv
import arcpy
from arcpy import env
from arcpy.sa import *
import logging

# local modules
from src import (SPATIAL_REFERENCE, URBAN_TREES_GDB, PROCESSED_PATH, MUNICIPALITY)
from src import logger
from src import arcpy_utils as au

# set console logger
logger.setup_logger(logfile=False)

# --------------------------------------------------------------------------- #
# RUN make_gdb and make_fc before running this file
# RUN on VDI long run time due to large dataset (1)
# TODO solution long runtime: split into two scripts CASE 3, 4 CASE 2, 1
# --------------------------------------------------------------------------- #

# set path variables
ds_urban_trees = os.path.join(URBAN_TREES_GDB, "urban_trees")
ds_joined_trees = os.path.join(URBAN_TREES_GDB, "joined_trees")

fc_urban_trees = os.path.join(URBAN_TREES_GDB, "urban_trees", "urban_trees") # joined dataset
fc_case_1_2 = os.path.join(ds_urban_trees, "join_case_1_2") 
#fc_case_1 = os.path.join(ds_joined_trees, "join_case_1") 
#fc_case_2 = os.path.join(ds_joined_trees, "join_case_2") 
fc_case_3 = os.path.join(ds_joined_trees, "join_case_3")
fc_case_4 = os.path.join(ds_joined_trees, "join_case_4")

# env settings
env.overwriteOutput = True
env.outputCoordinateSystem = arcpy.SpatialReference(SPATIAL_REFERENCE)
env.workspace = ds_urban_trees

au.addField_ifNotExists(
    featureclass= fc_urban_trees,
    fieldname="geo_relation",
    type="TEXT"
    )



# Create a feature layer from the input feature class
arcpy.MakeFeatureLayer_management(fc_urban_trees, "lyr")

field_crown_id = "crown_id_laser"
field_tree_id = "tree_id"
field_geo_relation = "geo_relation"

#query_case_1 = "COUNT_TARGET_FID = 1 And COUNT_JOIN_FID = 1"            # (polygon:point = 1:1)
#query_case_2 = "COUNT_TARGET_FID = 1 And COUNT_JOIN_FID > 1"            # (polygon:point = 1:n)
query_case_1_2 = f"{field_crown_id} IS NOT NULL AND {field_tree_id} IS NOT NULL" # (polygon:point = 1:1)
#query_1_2_b = f"{field_crown_id} IS NULL AND {field_tree_id} IS NOT NULL"   # (polygon:point = 0:1) # same as query 3?
query_case_3 = f"{field_crown_id} IS NULL AND {field_tree_id} IS NOT NULL"  # (polygon:point = 0:1) 
query_case_4 = f"{field_crown_id} IS NOT NULL AND {field_tree_id} IS NULL"  # (polygon:point = 1:0)

# --------------------------------------------------------------------------- #
# CASE 1 and CASE 2 --> split in script classify_case_1_2.py
# --------------------------------------------------------------------------- #

#Select case 1 and case 2 and export to new fc 
if arcpy.Exists(fc_case_1_2):
   arcpy.AddMessage(f"\tFeature {os.path.basename(fc_case_1_2)} already exists. Continue...")
else:
    arcpy.management.SelectLayerByAttribute(
        in_layer_or_view="lyr",
        selection_type="NEW_SELECTION",
        where_clause=query_case_1_2,
        invert_where_clause=None
    ) 
    
    #arcpy.SelectLayerByAttribute_management("lyr", "NEW_SELECTION", "{} IS NOT NULL AND {} IS NOT NULL".format(field_crown_id, field_tree_id))
    #arcpy.SelectLayerByAttribute_management("lyr", "ADD_TO_SELECTION", "{} IS NULL AND {} IS NOT NULL".format(field_crown_id, field_tree_id))
    arcpy.CopyFeatures_management("lyr", fc_case_1_2)
    logging.info(f'Case 1 and 2 selected and exported to {os.path.basename(fc_case_1_2)}')

# --------------------------------------------------------------------------- #
# CASE 3 
# --------------------------------------------------------------------------- #

# Select and export case 3 (0:1) 
if arcpy.Exists(fc_case_3):
    arcpy.AddMessage(f"\tFeature {os.path.basename(fc_case_3)} already exists. Continue...")
else:
    arcpy.management.SelectLayerByAttribute(
        in_layer_or_view="lyr",
        selection_type="NEW_SELECTION",
        where_clause=query_case_3,
        invert_where_clause=None
    )
    arcpy.CopyFeatures_management("lyr", fc_case_3)
    au.calculateField_ifEmpty(fc_case_3, field=field_geo_relation, expression= "Case 3")
    logging.info(f'Case 3 selected and exported to {os.path.basename(fc_case_3)}')

# --------------------------------------------------------------------------- #
# CASE 4 
# --------------------------------------------------------------------------- #
# Select and export case 4 (1:0) 
if arcpy.Exists(fc_case_4):
    arcpy.AddMessage(f"\tFeature {os.path.basename(fc_case_4)} already exists. Continue...")
else:
    arcpy.management.SelectLayerByAttribute(
        in_layer_or_view="lyr",
        selection_type="NEW_SELECTION",
        where_clause=query_case_4,
        invert_where_clause=None
    )
    arcpy.CopyFeatures_management("lyr", fc_case_4)
    au.calculateField_ifEmpty(fc_case_4, field=field_geo_relation, expression= "Case 4")
    logging.info(f'Case 4 selected and exported to {os.path.basename(fc_case_4)}')

