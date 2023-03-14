import os
import arcpy
from arcpy import env
from arcpy.sa import *

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
    
def create_RGB(d_las: str, r_rgb: str, study_area_path: str):
    """_summary_

    Args:
        d_las (str): The path to the LAS dataset. 
        r_rgb (str): The output path to the RGB raster.  
    """    
    arcpy.AddMessage("\t\tCreating RGB image...")
    
    r_mem = arcpy.LasDatasetToRaster_conversion(
        in_las_dataset = d_las, 
        out_raster = "",  # save in memory 
        value_field = "RGB", 
        interpolation_type = "BINNING NEAREST NATURAL_NEIGHBOR", 
        data_type = "INT", 
        sampling_type = "CELLSIZE", 
        sampling_value = "1", 
        z_factor = "1"
    )[0]
    
    arcpy.AddMessage("\t\tMasking the RGB image with the study area extent...")
    r_masked = arcpy.sa.ExtractByMask(
        in_raster=r_mem,
        in_mask_data= study_area_path, 
    )
    
    r_masked.save(r_rgb)


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

def create_DTM(d_las, r_dtm, spatial_resolution, study_area_path):
    """_summary_

    Args:
        d_las (_type_): _description_
        r_dtm (_type_): _description_
        spatial_resolution (_type_): _description_
    """    
    arcpy.AddMessage("\t\tCreating DTM ({}x{}m) ...".format(spatial_resolution, spatial_resolution))

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
    r_mem = arcpy.conversion.LasDatasetToRaster(
        in_las_dataset = l_dtm,
        out_raster = "", # save in memory 
        value_field = "ELEVATION",
        interpolation_type = "BINNING AVERAGE LINEAR",
        data_type = "INT",
        sampling_type = "CELLSIZE",
        sampling_value = spatial_resolution, 
        z_factor = 1
    )[0]
 
    arcpy.AddMessage("\t\tMasking the DTM with the study area extent...")
    r_masked = arcpy.sa.ExtractByMask(
        in_raster=r_mem,
        in_mask_data= study_area_path, 
    )   
    r_masked.save(r_dtm)
    

def create_DSM(d_las, r_dsm, spatial_resolution, class_code, return_values):
    """_summary_

    Args:
        d_las (_type_): _description_
        r_dsm (_type_): _description_
        spatial_resolution (_type_): _description_
        class_code (_type_): _description_
        return_values (_type_): _description_
    """    
    arcpy.AddMessage("\t\tCreating DSM ({}x{}m) ...".format(spatial_resolution, spatial_resolution))

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


def create_CHM(r_dtm, r_dsm, r_chm):
    """_summary_

    Args:
        r_dtm (_type_): _description_
        r_dsm (_type_): _description_
        r_chm (_type_): _description_
    """    
    arcpy.AddMessage("\t\tCreating CHM...")
    arcpy.gp.RasterCalculator_sa(
        '"{}"-"{}"'.format(r_dsm, r_dtm), 
        r_chm
    )
    
def extract_vegMask(v_tgi, r_chm, r_chm_tgi):
    """_summary_

    Args:
        v_tgi (_type_): _description_
        r_chm (_type_): _description_
        r_chm_tgi (_type_): _description_
    """    
    arcpy.AddMessage("\t\tRefining CHM with vegetation mask...")
    arcpy.gp.ExtractByMask_sa(
        r_chm, 
        v_tgi, 
        r_chm_tgi)

def extract_minHeight(input_chm, r_chm_h, min_heigth):
    """_summary_

    Args:
        input_chm (_type_): The path to the canopy height raster that needs to be filtered. 
        r_chm_h (_type_): _description_
        min_heigth (_type_): _description_
    """    
    arcpy.AddMessage("\t\tFiltering CHM by minimum height...")
    arcpy.gp.ExtractByAttributes_sa(
        input_chm, 
        "Value >= {}".format(min_heigth), 
        r_chm_h
    )

    
def focal_maxFilter(r_chm_h, r_chm_smooth, radius):
    """_summary_

    Args:
        r_chm_h (_type_): _description_
        r_chm_smooth (_type_): _description_
        radius (_type_): _description_
    """    
    arcpy.AddMessage("\t\tRefining CHM by a focal maximum filter with a {} MAP radius...".format(radius))
    neighborhood = NbrCircle(radius, "MAP")
    outFocalStat= FocalStatistics(
        r_chm_h,
        neighborhood,
        "MAXIMUM",
        "DATA",
        "90" 
    )
    outFocalStat.save(r_chm_smooth)

def watershed_segmentation(r_chm_smooth,r_chm_flip,r_flowdir,r_sinks,r_watersheds):

    # flip CHM
    def flip_CHM(r_chm_smooth):
        arcpy.AddMessage("\t\tFlipping CHM...")
        arcpy.gp.RasterCalculator_sa(
            '"{}"*(-1)'.format(r_chm_smooth), 
            r_chm_flip
        )
        return r_chm_flip
    
    # Compute flow direction
    def comp_flowDir(r_chm_flip):
        arcpy.AddMessage("\t\tComputing flow direction...")
        arcpy.gp.FlowDirection_sa(
            r_chm_flip, 
            r_flowdir
        )
        arcpy.Delete_management(r_chm_flip)
        return r_flowdir
    
    # Identify sinks
    def identify_sinks(r_flowdir):
        arcpy.AddMessage("\t\tIdentifying sinks...")
        arcpy.gp.Sink_sa(
            r_flowdir, 
            r_sinks
        )
        return r_sinks
    
    # identify watersheds 

    def identify_watersheds(r_flowdir, r_sinks):
        arcpy.AddMessage("\t\tIdentifying watersheds...")
        arcpy.gp.Watershed_sa(
            r_flowdir,
            r_sinks,
            r_watersheds,
            "Value"
        ) 
        arcpy.Delete_management(r_flowdir)
        #arcpy.Delete_management(r_sinks)
        return r_watersheds
        
    # call nested functions     

    flip_CHM(r_chm_smooth)
    comp_flowDir(r_chm_flip)
    identify_sinks(r_flowdir)
    identify_watersheds(r_flowdir, r_sinks)
    
    return r_watersheds 
        

