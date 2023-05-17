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
temp_c2_unique_crowns = os.path.join(ds_joined_trees, "temp_c2_unique_crowns") 

# Create a feature layer from the input feature class
arcpy.MakeFeatureLayer_management(point_layer, "point_lyr")
arcpy.CopyFeatures_management(polygon_layer, temp_c2_unique_crowns) # tree crown  

# delete duplicate crowns
table =  temp_c2_unique_crowns
field = "crown_id_laser"  
au.deleteDuplicates(table, field)


count_stems = int(arcpy.GetCount_management("point_lyr").getOutput(0))
count_crowns = int(arcpy.GetCount_management(temp_c2_unique_crowns).getOutput(0))
logging.info(f"Count of Case 2 Stems: {count_stems}")
logging.info(f"Count of Case 2 Crowns: {count_crowns}")

# Split each tree crown based on the number of stems. 
fields = ["OBJECTID", "tree_id", "crown_id_laser"]
with arcpy.da.SearchCursor(polygon_layer, fields) as cursor:
    for row in cursor:
        
        # create memory layers
        # error: cannot run workflow with using memory lyrs
        # mem_crown_lyr = "in_memory/temp_crown"
        # mem_thiessen_lyr = "in_memory/thiessen"
        # mem_split_crown_lyr = "in_memory/temp_split_crown" 
        
        tmp_crown_lyr = os.path.join(ds_joined_trees, "temp_crown") 
        tmp_thiessen_lyr = os.path.join(ds_joined_trees,"thiessen")
        tmp_split_crown_lyr = os.path.join(ds_joined_trees,"temp_split_crown") 
        
        # delete tmp/memory layers
        arcpy.Delete_management(tmp_crown_lyr)
        arcpy.Delete_management(tmp_thiessen_lyr)  
        arcpy.Delete_management(tmp_split_crown_lyr) 
        
        logging.info(f"START SPLITTING TREECROWN, OBJECTID: {row[0]}, crown_id: {row[2]}")
        
        # select tree crown by OBJECTID
        polygon_id = row[0]
        arcpy.MakeFeatureLayer_management(polygon_layer, "selected_polygon", f"OBJECTID = {polygon_id}")

        # Select stem points that intersect with the tree crown
        arcpy.SelectLayerByLocation_management("point_lyr", "WITHIN", "selected_polygon") # stem points
        arcpy.CopyFeatures_management("selected_polygon", tmp_crown_lyr) # tree crown  

        # log the tree_id values of the selected stem points
        fields_pnt = ["OBJECTID", "tree_id"]
        with arcpy.da.SearchCursor("point_lyr", fields_pnt) as cursor:
            for row in cursor:
                logging.info(f"OBJECTID: {row[0]}, tree_id: {row[1]}")


        #split the treecrown using the thiessen polygons
        env.extent = tmp_crown_lyr # tree crown area 
        arcpy.CreateThiessenPolygons_analysis("point_lyr", tmp_thiessen_lyr) 
        arcpy.Intersect_analysis([tmp_thiessen_lyr, tmp_crown_lyr], tmp_split_crown_lyr)
        arcpy.Append_management(
            inputs=tmp_split_crown_lyr,
            target= fc_c2_crowns_voronoi, 
            schema_type= "NO_TEST",
            field_mapping=None,
            subtype="",
            expression="",
            match_fields=None,
            update_geometry="NOT_UPDATE_GEOMETRY"
            )
        
        # delete tmp/memory layers
        arcpy.Delete_management(tmp_crown_lyr)
        arcpy.Delete_management(tmp_thiessen_lyr)  
        arcpy.Delete_management(tmp_split_crown_lyr)       
        #break

# delete duplicate crowns
table =  fc_c2_crowns_voronoi 
field = "tree_id"  
au.deleteDuplicates(table, field)

count_split_crowns = int(arcpy.GetCount_management(fc_c2_crowns_voronoi).getOutput(0))
logging.info(f"Count of splitted crowns: {count_split_crowns}")







