# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# perform_tree_detection_v1.py
# Description: Translation of Hanssen et al. (2021) tree detection algorithm
# from ArcMap model builder to ArcPy script - Version 3
# Author: Zofie Cimburova, Willeke A'Campo
# Dependencies: ArcGIS Pro 3.0, 3D analyst, image analyst, spatial analyst
# ---------------------------------------------------------------------------

import os
import time
import arcpy
from arcpy import env
import logging

# local sub-package modules
import tree
import split_chm
from src import LaserAttributes
from src import AdminAttributes
from src import GeometryAttributes

# local sub-package utils
from src import arcpy_utils as au
from src import (
    MUNICIPALITY,
    DATA_PATH,
    RAW_PATH,
    INTERIM_PATH,
    PROCESSED_PATH,
    SPATIAL_REFERENCE,
    COORD_SYSTEM,
    POINT_DENSITY,
)
from src import logger

# ------------------------------------------------------ #
# Functions
# ------------------------------------------------------ #


def end_time1(start_time1):
    end_time1 = time.time()
    execution_time1 = end_time1 - start_time1
    logger.info("\tTIME:\t {:.2f} sec".format(execution_time1))


# define the spatial resolution of the DSM/DTM/CHM grid based on lidar point density
# move to config
def get_spatial_resolution():
    if POINT_DENSITY >= 4:
        spatial_resolution = 0.25
    elif POINT_DENSITY < 4 and POINT_DENSITY >= 2:
        spatial_resolution = 0.5
    else:
        spatial_resolution = 1
    return spatial_resolution


