import os
import arcpy
from arcpy import env
from arcpy.sa import *
import logging

from src import logger

logger.setup_logger(logfile=False)
logger = logging.getLogger(__name__)

# ------------------------------------------------------ #
# 1.1 Create LAS Dataset
# ------------------------------------------------------ #


def create_lasDataset(l_las_folder: str, d_las: str):
    """
    Creates a LAS dataset using the arcpy module.

    Args:
    - l_las_folder (str): The path to the LAS files.
    - d_las (str): The output path to the LAS dataset.
    """

    logger.info("\t\tCreating LAS Dataset...")

    arcpy.CreateLasDataset_management(
        input=l_las_folder,
        out_las_dataset=d_las,
        relative_paths="RELATIVE_PATHS",
    )


# ------------------------------------------------------ #
# 1.2 CANOPY HEIGTH MODEL
# ------------------------------------------------------ #


def create_DTM(d_las, r_dtm, spatial_resolution, study_area_path):
    """_summary_

    Args:
    d_las (_type_): _description_
    r_dtm (_type_): _description_
    spatial_resolution (_type_): _description_
    """

    logger.info("\t\tCreating DTM ({}x{}m) ...".format(spatial_resolution, spatial_resolution))

    # select DTM points (class 2 = ground points)
    l_dtm = arcpy.CreateUniqueName("dtm_lyr")
    arcpy.MakeLasDatasetLayer_management(
        in_las_dataset=d_las,
        out_layer=l_dtm,
        class_code="2",
        return_values="2",
        no_flag="INCLUDE_UNFLAGGED",
        synthetic="INCLUDE_SYNTHETIC",
        keypoint="INCLUDE_KEYPOINT",
        withheld="EXCLUDE_WITHHELD",
        surface_constraints="",
    )

    # convert to DTM raster
    temp = os.path.join(r_dtm + "_temp")

    arcpy.conversion.LasDatasetToRaster(
        in_las_dataset=l_dtm,
        out_raster=temp,
        value_field="ELEVATION",
        interpolation_type="BINNING AVERAGE LINEAR",
        data_type="FLOAT",  # Set to "INT" for speeding up analysis
        sampling_type="CELLSIZE",
        sampling_value=spatial_resolution,
        z_factor=1,
    )

    logger.info("\t\tMasking the DTM with the study area extent...")
    r_masked = arcpy.sa.ExtractByMask(
        in_raster=temp,
        in_mask_data=study_area_path,
    )
    
    r_masked.save(r_dtm)
    arcpy.Delete_management(temp)


def create_DSM(
    d_las, r_dsm, spatial_resolution, class_code, return_values, study_area_path
):
    """_summary_

    Args:
        d_las (_type_): _description_
        r_dsm (_type_): _description_
        spatial_resolution (_type_): _description_
        class_code (_type_): _description_
        return_values (_type_): _description_
    """
    logger.info(
        "\t\tCreating DSM ({}x{}m) ...".format(
            spatial_resolution, spatial_resolution
        )
    )

    # select DSM points (= surface)
    l_dsm = arcpy.CreateUniqueName("dsm_lyr")
    arcpy.MakeLasDatasetLayer_management(
        in_las_dataset=d_las,
        out_layer=l_dsm,
        class_code=class_code,
        return_values=return_values,
        no_flag="INCLUDE_UNFLAGGED",
        synthetic="INCLUDE_SYNTHETIC",
        keypoint="INCLUDE_KEYPOINT",
        withheld="EXCLUDE_WITHHELD",
        surface_constraints="",
    )

    # convert to DSM raster
    temp = os.path.join(r_dsm + "_temp")

    arcpy.conversion.LasDatasetToRaster(
        in_las_dataset=l_dsm,
        out_raster=temp,
        value_field="ELEVATION",
        interpolation_type="BINNING MAXIMUM LINEAR",
        data_type="FLOAT",  # Set to "INT" for speeding up analysis
        sampling_type="CELLSIZE",
        sampling_value=spatial_resolution,
        z_factor=1,
    )

    logger.info("\t\tMasking the DSM with the study area extent...")
    r_masked = arcpy.sa.ExtractByMask(
        in_raster=temp,
        in_mask_data=study_area_path,
    )
    r_masked.save(r_dsm)
    arcpy.Delete_management(temp)


