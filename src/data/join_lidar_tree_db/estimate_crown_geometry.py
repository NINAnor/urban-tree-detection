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
import math
from arcpy.sa import *
from helpful_functions import *
import dotenv
from dotenv import dotenv_values
import datetime
import os

# start timer
#start_time0 = time.time()

# set the municipality (kommune) to be analyzed
kommune = "bodo"
current_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

if kommune == "oslo" or "baerum" or "kristiansand":
    spatial_reference = "ETRS 1989 UTM Zone 32N"

if kommune == "bodo" :
    spatial_reference = "ETRS 1989 UTM Zone 33N"

# create filegdb 
# create featureset
# create topology
# make sure XML database all in utm33n
# make XML database for utm32

# set topology rules 
# Must Be Properly Inside Polygons
# Delete Feature Delete removes point features that are not properly within polygon features.


# ------------------------------------------------------ #
# Path Variables  
# Protected Variables are stored in .env file 
# ------------------------------------------------------ #

# search for .env file in USER directory 
# user_dir = C:\\USERS\\<<firstname.lastname>>
user_dir = os.path.join(os.path.expanduser("~"))
dotenv_path = os.path.join(user_dir, '.env')

dotenv.load_dotenv(dotenv_path)
config = dotenv_values(dotenv_path)


# TODO move path var to main.py
# project data path variables 
DATA_PATH = os.getenv('DATA_PATH')
interim_data_path = os.path.join(DATA_PATH, kommune, "interim")
processed_data_path = os.path.join(DATA_PATH, kommune, "processed")

# specific file paths
admin_data_path = os.path.join(interim_data_path, kommune + "_AdminData.gdb")
study_area_path = os.path.join(admin_data_path, "analyseomrade")
laser_tree_path = os.path.join(processed_data_path, kommune + "_Laser_ByTre.gdb")
insitu_tree_path = os.path.join(processed_data_path, kommune + "_urban_trees.gdb")



# modelled lidar crowns 
treecrown_poly = os.path.join(laser_tree_path, "treecrown_poly")
treetop_pnt = os.path.join(laser_tree_path, "treetop_pnt")

#------------------------------------------------------ #
# Workspace settings
# ----------------------------------------------------- #
  
# create urban trees GDB if file does not exists
filegdb_name = kommune + "_urban_trees"
filegdb_path = os.path.join(processed_data_path, filegdb_name + ".gdb")
xml_schema_path = os.path.join(DATA_PATH, "municipality_urban_trees_schema.xml")

# Define the paths to the input and output feature layers
v_crown_laser = os.path.join(filegdb_path, "treecrown_laser")
v_top_laser = os.path.join(filegdb_path, "treetop_laser")

if arcpy.Exists(filegdb_path):
    arcpy.AddMessage("\tFileGDB {} already exists. Continue...".format(filegdb_name))
else:
    # create filegdb from XML schema
    arcpy.AddMessage("\t Create the FileGDB {} and import XML schema. Continue...".format(filegdb_name))
    arcpy.management.CreateFileGDB(processed_data_path, filegdb_name)
    arcpy.ImportXMLWorkspaceDocument_management(filegdb_path, xml_schema_path, "SCHEMA_ONLY")
 
    # Define a SQL expression to select all polygons from the input feature layer
    expression = "Shape_Area > 0"

    # Use the Append function to add the selected laser trees to the output feature layer
    arcpy.AddMessage("\t Import the laser tree crowns and treetops into the FileGDB {}. Continue...".format(filegdb_name))
    arcpy.management.Append(v_crown_laser, treecrown_poly, "NO_TEST", "", "", "", expression)
    arcpy.management.Append(v_top_laser, treetop_pnt, "NO_TEST", "", "", "", expression)


# env settings
env.overwriteOutput = True
env.outputCoordinateSystem = arcpy.SpatialReference(spatial_reference)
env.workspace = filegdb_path


#------------------------------------------------------ #
# Initialize data variables
# ----------------------------------------------------- #

## ADD JOIN STEP

# 0. JOIN
# join type
"ALS, intersecting BYM, Thiessen"
"ALS, intersecting BYM, LiDAR"
"not intersecting"

# other classes? check gdb
# join types:
# Case 1
# Case 2
# Case 3
# Case 4

# crown geometry origin 
# Case 1 - lidar geometry
# Case 2 - voronoi_geometry (thiesen)
# Case 3 - no_geometry --> model using in next step!




   
## data
# in-situ trees
#v_trees_insitu = r"C:\Users\zofie.cimburova\OneDrive - NINA\GENERAL_DATA\TREES\treedata.gdb\BYM_trees_OB_09_2018"
v_trees_insitu = os.path.join(insitu_tree_path, "test")


#v_crown_laser = r"C:\Users\zofie.cimburova\OneDrive - NINA\GENERAL_DATA\TREES\treedata.gdb\NINA_trees_OB_2014_polygons"
# modelled lidar crowns 
v_crown_laser = os.path.join(laser_tree_path, "treecrown_poly")
v_top_laser = os.path.join(laser_tree_path, "treetop_pnt")


