# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# perform_tree_detection_v1.py
# Description: Translation of Hanssen et al. (2021) tree detection algorithm
# from ArcMap model builder to ArcPy script - Version 1
# Author: Zofie Cimburova
# ---------------------------------------------------------------------------

# Import arcpy module
import arcpy
import os
from arcpy import env

# ------------------------------------------------------ #
# Functions
# ------------------------------------------------------ #
# Join "source_table" to "destination table" and copy attributes from "source table" to attributes in "destination table"
def join_and_copy(t_dest, join_a_dest, t_src, join_a_src, a_src, a_dest):
     
    name_dest = arcpy.Describe(t_dest).name
    name_src = arcpy.Describe(t_src).name
     
    # Create layer from "destination table"
    l_dest = "dest_lyr"
    arcpy.MakeFeatureLayer_management(t_dest, l_dest)
     
    # Join
    arcpy.AddJoin_management(l_dest, join_a_dest, t_src, join_a_src)
     
    # Copy attributes   
    i = 0
    for a in a_src:
        arcpy.AddMessage(
            "Copying values from " + name_src +  "." + a_src[i] + " to " + name_dest + "." + a_dest[i]
        )
        arcpy.CalculateField_management(
            l_dest, 
            name_dest + "." + a_dest[i], 
            "[" + name_src + "." + a_src[i] + "]"
        )
        i = i+1  


# ------------------------------------------------------ #
# Workspace settings
# ------------------------------------------------------ #
env.overwriteOutput = True
env.outputCoordinateSystem = arcpy.SpatialReference("ETRS 1989 UTM Zone 32N")
env.workspace = r"P:\15220700_gis_samordning_2022_(marea_spare_ecogaps)\Zofie\synergi_3_tree_accounts\DATA" # IF NECESSARY, CHANGE PATH TO DATA DIRECTORY


# ------------------------------------------------------ #
# Inputs
# ------------------------------------------------------ #
path_bydel = "neighbourhoods.gdb\\" # IF NECESSARY, CHANGE PATH TO GEODATABASE STORING NEIGHBOURHOOD POLYGONS
path_output = "data.gdb\\" # IF NECESSARY, CHANGE PATH TO GEODATABASE STORING OUTPUT DATA
v_buildings = r"R:\GeoSpatialData\Topography\Norway_FKB\Original\FKB-Bygning FGDB-format\Basisdata_03_Oslo_5972_FKB-Bygning_FGDB\Basisdata_03_Oslo_5972_FKB-Bygning_FGDB.gdb\fkb_bygning_omrade" # IF NECESSARY, CHANGE PATH TO DATASET STORING BUILDING POLYGONS
v_water = r"R:\GeoSpatialData\Topography\Norway_FKB\Original\FKB-Vann FGDB-format\Basisdata_0000_Norge_5973_FKB-Vann_FGDB\Basisdata_0000_Norge_5973_FKB-Vann_FGDB.gdb\fkb_vann_omrade" # IF NECESSARY, CHANGE PATH TO DATASET STORING WATER POLYGONS


# ------------------------------------------------------ #
# 1. Detect tree polygons (crowns) and tree points (tops) per neighbourhood
# ------------------------------------------------------ #
arcpy.AddMessage("Step 1: Detecting tree polygons and points per neighbourhood...")

# Iterate over bydel (here adjusted for Oslo - 16 bydel numbered 01-16 with prefix 0301)
list_tree_pnt_names = []
list_tree_poly_names = []  

