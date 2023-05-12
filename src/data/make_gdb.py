import os
import arcpy
from src import (MUNICIPALITY, ADMIN_GDB, IN_SITU_TREES_GDB, LASER_TREES_GDB, URBAN_TREES_GDB, SPATIAL_REFERENCE)
from src import arcpy_utils as au

# Define the geodatabase names and locations
geodatabase_locations = [ADMIN_GDB, IN_SITU_TREES_GDB, LASER_TREES_GDB, URBAN_TREES_GDB]

# Loop through the geodatabase locations and create them
for gdb in geodatabase_locations:
    au.createGDB_ifNotExists(gdb)

print(f"All geodatabases exist for {MUNICIPALITY} municipality.")




# create datasets in URBAN_TREES_GDB
ds_input_trees = os.path.join(URBAN_TREES_GDB, "input_trees")
if not arcpy.Exists(ds_input_trees):
    arcpy.CreateFeatureDataset_management(
        out_dataset_path=URBAN_TREES_GDB,
        out_name= "input_trees",
        spatial_reference=SPATIAL_REFERENCE)  

ds_joined_trees = os.path.join(URBAN_TREES_GDB, "joined_trees")
if not arcpy.Exists(ds_joined_trees):
    arcpy.CreateFeatureDataset_management(
        out_dataset_path=URBAN_TREES_GDB,
        out_name= "joined_trees",
        spatial_reference=SPATIAL_REFERENCE)

ds_itree_trees = os.path.join(URBAN_TREES_GDB, "itree_trees")
if not arcpy.Exists(ds_itree_trees):
    arcpy.CreateFeatureDataset_management(
        out_dataset_path=URBAN_TREES_GDB,
        out_name= "itree_trees",
        spatial_reference=SPATIAL_REFERENCE)

print(f"All datasets are created.")