"""
NAME:   Segment NINA tree crowns by thiessen tessealtion using BYM trees

AUTHOR(S): Zofie Cimburova < zofie.cimburova AT nina.no>
"""

"""
To Dos: 
"""

import arcpy
import math  
from arcpy import env
from arcpy.sa import *

## TODO 

  
## workspace settings
env.overwriteOutput = True
env.outputCoordinateSystem = arcpy.SpatialReference("ETRS 1989 UTM Zone 33N")
env.workspace = r"C:\Users\zofie.cimburova\NINA\15885100 - SIS - 2018 - URBAN Nature values PhD - Dokumenter\4. Data\i-Tree\DATA\Trees\DATA\input_trees.gdb"
   
## input data
# problematic tree crowns (with more than one BYM trunk)
v_crowns = "problematic_crowns"
l_crowns = arcpy.MakeFeatureLayer_management (v_crowns, "problematic_crowns_layer")

# problematic tree trunks (inside problematic crowns)
v_trunks = "problematic_points"
l_trunks = arcpy.MakeFeatureLayer_management (v_trunks, "problematic_points_layer")

## output data
# split problematic tree crowns
v_crowns_split = "output_crowns"
out_path = r"C:\Users\zofie.cimburova\NINA\15885100 - SIS - 2018 - URBAN Nature values PhD - Dokumenter\4. Data\i-Tree\DATA\Trees\DATA\input_trees.gdb"
arcpy.CreateFeatureclass_management (out_path, v_crowns_split, "POLYGON")

## Go through crowns and split by Thiessen polygons of trunks 
env.workspace = r"in_memory"
cursor = arcpy.da.SearchCursor(v_crowns, ['SHAPE@', 'OBJECTID'])

for row in cursor:
    crown_id  = row[1]
   
    arcpy.AddMessage("Processing crown {}.".format(crown_id))
    
    # select trunks inside this crown
    arcpy.SelectLayerByLocation_management(l_trunks, "INTERSECT", row[0])   
    
    # select this crown
    arcpy.SelectLayerByAttribute_management(l_crowns, "NEW_SELECTION", "OBJECTID = {}".format(crown_id))   
    
    # compute thiessen tesselation
    arcpy.env.extent = row[0].extent
    v_thiessen = "temp_thiessen_poly"
    arcpy.CreateThiessenPolygons_analysis (l_trunks, v_thiessen)
    
    # use vector to split crown
    v_crown_split = "temp_split_crown"
    arcpy.Intersect_analysis([v_thiessen, l_crowns], v_crown_split)
    arcpy.Delete_management(v_thiessen)
    
    # append to already processed crowns
    arcpy.Append_management (v_crown_split, out_path+"\\"+v_crowns_split, "NO_TEST")
    arcpy.Delete_management(v_crown_split)



