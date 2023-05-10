import os
import arcpy
from src import (MUNICIPALITY, ADMIN_GDB, IN_SITU_TREES_GDB, LASER_TREES_GDB, URBAN_TREES_GDB, SPATIAL_REFERENCE)
from src import arcpy_utils as au

# Define the geodatabase names and locations
geodatabase_locations = [ADMIN_GDB, IN_SITU_TREES_GDB, LASER_TREES_GDB, URBAN_TREES_GDB]

# Loop through the geodatabase locations and create them
for gdb in geodatabase_locations:
    au.createGDB_ifNotExists(gdb)

print(f"All geodatabases exist for {MUNICIPALITY}")

ds_urban_trees = os.path.join(URBAN_TREES_GDB, "urban_trees")

# Create the "urban_trees" feature dataset if it doesn't exist
if not arcpy.Exists(ds_urban_trees):
    arcpy.CreateFeatureDataset_management(
        out_dataset_path=URBAN_TREES_GDB,
        out_name= "urban_trees",
        SPATIAL_REFERENCE=SPATIAL_REFERENCE)