for i in range (1, 17): # IF NECESSARY, CHANGE NUMBER OF BYDEL

    bydel_code = "0301" + str(i).zfill(2) # IF NECESSARY, CHANGE CODE PREFIX OF BYDEL
    arcpy.AddMessage("  PROCESSING BYDEL {}".format(bydel_code))
    arcpy.AddMessage("  ---------------------".format(bydel_code))
   
    v_bydel = path_bydel + "\\b_" + bydel_code
    l_las_folder = r"lidar\{}".format(bydel_code) # IF NECESSARY, CHANGE PATH TO .las FILES
    
    # ------------------------------------------------------ #
    # 1.1 Create LAS Dataset
    # ------------------------------------------------------ #
    arcpy.AddMessage("  1.1: Creating LAS Dataset...")
    
    d_las = "data_" + bydel_code + "_001_lasdataset.lasd"
    arcpy.CreateLasDataset_management(
        input = l_las_folder, 
        out_las_dataset = d_las, 
        relative_paths = "RELATIVE_PATHS"
    )

    # ------------------------------------------------------ #
    # 1.2 Create RGB image
    # ------------------------------------------------------ #
    arcpy.AddMessage("  1.2: Creating RGB image...")
    
    r_rgb = path_output + "data_" + bydel_code + "_002_rgb" 
    arcpy.LasDatasetToRaster_conversion(
        in_las_dataset = d_las, 
        out_raster = r_rgb, 
        value_field = "RGB", 
        interpolation_type = "BINNING NEAREST NATURAL_NEIGHBOR", 
        data_type = "INT", 
        sampling_type = "CELLSIZE", 
        sampling_value = "1", 
        z_factor = "1"
    )

    # ------------------------------------------------------ #
    # 1.3 Create vegetation mask
    # ------------------------------------------------------ #
    arcpy.AddMessage("  1.3: Creating vegetation mask...")
    
    r_tgi = path_output + "data_" + bydel_code + "_003_tgi" 
    band_1 = arcpy.sa.Raster(r_rgb + "\\Band_1")
    band_2 = arcpy.sa.Raster(r_rgb + "\\Band_2")
    band_3 = arcpy.sa.Raster(r_rgb + "\\Band_3")

    output = arcpy.sa.Con(((band_2 - (0.39 * band_1) - (0.61 * band_3)) >= 0), 1)
    output.save(os.path.join(env.workspace, r_tgi))
    arcpy.Delete_management(r_rgb)
    
    # ------------------------------------------------------ #
    # 1.4 Vectorize vegetation mask
    # ------------------------------------------------------ #
    arcpy.AddMessage("  1.4: Vectorizing vegetation mask...")
    
    v_tgi = path_output + "data_" + bydel_code + "_004_tgi" 
    arcpy.RasterToPolygon_conversion(
        in_raster = r_tgi,
        out_polygon_features = v_tgi, 
        simplify = "SIMPLIFY", 
        raster_field = "Value", 
        create_multipart_features = "SINGLE_OUTER_PART", 
        max_vertices_per_feature = ""
    )
    arcpy.Delete_management(r_tgi)
    
    # ------------------------------------------------------ #
    # 1.5 Create DEM
    # ------------------------------------------------------ #
    arcpy.AddMessage("  1.5: Creating DEM...")

    # select DEM points (= terrain)
    l_dem = arcpy.CreateUniqueName('dem_lyr')
    arcpy.MakeLasDatasetLayer_management(
        in_las_dataset=d_las, 
        out_layer=l_dem, 
        class_code="2", 
        return_values="2", 
        no_flag="INCLUDE_UNFLAGGED", 
        synthetic="INCLUDE_SYNTHETIC", 
        keypoint="INCLUDE_KEYPOINT", 
        withheld="EXCLUDE_WITHHELD", 
        surface_constraints=""
    )

    # convert to DEM raster
    r_dem = path_output + "data_" + bydel_code + "_005_dem" 
    arcpy.conversion.LasDatasetToRaster(
        in_las_dataset = l_dem,
        out_raster = r_dem,
        value_field = "ELEVATION",
        interpolation_type = "BINNING AVERAGE LINEAR",
        data_type = "INT",
        sampling_type = "CELLSIZE",
        sampling_value = 0.5, 
        z_factor = 1
    )

    # ------------------------------------------------------ #
    # 1.6 Create DSM
    # ------------------------------------------------------ #
    arcpy.AddMessage("  1.6: Creating DSM...")

    # select DSM points (= surface)
    l_dsm = arcpy.CreateUniqueName('dsm_lyr')
    arcpy.MakeLasDatasetLayer_management(
        in_las_dataset=d_las, 
        out_layer=l_dsm, 
        class_code=["1", "3", "4", "5"], 
        return_values=["1", "3", "4", "5"], 
        no_flag="INCLUDE_UNFLAGGED", 
        synthetic="INCLUDE_SYNTHETIC", 
        keypoint="INCLUDE_KEYPOINT", 
        withheld="EXCLUDE_WITHHELD", 
        surface_constraints=""
    )

    # convert to DSM raster
    r_dsm = path_output + "data_" + bydel_code + "_006_dsm" 
    arcpy.conversion.LasDatasetToRaster(
        in_las_dataset = l_dsm,
        out_raster = r_dsm,
        value_field = "ELEVATION",
        interpolation_type = "BINNING MAXIMUM LINEAR",
        data_type = "INT",
        sampling_type = "CELLSIZE",
        sampling_value = 0.5, 
        z_factor = 1
    )
    arcpy.Delete_management(d_las)

    # ------------------------------------------------------ #
    # 1.7 Create CHM
    # ------------------------------------------------------ #
    arcpy.AddMessage("  1.7: Creating CHM...")
    
    r_chm = path_output + "data_" + bydel_code + "_007_chm"
    arcpy.gp.RasterCalculator_sa(
        '"{}"-"{}"'.format(r_dsm, r_dem), 
        r_chm
    )
    arcpy.Delete_management(r_dem)

    # ------------------------------------------------------ #
    # 1.8 Refine CHM with vegetation mask
    # ------------------------------------------------------ #
    arcpy.AddMessage("  1.8: Refining CHM with vegetation mask...")
    
    r_chm_tgi = path_output + "data_" + bydel_code + "_008_chm_tgi"
    arcpy.gp.ExtractByMask_sa(
        r_chm, 
        v_tgi, 
        r_chm_tgi)
    arcpy.Delete_management(v_tgi)
    arcpy.Delete_management(r_chm)

    # ------------------------------------------------------ #
    # 1.9 Filter CHM by minimum height
    # ------------------------------------------------------ #
    arcpy.AddMessage("  1.9: Filtering CHM by minimum height...")
    
    r_chm_h = path_output + "data_" + bydel_code + "_009_chm_h"
    h = 2.5
    arcpy.gp.ExtractByAttributes_sa(
        r_chm_tgi, 
        "Value >= {}".format(h), 
        r_chm_h
    )
    arcpy.Delete_management(r_chm_tgi)

    # ------------------------------------------------------ #
    # 1.10 Refine CHM by focal maximum filter
    # ------------------------------------------------------ #
    arcpy.AddMessage("  1.10: Refining CHM by focal maximum filter...")
    
    r_chm_smooth = path_output + "data_" + bydel_code + "_010_chm_smooth"
    arcpy.gp.FocalStatistics_sa(
        r_chm_h, 
        r_chm_smooth, 
        "Circle 1,5 MAP", 
        "MAXIMUM", 
        "DATA", 
        "90"
    )

    # ------------------------------------------------------ #
    # 1.11 Flip CHM
    # ------------------------------------------------------ #
    arcpy.AddMessage("  1.11: Flipping CHM...")
    
    r_chm_flip = path_output + "data_" + bydel_code + "_011_chm_flip"
    arcpy.gp.RasterCalculator_sa(
        '"{}"*(-1)'.format(r_chm_smooth), 
        r_chm_flip
    )
    arcpy.Delete_management(r_chm_smooth)

    # ------------------------------------------------------ #
    # 1.12 Compute flow direction
    # ------------------------------------------------------ #
    arcpy.AddMessage("  1.12: Computing flow direction...")
    
    r_flowdir = path_output + "data_" + bydel_code + "_012_flowdir"
    arcpy.gp.FlowDirection_sa(
        r_chm_flip, 
        r_flowdir
    )
    arcpy.Delete_management(r_chm_flip)

    # ------------------------------------------------------ #
    # 1.13 Identify sinks
    # ------------------------------------------------------ #
    arcpy.AddMessage("  1.13: Identifying sinks...")
    
    r_sinks = path_output + "data_" + bydel_code + "_013_sinks"
    arcpy.gp.Sink_sa(
        r_flowdir, 
        r_sinks
    )

    # ------------------------------------------------------ #
    # 1.14 Identify watersheds 
    # ------------------------------------------------------ #
    arcpy.AddMessage("  1.14: Identifying watersheds...")
    
    r_watersheds = path_output + "data_" + bydel_code + "_014_watersheds"
    arcpy.gp.Watershed_sa(
        r_flowdir,
        r_sinks,
        r_watersheds,
        "Value"
    ) 
    arcpy.Delete_management(r_flowdir)

    # ------------------------------------------------------ #
    # 1.15 Identify tree tops (I) by identifying focal flow
    # ------------------------------------------------------ #
    arcpy.AddMessage("  1.15: Identifying tree tops by focal flow...")
    
    r_focflow = path_output + "data_" + bydel_code + "_015_focflow"
    arcpy.gp.FocalFlow_sa(
        r_sinks, 
        r_focflow,
        "0,5"
    )
    arcpy.Delete_management(r_sinks)

    # ------------------------------------------------------ #
    # 1.16 Identify tree tops (II) by converting focal flow values from 0 to 1
    # ------------------------------------------------------ #
    arcpy.AddMessage("  1.16: Identifying tree tops by converting focal flow values from 0 to 1...")
    
    r_focflow_01 = path_output + "data_" + bydel_code + "_016_focflow_01"
    arcpy.gp.RasterCalculator_sa(
        'Con("{}" == 0, 1)'.format(r_focflow), 
        r_focflow_01
    )
    arcpy.Delete_management(r_focflow)

    # ------------------------------------------------------ #
    # 1.17 Vectorize tree tops to polygons
    # ------------------------------------------------------ #
    arcpy.AddMessage("  1.17: Vectorizing tree tops to polygons...")
    
    v_treetop_poly = path_output + "data_" + bydel_code + "_017_treetop_poly"
    arcpy.RasterToPolygon_conversion(
        in_raster = r_focflow_01,
        out_polygon_features = v_treetop_poly, 
        simplify = "SIMPLIFY", 
        raster_field = "Value", 
        create_multipart_features = "SINGLE_OUTER_PART", 
        max_vertices_per_feature = ""
    )
    arcpy.Delete_management(r_focflow_01)

    # ------------------------------------------------------ #
    # 1.18 Convert tree top polygons to points
    # ------------------------------------------------------ #
    arcpy.AddMessage("  1.18: Converting tree top polygons to points...")
    
    v_treetop_pnt = path_output + "data_" + bydel_code + "_018_treetop_pnt"
    arcpy.FeatureToPoint_management(
        in_features = v_treetop_poly,
        out_feature_class = v_treetop_pnt, 
        point_location = "INSIDE"
    )
    arcpy.Delete_management(v_treetop_poly)

    # Extract tree height (from CHM) and tree altitude (from DSM) to tree points   
    arcpy.gp.ExtractMultiValuesToPoints_sa(
        v_treetop_pnt,
        "'{}' tree_heigh;'{}' tree_altit".format(r_chm_h, r_dsm),
        "NONE"
        )
    arcpy.Delete_management(r_dsm)
    arcpy.Delete_management(r_chm_h)

    # ------------------------------------------------------ #
    # 1.19 Identify tree crowns by vectorizing watersheds
    # ------------------------------------------------------ #
    arcpy.AddMessage("  1.19: Identifying tree crowns by vectorizing watersheds...")
    
    v_watersheds = path_output + "data_" + bydel_code + "_019_watersheds"
    arcpy.RasterToPolygon_conversion(
        in_raster = r_watersheds,
        out_polygon_features = v_watersheds, 
        simplify = "SIMPLIFY", 
        raster_field = "Value", 
        create_multipart_features = "SINGLE_OUTER_PART", 
        max_vertices_per_feature = ""
    )
    arcpy.Delete_management(r_watersheds)
    
    # ------------------------------------------------------ #
    # 1.20 Select only tree points within neighbourhood
    # ------------------------------------------------------ #
    arcpy.AddMessage("  1.20: Selecting only tree points within neighbourhood...")
    
    l_tree_pnt = arcpy.MakeFeatureLayer_management(
        v_treetop_pnt, 
        "tree_pnt_lyr"
    )
    
    arcpy.SelectLayerByLocation_management(
        l_tree_pnt, 
        "INTERSECT",
        v_bydel,
        "",
        "NEW_SELECTION"
    )
    
    v_tree_pnt = path_output + "data_" + bydel_code + "_tree_pnt"
    arcpy.CopyFeatures_management(
        in_features = l_tree_pnt,
        out_feature_class = v_tree_pnt
    )    
    arcpy.Delete_management(v_treetop_pnt)

    # Store information on neighbourhood code
    arcpy.AddField_management(v_tree_pnt, "bydel_code", "TEXT")
    arcpy.CalculateField_management(v_tree_pnt, "bydel_code", bydel_code)
    
    # Delete useless attributes
    arcpy.DeleteField_management(
        v_tree_pnt, 
        ["Id", "gridcode", "ORIG_FID"]
    )
    
    list_tree_pnt_names.append(v_tree_pnt)

    # ------------------------------------------------------ #
    # 1.21 Select only tree polygons within neighbourhood (i.e., the ones that intersect with tree tops)
    # ------------------------------------------------------ #
    arcpy.AddMessage("  1.21: Selecting only tree polygons within neighbourhood...")
    
    l_tree_poly = arcpy.MakeFeatureLayer_management(
        v_watersheds, 
        "tree_poly_lyr"
    )
    
    arcpy.SelectLayerByLocation_management(
        l_tree_poly, 
        "INTERSECT",
        v_tree_pnt,
        "",
        "NEW_SELECTION"
    )

    v_tree_poly = path_output + "data_" + bydel_code + "_tree_poly"
    arcpy.CopyFeatures_management(
        in_features = l_tree_poly,
        out_feature_class = v_tree_poly
    )
    arcpy.Delete_management(v_watersheds)
    
    # Store information on neighbourhood code
    arcpy.AddField_management(v_tree_poly, "bydel_code", "TEXT")
    arcpy.CalculateField_management(v_tree_poly, "bydel_code", bydel_code)

    # Delete useless attributes
    arcpy.DeleteField_management(
        v_tree_poly, 
        ["Id", "gridcode"]
    )
   
    list_tree_poly_names.append(v_tree_poly)

    arcpy.AddMessage("  ---------------------")


