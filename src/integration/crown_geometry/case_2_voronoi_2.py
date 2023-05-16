""" 
Model Crown Geometry for Case 2. 
Case 2: one polygon contains more than one point (1:n), split crown with voronoi tesselation.
""" 
import os
import arcpy
from arcpy import env
import logging 

# local packages
from src import logger
from src import (SPATIAL_REFERENCE, URBAN_TREES_GDB, MUNICIPALITY)
from src import arcpy_utils as au


logger.setup_logger(logfile=False)
logging.info(f'Split Case 2 treecrowns for <{MUNICIPALITY}> municipality using a Voronoi diagram.')

# input data
ds_joined_trees = os.path.join(URBAN_TREES_GDB, "joined_trees")
fc_case_2_stems = os.path.join(ds_joined_trees, "c2_stems_cleaned") 
fc_case_2_crowns = os.path.join(ds_joined_trees, "c2_crowns_cleaned") 

# output data 
fc_c2_crowns_voronoi = os.path.join(ds_joined_trees, "c2_crowns_voronoi") 

# set environment 
env.overwriteOutput = True
env.outputCoordinateSystem = arcpy.SpatialReference(SPATIAL_REFERENCE)
env.workspace = ds_joined_trees

polygon_layer = fc_case_2_crowns # CASE 2 tree crowns
point_layer = fc_case_2_stems # CASE 2 tree stems 
temp_layer = os.path.join(ds_joined_trees, "temp_crown") 

# Create a feature layer from the input feature class
arcpy.MakeFeatureLayer_management(point_layer, "point_lyr")

# Define paths for temporary feature classes
tmp_crown_lyr = os.path.join(ds_joined_trees, "temp_crown") 
tmp_thiessen_lyr = os.path.join(ds_joined_trees, "thiessen")
tmp_split_crown_lyr = os.path.join(ds_joined_trees, "temp_split_crown") 

fields = ["tree_crown_id", "tree_id", "crown_id_laser"]
unique_tree_crown_ids = set()
with arcpy.da.SearchCursor(polygon_layer, fields) as cursor:
    for row in cursor:
        tree_crown_id = row[0]
        unique_tree_crown_ids.add(tree_crown_id)

for tree_crown_id in unique_tree_crown_ids:
    logging.info(f"START SPLITTING TREECROWN, tree_crown_id: {tree_crown_id}")

    # Select tree crowns by tree_crown_id
    arcpy.MakeFeatureLayer_management(polygon_layer, "selected_polygons", f"tree_crown_id = '{tree_crown_id}'")

    # Select stem points that intersect with the tree crowns
    arcpy.SelectLayerByLocation_management("point_lyr", "INTERSECT", "selected_polygons")
    arcpy.CopyFeatures_management("selected_polygons", tmp_crown_lyr)

    # Log the tree_id values of the selected stem points
    fields_pnt = ["OBJECTID", "tree_id"]
    with arcpy.da.SearchCursor("point_lyr", fields_pnt) as cursor_pnt:
        for row_pnt in cursor_pnt:
            logging.info(f"OBJECTID: {row_pnt[0]}, tree_id: {row_pnt[1]}")

    # Split the tree crowns using the Thiessen polygons
    env.extent = tmp_crown_lyr
    arcpy.CreateThiessenPolygons_analysis("point_lyr", tmp_thiessen_lyr)
    arcpy.Intersect_analysis([tmp_thiessen_lyr, tmp_crown_lyr], tmp_split_crown_lyr)
    arcpy.Append_management(
        inputs=tmp_split_crown_lyr,
        target=fc_c2_crowns_voronoi,
        schema_type="NO_TEST",
        field_mapping=None,
        subtype="",
        expression="",
        match_fields=None,
        update_geometry="NOT_UPDATE_GEOMETRY"
    )

# Delete temporary feature classes
arcpy.Delete_management(tmp_crown_lyr)
arcpy.Delete_management(tmp_thiessen_lyr)
arcpy.Delete_management(tmp_split_crown_lyr)

    
    