def create_CHM(r_dtm, r_dsm, r_chm):
    """_summary_

    Args:
        r_dtm (_type_): _description_
        r_dsm (_type_): _description_
        r_chm (_type_): _description_
    """
    logger.info("\t\tCreating CHM...")
    arcpy.gp.RasterCalculator_sa('"{}"-"{}"'.format(r_dsm, r_dtm), r_chm)


# ------------------------------------------------------ #
# 1.3 VEGETATION MASK
# ------------------------------------------------------ #


def create_RGB(
    d_las: str, r_rgb: str, study_area_path: str
):
    """_summary_

    Args:
        d_las (str): The path to the LAS dataset.
        r_rgb (str): The output path to the RGB raster.
    """
    logger.info("\t\tCreating RGB image...")

    temp = os.path.join(r_rgb + "_temp")
    arcpy.LasDatasetToRaster_conversion(
        in_las_dataset=d_las,
        out_raster=temp,
        value_field="RGB",
        interpolation_type="BINNING NEAREST NATURAL_NEIGHBOR",
        data_type="INT",  # must be INT
        sampling_type="CELLSIZE",
        sampling_value="1", # must be 1
        z_factor="1",
    )

    logger.info("\t\tMasking the RGB image with the study area extent...")
    r_masked = arcpy.sa.ExtractByMask(
        in_raster=temp,
        in_mask_data=study_area_path,
    )

    r_masked.save(r_rgb)
    arcpy.Delete_management(temp)


def create_vegMask(r_rgb: str, r_tgi: str):
    """_summary_

    Args:
        r_rgb (str): The path to the RGB raster.
        r_tgi (str): The output path to TGI vegetation mask raster.
    """
    logger.info("\t\tCreating vegetation mask...")

    band_1 = arcpy.sa.Raster(r_rgb + "\\Band_1")
    band_2 = arcpy.sa.Raster(r_rgb + "\\Band_2")
    band_3 = arcpy.sa.Raster(r_rgb + "\\Band_3")

    output = arcpy.sa.Con(
        ((band_2 - (0.39 * band_1) - (0.61 * band_3)) >= 0), 1
    )
    output.save(os.path.join(env.workspace, r_tgi))
    arcpy.Delete_management(r_rgb)


def tgi_toVector(r_tgi, v_tgi):
    """_summary_

    Args:
        r_tgi (_type_): _description_
        v_tgi (_type_): _description_
    """
    logger.info("\t\tVectorizing vegetation mask...")

    arcpy.RasterToPolygon_conversion(
        in_raster=r_tgi,
        out_polygon_features=v_tgi,
        simplify="SIMPLIFY",  # treedetection_v1 uses "SIMPLIFY" to speed up the processingtime
        raster_field="Value",
        create_multipart_features="SINGLE_OUTER_PART",
        max_vertices_per_feature="",
    )
    arcpy.Delete_management(r_tgi)


# ------------------------------------------------------ #
# 1.4 SMOOTHING AND FILTERING CANOPY HEIGHT MODEL
# ------------------------------------------------------ #


def extract_vegMask(v_tgi, r_chm, r_chm_tgi):
    """_summary_

    Args:
        v_tgi (_type_): _description_
        r_chm (_type_): _description_
        r_chm_tgi (_type_): _description_
    """
    logger.info("\t\tRefining CHM with vegetation mask...")
    arcpy.gp.ExtractByMask_sa(r_chm, v_tgi, r_chm_tgi)


