"""
NAME:   Segment NINA tree crowns by thiessen tessealtion using BYM trees

AUTHOR(S): Zofie Cimburova < zofie.cimburova AT nina.no>
"""

"""
To Dos: 
"""

# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# perform_tree_detection_v1.py
# Description: Translation of Hanssen et al. (2021) tree detection algorithm
# from ArcMap model builder to ArcPy script - Version 1
# Author: Zofie Cimburova, Willeke A'Campo
# Dependencies: ArcGIS Pro 3.0, 3D analyst, image analyst, spatial analyst
# ---------------------------------------------------------------------------

# Import modules
import arcpy
from arcpy import env
from arcpy.sa import *

import dotenv
from dotenv import dotenv_values
import datetime
import os
import csv

from src import createGDB_ifNotExists
from src import addField_ifNotExists
# start timer
#start_time0 = time.time()

# set the municipality (kommune) to be analyzed
kommune = "bodo"
current_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

if kommune == "oslo" or "baerum" or "kristiansand":
    spatial_reference = "ETRS 1989 UTM Zone 32N"

if kommune == "bodo" :
    spatial_reference = "ETRS 1989 UTM Zone 33N"


# ------------------------------------------------------ #
# Path Variables  
# Protected Variables are stored in .env file 
# ------------------------------------------------------ #

# search for .env file in USER directory 
# user_dir = C:\\USERS\\<<firstname.lastname>>
user_dir = os.path.join(os.path.expanduser("~"))
dotenv_path = os.path.join(user_dir, 'trekroner.env')

dotenv.load_dotenv(dotenv_path)
config = dotenv_values(dotenv_path)


# TODO move path var to main.py
# project data path variables 
DATA_PATH = os.getenv('DATA_PATH')
interim_data_path = os.path.join(DATA_PATH, kommune, "interim")
processed_data_path = os.path.join(DATA_PATH, kommune, "processed")

# interim file paths 
admin_data_path = os.path.join(interim_data_path, kommune + "_admin.gdb")
study_area_path = os.path.join(admin_data_path, "analyseomrade")
laser_tree_path = os.path.join(interim_data_path, kommune + "_laser_trees.gdb")
crown_1to1_path =os.path.join(laser_tree_path,"crown_1to1")
top_1to1_path = os.path.join(laser_tree_path, "top_1to1")
in_situ_tree_path = os.path.join(interim_data_path, kommune + "_in_situ_trees.gdb", "stem_in_situ") 

# ------------------------------------------------------ #
# CREATE URBAN TREES FILEGDB  
# %xxx%_urban_trees = combined municipal and laser tree dataset 
# ------------------------------------------------------ #

# create urban trees GDB if file does not exists
urban_tree_gdb_path = os.path.join(processed_data_path, kommune + "_urban_trees" ".gdb")
urban_tree_path = os.path.join(urban_tree_gdb_path, "urban_trees")
createGDB_ifNotExists(urban_tree_gdb_path)
#xml_schema_path = os.path.join(DATA_PATH, "municipality_urban_trees_schema.xml")

# Create the "urban_trees" feature dataset if it doesn't exist
if not arcpy.Exists(urban_tree_path):
    arcpy.CreateFeatureDataset_management(
        out_dataset_path=urban_tree_gdb_path,
        out_name= "urban_trees",
        spatial_reference=spatial_reference)


# ------------------------------------------------------ #
# COPY - IN SITU TREES
# %xxx%_in_situ_trees = municipal tree dataset
# stem_point  
# ------------------------------------------------------ #
stem_in_situ = os.path.join(urban_tree_path, "stem_in_situ")

if not arcpy.Exists(stem_in_situ):
    arcpy.CopyFeatures_management(
        in_features=in_situ_tree_path,
        out_feature_class=stem_in_situ
    )

# ------------------------------------------------------ #
# COPY - LASER TREES
# %xxx%_laser_trees = laser segmented tree dataset
# crown_laser(tree crown polygon)
# top_laser (tree top point) 
# ------------------------------------------------------ #

crown_laser = os.path.join(urban_tree_path, "crown_laser")
top_laser = os.path.join(urban_tree_path,"top_laser")

if not arcpy.Exists(crown_laser):
    arcpy.CopyFeatures_management(
        in_features= crown_1to1_path,
        out_feature_class= crown_laser
    )

if not arcpy.Exists(top_laser):
    arcpy.CopyFeatures_management(
        in_features= top_1to1_path,
        out_feature_class= top_laser
    )



#------------------------------------------------------ #
# Workspace settings
# ----------------------------------------------------- #

# env settings
env.overwriteOutput = True
env.outputCoordinateSystem = arcpy.SpatialReference(spatial_reference)
env.workspace = urban_tree_path


#------------------------------------------------------ #
# SPATIAL JOIN - TREE CROWN POLYGON CONTAINS STEM POINT
# ----------------------------------------------------- #
arcpy.AddMessage(f"\tCreating a joined feature class <urban_trees> by joining the in situ stem points to the crown polygons that they intersect ... ")
v_urban_trees = os.path.join(urban_tree_path, "urban_trees")

