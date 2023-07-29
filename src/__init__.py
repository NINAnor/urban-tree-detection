"""Top-level package for treeDetection."""
# specify module imports here that are used across multiple packages in the project
# do not specify module imports that are only used in the local subpackages
# sepecify there imports in their local __init__.py

__author__ = """Willeke A'Campo"""
__email__ = "willeke.acampo@nina.com"
__version__ = "0.1.0"

# Import specific functions and classes
from src.utils.config import (
    ADMIN_GDB,
    AR5_LANDUSE_PATH,
    TOOL_PATH,
    DATA_PATH,
    FKB_BUILDING_PATH,
    FKB_WATER_PATH,
    INTERIM_PATH,
    IN_SITU_TREES_GDB,
    LASER_TREES_GDB,
    MUNICIPALITY,
    PROCESSED_PATH,
    RAW_PATH,
    SSB_DISTRICT_PATH,
    SPATIAL_REFERENCE,
    COORD_SYSTEM,
    URBAN_TREES_GDB,
    RGB_AVAILABLE,
    VEG_CLASSES_AVAILABLE,
    POINT_DENSITY,
    MIN_HEIGHT,
    FOCAL_MAX_RADIUS,
)
from src.utils import logger
from src.utils import arcpy_utils
from src.compute_attributes.admin_attributes import AdminAttributes
from src.compute_attributes.laser_attributes import LaserAttributes 
from src.compute_attributes.geometry_attributes import GeometryAttributes

