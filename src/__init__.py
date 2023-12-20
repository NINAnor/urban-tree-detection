"""Top-level package for treeDetection."""
# specify module imports here that are used across multiple packages in the project
# do not specify module imports that are only used in the local subpackages
# sepecify there imports in their local __init__.py

__author__ = """Willeke A'Campo"""
__email__ = "willeke.acampo@nina.com"
__version__ = "0.1.0"

import logging

from src.logger import setup_logging  # noqa
from src.utils import yaml_load  # noqa

# Import specific functions and classes
from src.utils.config import (  # noqa
    ADMIN_GDB,
    AR5_LANDUSE_PATH,
    COORD_SYSTEM,
    DATA_PATH,
    FKB_BUILDING_PATH,
    FKB_WATER_PATH,
    FOCAL_MAX_RADIUS,
    IN_SITU_TREES_GDB,
    INTERIM_PATH,
    LASER_TREES_GDB,
    MIN_HEIGHT,
    MUNICIPALITY,
    POINT_DENSITY,
    PROCESSED_PATH,
    RAW_PATH,
    RGB_AVAILABLE,
    SPATIAL_REFERENCE,
    SSB_DISTRICT_PATH,
    TOOL_PATH,
    URBAN_TREES_GDB,
    VEG_CLASSES_AVAILABLE,
)

logging.getLogger(__name__).addHandler(logging.NullHandler())