fm_crown_id = str(f'crown_id_laser "crown_id_laser" true true false 4 Long 0 0,First,#,{crown_laser},crown_id_laser,-1,-1')
fm_crown_diam = str(f'crown_diam "crown_diam" true true false 4 Float 0 0,First,#,{crown_laser},crown_diam,-1,-1')
fm_crown_area = str(f'crown_area "crown_area" true true false 4 Float 0 0,First,#,{crown_laser},crown_area,-1,-1')
fm_tree_height = str(f'tree_height "tree_height" true true false 4 Float 0 0,First,#,{crown_laser},tree_height,-1,-1')
fm_tree_id = str(f'tree_id "tree_id" true true false 4 Long 0 0,First,#,{stem_in_situ},tree_id,-1,-1')
fm_dbh = str(f'dbh "dbh" true true false 4 Long 0 0,First,#,{stem_in_situ},dbh,-1,-1')
fm_crown_radius = str(f'crown_radius "crown_radius" true true false 4 Long 0 0,First,#,{stem_in_situ},crown_radius,-1,-1')
fm_norwegian_name = str(f'norwegian_name "norwegian_name" true true false 255 Text 0 0,First,#,{stem_in_situ},norwegian_name,0,255')

fm_list = [fm_crown_id,fm_crown_diam,fm_crown_area,fm_tree_height,fm_tree_id,fm_dbh,fm_crown_radius,fm_norwegian_name]

fieldmapping= ""
for string in fm_list:
    fieldmapping += string + ";"
fieldmapping = fieldmapping[:-1] # remove the last semicolon

print(fieldmapping)

#if not arcpy.Exists(v_urban_trees):
arcpy.analysis.SpatialJoin(
    target_features=crown_laser,
    join_features=stem_in_situ,
    out_feature_class=v_urban_trees,
    join_operation="JOIN_ONE_TO_MANY",
    join_type="KEEP_ALL",
    field_mapping = fieldmapping,
    match_option="CONTAINS",
    search_radius=None,
    distance_field_name=""
)
    
    
# Add a new text field "geo_relation" to the output feature class
#arcpy.AddField_management(
#    in_table=v_urban_trees, 
#    field_name= "geo_relation",
#    field_type = "TEXT",
#    field_length = 10
#)

print("field created")

#------------------------------------------------------ #
# Classify the geometrical relatisonship
# TODO not working all classified as Case 1
# Join FID -1
# JOIN
# ----------------------------------------------------- #

# Calculate the "geo_relation" field based on the spatial relationship
# between each polygon and point
with arcpy.da.UpdateCursor(v_urban_trees, ["JOIN_FID", "geo_relation"]) as cursor:
    for row in cursor:
        # Get the number of points and polygons involved in the relationship
        join_fid = str(row[0])
        point_count = join_fid.count(";") + 1
        polygon_count = 1
        
        # Check the relationship case and update the "" field
        if point_count == 1 and polygon_count == 1:
            #Case 1 - 1:1 one polygon contains one point
            row[1] = "Case 1"
        elif point_count > 1 and polygon_count == 1:
            #Case 2 - 1:n one polygon contains more than one point
            row[1] = "Case 2"
        elif point_count == 0 and polygon_count == 1:
            # Case 3 - 0:1 a point is not overlapped by any polygon
            row[1] = "Case 3"
        elif point_count == 1 and polygon_count == 0:
            # "Case 4- 1:0 a polygon does not contain any point"
            row[1] = "Case 4"
        cursor.updateRow(row)


with arcpy.da.UpdateCursor(v_urban_trees, ["TARGET_FID", "JOIN_FID", "geo_relation"]) as cursor:
    for row in cursor:
        target_count = row[0].count(";") + 1
        join_count = row[1].count(";") + 1
        if target_count == 1 and join_count == 1:
            row[2] = "Case 1"
        elif target_count > 1 and join_count == 1:
            row[2] = "Case 2"
        elif target_count == 0 and join_count == 1:
            row[2] = "Case 3"
        elif target_count == 1 and join_count == 0:
            row[2] = "Case 4"
        cursor.updateRow(row)


#------------------------------------------------------ #
# EXPORT to CSV
# ----------------------------------------------------- #

output_csv = os.path.join(processed_data_path, "geometrical_relationship_stat.csv")

# Create a dictionary to store the counts for each case
case_counts = {"Case 1": 0, "Case 2": 0, "Case 3": 0, "Case 4": 0}


# Iterate over the rows of the v_urban_trees feature class and count the number of rows for each case
with arcpy.da.SearchCursor(v_urban_trees, "geo_relation") as cursor:
    for row in cursor:
        case_counts[row[0]] += 1

# Write the counts to a CSV file
with open(output_csv, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["case number", "count"])
    for case, count in case_counts.items():
        writer.writerow([case, count])
        print("Number of rows with geo_relation = {}: {}".format(case, count))