# 1. compute crown radius
AddFieldIfNotexists(v_trees_insitu, "temp_crown_radius", "Double")

# crown geometry known 
#   -> NULL (NONE)


# crown geometry not known
#   -> DBH known (measured or estimated from measured h) and species known
#       -> crown width estimated by i-Tree

#   -> DBH known (measured or estimated from measured h) and species not known 
#       -> crown width estimated by NINA equation (OSLO)

   
codeblock_radius = """def calculateRadius(cd_orig, dbh_orig, it_code, itree_width, dbh_cm):
    if cd_orig == "ALS, intersecting BYM, Thiessen" or cd_orig == "ALS, intersecting BYM, LiDAR":
        return None
    elif cd_orig != "ALS, intersecting BYM, Thiessen" and cd_orig != "ALS, intersecting BYM, LiDAR":
        if dbh_orig and it_code:
            return itree_width/2
        elif dbh_orig and not it_code:
            return 3.48 * math.pow(dbh_cm,0.38)/2
        else: 
            return None
    else:
        return None
"""   
arcpy.CalculateField_management(v_trees_insitu, "temp_crown_radius", "calculateRadius(!CD_origin!, !DBH_origin!, !it_code!, !crown_width_itree!, !DBH_corr_cm!)", "PYTHON_9.3", codeblock_radius)

# 2. compute buffer
v_buffer = "temp_cd_1_buffer"
arcpy.Buffer_analysis(v_trees_insitu, v_buffer, "temp_crown_radius", "", "", "ALL")    
   
# 3. subtract ALS crowns from buffer
v_erase = "temp_cd_2_erase"
arcpy.Erase_analysis (v_buffer, v_crown_laser, v_erase)   
arcpy.Delete_management(v_buffer)

# 3. Dissolve
v_dissolve = "temp_cd_2_dissolve"
arcpy.Dissolve_management (v_erase, v_dissolve)
arcpy.Delete_management(v_erase) 
 
# 4. Convert to singlepart
v_singlepart = "temp_cd_3_singlepart"
arcpy.MultipartToSinglepart_management(v_dissolve, v_singlepart) 
arcpy.Delete_management(v_dissolve) 
 
# 5. Export only trees which have estimated crown
l_trees = arcpy.MakeFeatureLayer_management (v_trees_insitu, "trees_layer")
arcpy.FeatureClassToFeatureClass_conversion  (l_trees, r"C:\Users\zofie.cimburova\NINA\15885100 - SIS - 2018 - URBAN Nature values PhD - Dokumenter\4. Data\i-Tree\DATA\Trees\DATA\input_trees.gdb", "temp_trees_with_modelled_crown", "temp_crown_radius IS NOT NULL")

# 6. manually - split crowns with more than one temp_trees_with_modelled_crown
v_crown_laser_split_geometry = "temp_cd_3_singlepart_join4"

# 7. join with ID of tree crowns (from those with modelled crown and suitable for i-Tree)
l_trees_crowns = arcpy.MakeFeatureLayer_management ("temp_trees_with_modelled_crown", "trees_layer2")
arcpy.SelectLayerByAttribute_management(l_trees_crowns, "NEW_SELECTION", "suitable_for_itree_spec_dbh = 1")

v_crown_laser_modelled = "estimated_crowns_for_BYM_OB"
arcpy.SpatialJoin_analysis(v_crown_laser_split_geometry, l_trees_crowns, v_crown_laser_modelled, "JOIN_ONE_TO_ONE", "KEEP_ALL")

# delete unwanted fields, adjust manually - only keep TREE_ID
arcpy.DeleteField_management(v_crown_laser_modelled, drop_field="TARGET_FID;AnleggNavn;Foreslått_tiltak;Stammediameter;Stammeomkrets;Stammeform;Livsfase;Plantedato;Stammeskade;Råte;Hulrom;Sopplegeme;Sykdom;Saltskade;Mekanisk__Brekkasjerisiko_;Vekt;Skadepotensiale;TiltakDato;Skader_reg_i_AT;Bydel;RiskRegDato;NSkode;RegDato;Registrant;Rotskade;Vitalitet;OpprettetAv;OpprettetDato;EndretAv;EndretDato;Risiko;Sår_Ø5cm;Tilleggskommentar;Kronediameter;TRE_ID_NR;Kronestabilisering;Kronestabilisering_Installasjonsdato;Bevaringsstatus;Grenbrekkasje;Treslag;Vaksinasjonsnavn;Vaksinasjonsdato;Vaksinasjon_utført_av;x;y;BotNavn_backup;Artsnavn_backup;diameter_from_perimeter;perimeter_from_diameter;diameter_diff;perimeter_diff;Stammediameter_backup;Stammeomkrets_backup;DBH_corr_cm;DBH_orig;DBH_comment;H;botnavn_corr;botnavn_corr2;botnavn_corr2_comment;artsnavn_corr1;artsnavn_corr2;artsnavn_botnavn_comment;artsnavn_corr3;botnavn_corr3;JOIN_ID;it_origin;it_ID;it_code;it_sc_name;it_co_name;it_genus;it_family;it_order;it_class;it_gr_form;it_p_ltype;it_ltype;it_gr_rate;it_longev;it_h;lc_ssb;CROWN_ID;MGBDIAM;BLD_DIST_1;BLD_DIST_2;BLD_DIST_3;BLD_DIR_1;BLD_DIR_2;BLD_DIR_3;CLE_CLASS;CLE_PERC;lc_ssb_hoved;lc_ssb_under;lc_ar5;lc_itree;H_origin;DBH_origin;CD_origin;N_S_WIDTH;E_W_WIDTH;WGS84_LON;WGS84_LAT;DBH_MEASURED;STREET_TREE;suitable_for_itree_spec_dbh;crown_width_itree;height_to_crown_base_itree;crown_height_itree;crown_radius_itree;temp_crown_radius")

