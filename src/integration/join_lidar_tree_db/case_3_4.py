""" 
Classify the geometric relation between the stem points (in situ) and the crown polygons (laser)
Case 1: one polygon contains one point (1:1), simple join.  
Case 2: one polygon contains more than one point (1:n), split crown with voronoi tesselation.
Case 3: a point is not overlapped by any polygon (0:1), model tree crown using oslo formula.
Case 4: a polygon does not contain any point (1:0), not used to train i-tree eco/dataset for extrapolation.
"""

# run make_gdb.py and make_fc.py before running this file

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
fc_stem_in_situ = os.path.join(ds_input_trees, "stem_in_situ") 
fc_joined_trees = os.path.join(ds_joined_trees, "joined_trees") 

# output
fc_case_1_2 = os.path.join(ds_joined_trees, "join_case_1_2") 
fc_case_3 = os.path.join(ds_joined_trees, "join_case_3")
fc_case_3_stems = os.path.join(ds_joined_trees, "join_case_3_stems")
fc_case_4 = os.path.join(ds_joined_trees, "join_case_4")

# env settings
env.overwriteOutput = True
env.outputCoordinateSystem = arcpy.SpatialReference(SPATIAL_REFERENCE)
env.workspace = ds_joined_trees

au.addField_ifNotExists(
    featureclass= fc_joined_trees,
    fieldname="geo_relation",
    type="TEXT"
    )

# Create a feature layer from the input feature class
arcpy.MakeFeatureLayer_management(fc_joined_trees, "lyr")

field_crown_id = "crown_id_laser"
field_tree_id = "tree_id"
field_geo_relation = "geo_relation"

query_case_1_2 = f"{field_crown_id} IS NOT NULL AND {field_tree_id} IS NOT NULL" # (polygon:point = 1:1)
query_case_3 = f"{field_crown_id} IS NULL AND {field_tree_id} IS NOT NULL"  # (polygon:point = 0:1) 
query_case_4 = f"{field_crown_id} IS NOT NULL AND {field_tree_id} IS NULL"  # (polygon:point = 1:0)

# --------------------------------------------------------------------------- #
# CASE 1 and CASE 2 (n:n) --> split in script classify_case_1_2.py
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
    arcpy.CopyFeatures_management("lyr", fc_case_1_2)
    logging.info(f'Case 1 and 2 selected and exported to {os.path.basename(fc_case_1_2)}')

# --------------------------------------------------------------------------- #
# CASE 3 (0:1)
# --------------------------------------------------------------------------- #

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
    arcpy.management.CalculateField(
        in_table=fc_case_3,
        field=field_geo_relation,
        expression='"Case 3"',
        expression_type="PYTHON_9.3",
        code_block="",
        field_type="TEXT",
        enforce_domains="NO_ENFORCE_DOMAINS"
        )
    logging.info(f'Case 3 selected and exported to {os.path.basename(fc_case_3)}')


    id_field = "tree_id"
    au.extractFeatures_byID(
        target_feature=fc_stem_in_situ, 
        id_feature=fc_case_3, 
        output_feature=fc_case_3_stems, 
        id_field = id_field)
    
# --------------------------------------------------------------------------- #
# CASE 4 (1:0) 
# --------------------------------------------------------------------------- #

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
    arcpy.management.CalculateField(
        in_table=fc_case_4,
        field=field_geo_relation,
        expression='"Case 4"',
        expression_type="PYTHON_9.3",
        code_block="",
        field_type="TEXT",
        enforce_domains="NO_ENFORCE_DOMAINS"
        )
    logging.info(f'Case 4 selected and exported to {os.path.basename(fc_case_4)}')


# --------------------------------------------------------------------------- #
# Clean the results
# --------------------------------------------------------------------------- #    
    
# list of fields to be kept
keep_fields = ["TARGET_FID", "JOIN_FID", "crown_id_laser", "tree_id", "geo_relation"]

method = "KEEP_FIELDS"
arcpy.DeleteField_management(fc_case_3,keep_fields, "KEEP_FIELDS")
arcpy.DeleteField_management(fc_case_3_stems,keep_fields, "KEEP_FIELDS")
arcpy.DeleteField_management(fc_case_4,keep_fields, "KEEP_FIELDS")