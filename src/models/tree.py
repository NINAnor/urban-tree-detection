import os
import arcpy
from arcpy import env

def create_lasDataset(l_las_folder: str, d_las: str):
    """
    Creates a LAS dataset using the arcpy module.

    Parameters:
    - l_las_folder (str): The folder path where the LAS files are located.
    - d_las (str): The output LAS dataset path and name.

    Returns:
    - None

    Example Usage:
    create_lasDataset("C:/data/las_files", "C:/data/las_datasets/tile_001.lasd")
    """
    
    arcpy.AddMessage("\t\tCreating LAS Dataset...")

    arcpy.CreateLasDataset_management(
        input=l_las_folder,
        out_las_dataset=d_las,
        relative_paths="RELATIVE_PATHS"
    )

def create_RGB(d_las, r_rgb):
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


def create_vegMask(r_rgb, r_tgi):
    arcpy.AddMessage("\t\tCreating vegetation mask...")

    band_1 = arcpy.sa.Raster(r_rgb + "\\Band_1")
    band_2 = arcpy.sa.Raster(r_rgb + "\\Band_2")
    band_3 = arcpy.sa.Raster(r_rgb + "\\Band_3")

    output = arcpy.sa.Con(((band_2 - (0.39 * band_1) - (0.61 * band_3)) >= 0), 1)
    output.save(os.path.join(env.workspace, r_tgi))
    arcpy.Delete_management(r_rgb)