# ------------------------------------------------------ #
# 2. Merge detected trees into one file
# ------------------------------------------------------ #
arcpy.AddMessage("Step 2: Merging detected trees into one file...")

v_tree_poly_merge = path_output + "data_200_tree_poly_merge"
arcpy.Merge_management(
    inputs = list_tree_poly_names,
    output = v_tree_poly_merge
)

v_tree_pnt_merge = path_output + "data_200_tree_pnt_merge"
arcpy.Merge_management(
    inputs = list_tree_pnt_names,
    output = v_tree_pnt_merge
)


# ------------------------------------------------------ #
# 3. Select trees outside buildings and sea
# ------------------------------------------------------ #
arcpy.AddMessage("Step 3: Selecting trees outside buildings and sea...")

# Define sea
l_sea = arcpy.MakeFeatureLayer_management(
    v_water, 
    "sea_lyr"
)

arcpy.SelectLayerByAttribute_management(
    l_sea, 
    "NEW_SELECTION",
    "objtype = 'Havflate'"    
)

v_sea = path_output + "tmp_sea"
arcpy.CopyFeatures_management(
    in_features = l_sea,
    out_feature_class = v_sea
)   

# Select tree points falling outside building and sea polygons
l_tree_pnt_outside = arcpy.MakeFeatureLayer_management(
    v_tree_pnt_merge, 
    "tree_pnt_outside_lyr"
)
arcpy.SelectLayerByLocation_management(
    l_tree_pnt_outside, 
    "INTERSECT",
    v_buildings,
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

v_tree_pnt_result = path_output + "tree_pnt_OB_2021"
arcpy.CopyFeatures_management(
    in_features = l_tree_pnt_outside,
    out_feature_class = v_tree_pnt_result
)   

arcpy.Delete_management(v_sea)

# Select tree polygons that do not intersect the removed points
l_tree_poly_outside = arcpy.MakeFeatureLayer_management(
    v_tree_poly_merge, 
    "tree_poly_outside_layer"
)
arcpy.SelectLayerByLocation_management(
    l_tree_poly_outside, 
    "INTERSECT",
    v_tree_pnt_result,
    "",
    "NEW_SELECTION",
)

v_tree_poly_result = path_output + "tree_poly_OB_2021"
arcpy.CopyFeatures_management(
    in_features = l_tree_poly_outside,
    out_feature_class = v_tree_poly_result
)  

arcpy.Delete_management(v_tree_poly_merge)
arcpy.Delete_management(v_tree_pnt_merge)


# ------------------------------------------------------ #
# 4. Compute additional attributes
# ------------------------------------------------------ #
arcpy.AddMessage("Step 4: Computing additional attributes...")

# Assign a unique ID to each tree polygon
arcpy.AddField_management(v_tree_poly_result, "crown_id", "LONG")
arcpy.CalculateField_management(v_tree_poly_result, "crown_id", '[OBJECTID]')

# Compute crown diameter for each tree polygon using Minimum Bounding Geometry
v_mbg = path_output + "tmp_mbg"
arcpy.MinimumBoundingGeometry_management(
    v_tree_poly_result,
    v_mbg,
    "CIRCLE", # TODO - adjust geometry here if necessary
    "NONE", 
    "", 
    "MBG_FIELDS"
)

arcpy.AddField_management(v_tree_poly_result, "crown_diam", "FLOAT")
join_and_copy(v_tree_poly_result, "crown_id", v_mbg, "crown_id", ["MBG_Diameter"], ["crown_diam"])
arcpy.Delete_management(v_mbg)

# Compute crown area and perimeter
arcpy.AddField_management(v_tree_poly_result, "crown_area", "FLOAT")
arcpy.AddField_management(v_tree_poly_result, "crown_peri", "FLOAT")

arcpy.CalculateField_management(v_tree_poly_result, "crown_area", '[Shape_Area]')
arcpy.CalculateField_management(v_tree_poly_result, "crown_peri", '[Shape_Length]')

# Assign tree polygon ID to tree points
arcpy.AddField_management(v_tree_pnt_result, "tmp_id", "LONG") # temporary ID for tree points to avoid issues with join_and_copy()
arcpy.CalculateField_management(v_tree_pnt_result, "tmp_id", '[OBJECTID]')

v_join = path_output + "tmp_join"
arcpy.SpatialJoin_analysis(
    v_tree_pnt_result,
    v_tree_poly_result, 
    v_join,
    "JOIN_ONE_TO_ONE", 
    "KEEP_ALL", 
    match_option="INTERSECT"
)

arcpy.AddField_management(v_tree_pnt_result, "crown_id", "LONG")
join_and_copy(
    v_tree_pnt_result, 
    "tmp_id", 
    v_join, 
    "tmp_id", 
    ["crown_id"], 
    ["crown_id"]
)

arcpy.Delete_management(v_join)
arcpy.DeleteField_management(v_tree_pnt_result, "tmp_id")

# Copy crown_diam, crown_area, crown_peri from tree polygons to tree points
arcpy.AddField_management(v_tree_pnt_result, "crown_diam", "FLOAT")
arcpy.AddField_management(v_tree_pnt_result, "crown_area", "FLOAT")
arcpy.AddField_management(v_tree_pnt_result, "crown_peri", "FLOAT")

join_and_copy(
    v_tree_pnt_result, 
    "crown_id", 
    v_tree_poly_result, 
    "crown_id", 
    ["crown_diam", "crown_area", "crown_peri"], 
    ["crown_diam", "crown_area", "crown_peri"]
)

# Copy tree_heigh, tree_altit from tree points to tree polygons
arcpy.AddField_management(v_tree_poly_result, "tree_heigh", "SHORT")
arcpy.AddField_management(v_tree_poly_result, "tree_altit", "LONG")

join_and_copy(
    v_tree_poly_result, 
    "crown_id", 
    v_tree_pnt_result, 
    "crown_id", 
    ["tree_heigh", "tree_altit"], 
    ["tree_heigh", "tree_altit"]
)

# Calculate tree volume
arcpy.AddField_management(v_tree_poly_result, "tree_volum", "FLOAT")
arcpy.CalculateField_management(
    in_table=v_tree_poly_result,
    field="tree_volum", 
    expression="(1.0/3.0) * math.pi * ( !crown_diam! /2.0 ) * ( !crown_diam! /2.0) * float(!tree_heigh!)",
    expression_type="PYTHON_9.3", 
    code_block=""
)

arcpy.AddField_management(v_tree_pnt_result, "tree_volum", "FLOAT")
arcpy.CalculateField_management(
    in_table=v_tree_pnt_result,
    field="tree_volum", 
    expression="(1.0/3.0) * math.pi * ( !crown_diam! /2.0 ) * ( !crown_diam! /2.0) * float(!tree_heigh!)",
    expression_type="PYTHON_9.3", 
    code_block=""
)