# 8. add CROWN_ID - 100.000 + OBJECTID
AddFieldIfNotexists(v_crown_laser_modelled, "CROWN_ID", "Long")
arcpy.CalculateField_management(v_crown_laser_modelled, "CROWN_ID", "[OBJECTID] + 100000")

# 9. Add field for crown origin
AddFieldIfNotexists(v_crown_laser_modelled, "origin", "Text")
arcpy.CalculateField_management(v_crown_laser_modelled, "origin", '"estimated from DBH"')

# 10. Compute MGBDIAM, POLY_AREA, PERIMETER
v_crown_laser_modelled = "temp_correction_crowns_combined"
v_circle = "temp_circumscribed_circle"
arcpy.MinimumBoundingGeometry_management(v_crown_laser_modelled, v_circle, "CIRCLE", "NONE", "", "MBG_FIELDS")

AddFieldIfNotexists(v_crown_laser_modelled, "MGBDIAM", "Double")
join_and_copy(v_crown_laser_modelled, "CROWN_ID", v_circle, "CROWN_ID", ["MBG_Diameter"], ["MGBDIAM"])
arcpy.Delete_management(v_circle)

AddFieldIfNotexists(v_crown_laser_modelled, "POLY_AREA", "Double")
AddFieldIfNotexists(v_crown_laser_modelled, "PERIMETER", "Double")
arcpy.CalculateField_management(v_crown_laser_modelled, "POLY_AREA", "[Shape_Area]")
arcpy.CalculateField_management(v_crown_laser_modelled, "PERIMETER", "[Shape_Length]")

# 11. Compute N_S_WIDTH, E_W_WIDTH
v_envelope = "temp_envelope"
arcpy.MinimumBoundingGeometry_management(v_crown_laser_modelled, v_envelope, "ENVELOPE", "NONE", "", "MBG_FIELDS")

AddFieldIfNotexists(v_envelope, "Angle", "Double")
arcpy.CalculatePolygonMainAngle_cartography (v_envelope, "Angle", "GEOGRAPHIC")

AddFieldIfNotexists(v_envelope, "N_S_WIDTH", "Double")
AddFieldIfNotexists(v_envelope, "E_W_WIDTH", "Double")
codeblock_evelope = """def calculateEnvelope(envelope_width, envelope_length, envelope_angle, computed_measure):
    eps = 1e-2
    if abs(envelope_angle+90) < eps:
        if computed_measure == "N_S":
            return envelope_length
        elif computed_measure == "E_W":
            return envelope_width
        else:    
            return None
    elif abs(envelope_angle) < eps:
        if computed_measure == "N_S":
            return envelope_width
        elif computed_measure == "E_W":
            return envelope_length
        else:    
            return None
    else:
        return None
"""   
arcpy.CalculateField_management(v_envelope, "N_S_WIDTH", 'calculateEnvelope(!MBG_Width!, !MBG_Length!, !Angle!, "N_S")', "PYTHON_9.3", codeblock_evelope)
arcpy.CalculateField_management(v_envelope, "E_W_WIDTH", 'calculateEnvelope(!MBG_Width!, !MBG_Length!, !Angle!, "E_W")', "PYTHON_9.3", codeblock_evelope)

AddFieldIfNotexists(v_crown_laser_modelled, "N_S_WIDTH", "Double")
AddFieldIfNotexists(v_crown_laser_modelled, "E_W_WIDTH", "Double")
join_and_copy(v_crown_laser_modelled, "CROWN_ID", v_envelope, "CROWN_ID", ["N_S_WIDTH", "E_W_WIDTH"], ["N_S_WIDTH", "E_W_WIDTH"])
arcpy.Delete_management(v_envelope)

# 9. join with ALS estimated crowns
v_crown_laser_ALS = "crowns_NINA_segmented" 
v_crown_laser_merged = "crowns_NINA_segmented_estimated"
arcpy.Merge_management([v_crown_laser_ALS, v_crown_laser_modelled], v_crown_laser_merged)

# 10. join to i-Tree db
join_and_copy(v_trees_insitu, "TREE_ID", v_crown_laser_merged, "TREE_ID", ["CROWN_ID", "MGBDIAM", "N_S_WIDTH", "E_W_WIDTH", "origin"], ["CROWN_ID", "MGBDIAM", "N_S_WIDTH", "E_W_WIDTH", "CD_origin"])

