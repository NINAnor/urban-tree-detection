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


logger.setup_logger(logfile=True)
logging.info(f'Clean data for <{MUNICIPALITY}> municipality.')

# input data
ds_joined_trees = os.path.join(URBAN_TREES_GDB, "joined_trees")
fc_c2_stems_in = os.path.join(ds_joined_trees, "c2_stems") 
fc_c2_crowns_in = os.path.join(ds_joined_trees, "c2_crowns") 

fc_case_2_stems = os.path.join(ds_joined_trees, "c2_stems_cleaned") 
fc_case_2_crowns = os.path.join(ds_joined_trees, "c2_crowns_cleaned") 

# clean layers 
keep_list = ["tree_id","crown_id_laser","geo_relation"]

au.deleteFields(
    in_table=fc_c2_stems_in,
    out_table=fc_case_2_stems,
    keep_list= keep_list
    )

au.deleteFields(
    in_table=fc_c2_crowns_in,
    out_table=fc_case_2_crowns,
    keep_list= keep_list
    )

# delete intermediate data
arcpy.Delete_management(fc_c2_stems_in)
arcpy.Delete_management(fc_c2_crowns_in)


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
    
