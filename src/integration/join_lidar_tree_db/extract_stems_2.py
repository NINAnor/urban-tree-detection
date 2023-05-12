# -*- coding: utf-8 -*-
import os
import arcpy
from arcpy import env
from arcpy.sa import *
import logging

# local modules
from src import (SPATIAL_REFERENCE, URBAN_TREES_GDB)
from src import arcpy_utils as au

# set path variables
ds_input_trees = os.path.join(URBAN_TREES_GDB, "input_trees")
ds_joined_trees = os.path.join(URBAN_TREES_GDB, "joined_trees")

fc_case_1 = os.path.join(ds_joined_trees, "join_case_1") 
fc_case_2 = os.path.join(ds_joined_trees, "join_case_2") 

fc_stem_in_situ = os.path.join(ds_input_trees, "stem_in_situ") # point layer 
fc_case_2_stems = os.path.join(ds_joined_trees, "join_case_2_stems") # output point layer 

# env settings
env.overwriteOutput = True
env.outputCoordinateSystem = arcpy.SpatialReference(SPATIAL_REFERENCE)
env.workspace = ds_joined_trees

point_layer = fc_stem_in_situ
polygon_layer = fc_case_1

# Create a temporary layer of points with only the tree_id attribute
temp_layer = arcpy.management.MakeFeatureLayer(point_layer, "temp_layer", where_clause="tree_id IS NOT NULL")

# Perform a spatial join between the polygon layer and the temporary point layer based on the tree_id attribute
join_layer = arcpy.analysis.SpatialJoin(polygon_layer, temp_layer, "in_memory\\join_layer", join_type="KEEP_COMMON", match_option="INTERSECT")

# Create a set of unique tree_ids from the join_layer
tree_ids = set(row[0] for row in arcpy.da.SearchCursor(join_layer, "tree_id"))

# Use a table join to extract the points from the original point layer that have a tree_id in the tree_ids set
arcpy.management.JoinField(point_layer, "tree_id", join_layer, "tree_id")

# Create a new layer that only includes the matched points
arcpy.management.MakeFeatureLayer(point_layer, fc_case_2_stems, where_clause=f"tree_id IN {tuple(tree_ids)}")
