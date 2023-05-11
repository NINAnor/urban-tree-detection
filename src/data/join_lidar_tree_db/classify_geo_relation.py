""" 
Classify the geometric relation between the stem points (in situ) and the crown polygons (laser)
Case 1: one polygon contains one point (1:1), simple join.
Case 2: one polygon contains more than one point (1:n), split crown with voronoi tesselation.
Case 3: a point is not overlapped by any polygon (0:1), model tree crown using oslo formula.
Case 4: a polygon does not contain any point (1:0), not used to train i-tree eco/dataset for extrapolation.
result: geo_relation (attr. field in urban_trees feature class) 

Bodo:
Case 1 and 2: 4583
Case 1:  (unique JOIN_FID and unique TARGET_FID)
Case 2: (multiple JOIN_FID and unique TARGET FID)
Case 3: 0
Case 4: 76 399 (join_count (0))

stem in situ # join (JOIN_FID)
crown laser # target (TARGET_FID)
"""

# -*- coding: utf-8 -*-
import os
import csv
import arcpy
from arcpy import env
from arcpy.sa import *
import logging

# local modules
from src import (SPATIAL_REFERENCE, URBAN_TREES_GDB, PROCESSED_PATH, MUNICIPALITY)
from src import logger
from src import arcpy_utils as au

# set console logger
logger.setup_logger(logfile=False)

# --------------------------------------------------------------------------- #
# RUN make_gdb and make_fc before running this file
# RUN on VDI long run time
# --------------------------------------------------------------------------- #

# set path variables
ds_urban_trees = os.path.join(URBAN_TREES_GDB, "urban_trees")
ds_joined_trees = os.path.join(URBAN_TREES_GDB, "joined_trees")

fc_urban_trees = os.path.join(URBAN_TREES_GDB, "urban_trees", "urban_trees") # joined dataset
fc_case_1_2 = os.path.join(ds_urban_trees, "join_case_1_2") 
fc_case_1 = os.path.join(ds_joined_trees, "join_case_1") 
fc_case_2 = os.path.join(ds_joined_trees, "join_case_2") 
fc_case_3 = os.path.join(ds_joined_trees, "join_case_3")
fc_case_4 = os.path.join(ds_joined_trees, "join_case_4")

# env settings
env.overwriteOutput = True
env.outputCoordinateSystem = arcpy.SpatialReference(SPATIAL_REFERENCE)
env.workspace = ds_urban_trees

au.addField_ifNotExists(
    featureclass= fc_urban_trees,
    fieldname="geo_relation",
    type="TEXT"
    )

# Unique count of JOIN FID and TARGET FID
# add field
au.addField_ifNotExists(
    featureclass= fc_urban_trees,
    fieldname= "COUNT_JOIN_FID",
    type= "LONG"
)
au.addField_ifNotExists(
    featureclass= fc_urban_trees,
    fieldname= "COUNT_TARGET_FID",
    type= "LONG"
    
)

# --------------------------------------------------------------------------- #
# Calculate TARGET and JOIN COUNT
# --------------------------------------------------------------------------- #

if au.fieldExist(fc_urban_trees, "COUNT_JOIN_FID") or au.fieldExist(fc_urban_trees, "COUNT_TRAGET_FID"):
    arcpy.AddMessage(f"The fields COUNT_JOIN_FID and COUNT_TARGET_FID exists in {os.path.basename(fc_urban_trees)}. Continue... ")
else:
    # calculate count JOIN_FID 
    join_fid_count_stats = arcpy.Statistics_analysis(
        in_table= fc_urban_trees, 
        out_table="in_memory/join_fid_count_table",
        statistics_fields= [["JOIN_FID", "COUNT"]], 
        case_field="TARGET_FID"
        )

    # add COUNT_JOIN_FID as field to fc
    arcpy.JoinField_management(
        in_data=fc_urban_trees, 
        in_field="TARGET_FID", 
        join_table=join_fid_count_stats,
        join_field="TARGET_FID", 
        fields="COUNT_JOIN_FID"
        )

    # calculate count TARGET_FID 
    target_fid_count_stats = arcpy.Statistics_analysis(
        fc_urban_trees, 
        "in_memory/target_fid_count_table", 
        [["TARGET_FID", "COUNT"]], 
        "JOIN_FID"
        )
    # add COUNT_TARGET_FID as field to fc 
    arcpy.JoinField_management(
        fc_urban_trees, 
        "JOIN_FID", 
        target_fid_count_stats, 
        "JOIN_FID", 
        "COUNT_TARGET_FID"
        )


#------------------------------------------------------ #
# Classify the geometrical relatisonship
# TODO check case 3 and case 4
# TODO split case 1 and case 2
# ----------------------------------------------------- #

# Create a feature layer from the input feature class
arcpy.MakeFeatureLayer_management(fc_urban_trees, "lyr")

field_crown_id = "crown_id_laser"
field_tree_id = "tree_id"
field_geo_relation = "geo_relation"

# Select and export case 4 (1:0) 
if arcpy.Exists(fc_case_4):
    arcpy.AddMessage(f"\tFeature {os.path.basename(fc_case_4)} already exists. Continue...")
else:
    query = f"{field_crown_id} IS NOT NULL AND {field_tree_id} IS NULL"
    arcpy.management.SelectLayerByAttribute(
        in_layer_or_view="lyr",
        selection_type="NEW_SELECTION",
        where_clause=query,
        invert_where_clause=None
    )
    arcpy.CopyFeatures_management("lyr", fc_case_4)
    au.calculateField_ifEmpty(fc_case_4, field=field_geo_relation, expression= "Case 4")
    logging.info(f'Case 4 selected and exported to {os.path.basename(fc_case_4)}')