def extract_Mask(mask_path, input_chm, r_chm_mask):
    """_summary_

    Args:
        v_tgi (_type_): _description_
        r_chm (_type_): _description_
        r_chm_tgi (_type_): _description_
    """
    logger.info("\t\tMasking CHM with municipality specific mask...")
    arcpy.gp.ExtractByMask_sa(input_chm, mask_path, r_chm_mask)


def extract_minHeight(r_chm_mask, r_chm_h, min_heigth):
    """_summary_

    Args:
        input_chm (_type_): The path to the canopy height raster that needs to be filtered.
        r_chm_h (_type_): _description_
        min_heigth (_type_): _description_
    """
    logger.info("\t\tFiltering CHM by minimum height...")
    arcpy.gp.ExtractByAttributes_sa(
        r_chm_mask, "Value >= {}".format(min_heigth), r_chm_h
    )


def focal_meanFilter(r_chm_h, chm_noise_removal):
    """_summary_

    Args:
        r_chm_h (raster): input path to height filter chm raster
        chm_noise_removal (raster): ouput path to noise removal chm raster
    """
    outFocalStat = arcpy.ia.FocalStatistics(
        in_raster=r_chm_h,
        neighborhood="Rectangle 1.5 1.5 MAP",  # 1 for kristiansand, 1.5 for bodo
        statistics_type="MEAN",
        ignore_nodata="NODATA",
        percentile_value=90,
    )

    outFocalStat.save(chm_noise_removal)

    return


def focal_maxFilter(r_chm_h, r_chm_smooth, radius):
    """_summary_

    Args:
        r_chm_h (_type_): _description_
        r_chm_smooth (_type_): _description_
        radius (_type_): _description_
    """
    logger.info(
        "\t\tRefining CHM by a focal maximum filter with a {} MAP radius...".format(
            radius
        )
    )
    neighborhood = NbrCircle(radius, "MAP")
    outFocalStat = FocalStatistics(
        r_chm_h, neighborhood, "MAXIMUM", "DATA", "90"
    )
    outFocalStat.save(r_chm_smooth)


# ------------------------------------------------------ #
# 1.5 THE WATERSHED SEGMENTATION METHOD
# ------------------------------------------------------ #


def watershed_segmentation(
    r_chm_input, r_chm_flip, r_flowdir, r_sinks, r_watersheds
):
    """Watershed Segmentation Method:

    The method is based on the following steps:
    1. Flip CHM raster (multiply by -1)
    2. Compute flow direction
    3. Identify sinks
    4. Identify watersheds

    Best to use a CHM that is clipped to a smaller area (e.g. municipality) to speed up processing time.
    Note that when clipping the CHM to a smaller area, you need to buffer the CHM to avoid edge effects.

    Args:
        r_chm_input (_type_): input chm raster path
        r_chm_flip (_type_): path tho the flipped chm raster
        r_flowdir (_type_): path to the flow direction raster
        r_sinks (_type_): path to the sinks raster
        r_watersheds (_type_): path to the watersheds raster

    Returns:
        _type_: _description_
    """
    # flip CHM
    def flip_CHM(r_chm_input):
        logger.info("\t\tFlipping CHM...")
        arcpy.gp.RasterCalculator_sa(
            '"{}"*(-1)'.format(r_chm_input), r_chm_flip
        )
        return r_chm_flip

    # Compute flow direction
    def comp_flowDir(r_chm_flip):
        logger.info("\t\tComputing flow direction...")
        arcpy.gp.FlowDirection_sa(r_chm_flip, r_flowdir)
        # arcpy.Delete_management(r_chm_flip)
        return r_flowdir

    # Identify sinks
    def identify_sinks(r_flowdir):
        logger.info("\t\tIdentifying sinks...")
        arcpy.gp.Sink_sa(r_flowdir, r_sinks)
        return r_sinks

    # identify watersheds
    def identify_watersheds(r_flowdir, r_sinks):
        logger.info("\t\tIdentifying watersheds...")
        arcpy.gp.Watershed_sa(r_flowdir, r_sinks, r_watersheds, "Value")
        # arcpy.Delete_management(r_flowdir)
        # arcpy.Delete_management(r_sinks)
        return r_watersheds

    # call nested functions

    flip_CHM(r_chm_input)
    comp_flowDir(r_chm_flip)
    identify_sinks(r_flowdir)
    identify_watersheds(r_flowdir, r_sinks)

    return r_watersheds


