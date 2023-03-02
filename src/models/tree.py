import os
import arcpy
from arcpy import env

def create_lasDataset(l_las_folder: str, d_las: str):
    """
    Creates a LAS dataset using the arcpy module.

    Args:
    - l_las_folder (str): The path to the LAS files.
    - d_las (str): The output path to the LAS dataset.
    """
    
    arcpy.AddMessage("\t\tCreating LAS Dataset...")

    arcpy.CreateLasDataset_management(
        input=l_las_folder,
        out_las_dataset=d_las,
        relative_paths="RELATIVE_PATHS"
    )

def create_RGB(d_las: str, r_rgb: str):
    """_summary_

    Args:
        d_las (str): The path to the LAS dataset. 
        r_rgb (str): The output path to the RGB raster.  
    """    
    arcpy.AddMessage("\t\tCreating RGB image...")
    
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


def create_vegMask(r_rgb: str, r_tgi: str):
    """_summary_

    Args:
        r_rgb (str): The path to the RGB raster.
        r_tgi (str): The output path to TGI vegetation mask raster. 
    """    
    arcpy.AddMessage("\t\tCreating vegetation mask...")

    band_1 = arcpy.sa.Raster(r_rgb + "\\Band_1")
    band_2 = arcpy.sa.Raster(r_rgb + "\\Band_2")
    band_3 = arcpy.sa.Raster(r_rgb + "\\Band_3")

    output = arcpy.sa.Con(((band_2 - (0.39 * band_1) - (0.61 * band_3)) >= 0), 1)
    output.save(os.path.join(env.workspace, r_tgi))
    arcpy.Delete_management(r_rgb)

def tgi_toVector(r_tgi, v_tgi):
    """_summary_

    Args:
        r_tgi (_type_): _description_
        v_tgi (_type_): _description_
    """    
    arcpy.AddMessage("\t\tVectorizing vegetation mask...")
    
    arcpy.RasterToPolygon_conversion(
        in_raster = r_tgi,
        out_polygon_features = v_tgi, 
        simplify = "SIMPLIFY", 
        raster_field = "Value", 
        create_multipart_features = "SINGLE_OUTER_PART", 
        max_vertices_per_feature = ""
    )
    arcpy.Delete_management(r_tgi)

def create_DTM(d_las, r_dtm, spatial_resolution):
    """_summary_

    Args:
        d_las (_type_): _description_
        r_dtm (_type_): _description_
        spatial_resolution (_type_): _description_
    """    
    arcpy.AddMessage("\t\tCreating DTM...")

    # select DTM points (class 2 = ground points)
    l_dtm = arcpy.CreateUniqueName('dtm_lyr')
    arcpy.MakeLasDatasetLayer_management(
        in_las_dataset=d_las, 
        out_layer=l_dtm, 
        class_code="2", 
        return_values="2", 
        no_flag="INCLUDE_UNFLAGGED", 
        synthetic="INCLUDE_SYNTHETIC", 
        keypoint="INCLUDE_KEYPOINT", 
        withheld="EXCLUDE_WITHHELD", 
        surface_constraints=""
    )

    # convert to DTM raster
    arcpy.conversion.LasDatasetToRaster(
        in_las_dataset = l_dtm,
        out_raster = r_dtm,
        value_field = "ELEVATION",
        interpolation_type = "BINNING AVERAGE LINEAR",
        data_type = "INT",
        sampling_type = "CELLSIZE",
        sampling_value = spatial_resolution, 
        z_factor = 1
    )

def create_DSM(d_las, r_dsm, spatial_resolution, class_code, return_values):
    """_summary_

    Args:
        d_las (_type_): _description_
        r_dsm (_type_): _description_
        spatial_resolution (_type_): _description_
        class_code (_type_): _description_
        return_values (_type_): _description_
    """    
    arcpy.AddMessage("\t\t\tCreating DSM...")

    # select DSM points (= surface)
    l_dsm = arcpy.CreateUniqueName('dsm_lyr')
    arcpy.MakeLasDatasetLayer_management(
        in_las_dataset=d_las, 
        out_layer=l_dsm, 
        class_code=class_code, 
        return_values=return_values, 
        no_flag="INCLUDE_UNFLAGGED", 
        synthetic="INCLUDE_SYNTHETIC", 
        keypoint="INCLUDE_KEYPOINT", 
        withheld="EXCLUDE_WITHHELD", 
        surface_constraints=""
    )

    # convert to DSM raster
    arcpy.conversion.LasDatasetToRaster(
        in_las_dataset = l_dsm,
        out_raster = r_dsm,
        value_field = "ELEVATION",
        interpolation_type = "BINNING MAXIMUM LINEAR",
        data_type = "INT",
        sampling_type = "CELLSIZE",
        sampling_value = spatial_resolution, 
        z_factor = 1
    )
    arcpy.Delete_management(d_las)

def create_CHM(r_dtm, r_dsm, r_chm):
    """_summary_

    Args:
        r_dtm (_type_): _description_
        r_dsm (_type_): _description_
        r_chm (_type_): _description_
    """    
    arcpy.AddMessage("\t\t\tCreating CHM...")
    arcpy.gp.RasterCalculator_sa(
        '"{}"-"{}"'.format(r_dsm, r_dtm), 
        r_chm
    )
    arcpy.Delete_management(r_dtm)