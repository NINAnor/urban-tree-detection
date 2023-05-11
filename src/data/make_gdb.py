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

ds_urban_trees = os.path.join(URBAN_TREES_GDB, "urban_trees")


# Create the "urban_trees" feature dataset if it doesn't exist
if not arcpy.Exists(ds_urban_trees):
    arcpy.CreateFeatureDataset_management(
        out_dataset_path=URBAN_TREES_GDB,
        out_name= "urban_trees",
        spatial_reference=SPATIAL_REFERENCE)
    

# Create the "joined_trees" feature dataset if it doesn't exist
ds_joined_trees = os.path.join(URBAN_TREES_GDB, "joined_trees")
if not arcpy.Exists(ds_joined_trees):
    arcpy.CreateFeatureDataset_management(
        out_dataset_path=URBAN_TREES_GDB,
        out_name= "joined_trees",
        spatial_reference=SPATIAL_REFERENCE)