# ------------------------------------------------------ #
# 1.6 IDENTIFY TREE TOPS
# step 7 perform_tree_detection_v2 (version 1 not used)
# ------------------------------------------------------ #


def identify_treeTops(
    r_sinks, r_focflow, v_top_poly, v_top_singlepoly, v_top_watershed
):

    # Identify tree tops (I) by identifying focal flow
    def identify_focalFlow():
        logger.info("\t\tIdentifying tree tops by focal flow...")

        arcpy.gp.FocalFlow_sa(r_sinks, r_focflow, "0,5")
        return r_focflow

    # Vectorize tree tops to polygons
    def focalFlow_toVector():
        logger.info("\t\tVectorizing tree tops to polygons...")

        arcpy.RasterToPolygon_conversion(
            in_raster=r_focflow,
            out_polygon_features=v_top_poly,
            simplify="NO_SIMPLIFY",  # treedetection_v1 uses "SIMPLIFY" to speed up the processingtime
            raster_field="Value",
            create_multipart_features="SINGLE_OUTER_PART",
            max_vertices_per_feature="",
        )
        arcpy.Delete_management(r_focflow)
        return v_top_poly

    # Convert tree top polygons to points
    def focalFlow_vectorToPoint():
        logger.info("\t\tConverting tree top polygons to points...")

        # Convert multipart polygons to single part polgyons
        # This ensures that tree top polygons can be converted to points
        arcpy.MultipartToSinglepart_management(
            in_features=v_top_poly,
            out_feature_class=v_top_singlepoly,
        )
        arcpy.FeatureToPoint_management(
            in_features=v_top_poly,
            out_feature_class=v_top_watershed,
            point_location="INSIDE",
        )
        arcpy.Delete_management(v_top_poly)
        arcpy.Delete_management(v_top_singlepoly)

        return v_top_watershed

    identify_focalFlow()

    focalFlow_toVector()
    focalFlow_vectorToPoint()

    return v_top_watershed


# ------------------------------------------------------ #
#  1.7 IDENTIFY TREE CROWNS
# ------------------------------------------------------ #


def identify_treeCrowns(r_watersheds, v_crown_watershed):
    logger.info("\t\tIdentifying tree crowns by vectorizing watersheds...")

    arcpy.RasterToPolygon_conversion(
        in_raster=r_watersheds,
        out_polygon_features=v_crown_watershed,
        simplify="NO_SIMPLIFY",  # treedetection_v1 uses "SIMPLIFY" to speed up the processingtime
        raster_field="Value",
        create_multipart_features="SINGLE_OUTER_PART",
        max_vertices_per_feature="",
    )
    # arcpy.Delete_management(r_watersheds)

    return v_crown_watershed


# ------------------------------------------------------ #
#  1.8
# ------------------------------------------------------ #


def topology_crownTop(input_tree, selecting_tree, output_tree):
    input_tree_lyr = arcpy.MakeFeatureLayer_management(
        input_tree, "temp_lyr"  # tmp_lyr_name,
    )

    arcpy.SelectLayerByLocation_management(
        input_tree_lyr, "INTERSECT", selecting_tree, "", "NEW_SELECTION"
    )

    arcpy.CopyFeatures_management(
        in_features=input_tree_lyr, out_feature_class=output_tree
    )

    return output_tree


if __name__ == "__main__":
    pass
