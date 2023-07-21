import os
from src.utils import yaml_load
from dotenv import load_dotenv

# --------------------------------------------------------------------------- #
# Load YAML dictionairy 
# --------------------------------------------------------------------------- #

# for .env file in USER directory 
# user_dir = C:\\USERS\\<<firstname.lastname>>
user_dir = os.path.join(os.path.expanduser("~"))
dotenv_path = os.path.join(user_dir, 'trekroner.env')
load_dotenv(dotenv_path)

# path to yaml project configuration file 
LOCAL_GIT = os.getenv('LOCAL_GIT')  
config_file = os.path.join(LOCAL_GIT, "NINAnor", "urban-treeDetection", "config.yaml")

with open(config_file, 'r') as f:
    config = yaml_load(f)

# --------------------------------------------------------------------------- #
# Global path variables
# --------------------------------------------------------------------------- #

# get municipality (kommune) 
MUNICIPALITY = config['municipality']

# get path to log folder 
LOG_PATH = os.path.join(LOCAL_GIT, "src", "log")

# get static datasets
FKB_BUILDING_PATH = config['paths']['fkb_building']
FKB_WATER_PATH = config['paths']['fkb_water']
SSB_DISTRICT_PATH = config['paths']['ssb_district']
AR5_LANDUSE_PATH = config['paths']['ar5_landuse']

# get project data paths 
DATA_PATH = config['paths']['data_path']
TOOL_PATH = config['paths']['tool_path']
RAW_PATH = os.path.join(DATA_PATH, MUNICIPALITY, 'raw')
INTERIM_PATH = os.path.join(DATA_PATH, MUNICIPALITY, 'interim')
PROCESSED_PATH = os.path.join(DATA_PATH, MUNICIPALITY, 'processed')

# project file gdbs
ADMIN_GDB = os.path.join(INTERIM_PATH, f"{MUNICIPALITY}_admin.gdb")
IN_SITU_TREES_GDB = os.path.join(INTERIM_PATH, MUNICIPALITY + "_in_situ_trees.gdb") # municipal tree dataset (stem points)
LASER_TREES_GDB = os.path.join(INTERIM_PATH, MUNICIPALITY + "_laser_trees.gdb") # segmented laser tree dataset (tree top points, tree crown polygons)
URBAN_TREES_GDB = os.path.join(PROCESSED_PATH, MUNICIPALITY + "_urban_trees.gdb") # joined tree dataset (input for itree eco)

# --------------------------------------------------------------------------- #
# Set spatial reference system
# --------------------------------------------------------------------------- #
if MUNICIPALITY == "oslo" or "baerum" or "kristiansand":
    SPATIAL_REFERENCE = config['spatial_reference']['utm32']

if MUNICIPALITY == "bodo" :
    SPATIAL_REFERENCE = config['spatial_reference']['utm33']