def detect_watershed(neighbourhood_list, r_chm):
    logger.info("1. Start watershed segmentation method...")
    logger.info("-" * 100)
    logger.info("Processing neighbourhoods...")
    logger.info(neighbourhood_list)

    # Detect trees per neighbourhood
    for n_code in neighbourhood_list:
        logger.info("\t---------------------".format(n_code))
        logger.info("\tPROCESSING NEIGHBOURHOOD <<{}>>".format(n_code))
        logger.info("\t---------------------".format(n_code))

        # temporary filegdb containing detected trees per neighbourhood
        filegdb_path = os.path.join(
            tree_detection_path, "tree_detection_b" + n_code + ".gdb"
        )
        au.createGDB_ifNotExists(filegdb_path)

        # workspace settings
        env.overwriteOutput = True
        env.outputCoordinateSystem = arcpy.SpatialReference(SPATIAL_REFERENCE)
        # not necessary as full paths are used, change accordingly if you work with relative paths
        # env.workspace = filegdb_path

        # ------------------------------------------------------ #
        # Dynamic Path Variables
        # ------------------------------------------------------ #

        # neighbourhood specific file paths
        v_neighb = os.path.join(split_neighbourhoods_gdb, "b_" + n_code)
        v_neighb_buffer = os.path.join(
            split_neighbourhoods_gdb, "b_" + n_code + "_buffer200"
        )

        # chm clipped by neighbourhood
        r_chm_neighb = os.path.join(
            split_chm_gdb, "chm_" + "b_" + n_code + "_buffer200"
        )

        # watershed segmentation
        r_chm_flip = os.path.join(filegdb_path, "chm_flip")
        r_flowdir = os.path.join(filegdb_path, "flowdir")
        r_sinks = os.path.join(filegdb_path, "sinks")
        r_watersheds = os.path.join(filegdb_path, "watersheds")

        # identify tree tops
        r_focflow = os.path.join(filegdb_path, "focflow_temp")
        v_top_poly = os.path.join(filegdb_path, "top_poly_temp")
        v_top_singlepoly = os.path.join(filegdb_path, "top_singlepoly_temp")
        v_top_ws_temp = os.path.join(filegdb_path, "top_ws_temp")
        v_top_watershed = os.path.join(
            filegdb_path, "tops_watershed_" + n_code
        )  # RESULTING tree tops from watershed

        # identify tree crowns
        v_crown_ws_temp = os.path.join(filegdb_path, "crown_ws_temp")
        v_crown_watershed = os.path.join(
            filegdb_path, "crowns_watershed_" + n_code
        )  # RESULTING tree crowns from watershed

        # ------------------------------------------------------ #
        # 1.1 Clip CHM to neighbourhood + 200m buffer to avoid edge effects
        # ------------------------------------------------------ #
        try:
            logger.info(
                "\t1.1 Clip CHM to {} + 200m buffer to avoid edge effects".format(
                    n_code
                )
            )
            if arcpy.Exists(r_chm_neighb):
                logger.info(
                    "\t\tThe clipped CHM for neighbourhood <<{}>> exists in database. Continue ...".format(
                        n_code
                    )
                )
            else:
                arcpy.Buffer_analysis(
                    in_features=v_neighb,
                    out_feature_class=v_neighb_buffer,
                    buffer_distance_or_field=200,
                )

                arcpy.Clip_management(
                    in_raster=r_chm,
                    out_raster=r_chm_neighb,
                    in_template_dataset=v_neighb_buffer,
                    clipping_geometry="ClippingGeometry",
                )

        except Exception as e:
            # catch any exception and print error message.
            logger.info(f"\t\tERROR: {e}. \nContinue...")

        # ------------------------------------------------------ #
        # 1.2 THE WATERSHED SEGMENTATION METHOD
        #     Flip CHM (old 1.11)
        #     Compute flow direction (old 1.12)
        #     Identify sinks (old 1.13)
        #     Identify watersheds (old 1.14)
        # ------------------------------------------------------ #

        try:
            logger.info("\t1.2 The Watershed Segmentation Method")
            start_time1 = time.time()
            if arcpy.Exists(r_watersheds):
                logger.info(
                    "\t\t The watershed raster for neighbourhood <<{}>> exists in database. Continue ...".format(
                        n_code
                    )
                )
            else:
                # nested function for watershed segmentation method
                tree.watershed_segmentation(
                    r_chm_neighb, r_chm_flip, r_flowdir, r_sinks, r_watersheds
                )
                end_time1(start_time1)
        except Exception as e:
            # catch any exception and print error message.
            logger.info(f"\t\tERROR: {e}. \nContinue...")

        # ------------------------------------------------------ #
        # 1.3 IDENTIFY TREE TOPS
        #     Identify tree tops (I) by identifying focal flow (old 1.15)
        #     Identify tree tops (II) by converting focal flow values from 0 to 1 (old 1.16)
        #     Vectorize tree tops to polygons (old 1.17)
        #     Convert tree top polygons to points (old 1.18)
        # ------------------------------------------------------ #

        try:
            logger.info("\t1.3 Identify Tree Tops  ")
            start_time1 = time.time()
            if arcpy.Exists(v_top_ws_temp):
                logger.info(
                    "\t\tThe treetop vector for neighbourhood <<{}>> exists in database. Continue ...".format(
                        n_code
                    )
                )
            else:
                # nested function to identify treeTops
                tree.identify_treeTops(
                    r_sinks,
                    r_focflow,
                    v_top_poly,
                    v_top_singlepoly,
                    v_top_ws_temp,
                )
                end_time1(start_time1)
        except Exception as e:
            # catch any exception and print error message.
            logger.info(f"\t\tERROR: {e}. \nContinue...")

        # ------------------------------------------------------ #
        #  1.4 IDENTIFY TREE CROWNS
        #      Identify tree crowns by vectorizing watersheds (old 1.19)
        # ------------------------------------------------------ #

        logger.info("\t1.4 Identify Tree Crowns ")
        start_time1 = time.time()
        if arcpy.Exists(v_crown_ws_temp):
            logger.info(
                "\t\tThe tree crown vector for neighbourhood <<{}>> exists in database. Continue ...".format(
                    n_code
                )
            )
        else:
            tree.identify_treeCrowns(r_watersheds, v_crown_ws_temp)
            end_time1(start_time1)

        # ------------------------------------------------------ #
        # 1.5 DELETE TREES THAT ARE NOT WHITHIN THE NEIGHBOURHOOD
        # ------------------------------------------------------ #

        # TOPS
        logger.info(
            "\t1.5 Delete trees that are not located whithin the neighbourhood."
        )

        # create a layer using the the tops within the buffered neighbourhood
        l_top_watershed = arcpy.MakeFeatureLayer_management(
            v_top_ws_temp, "lyr_top_watershed"
        )
        arcpy.SelectLayerByLocation_management(
            l_top_watershed, "INTERSECT", v_neighb, "", "NEW_SELECTION"
        )

        # save selection to ouput file
        arcpy.CopyFeatures_management(
            l_top_watershed, v_top_watershed  # output
        )

        # CROWNS
        # create a layer using the the crowns within the buffered neighbourhood
        l_crown_watershed = arcpy.MakeFeatureLayer_management(
            v_crown_ws_temp, "lyr_crown_watershed"
        )
        # only select crowns that intersect with the tree tops that fall within the neighbourhood
        arcpy.SelectLayerByLocation_management(
            l_crown_watershed, "INTERSECT", v_top_watershed, "", "NEW_SELECTION"
        )

        # save selection to ouput file
        arcpy.CopyFeatures_management(
            l_crown_watershed, v_crown_watershed  # output
        )

        # ------------------------------------------------------ #
        # 1.6 ADD METHOD AS ATTRIBUTE TO TREES
        # ------------------------------------------------------ #

        # init attribute classes
        LaserAttribute = LaserAttributes(
            filegdb_path, v_crown_watershed, v_top_watershed
        )

        AdminAttribute = AdminAttributes(
            filegdb_path, v_crown_watershed, v_top_watershed
        )

        logger.info("\t1.6 Add tree detection method as attribute to trees.")
        segmentation_method = '"watershed_segmentation"'
        LaserAttribute.attr_segMethod(segmentation_method)

        # ------------------------------------------------------ #
        # 1.7 ADD NEIGHBOURHOOD CODE AS ATTRIBUTE TO TREES
        # ------------------------------------------------------ #

        logger.info("\t1.7 Add neighbourhood code as attribute to trees.")
        AdminAttribute.delete_adminAttr()
        AdminAttribute.attr_neighbCode(n_code)

        # ------------------------------------------------------ #
        # 1.8 ADD TREE HEIGHT AS ATTRIBUTE TO TREE TOPS
        # ------------------------------------------------------ #
        logger.info(
            "\t1.8 Add tree height and tree altitude as attribute to tree tops."
        )
        str_multiplier = "100x"
        LaserAttribute.attr_topHeight(
            v_top_watershed, r_chm_neighb, r_dtm, str_multiplier
        )

        # ------------------------------------------------------ #
        # 1.9 DELETE TEMPORARY LARYERS
        # ------------------------------------------------------ #
        logger.info("\t1.9 Delete temporary layers.")
        temp_layers = [
            r_chm_flip,
            r_flowdir,
            r_sinks,
            r_watersheds,
            r_focflow,
            v_top_poly,
            v_top_singlepoly,
            v_top_ws_temp,
            v_crown_ws_temp,
        ]
        for layer in temp_layers:
            arcpy.Delete_management(layer)

    logger.info(
        "Finished modelling treecrowns using the Watershed Segmentation Method ..."
    )
    logger.info(
        "The watershed-trees are stored in the interim file geodatabase tree_detection_<<bydelcode>>:"
    )
    logger.info("\t\tTops:\t tops_watershed_<<bydelcode>>")
    logger.info("\t\tCrowns:\t crowns_watershed_<<bydelcode>>")
    logger.info("-" * 100)

    # ------------------------------------------------------ #


