"""
NAME:   Segment NINA tree crowns by thiessen tessealtion using BYM trees

AUTHOR(S): Zofie Cimburova < zofie.cimburova AT nina.no>
"""

"""
To Dos: 
"""

import os
import arcpy
from arcpy import env
from arcpy.sa import *

# local modules
from src import (SPATIAL_REFERENCE, URBAN_TREES_GDB)
from src import arcpy_utils as au


ds_joined_trees = os.path.join(URBAN_TREES_GDB, "joined_trees")

# input data
fc_case_2_stems = os.path.join(ds_joined_trees, "join_case_2_stems") 
fc_case_2_crowns = os.path.join(ds_joined_trees, "join_case_2") 

# output data
fc_case_2_crowns_voronoi = os.path.join(ds_joined_trees, "join_case_2_crowns_voronoi") 

  
# env settings
env.overwriteOutput = True
env.outputCoordinateSystem = arcpy.SpatialReference(SPATIAL_REFERENCE)
env.workspace = ds_joined_trees

   
## input data
# problematic tree crowns (with more than one BYM trunk)
v_crowns = fc_case_2_crowns
l_crowns = arcpy.MakeFeatureLayer_management (v_crowns, "problematic_crowns_layer")

# problematic tree trunks (inside problematic crowns)
v_trunks = fc_case_2_stems
l_trunks = arcpy.MakeFeatureLayer_management (v_trunks, "problematic_points_layer")

## output data
arcpy.CreateFeatureclass_management(
    out_path=ds_joined_trees,
    out_name = "join_case_2_crowns_voronoi", 
    geometry_type="POLYGON"
    )

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
    arcpy.Append_management (
        inputs=v_crown_split,
        target= fc_case_2_crowns_voronoi, 
        schema_type= "NO_TEST")
    
    # delete temp layer
    arcpy.Delete_management(v_crown_split)



