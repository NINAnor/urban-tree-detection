""" 
Classify the geometric relation between the stem points (in situ) and the crown polygons (laser)
Case 1: one polygon contains one point (1:1), simple join.  
Case 2: one polygon contains more than one point (1:n), split crown with voronoi tesselation.
Case 3: a point is not overlapped by any polygon (0:1), model tree crown using oslo formula.
Case 4: a polygon does not contain any point (1:0), not used to train i-tree eco/dataset for extrapolation.

Bodo:
Case 1 and 2: 4583
Case 1: 1005 (unique JOIN_FID and unique TARGET_FID)
Case 2: 3576 (multiple JOIN_FID and unique TARGET FID)
Case 3: 0
Case 4: 76 399 (join_count (0))

stem in situ # join (JOIN_FID)
crown laser # target (TARGET_FID)
"""


# run classify_case_3_4.py before running this file

# -*- coding: utf-8 -*-
import os
import arcpy
from arcpy import env
from arcpy.sa import *
import logging

# local modules
from src import (SPATIAL_REFERENCE, URBAN_TREES_GDB)
from src import logger
from src import arcpy_utils as au

# set console logger
logger.setup_logger(logfile=False)

# set path variables
ds_input_trees = os.path.join(URBAN_TREES_GDB, "input_trees")
ds_joined_trees = os.path.join(URBAN_TREES_GDB, "joined_trees")

# input
fc_case_1_2 = os.path.join(ds_joined_trees, "c1_c2_crowns") 
fc_stem_in_situ = os.path.join(ds_input_trees, "stem_in_situ") 

# output
fc_case_1 = os.path.join(ds_joined_trees, "c1_crowns") # case 1 crowns
fc_case_2 = os.path.join(ds_joined_trees, "c2_crowns") # case 2 crowns
fc_case_1_stems = os.path.join(ds_joined_trees, "c1_stems") # case 1 stems
fc_case_2_stems = os.path.join(ds_joined_trees, "c2_stems") # case 2 stems


# env settings
env.overwriteOutput = True
env.outputCoordinateSystem = arcpy.SpatialReference(SPATIAL_REFERENCE)
env.workspace = ds_joined_trees

au.addField_ifNotExists(
    featureclass= fc_case_1_2,
    fieldname="geo_relation",
    type="TEXT"
    )

# --------------------------------------------------------------------------- #
# Calculate TARGET and JOIN COUNT
# --------------------------------------------------------------------------- #

# calculate COUNT_JOIN_FID
join_fid_count_stats = arcpy.Statistics_analysis(
    in_table= fc_case_1_2, 
    out_table="in_memory/join_fid_count_table",
    statistics_fields= [["JOIN_FID", "COUNT"]], 
    case_field="TARGET_FID"
    )

# add COUNT_JOIN_FID as field to fc
arcpy.JoinField_management(
    in_data=fc_case_1_2, 
    in_field="TARGET_FID", 
    join_table=join_fid_count_stats,
    join_field="TARGET_FID", 
    fields="COUNT_JOIN_FID"
    )

# calculate COUNT_TARGET_FID
target_fid_count_stats = arcpy.Statistics_analysis(
    fc_case_1_2, 
    "in_memory/target_fid_count_table", 
    [["TARGET_FID", "COUNT"]], 
    "JOIN_FID"
    )
# add COUNT_TARGET_FID as field to fc 
arcpy.JoinField_management(
    fc_case_1_2, 
    "JOIN_FID", 
    target_fid_count_stats, 
    "JOIN_FID", 
    "COUNT_TARGET_FID"
    )

# Create a feature layer from the input feature class
arcpy.MakeFeatureLayer_management(fc_case_1_2, "lyr")

field_geo_relation = "geo_relation"
query_case_1 = "COUNT_TARGET_FID_1 = 1 And COUNT_JOIN_FID_1 = 1"   # (polygon:point = 1:1)
query_case_2 = "COUNT_TARGET_FID_1 = 1 And COUNT_JOIN_FID_1 > 1"   # (polygon:point = 1:n)


# --------------------------------------------------------------------------- #
# CASE 1 (1:1)
# --------------------------------------------------------------------------- #

if arcpy.Exists(fc_case_1):
    arcpy.AddMessage(f"\tFeature {os.path.basename(fc_case_1)} already exists. Continue...")
else:   
    arcpy.management.SelectLayerByAttribute(
        in_layer_or_view="lyr",
        selection_type="NEW_SELECTION",
        where_clause=query_case_1,
        invert_where_clause=None
    )
    arcpy.CopyFeatures_management("lyr", fc_case_1)
    arcpy.management.CalculateField(
    in_table=fc_case_1,
    field=field_geo_relation,
    expression='"Case 1"',
    expression_type="PYTHON_9.3",
    code_block="",
    field_type="TEXT",
    enforce_domains="NO_ENFORCE_DOMAINS"
    )
    logging.info(f'Case 1 selected and exported to {os.path.basename(fc_case_1)}')

# --------------------------------------------------------------------------- #
# CASE 2 (1:n)
# --------------------------------------------------------------------------- #

if arcpy.Exists(fc_case_2):
    arcpy.AddMessage(f"\tFeature {os.path.basename(fc_case_2)} already exists. Continue...")
else:   
    arcpy.management.SelectLayerByAttribute(
        in_layer_or_view="lyr",
        selection_type="NEW_SELECTION",
        where_clause=query_case_2,
        invert_where_clause=None
    )
    arcpy.CopyFeatures_management("lyr", fc_case_2)
    arcpy.management.CalculateField(
        in_table=fc_case_2,
        field=field_geo_relation,
        expression='"Case 2"',
        expression_type="PYTHON_9.3",
        code_block="",
        field_type="TEXT",
        enforce_domains="NO_ENFORCE_DOMAINS"
    )
    logging.info(f'Case 2 selected and exported to {os.path.basename(fc_case_2)}')  


# --------------------------------------------------------------------------- #
# Clean results
# --------------------------------------------------------------------------- #    
    
# list of fields to be kept
keep_fields = ["TARGET_FID", "JOIN_FID", "COUNT_TARGET_FID_1", "COUNT_JOIN_FID_1", "crown_id_laser", "tree_id", "geo_relation"]

method = "KEEP_FIELDS"
arcpy.DeleteField_management(fc_case_1,keep_fields, "KEEP_FIELDS")
arcpy.DeleteField_management(fc_case_2,keep_fields, "KEEP_FIELDS")

# --------------------------------------------------------------------------- #
# Extract crowns to stems 
# --------------------------------------------------------------------------- # 

id_field = "tree_id"
au.extractFeatures_byID(
    target_feature=fc_stem_in_situ, 
    id_feature=fc_case_1, 
    output_feature=fc_case_1_stems, 
    id_field = id_field)
au.extractFeatures_byID(fc_stem_in_situ, fc_case_2, fc_case_2_stems, id_field)