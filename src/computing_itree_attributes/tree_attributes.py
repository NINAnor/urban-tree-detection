"""
NAME:   Segment NINA tree crowns by thiessen tessealtion using BYM trees

AUTHOR(S): Zofie Cimburova < zofie.cimburova AT nina.no>
"""

"""
To Dos: 
# RECALUCULATE CROWN RADIUS segmentation/comput_attribute.py/attr_crownDiam /2 

laser_trees = LaserAttributes(laser_trees_path, v_crown_mask_1to1, v_top_mask_1to1)
laser_trees.attr_crownID()
laser_trees.attr_crownDiam()
laser_trees.attr_crownArea()
laser_trees.join_crownID_toTop()
laser_trees.join_topAttr_toCrown()
laser_trees.attr_crownVolume()
 
"""

## TODO works manually in arcgispro make it automatic!

import arcpy
import math  
from arcpy import env
from arcpy.sa import *
from helpful_functions import *
  
## workspace settings
env.overwriteOutput = True
env.outputCoordinateSystem = arcpy.SpatialReference("ETRS 1989 UTM Zone 33N")
env.workspace = r"C:\Users\zofie.cimburova\NINA\15885100 - SIS - 2018 - URBAN Nature values PhD - Dokumenter\4. Data\i-Tree\DATA\Trees\DATA\copy_input_trees.gdb"
   
## data
#v_trees = r"C:\Users\zofie.cimburova\OneDrive - NINA\GENERAL_DATA\TREES\treedata.gdb\BYM_trees_OB_09_2018"
#v_crowns = r"C:\Users\zofie.cimburova\OneDrive - NINA\GENERAL_DATA\TREES\treedata.gdb\NINA_trees_OB_2014_polygons"
   
# 1. compute crown radius
#AddFieldIfNotexists(v_trees, "temp_crown_radius", "Double")

# crown geometry known 
#   -> NULL


# 8. add CROWN_ID - 100.000 + OBJECTID
#AddFieldIfNotexists(v_crowns_modelled, "CROWN_ID", "Long")
#arcpy.CalculateField_management(v_crowns_modelled, "CROWN_ID", "[OBJECTID] + 100000")

# 9. Add field for crown origin
# Crown origin = spatial relation 
# Case 1 = 1:1 relation ALS crown : in situ stem (ALS crown)
# Case 2 = n:1 relation ALS crown : in situ stem  (voronoi crown) 
# Case 3 = 0:1 relation ALS crown : in situ stem (modelled crown)
# Case 4 = 1:0 relation ALS crown : in situ stem (ALS crown)


# 10. Compute MGBDIAM, POLY_AREA, PERIMETER
# MGBDIAM = diameter of the minimum bounding circle of the crown 
# or it is the Mean Basal Area  Diameter of the crown, which is
# the cross-sectional circel of the tree trunk at 1.3 m height (breast height)
# POLY_AREA = area of the crown polygon (shape_area)
# PERIMETER = perimeter of the crown polygon (shape_length)






arcpy.management.MinimumBoundingGeometry(
    in_features="training_crowns_2205",
    out_feature_class=r"P:\152022_itree_eco_ifront_synliggjore_trars_rolle_i_okosyst\02_arcgispro\prepare_iTree_Eco\temp.gdb\training_crowns_2205_MB_fields",
    geometry_type="ENVELOPE",
    group_option="NONE",
    group_field=None,
    mbg_fields_option="MBG_FIELDS"
)
# 11. Compute N_S_WIDTH, E_W_WIDTH



v_envelope = "temp_envelope"
arcpy.MinimumBoundingGeometry_management(v_crowns_modelled, v_envelope, "ENVELOPE", "NONE", "", "MBG_FIELDS")

AddFieldIfNotexists(v_envelope, "Angle", "Double")
arcpy.CalculatePolygonMainAngle_cartography (v_envelope, "Angle", "GEOGRAPHIC")

AddFieldIfNotexists(v_envelope, "N_S_WIDTH", "Double") #NS_width
AddFieldIfNotexists(v_envelope, "E_W_WIDTH", "Double") #EW_width_
codeblock = """def calculateEnvelope(envelope_width, envelope_length, envelope_angle, computed_measure):
    eps = 1e-1 # 0.1 degree
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
arcpy.CalculateField_management(v_envelope, "N_S_WIDTH", 'calculateEnvelope(!MBG_Width!, !MBG_Length!, !Angle!, "N_S")', "PYTHON_9.3", codeblock)
arcpy.CalculateField_management(v_envelope, "E_W_WIDTH", 'calculateEnvelope(!MBG_Width!, !MBG_Length!, !Angle!, "E_W")', "PYTHON_9.3", codeblock)

AddFieldIfNotexists(v_crowns_modelled, "N_S_WIDTH", "Double")
AddFieldIfNotexists(v_crowns_modelled, "E_W_WIDTH", "Double")
join_and_copy(v_crowns_modelled, "CROWN_ID", v_envelope, "CROWN_ID", ["N_S_WIDTH", "E_W_WIDTH"], ["N_S_WIDTH", "E_W_WIDTH"])
arcpy.Delete_management(v_envelope)

# 12. Add Total tree height and live tree height (from ALS)

# 13. Check if DBH is avaialble
# 14. Set dbh_height to oslo standard