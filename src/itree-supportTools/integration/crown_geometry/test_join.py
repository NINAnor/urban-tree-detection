import os
import arcpy
from arcpy import env
import logging 

# local packages
from src import logger
from src import (SPATIAL_REFERENCE, URBAN_TREES_GDB, MUNICIPALITY)
from src import arcpy_utils as au


# input data
ds_joined_trees = os.path.join(URBAN_TREES_GDB, "joined_trees")
fc_case_2_stems = os.path.join(ds_joined_trees, "c2_stems_cleaned") 
fc_case_2_stems2 = os.path.join(ds_joined_trees, "c2_stems_cleaned2") 
fc_case_2_crowns = os.path.join(ds_joined_trees, "c2_crowns_cleaned") 

join_table = arcpy.management.AddJoin(
    in_layer_or_view=fc_case_2_stems,
    in_field="tree_id",
    join_table=fc_case_2_crowns,
    join_field="tree_id",
    join_type="KEEP_COMMON",
    index_join_fields="NO_INDEX_JOIN_FIELDS"
)


# clean layers 
keep_list = ["tree_id","crown_id_laser","geo_relation"]

au.deleteFields(
    in_table=join_table,
    out_table=fc_case_2_stems2,
    keep_list= keep_list
    )

# au.join_and_copy(
#     t_dest=fc_case_2_stems, # input table 
#     join_a_dest="tree_id", 
#     t_src=fc_case_2_crowns, # join table 
#     join_a_src="tree_id", 
#     a_src=["crown_id_laser", "geo_relation"], # name of the (source) fields you like to copy (join table)
#     a_dest=["crown_id_laser", "geo_relation"] # name of the (new) destination field (input table)
# )