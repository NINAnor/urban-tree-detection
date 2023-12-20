import os

import arcpy
from arcpy import env


def split_chm(
    split_neighbourhoods_gdb, neighbourhood_list, r_chm, gdb_split_chm
):

    # Detect trees per neighbourhood
    for n_code in neighbourhood_list:

        # workspace settings
        env.overwriteOutput = True

        # neighbourhood specific file paths
        v_neighb = os.path.join(split_neighbourhoods_gdb, "b_" + n_code)
        v_neighb_buffer = os.path.join(
            split_neighbourhoods_gdb, "b_" + n_code + "_buffer200"
        )

        # chm clipped by neighbourhood
        r_chm_neighb = os.path.join(
            gdb_split_chm, "chm_" + "b_" + n_code + "_buffer200"
        )

        arcpy.Buffer_analysis(
            in_features=v_neighb,
            out_feature_class=v_neighb_buffer,
            buffer_distance_or_field=200,
        )

        arcpy.management.Clip(
            in_raster=r_chm,
            rectangle="#",
            out_raster=r_chm_neighb,
            in_template_dataset=v_neighb_buffer,
            nodata_value="",
            clipping_geometry="ClippingGeometry",
            maintain_clipping_extent="NO_MAINTAIN_EXTENT",
        )

        print("done:", n_code)


if __name__ == "__main__":

    # list
    # neighbourhood_list = ['420409', '420411'] # kristiansand
    # end list til ..10
    neighbourhood_list = [
        "180401",
        "180402",
        "180403",
        "180404",
        "180405",
        "180406",
        "180407",
        "180408",
        "180409",
        "180410",
    ]  # bodo

    # paths
    split_neighbourhoods_gdb = r"C:\Data\offline_data\trekroner\urban-treeDetection\data\bodo\urban-treeDetection\interim\bydeler_split.gdb"
    r_chm = r"C:\Data\offline_data\trekroner\urban-treeDetection\data\bodo\general\bodo_hoydedata.gdb\chm_05m_int_100x"
    gdb_split_chm = r"C:\Data\offline_data\trekroner\urban-treeDetection\data\bodo\urban-treeDetection\interim\chm_split.gdb"

    split_chm(
        split_neighbourhoods_gdb, neighbourhood_list, r_chm, gdb_split_chm
    )

# test black2
