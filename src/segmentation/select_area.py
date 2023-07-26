import arcpy
import os

# TODO this module is not used anymore. Delete it.

def select_sea(input_path, study_area_path, output_path):
    
    arcpy.AddMessage("\t\tCreating a temporay water layer for the municipality from FKB data...")
    l_sea = arcpy.MakeFeatureLayer_management(
        input_path, 
        "sea_lyr"
        )
    
    arcpy.SelectLayerByLocation_management(
        l_sea, 
        "INTERSECT",
        study_area_path,
        "",
        "NEW_SELECTION"
        )

    arcpy.SelectLayerByAttribute_management(
        l_sea, 
        "SUBSET_SELECTION",
        "objtype = 'Havflate'"
        )

    v_sea = os.path.join(output_path, "FKB_vann_havflate")
    arcpy.CopyFeatures_management(
        in_features = l_sea,
        out_feature_class = v_sea
        )
    
    return v_sea


def select_building(input_path, study_area_path, output_path):
    arcpy.AddMessage("\t\tCreate a temporay building layer for the municipality from FKB data.")
    l_building = arcpy.MakeFeatureLayer_management(
        input_path, 
        "building_lyr"
        )
    
    arcpy.SelectLayerByLocation_management(
        l_building, 
        "INTERSECT",
        study_area_path,
        "",
        "NEW_SELECTION"
        )

    v_building = os.path.join(output_path, "FKB_bygning_omrade")
    arcpy.CopyFeatures_management(
        in_features = l_building,
        out_feature_class = v_building
        )
    
    return v_building

def mask_tree(all_trees, v_building, v_sea, selected_trees):

    arcpy.AddMessage("\t\tSelecting trees outside building footprints and sea areas...")
    l_tree_pnt_outside = arcpy.MakeFeatureLayer_management(
        all_trees, "tree_pnt_outside_lyr"
        )
    
    arcpy.SelectLayerByLocation_management(
        l_tree_pnt_outside, 
        "INTERSECT",
        v_building,
        "",
        "NEW_SELECTION",
        invert_spatial_relationship = True    
    )
    arcpy.SelectLayerByLocation_management(
        l_tree_pnt_outside, 
        "INTERSECT",
        v_sea,
        "",
        "REMOVE_FROM_SELECTION"
    )
    
    arcpy.CopyFeatures_management(
        in_features = l_tree_pnt_outside,
        out_feature_class = selected_trees
    )   
    
    return selected_trees



    



   