def detect_other_trees(neighbourhood_list):
    logger.info(
        "2. Start detecting trees that are NOT detected with the watershed segmentation method..."
    )
    logger.info("-" * 100)
    logger.info("Processing neighbourhoods...")
    logger.info(neighbourhood_list)

    # Detect trees per neighbourhood
    for n_code in neighbourhood_list:
        logger.info("\t---------------------".format(n_code))
        logger.info("\tPROCESSING NEIGHBOURHOOD <<{}>>".format(n_code))
        logger.info("\t---------------------".format(n_code))

        # temporary filegdb containing detected trees per neighbourhood
        filegdb_path = os.path.join(
            tree_detection_path, "tree_detection_b" + n_code + ".gdb"
        )

        # workspace settings
        env.overwriteOutput = True
        env.outputCoordinateSystem = arcpy.SpatialReference(SPATIAL_REFERENCE)
        # not necessary as full paths are used, change accordingly if you work with relative paths
        # env.workspace = filegdb_path

        # ------------------------------------------------------ #
        # Dynamic Path Variables
        # ------------------------------------------------------ #

        # neighbourhood specific file paths
        v_neighb = os.path.join(split_neighbourhoods_gdb, "b_" + n_code)

        # chm clipped by neighbourhood
        r_chm_neighb = os.path.join(
            split_chm_gdb, "chm_" + "b_" + n_code + "_buffer200"
        )

        # watershed trees
        v_crown_watershed = os.path.join(
            filegdb_path, "crowns_watershed_" + n_code
        )  # RESULTING tree crowns from watershed

        # other trees
        v_chm_polygons = os.path.join(filegdb_path, "chm_polygons")
        v_other_crowns_temp = os.path.join(filegdb_path, "other_crowns_temp")
        v_other_crowns_dissolved = os.path.join(
            filegdb_path, "other_crowns_dissolved_temp"
        )
        v_other_crowns_all = os.path.join(
            filegdb_path, "other_crowns_dissolved"
        )
        v_other_crowns = os.path.join(
            filegdb_path, "crowns_other_" + n_code
        )  # Resulting other crowns

        # other tops
        r_zonal_max = os.path.join(filegdb_path, "chm_zonal_max")
        v_other_tops = os.path.join(
            filegdb_path, "tops_other_" + n_code
        )  # Resulting other tops

        if arcpy.Exists(v_other_crowns) and arcpy.Exists(v_other_tops):
            logger.info(
                "\t\tThe other-trees for neighbourhood <<{}>> exist in database. Continue ...".format(
                    n_code
                )
            )
            continue

        # ------------------------------------------------------ #
        # 2.1 Convert CHM to polygons
        # TODO move to tree module
        # ------------------------------------------------------ #

        # if exists continue
        if not arcpy.Exists(v_chm_polygons):
            logging.info("\t2.1 Convert CHM to polygons")
            arcpy.conversion.RasterToPolygon(
                in_raster=r_chm_neighb,
                out_polygon_features=v_chm_polygons,
                simplify="SIMPLIFY",
                raster_field="Value",
                create_multipart_features="SINGLE_OUTER_PART",
                max_vertices_per_feature=None,
            )

        # ------------------------------------------------------ #
        # 2.2 Select polygons that do not intersect with watershed trees
        # ------------------------------------------------------ #

        logging.info(
            "\t2.2 Select polygons that do not intersect with watershed trees"
        )
        # create a layer for the converted CHM polygons
        l_chm_polygons = arcpy.MakeFeatureLayer_management(
            v_chm_polygons, "lyr_chm_polygons"
        )

        # inverse selection of watershed trees
        arcpy.SelectLayerByLocation_management(
            l_chm_polygons,
            "INTERSECT",
            v_crown_watershed,
            None,
            "NEW_SELECTION",
            "INVERT",
        )

        # save selection to ouput file
        arcpy.CopyFeatures_management(
            l_chm_polygons, v_other_crowns_temp  # output
        )

        # ------------------------------------------------------ #
        # 2.3 Disolve polygons to crowns
        # ------------------------------------------------------ #
        logging.info("\t2.3 Disolve polygons to crowns")
        arcpy.management.Dissolve(
            in_features=v_other_crowns_temp,
            out_feature_class=v_other_crowns_dissolved,
            dissolve_field=None,
            statistics_fields=None,
            multi_part="SINGLE_PART",
            unsplit_lines="DISSOLVE_LINES",
            concatenation_separator="",
        )

        # ------------------------------------------------------ #
        # 2.4 Delete crowns that are not whithin the neighbourhood
        # ------------------------------------------------------ #

        logging.info(
            "\t2.4 Delete other trees that are not located whithin the neighbourhood."
        )

        # create a layer using the the crowns within the buffered neighbourhood
        l_other_crowns = arcpy.MakeFeatureLayer_management(
            v_other_crowns_dissolved, "lyr_crown_watershed"
        )
        # only select crowns that intersect with the tree tops that fall within the neighbourhood
        arcpy.SelectLayerByLocation_management(
            l_other_crowns, "INTERSECT", v_neighb, "", "NEW_SELECTION"
        )

        # save selection to ouput file
        arcpy.CopyFeatures_management(
            l_other_crowns, v_other_crowns_all  # output
        )

        # ------------------------------------------------------ #
        # 2.5 Delete crowns smaller than 4 m2
        # ------------------------------------------------------ #

        lyr_crowns_other = arcpy.MakeFeatureLayer_management(
            v_other_crowns_all, "lyr_crowns_other"
        )
        lyr_roads = arcpy.MakeFeatureLayer_management(
            fkb_veg_omrade, "lyr_roads"
        )
        lyr_buildings = arcpy.MakeFeatureLayer_management(
            fkb_bygning_omrade, "lyr_buildings"
        )

        # ------------------------------------------------------ #
        # 4.2 Detect False Positives for the other_dissolve_method
        # ------------------------------------------------------ #

        logger.info(
            "\t2.5 Detect False Positives for the other tree detection method."
        )
        logger.info(
            "\t Delete trees that intersect with buildings (+2m buffer), roads and are smaller than 12 m2."
        )
        # select crowns that intersect or ar within 2m of buildings
        arcpy.SelectLayerByLocation_management(
            lyr_crowns_other,
            "INTERSECT",
            lyr_buildings,
            "2",
            "SUBSET_SELECTION",
            invert_spatial_relationship=False,
        )

        # add crowns that intersect with roads to selection
        arcpy.SelectLayerByLocation_management(
            lyr_crowns_other,
            "INTERSECT",
            lyr_roads,
            "",
            "ADD_TO_SELECTION",
            invert_spatial_relationship=False,
        )

        # add crowns that are smaller than 12 m2 to selection
        arcpy.management.SelectLayerByAttribute(
            in_layer_or_view=lyr_crowns_other,
            selection_type="ADD_TO_SELECTION",
            where_clause="Shape_Area < 12",
        )

        # switch selection e.g. keep on
        arcpy.SelectLayerByAttribute_management(
            in_layer_or_view=lyr_crowns_other, selection_type="SWITCH_SELECTION"
        )

        arcpy.CopyFeatures_management(
            in_features=lyr_crowns_other, out_feature_class=v_other_crowns
        )

        # ------------------------------------------------------ #
        # 2.6 Identify "other" tree tops
        # ------------------------------------------------------ #

        # polygon to point
        arcpy.management.FeatureToPoint(
            in_features=v_other_crowns,
            out_feature_class=v_other_tops,
            point_location="INSIDE",
        )

        # ------------------------------------------------------ #
        # 2.8 ADD METHOD AS ATTRIBUTE TO TREES
        # ------------------------------------------------------ #

        # init attribute classes
        LaserAttribute = LaserAttributes(
            filegdb_path, v_other_crowns, v_other_tops
        )

        AdminAttribute = AdminAttributes(
            filegdb_path, v_other_crowns, v_other_tops
        )

        logger.info("\t2.7 Add tree detection method as attribute to trees.")

        segmentation_method = '"other_dissolve"'
        LaserAttribute.attr_segMethod(segmentation_method)

        # ------------------------------------------------------ #
        # 2.7 ADD NEIGHBOURHOOD CODE AS ATTRIBUTE TO TREES
        # ------------------------------------------------------ #

        logger.info("\t2.9 Add neighbourhood code as attribute to trees.")
        AdminAttribute.delete_adminAttr()
        AdminAttribute.attr_neighbCode(n_code)

        # ------------------------------------------------------ #
        # 2.9 ADD TREE HEIGHT AS ATTRIBUTE TO TREES
        # ------------------------------------------------------ #
        logger.info(
            "\t2.9 Add tree height and tree altitude as attribute to tree tops."
        )
        # use zonal max to determin highest value in crown area
        zonalMax = arcpy.ia.ZonalStatistics(
            in_zone_data=v_other_crowns,
            zone_field="OBJECTID",
            in_value_raster=r_chm_neighb,
            statistics_type="MAXIMUM",
            ignore_nodata="DATA",
            process_as_multidimensional="CURRENT_SLICE",
            percentile_value=90,
            percentile_interpolation_type="AUTO_DETECT",
            circular_calculation="ARITHMETIC",
            circular_wrap_value=360,
        )
        zonalMax.save(r_zonal_max)

        str_multiplier = "100x"

        LaserAttribute.attr_topHeight(
            v_other_tops, r_zonal_max, r_dtm, str_multiplier
        )

        # ------------------------------------------------------ #
        # 2.9 DELETE TEMPORARY LARYERS
        # ------------------------------------------------------ #
        logger.info("\t2.9 Delete temporary layers.")
        temp_layers = [
            v_chm_polygons,
            v_other_crowns_temp,
            v_other_crowns_dissolved,
            v_other_crowns_all,
            r_zonal_max,
        ]
        for layer in temp_layers:
            arcpy.Delete_management(layer)

    logger.info(
        "Finished modelling the treecrowns that could not be identified with the watershed segmentation method  ..."
    )
    logger.info(
        "The other-trees are stored in the interim file geodatabase tree_detection_<<bydelcode>>:\n\t"
    )
    logger.info("\t\tTops:\t other_tops_<<bydelcode>>")
    logger.info("\t\tCrowns:\t other_crowns_<<bydelcode>>")
    logger.info("-" * 100)

    # ------------------------------------------------------ #


