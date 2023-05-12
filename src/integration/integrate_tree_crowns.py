""" 
Integrates the tree crown polygons derived from different analysis into one unified dataet.  
Trees from Case 1, 2, and 3 are the training dataset for the i-Tree Eco model
Trees from Case 4 are the extrapolation dataset.  

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

# local modules
from src import (URBAN_TREES_GDB, SPATIAL_REFERENCE)

# set path variables
ds_joined_trees = os.path.join(URBAN_TREES_GDB, "joined_trees")
ds_itree_trees = os.path.join(URBAN_TREES_GDB, "itree_trees")

fc_case_1 = os.path.join(ds_joined_trees, "join_case_1") 
fc_case_2 = os.path.join(ds_joined_trees, "join_case_2") 
fc_case_3 = os.path.join(ds_joined_trees, "join_case_3")
fc_case_4 = os.path.join(ds_joined_trees, "join_case_4")
fc_training = os.path.join(ds_itree_trees, "training_trees")
fc_extrapolation= os.path.join(ds_itree_trees, "extrapolation_trees")

# env settings
env.overwriteOutput = True
env.outputCoordinateSystem = arcpy.SpatialReference(SPATIAL_REFERENCE)
env.workspace = ds_joined_trees

# --------------------------------------------------------------------------- #
# create training dataset
# --------------------------------------------------------------------------- #

fc_input= "join_case_1;join_case_2;join_case_3"
fm_string= str(
    'tree_id "tree_id" true true false 4 Long 0 0,First,#,join_case_1,tree_id,-1,-1,join_case_2,tree_id,-1,-1,join_case_3,tree_id,-1,-1;\
    crown_id_laser "crown_id_laser" true true false 4 Long 0 0,First,#,join_case_1,crown_id_laser,-1,-1,join_case_2,crown_id_laser,-1,-1,join_case_3,crown_id_laser,-1,-1;\
    geo_relation "geo_relation" true true false 255 Text 0 0,First,#,join_case_1,geo_relation,0,255,join_case_2,geo_relation,0,255,join_case_3,geo_relation,0,255;\
    Shape_Length "Shape_Length" false true true 8 Double 0 0,First,#,join_case_1,Shape_Length,-1,-1,join_case_2,Shape_Length,-1,-1,join_case_3,Shape_Length,-1,-1;\
    Shape_Area "Shape_Area" false true true 8 Double 0 0,First,#,join_case_1,Shape_Area,-1,-1,join_case_2,Shape_Area,-1,-1,join_case_3,Shape_Area,-1,-1'
)

if arcpy.Exists(fc_training):
    arcpy.AddMessage(f"\tFeature {os.path.basename(fc_training)} already exists. Continue...")
else:
    arcpy.management.Merge(
        inputs=fc_input,
        output=fc_training,
        field_mappings= fm_string,
        add_source="NO_SOURCE_INFO"
    )

# --------------------------------------------------------------------------- #
# create extrapolation dataset
# --------------------------------------------------------------------------- #

if arcpy.Exists(fc_extrapolation):
    arcpy.AddMessage(f"\tFeature {os.path.basename(fc_extrapolation)} already exists. Continue...")
else:
    arcpy.management.CopyFeatures(
        in_features="join_case_4",
        out_feature_class=fc_extrapolation
    )
        
    # list of fields to be kept
    keep_fields = ["tree_id", "geo_relation", "crown_id_laser"]
    method = "KEEP_FIELDS"
    arcpy.DeleteField_management(fc_extrapolation, keep_fields, "KEEP_FIELDS")
