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
ds_joined_trees = os.path.join(URBAN_TREES_GDB, "joined_trees")

logger.setup_logger(logfile=True)
logging.info(f'Split Case 2 treecrowns for <{MUNICIPALITY}> municipality using a Voronoi diagram.')

# input data


# input
fc_case_1_2 = os.path.join(ds_joined_trees, "c1_c2_crowns") 
fc_stem_in_situ = os.path.join(ds_input_trees, "stem_in_situ") 

# output
fc_case_2_stems = os.path.join(ds_joined_trees, "c2_stems") 
fc_case_2_crowns = os.path.join(ds_joined_trees, "c2_crowns") 

# output data 
fc_c2_crowns_voronoi = os.path.join(ds_joined_trees, "c2_crowns_voronoi") 
if arcpy.Exists(fc_c2_crowns_voronoi):
    logging.info(f"Feature {os.path.basename(fc_c2_crowns_voronoi)} already exists. Continue...")
else:  
    arcpy.CreateFeatureclass_management(
        out_path=ds_joined_trees,
        out_name = "c2_crowns_voronoi", 
        geometry_type="POLYGON"
        )
    
    au.addField_ifNotExists(fc_c2_crowns_voronoi, "tree_id", "LONG")
    au.addField_ifNotExists(fc_c2_crowns_voronoi, "crown_id_laser", "LONG")
    au.addField_ifNotExists(fc_c2_crowns_voronoi, "geo_relation", "TEXT")
    
    logging.info(f"Feature {os.path.basename(fc_c2_crowns_voronoi)} is created.")

# set environment 
env.overwriteOutput = True
env.outputCoordinateSystem = arcpy.SpatialReference(SPATIAL_REFERENCE)
env.workspace = ds_joined_trees

# set layers for analysis 
polygon_layer = fc_case_2_crowns # CASE 2 tree crowns
point_layer = fc_case_2_stems # CASE 2 tree stems 
temp_layer = os.path.join(ds_joined_trees, "temp_crown") 

# clean layers
keep_fields = ["OBJECTID","tree_id","crown_id_laser","geo_relation"]
arcpy.DeleteField_management(polygon_layer,keep_fields, "KEEP_FIELDS")
arcpy.DeleteField_management(point_layer,keep_fields, "KEEP_FIELDS")

# Create a feature layer from the input feature class
arcpy.MakeFeatureLayer_management(point_layer, "point_lyr")

# Split each tree crown based on the number of stems. 
fields = ["OBJECTID", "tree_id", "crown_id_laser"]
with arcpy.da.SearchCursor(polygon_layer, fields) as cursor:
    for row in cursor:
        
        # create memory layers
        mem_crown_lyr = "in_memory/temp_crown"
        mem_thiessen_lyr = "in_memory/thiessen"
        mem_split_crown_lyr = "in_memory/temp_split_crown" 
        
        logging.info(f"START SPLITTING TREECROWN, OBJECTID: {row[0]}, crown_id: {row[2]}")
        
        # select tree crown by OBJECTID
        polygon_id = row[0]
        arcpy.MakeFeatureLayer_management(polygon_layer, "selected_polygon", f"OBJECTID = {polygon_id}")

        # Select stem points that intersect with the tree crown
        arcpy.SelectLayerByLocation_management("point_lyr", "INTERSECT", "selected_polygon") # stem points
        arcpy.CopyFeatures_management("selected_polygon", mem_crown_lyr) # tree crown  

        # log the tree_id values of the selected stem points
        with arcpy.da.SearchCursor("point_lyr", fields) as cursor:
            for row in cursor:
                logging.info(f"OBJECTID: {row[0]}, tree_id: {row[1]}, crown_id: {row[2]}")


        # split the treecrown using the thiessen polygons
        env.extent = mem_crown_lyr # tree crown area 
        arcpy.CreateThiessenPolygons_analysis("point_lyr", mem_thiessen_lyr) 
        arcpy.Intersect_analysis([mem_thiessen_lyr, mem_crown_lyr], mem_split_crown_lyr)
        arcpy.Append_management(
            inputs=mem_split_crown_lyr,
            target= fc_c2_crowns_voronoi, 
            schema_type= "NO_TEST",
            field_mapping=None,
            subtype="",
            expression="",
            match_fields=None,
            update_geometry="NOT_UPDATE_GEOMETRY"
            )
        # delete memory layers
        arcpy.Delete_management(mem_crown_lyr)
        arcpy.Delete_management(mem_thiessen_lyr)  
        arcpy.Delete_management(mem_split_crown_lyr)       
        break
    
    


