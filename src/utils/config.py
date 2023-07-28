import os
from src.utils import yaml_load
from dotenv import load_dotenv

# --------------------------------------------------------------------------- #
# Load YAML dictionairy
# --------------------------------------------------------------------------- #

# for .env file in USER directory
# user_dir = C:\\USERS\\<<firstname.lastname>>
user_dir = os.path.join(os.path.expanduser("~"))
dotenv_path = os.path.join(user_dir, "trekroner.env")
load_dotenv(dotenv_path)

# path to yaml project configuration file
LOCAL_GIT = os.getenv("LOCAL_GIT")
config_file = os.path.join(
    LOCAL_GIT, "NINAnor", "urban-treeDetection", "config.yaml"
)

with open(config_file, "r") as f:
    config = yaml_load(f)

# --------------------------------------------------------------------------- #
# Global path variables
# --------------------------------------------------------------------------- #

# get municipality (kommune)
MUNICIPALITY = config["municipality"]

# get path to log folder
LOG_PATH = os.path.join(LOCAL_GIT, "src", "log")

# get static datasets
FKB_BUILDING_PATH = config["paths"]["fkb_building"]
FKB_WATER_PATH = config["paths"]["fkb_water"]
SSB_DISTRICT_PATH = config["paths"]["ssb_district"]
AR5_LANDUSE_PATH = config["paths"]["ar5_landuse"]

# get project data paths
DATA_PATH = config["paths"]["data_path"]
TOOL_PATH = config["paths"]["tool_path"]
RAW_PATH = os.path.join(DATA_PATH, MUNICIPALITY, "urban-treeDetection", "raw")
INTERIM_PATH = os.path.join(
    DATA_PATH, MUNICIPALITY, "urban-treeDetection", "interim"
)
PROCESSED_PATH = os.path.join(
    DATA_PATH, MUNICIPALITY, "urban-treeDetection", "processed"
)

# project file gdbs
ADMIN_GDB = os.path.join(INTERIM_PATH, f"{MUNICIPALITY}_admin.gdb")
IN_SITU_TREES_GDB = os.path.join(
    INTERIM_PATH, MUNICIPALITY + "_in_situ_trees.gdb"
)  # municipal tree dataset (stem points)
LASER_TREES_GDB = os.path.join(
    INTERIM_PATH, MUNICIPALITY + "_laser_trees.gdb"
)  # segmented laser tree dataset (tree top points, tree crown polygons)
URBAN_TREES_GDB = os.path.join(
    PROCESSED_PATH, MUNICIPALITY + "_urban_trees.gdb"
)  # joined tree dataset (input for itree eco)

# --------------------------------------------------------------------------- #
# Tree segmentation configuration
# --------------------------------------------------------------------------- #
if MUNICIPALITY.lower() == "oslo" or "baerum":
    SPATIAL_REFERENCE = config["spatial_reference"]["utm32"]
    COORD_SYSTEM = 'PROJCS["ETRS_1989_UTM_Zone_32N",\
            GEOGCS["GCS_ETRS_1989",DATUM["D_ETRS_1989",SPHEROID["GRS_1980",6378137.0,298.257222101]],\
            PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],\
            PROJECTION["Transverse_Mercator"],\
            PARAMETER["False_Easting",500000.0],PARAMETER["False_Northing",0.0],PARAMETER["Central_Meridian",9.0],\
            PARAMETER["Scale_Factor",0.9996],PARAMETER["Latitude_Of_Origin",0.0],UNIT["Meter",1.0]]'
    RGB_AVAILABLE = True
    VEG_CLASSES_AVAILABLE = True
    POINT_DENSITY = 10
    MIN_HEIGHT = 2.5
    FOCAL_MAX_RADIUS = 1.5
if MUNICIPALITY.lower() == "kristiansand":
    SPATIAL_REFERENCE = config["spatial_reference"]["utm32"]
    COORD_SYSTEM = 'PROJCS["ETRS_1989_UTM_Zone_32N",\
        GEOGCS["GCS_ETRS_1989",DATUM["D_ETRS_1989",SPHEROID["GRS_1980",6378137.0,298.257222101]],\
        PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],\
        PROJECTION["Transverse_Mercator"],\
        PARAMETER["False_Easting",500000.0],PARAMETER["False_Northing",0.0],PARAMETER["Central_Meridian",9.0],\
        PARAMETER["Scale_Factor",0.9996],PARAMETER["Latitude_Of_Origin",0.0],UNIT["Meter",1.0]]'
    RGB_AVAILABLE = False
    VEG_CLASSES_AVAILABLE = False
    POINT_DENSITY = 5
    MIN_HEIGHT = 2.5
    FOCAL_MAX_RADIUS = 1.5  # specifically tested for Bærum, r= 1.5 gives most realistic results
if MUNICIPALITY.lower() == "bodo":
    # Bærum specific configurations
    SPATIAL_REFERENCE = config["spatial_reference"]["utm33"]
    RGB_AVAILABLE = False
    VEG_CLASSES_AVAILABLE = False
    POINT_DENSITY = 2
    MIN_HEIGHT = 2
    FOCAL_MAX_RADIUS = 1  # 1.5 makes trees too big!

# TODO add focal_mean_radius to config.yaml (1.5 bodo, 1 kristiansand)
# test