# Select case 3 and export to new fc 
if arcpy.Exists(fc_case_3):
    arcpy.AddMessage(f"\tFeature {os.path.basename(fc_case_3)} already exists. Continue...")
else:
    query = f"{field_crown_id} IS NULL AND {field_tree_id} IS NOT NULL"
    arcpy.management.SelectLayerByAttribute(
        in_layer_or_view="lyr",
        selection_type="NEW_SELECTION",
        where_clause=query,
        invert_where_clause=None
    )
    arcpy.CopyFeatures_management("lyr", fc_case_3)
    au.calculateField_ifEmpty(fc_case_4, field=field_geo_relation, expression= "Case 3")
    logging.info(f'Case 3 selected and exported to {os.path.basename(fc_case_3)}')

# Select case 1 and case 2 and export to new fc 
#if arcpy.Exists(fc_case_1_2):
#    arcpy.AddMessage(f"\tFeature {os.path.basename(fc_case_1_2)} already exists. Continue...")
#else:
#    arcpy.SelectLayerByAttribute_management("lyr", "NEW_SELECTION", "{} IS NOT NULL AND {} IS NOT NULL".format(field_crown_id, field_tree_id))
#    arcpy.SelectLayerByAttribute_management("lyr", "ADD_TO_SELECTION", "{} IS NULL AND {} IS NOT NULL".format(field_crown_id, field_tree_id))
#    arcpy.CopyFeatures_management("lyr", fc_case_1_2)
#    logging.info(f'Case 1 and 2 selected and exported to {os.path.basename(fc_case_1_2)}')

    
# Separate case 1 and case 2 and export to new fcs 
# Make a feature layer
arcpy.MakeFeatureLayer_management(fc_case_1_2, "lyr2")


# Unique count of JOIN FID and TARGET FID
# add field
au.addField_ifNotExists(
    featureclass= fc_case_1_2,
    fieldname= "COUNT_JOIN_FID",
    type= "LONG"
)
au.addField_ifNotExists(
    featureclass= fc_case_1_2,
    fieldname= "COUNT_TARGET_FID",
    type= "LONG"
    
)

if au.fieldExist(fc_case_1_2, "COUNT_JOIN_FID") or au.fieldExist(fc_case_1_2, "COUNT_TRAGET_FID"):
    arcpy.AddMessage(f"The fields COUNT_JOIN_FID and COUNT_TARGET_FID exists in {os.path.basename(fc_case_1_2)}. Continue... ")
else:
    # calculate count JOIN_FID 
    join_fid_count_stats = arcpy.Statistics_analysis(
        in_table= fc_case_1_2, 
        out_table="in_memory/join_fid_count_table",
        statistics_fields= [["JOIN_FID", "COUNT"]], 
        case_field="TARGET_FID"
        )

    # add COUNT_JOIN_FID as field to fc
    arcpy.JoinField_management(
        in_data=fc_case_1_2, 
        in_field="TARGET_FID", 
        join_table=join_fid_count_stats,
        join_field="TARGET_FID", 
        fields="COUNT_JOIN_FID"
        )

    # calculate count TARGET_FID 
    target_fid_count_stats = arcpy.Statistics_analysis(
        fc_case_1_2, 
        "in_memory/target_fid_count_table", 
        [["TARGET_FID", "COUNT"]], 
        "JOIN_FID"
        )
    # add COUNT_TARGET_FID as field to fc 
    arcpy.JoinField_management(
        fc_case_1_2, 
        "JOIN_FID", 
        target_fid_count_stats, 
        "JOIN_FID", 
        "COUNT_TARGET_FID"
        )

# Select features in class 1
if arcpy.Exists(fc_case_1):
    arcpy.AddMessage(f"\tFeature {os.path.basename(fc_case_1)} already exists. Continue...")
else:   
    query = "COUNT_JOIN_FID_1 > 1 And COUNT_TARGET_FID_1 = 1"  
    arcpy.management.SelectLayerByAttribute(
        in_layer_or_view="lyr2",
        selection_type="NEW_SELECTION",
        where_clause=query,
        invert_where_clause=None
    )
    arcpy.CopyFeatures_management("lyr2", fc_case_1)
    logging.info(f'Case 1 selected and exported to {os.path.basename(fc_case_1)}')

# Select features in class 2
if arcpy.Exists(fc_case_2):
    arcpy.AddMessage(f"\tFeature {os.path.basename(fc_case_2)} already exists. Continue...")
else:   
    # Select features in class 1
    query = "COUNT_JOIN_FID_1 = 1 And COUNT_TARGET_FID_1 = 1"
    arcpy.management.SelectLayerByAttribute(
        in_layer_or_view="lyr2",
        selection_type="NEW_SELECTION",
        where_clause=query,
        invert_where_clause=None
    )
    arcpy.CopyFeatures_management("lyr2", fc_case_2)
    logging.info(f'Case 2 selected and exported to {os.path.basename(fc_case_2)}')   

#------------------------------------------------------ #
# EXPORT to case number count to CSV
# TODO geo_relation in case in stead of 1:0 etc. 
# ----------------------------------------------------- #

output_csv = os.path.join(PROCESSED_PATH, MUNICIPALITY + "_geo_relation_stat.csv")

# Create a dictionary to store the counts for each case
case_counts = {"Case 1": 0, "Case 2": 0, "Case 3": 0, "Case 4": 0}

# Iterate over the rows of the v_urban_trees feature class and count the number of rows for each case
with arcpy.da.SearchCursor(fc_urban_trees, "geo_relation") as cursor:
    for row in cursor:
        case_counts[row[0]] += 1

# Write the counts to a CSV file
with open(output_csv, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["case number", "count"])
    for case, count in case_counts.items():
        writer.writerow([case, count])
        print("Number of rows with geo_relation = {}: {}".format(case, count))