def merge_trees(neighbourhood_list):
    logger.info("3. Merge Trees with Other Trees...")
    logger.info("-" * 100)
    logger.info("Processing neighbourhoods...")
    logger.info(neighbourhood_list)

    # Detect trees per neighbourhood
    for n_code in neighbourhood_list:
        logger.info("\t---------------------".format(n_code))
        logger.info("\tPROCESSING NEIGHBOURHOOD <<{}>>".format(n_code))
        logger.info("\t---------------------".format(n_code))

        # temporary filegdb containing detected trees per neighbourhood
        filegdb_path = os.path.join(
            tree_detection_path, "tree_detection_b" + n_code + ".gdb"
        )

        # workspace settings
        env.overwriteOutput = True
        env.outputCoordinateSystem = arcpy.SpatialReference(SPATIAL_REFERENCE)
        # not necessary as full paths are used, change accordingly if you work with relative paths
        # env.workspace = filegdb_path

        # ------------------------------------------------------ #
        # Dynamic Path Variables
        # ------------------------------------------------------ #

        v_top_watershed = os.path.join(
            filegdb_path, "tops_watershed_" + n_code
        )  # RESULTING tree tops from watershed
        v_crown_watershed = os.path.join(
            filegdb_path, "crowns_watershed_" + n_code
        )  # RESULTING tree crowns from watershed
        v_other_crowns = os.path.join(
            filegdb_path, "crowns_other_" + n_code
        )  # Resulting other crowns
        v_other_tops = os.path.join(
            filegdb_path, "tops_other_" + n_code
        )  # Resulting other tops

        v_top_temp = os.path.join(filegdb_path, "tops_tmp_" + n_code)
        v_crown_temp = os.path.join(filegdb_path, "crowns_tmp_" + n_code)

        v_top = os.path.join(filegdb_path, "tops_" + n_code)
        v_crown = os.path.join(filegdb_path, "crowns_" + n_code)

        # ------------------------------------------------------ #
        # 3. Merge detected trees into one file
        # ------------------------------------------------------ #
        logger.info("-" * 100)
        logger.info("3.1 Merging detected trees into one file...")
        logger.info("-" * 100)

        start_time1 = time.time()
        if arcpy.Exists(v_top):
            logger.info("\tThe tree tops are already merged. Continue ...")
        else:
            logger.info(
                "\tMerge tree tops for all tiles into one polygon file."
            )
            arcpy.Merge_management(
                inputs=[v_top_watershed, v_other_tops], output=v_top_temp
            )
        end_time1(start_time1)

        start_time1 = time.time()
        if arcpy.Exists(v_crown):
            logger.info("\tThe tree crowns are already merged. Continue ...")
        else:
            logger.info(
                "\t\tMerge tree crowns for all tiles into one polygon file."
            )
            arcpy.Merge_management(
                inputs=[v_crown_watershed, v_other_crowns], output=v_crown_temp
            )
        end_time1(start_time1)

    logger.info("Finished merging the detected trees into one file ...")


