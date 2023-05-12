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

fc_case_1_2 = os.path.join(ds_joined_trees, "join_case_1_2") 
fc_case_1 = os.path.join(ds_joined_trees, "join_case_1") 
fc_case_2 = os.path.join(ds_joined_trees, "join_case_2") 

# env settings
env.overwriteOutput = True
env.outputCoordinateSystem = arcpy.SpatialReference(SPATIAL_REFERENCE)
env.workspace = ds_joined_trees

# --------------------------------------------------------------------------- #
# Select corresponding stem points 
# --------------------------------------------------------------------------- #

# Create a feature layer from the input feature class
fc_stem_in_situ = os.path.join(ds_input_trees, "stem_in_situ")
fc_case_2_stems = os.path.join(ds_joined_trees, "join_case_2_stems") 
arcpy.MakeFeatureLayer_management(fc_stem_in_situ, "lyr_stems")

arcpy.management.SelectLayerByLocation(
    in_layer=fc_stem_in_situ,
    overlap_type="INTERSECT",
    select_features=fc_case_2,
    search_distance=None,
    selection_type="NEW_SELECTION",
    invert_spatial_relationship="NOT_INVERT"
)

arcpy.CopyFeatures_management("lyr_stems", fc_case_2_stems)
logging.info(f'In situ trees selected that overlap with Case 2 polygons and exported to {os.path.basename(fc_case_2_stems)}.') 

