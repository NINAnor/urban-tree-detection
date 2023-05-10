"""
Imports cleaned municipal tree dataset (stem points) and 
segmented laser tree dataset (tree top points, tree crown polygons) 
into the urban tree geodatabase
"""

import os 

# import local packages
from src import (IN_SITU_TREES_GDB, URBAN_TREES_GDB, LASER_TREES_GDB)
from src import arcpy_utils as au

# --------------------------------------------------------------------------- #
# Import municipal tree dataset (stem points)
# --------------------------------------------------------------------------- #

# stem points
in_fc = os.path.join(IN_SITU_TREES_GDB, "stem_in_situ") 
out_fc = os.path.join(URBAN_TREES_GDB, "urban_trees", "stem_in_situ")

au.copyFeature_ifNotExists(
    in_fc=in_fc,
    out_fc=out_fc
)

# --------------------------------------------------------------------------- #
# Import laser tree dataset (tree top points, tree crown polygons)
# --------------------------------------------------------------------------- #

# tree top points
in_fc = os.path.join(LASER_TREES_GDB, "top_1to1")
out_fc = os.path.join(URBAN_TREES_GDB, "urban_trees", "top_laser")

au.copyFeature_ifNotExists(
    in_fc=in_fc,
    out_fc=out_fc
)

# tree crown polygons 
in_fc = os.path.join(LASER_TREES_GDB,"crown_1to1")
out_fc = os.path.join(URBAN_TREES_GDB, "urban_trees", "crown_laser")

au.copyFeature_ifNotExists(
    in_fc=in_fc,
    out_fc=out_fc
)