def calculate_attributes():
    logger.info("5. Calculate Attributes...")
    logger.info("-" * 100)
    logger.info("Processing neighbourhoods...")
    logger.info(neighbourhood_list)

    # Detect trees per neighbourhood
    for n_code in neighbourhood_list:
        logger.info("\t---------------------".format(n_code))
        logger.info("\tPROCESSING NEIGHBOURHOOD <<{}>>".format(n_code))
        logger.info("\t---------------------".format(n_code))

        # temporary filegdb containing detected trees per neighbourhood
        filegdb_path = os.path.join(
            tree_detection_path, "tree_detection_b" + n_code + ".gdb"
        )

        # workspace settings
        env.overwriteOutput = True
        env.outputCoordinateSystem = arcpy.SpatialReference(SPATIAL_REFERENCE)
        # not necessary as full paths are used, change accordingly if you work with relative paths
        # env.workspace = filegdb_path

        # ------------------------------------------------------ #
        # Dynamic Path Variables
        # ------------------------------------------------------ #
        v_top_temp = os.path.join(filegdb_path, "tops_tmp_" + n_code)
        v_crown_temp = os.path.join(filegdb_path, "crowns_tmp_" + n_code)

        # ------------------------------------------------------ #
        # 4. Calculate attributes
        # ------------------------------------------------------ #

        # init class to calculate attributes
        AdminAttribute = AdminAttributes(filegdb_path, v_crown_temp, v_top_temp)
        LaserAttribute = LaserAttributes(filegdb_path, v_crown_temp, v_top_temp)
        GeometryAttribute = GeometryAttributes(
            filegdb_path, v_crown_temp, v_top_temp
        )
        # calculate attributes for tree crowns
        # nb_code in loop
        AdminAttribute.delete_adminAttr()
        AdminAttribute.attr_crownID(n_code)
        GeometryAttribute.attr_crownDiam()
        GeometryAttribute.attr_crownArea()  # crown_area and crown_perimeter

        # calculate attributes for enclosing circle, convex hull and envelope
        # if you want to keep the temporary MBG layers, set keep_temp=True
        GeometryAttribute.attr_enclosingCircle(keep_temp=True)
        GeometryAttribute.attr_convexHull(keep_temp=True)
        GeometryAttribute.attr_envelope(keep_temp=True)

        # calculate attributes for tree tops
        # nb_code and tree height/altitude in loop
        AdminAttribute.delete_adminAttr()
        AdminAttribute.join_crownID_toTop()

        # join top attributes to crown polygons
        LaserAttribute.join_topAttr_toCrown()  # tree_height_laser and tree_altit
        GeometryAttribute.attr_crownVolume()

    logger.info("Finished calculating attributes for the detected trees ...")