def identify_treeTops(r_sinks, r_focflow, r_focflow_01, v_treetop_poly,v_treetop_singlepoly, r_chm_h, r_dsm, v_treetop_pnt):
    
    # Identify tree tops (I) by identifying focal flow
    def identify_focalFlow():
        arcpy.AddMessage("\t\tIdentifying tree tops by focal flow...")
        arcpy.gp.FocalFlow_sa(
            r_sinks, 
            r_focflow,
            "0,5"
        )
        #arcpy.Delete_management(r_sinks)
        return r_focflow
    
    # Identify tree tops (II) by converting focal flow values from 0 to 1
    def convert_focalFlow():
        arcpy.AddMessage("\t\tIdentifying tree tops by converting focal flow values from 0 to 1...")
    
        arcpy.gp.RasterCalculator_sa(
            'Con("{}" == 0, 1)'.format(r_focflow), 
            r_focflow_01
        )
        arcpy.Delete_management(r_focflow)
        return r_focflow_01
    
    # Vectorize tree tops to polygons
    def focalFlow_toVector():
        arcpy.AddMessage("\t\tVectorizing tree tops to polygons...")
    
        arcpy.RasterToPolygon_conversion(
            in_raster = r_focflow_01,
            out_polygon_features = v_treetop_poly, 
            simplify = "SIMPLIFY", 
            raster_field = "Value", 
            create_multipart_features = "SINGLE_OUTER_PART", 
            max_vertices_per_feature = ""
        )
        arcpy.Delete_management(r_focflow_01)
        return v_treetop_poly
      

    # Convert tree top polygons to points
    def focalFlow_vectorToPoint():
        arcpy.AddMessage("\t\tConverting tree top polygons to points...")
        
        # Convert multipart polygons to single part polgyons 
        # This ensures that tree top polygons can be converted to points
        arcpy.MultipartToSinglepart_management(
            in_features=v_treetop_poly, 
            out_feature_class=v_treetop_singlepoly, 
        )
        arcpy.FeatureToPoint_management(
            in_features = v_treetop_poly,
            out_feature_class = v_treetop_pnt, 
            point_location = "INSIDE"
        )
        arcpy.Delete_management(v_treetop_poly)
        arcpy.Delete_management(v_treetop_singlepoly)

        # Extract tree height (from CHM) and tree altitude (from DSM) to tree points   
        arcpy.gp.ExtractMultiValuesToPoints_sa(
            v_treetop_pnt,
            "'{}' tree_height;'{}' tree_altit".format(r_chm_h, r_dsm),
            "NONE"
            )
        return v_treetop_pnt
    
    identify_focalFlow()
    convert_focalFlow()
    focalFlow_toVector()
    focalFlow_vectorToPoint()
    
    return v_treetop_pnt
    
def identify_treeCrowns(r_watersheds, v_treecrown_poly):
    arcpy.AddMessage("\t\tIdentifying tree crowns by vectorizing watersheds...")
    
    arcpy.RasterToPolygon_conversion(
        in_raster = r_watersheds,
        out_polygon_features = v_treecrown_poly, 
        simplify = "SIMPLIFY", 
        raster_field = "Value", 
        create_multipart_features = "SINGLE_OUTER_PART", 
        max_vertices_per_feature = ""
    )
    #arcpy.Delete_management(r_watersheds)
    
    return v_treecrown_poly

def SelectTrees_ByStudyArea(study_area_path, tile_code, v_treetop_pnt,  v_tree_pnt, v_treecrown_poly, v_tree_poly):
    arcpy.AddMessage("\t\tSelecting tree points within the study area...")
    
    l_tree_pnt = arcpy.MakeFeatureLayer_management(
        v_treetop_pnt, 
        "tree_pnt_lyr"
    )

    arcpy.SelectLayerByLocation_management(
        l_tree_pnt, 
        "INTERSECT",
        study_area_path,
        "",
        "NEW_SELECTION"
    )

    arcpy.CopyFeatures_management(
        in_features = l_tree_pnt,
        out_feature_class = v_tree_pnt
    )    

    # Store information on neighbourhood code
    arcpy.AddField_management(v_tree_pnt, "tile_code", "TEXT")
    arcpy.CalculateField_management(v_tree_pnt, "bydel_code", tile_code)
    
    # Delete useless attributes
    arcpy.DeleteField_management(
        v_tree_pnt, 
        ["Id", "gridcode", "ORIG_FID"]
    )

    arcpy.AddMessage("\t\tSelecting tree polygons within neighbourhood...")
    
    l_tree_poly = arcpy.MakeFeatureLayer_management(
        v_treecrown_poly, 
        "tree_poly_lyr"
    )
    
    arcpy.SelectLayerByLocation_management(
        l_tree_poly, 
        "INTERSECT",
        v_tree_pnt,
        "",
        "NEW_SELECTION"
    )

    arcpy.CopyFeatures_management(
        in_features = l_tree_poly,
        out_feature_class = v_tree_poly
    )
    
    # Store information on neighbourhood code
    arcpy.AddField_management(v_tree_poly, "tile_code", "TEXT")
    arcpy.CalculateField_management(v_tree_poly, "tile_code", tile_code)

    # Delete useless attributes
    arcpy.DeleteField_management(
        v_tree_poly, 
        ["Id", "gridcode"]
    )
   
    