def detect_falsePositives(neighbourhood_list):
    logger.info("4. Detect False Positives...")
    logger.info("-" * 100)
    logger.info("Processing neighbourhoods...")
    logger.info(neighbourhood_list)

    # layers for selection
    lyr_roads = arcpy.MakeFeatureLayer_management(fkb_veg_omrade, "lyr_roads")

    # Detect trees per neighbourhood
    for n_code in neighbourhood_list:
        logger.info("\t---------------------".format(n_code))
        logger.info("\tPROCESSING NEIGHBOURHOOD <<{}>>".format(n_code))
        logger.info("\t---------------------".format(n_code))

        # temporary filegdb containing detected trees per neighbourhood
        filegdb_path = os.path.join(
            tree_detection_path, "tree_detection_b" + n_code + ".gdb"
        )
        au.createGDB_ifNotExists(filegdb_path)

        # workspace settings
        env.overwriteOutput = True
        env.outputCoordinateSystem = arcpy.SpatialReference(SPATIAL_REFERENCE)
        env.workspace = filegdb_path

        # ------------------------------------------------------ #
        # Dynamic Path Variables
        # ------------------------------------------------------ #
        # input
        v_top_temp = os.path.join(filegdb_path, "tops_tmp_" + n_code)
        v_crown_temp = os.path.join(filegdb_path, "crowns_tmp_" + n_code)
        lyr_crown_temp = arcpy.MakeFeatureLayer_management(
            v_crown_temp, "lyr_crown_temp"
        )

        # output
        v_top = os.path.join(ds_tops, "b_" + n_code + "topper")
        v_crown = os.path.join(ds_crowns, "b_" + n_code + "_kroner")
        v_crown_false_positives = os.path.join(
            ds_false_positives, "b_" + n_code + "_fp_kroner"
        )

        # ------------------------------------------------------ #
        # 4.1 Detect False Positives based on polygon geometry
        # - lampposts: perfect circles that intersect with roads
        # - outliers in crown_area
        # - outliers in ratio crown/area convex hull
        # - outliers in ratio crown/area enclosing circle
        # ------------------------------------------------------ #

        logger.info("\t4.1 Detect False Positives based on polygon geometry.")

        # lamp posts
        arcpy.SelectLayerByLocation_management(
            lyr_crown_temp,
            "INTERSECT",
            lyr_roads,
            "",
            "NEW_SELECTION",
            invert_spatial_relationship=False,
        )

        arcpy.management.SelectLayerByAttribute(
            in_layer_or_view=lyr_crown_temp,
            selection_type="SUBSET_SELECTION",
            where_clause="crown_area > 6.5 And crown_area < 9 And ratio_CA_CHA > 0.85 And ratio_CA_ECA > 0.7",
        )

        # geometery outliers
        arcpy.management.SelectLayerByAttribute(
            in_layer_or_view=lyr_crown_temp,
            selection_type="ADD_TO_SELECTION",
            where_clause="outlier_CA <> 0 Or outlier_ratio_CA_CHA <> 0 Or outlier_ratio_CA_ECA <> 0",
            invert_where_clause=None,
        )

        # export false positives
        arcpy.CopyFeatures_management(
            in_features=lyr_crown_temp,
            out_feature_class=v_crown_false_positives,
        )

        # switch selection
        arcpy.SelectLayerByAttribute_management(
            in_layer_or_view=lyr_crown_temp, selection_type="SWITCH_SELECTION"
        )

        # copy features that passed the test to separate feature class
        arcpy.CopyFeatures_management(
            in_features=lyr_crown_temp, out_feature_class=v_crown
        )
        # topology check delete all tops (false positives) that are not within the crown layer
        tree.topology_crownTop(v_top_temp, v_crown, v_top)

        # ------------------------------------------------------ #

    logger.info("Finished detecting false positives ...")
    logger.info(
        "The false postives and the cleaned tree dataset is stored in the filegdb {}:\n\t".format(
            gdb_laser_urban_trees
        )
    )
    return


if __name__ == "__main__":
    logger.setup_logger(logfile=True)
    logger = logging.getLogger(__name__)

    # start timer
    start_time0 = time.time()
    kommune = MUNICIPALITY
    # TODO move get_spatial_resolution() to config file
    spatial_resolution = get_spatial_resolution()

    # ------------------------------------------------------ #
    # INPUT PATHS
    # ------------------------------------------------------ #

    # specific file paths
    tree_detection_path = os.path.join(INTERIM_PATH, "tree_detection")
    # create folder in tree_detection_path if not exits
    if not os.path.exists(tree_detection_path):
        logger.info("Creating folder {} ...".format(tree_detection_path))
        os.makedirs(tree_detection_path)

    # admin data
    admin_data_path = os.path.join(
        DATA_PATH, kommune, "general", kommune + "_admindata.gdb"
    )
    study_area_path = os.path.join(admin_data_path, "analyseomrade")

    # neighbourhood list
    neighbourhood_path = os.path.join(admin_data_path, "bydeler")
    n_field_name = "bydelnummer"

    # TODO add test an prod config settings
    user_input = input("Is this a TEST or PROD run? (TEST/PROD):")

    if user_input == "TEST" or "test" or "Test":
        if kommune == "kristiansand":
            n_test = ["420409", "420411"]
        if kommune == "bodo":
            n_test = ["180402", "180403"]
        if kommune == "baerum":
            n_test = ["302401", "302412"]
        logger.info(
            "Test neighbourhoods in {} are {}: ".format(kommune, n_test)
        )
        neighbourhood_list = n_test
        logger.info(
            "Test starts for neighbourhood(s): {}".format(neighbourhood_list)
        )
        keep_temp = True
        logger.info("\tInterim filegdb's will be kept ...")

    if user_input == "PROD" or "prod" or "Prod":
        neighbourhood_list = au.get_neighbourhood_list(
            neighbourhood_path, n_field_name
        )
        logger.info("Processing neighbourhoods: {}".format(neighbourhood_list))
        keep_temp = False
        logger.info("\tInterim filegdb's will be deleted ...")

    keep_temp = True
    # split neighbourhoods
    split_neighbourhoods_gdb = os.path.join(INTERIM_PATH, "bydeler_split.gdb")
    if not arcpy.Exists(split_neighbourhoods_gdb):
        logger.info("Splitting neighbourhoods...")
        au.split_neighbourhoods(
            neighbourhood_path, n_field_name, split_neighbourhoods_gdb
        )

    # base data
    base_data_path = os.path.join(
        DATA_PATH, kommune, "general", kommune + "_basisdata.gdb"
    )
    fkb_bygning_omrade = os.path.join(base_data_path, "fkb_bygning_omrade")
    fkb_vann_omrade = os.path.join(base_data_path, "fkb_vann_omrade")
    fkb_veg_omrade = os.path.join(base_data_path, "fkb_veg_omrade")

    # terrain data
    # if database does not exists exit the code with the message: "The elevation data for the kommune is not available. Please run the script 'model_chm.py' first."
    gdb_elevation_data = os.path.join(
        DATA_PATH, kommune, "general", kommune + "_hoydedata.gdb"
    )

    if not arcpy.Exists(gdb_elevation_data):
        logger.error(
            f"The elevation and canopy height model data for {kommune} kommune is not available.\
                     \nPlease run the script 'model_chm.py' first."
        )
        exit()

    # canopy height raster (note values are x100)
    # TODO move chm_025m_int_100x to config file
    str_resolution = str(spatial_resolution).replace(".", "")

    r_chm = os.path.join(
        gdb_elevation_data, "chm_" + str(str_resolution) + "m_int_100x"
    )
    r_dtm = os.path.join(
        gdb_elevation_data, "dtm_" + str(str_resolution) + "m_int_100x"
    )  # for adding tree altitude to tree points

    # split neighbourhoods
    split_chm_gdb = os.path.join(INTERIM_PATH, "chm_split.gdb")
    if not arcpy.Exists(split_chm_gdb):
        au.createGDB_ifNotExists(split_chm_gdb)
    # TODO check if folder structure exists (especially intierm/tree_detection)
    # ------------------------------------------------------ #
    # OUTPUT PATHS
    # ------------------------------------------------------ #

    gdb_laser_urban_trees = os.path.join(
        PROCESSED_PATH, kommune + "_laser_bytraer.gdb"
    )
    au.createGDB_ifNotExists(gdb_laser_urban_trees)

    ds_false_positives = os.path.join(
        gdb_laser_urban_trees, "falsk_positive_trekroner"
    )
    au.createDataset_ifNotExists(
        gdb_laser_urban_trees, "falsk_positive_trekroner", COORD_SYSTEM
    )

    ds_crowns = os.path.join(gdb_laser_urban_trees, "trekroner")
    au.createDataset_ifNotExists(
        gdb_laser_urban_trees, "trekroner", COORD_SYSTEM
    )

    ds_tops = os.path.join(gdb_laser_urban_trees, "tretopper")
    au.createDataset_ifNotExists(
        gdb_laser_urban_trees, "tretopper", COORD_SYSTEM
    )

    # ------------------------------------------------------ #

    logger.info("-" * 100)
    logger.info("municipality:\t\t\t" + kommune)
    logger.info("spatial reference:\t\t" + SPATIAL_REFERENCE)
    logger.info("Spatial Resolution:\t\t" + str(spatial_resolution))
    logger.info("Canopy Height Model:\t\t" + os.path.basename(r_chm))
    logger.info("Output gdb:\t\t\t" + gdb_laser_urban_trees)
    logger.info("-" * 100)

    # ------------------------------------------------------ #
    # RUN FUNCTIONS
    # ------------------------------------------------------ #

    # TODO move functions to separate modules and run from root
    split_chm.split_chm_nb(
        neighbourhood_list, split_neighbourhoods_gdb, r_chm, split_chm_gdb
    )
    # detect_watershed(neighbourhood_list, r_chm)
    detect_other_trees(neighbourhood_list)
    merge_trees(neighbourhood_list)
    calculate_attributes()
    detect_falsePositives(neighbourhood_list)

    # delete all interim filegdb's
    if keep_temp == False:
        logger.info("\n\tDeleting all interim filegdb's ...")
        for file in os.listdir(tree_detection_path):
            if file.startswith("tree_detection"):
                arcpy.Delete_management(os.path.join(tree_detection_path, file))

    end_time0 = time.time()
    execution_time1 = end_time0 - start_time0
    logger.info("\n\tEXCEUTION TIME:\t {:.2f} sec".format(execution_time1))
