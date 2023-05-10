import os
from src.utils.yaml_utils import yaml_load
from dotenv import load_dotenv

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

# Get the municipality from the environment variable or the config file
municipality = config['municipality']

# Define the configuration variables as module-level variables

# static datasets
FKB_BUILDING_PATH = config['paths']['fkb_building']
FKB_WATER_PATH = config['paths']['fkb_water']
SSB_DISTRICT_PATH = config['paths']['ssb_district']
AR5_LANDUSE_PATH = config['paths']['ar5_landuse']

# project data paths 
DATA_PATH = config['paths']['data_path']
RAW_PATH = os.path.join(DATA_PATH, municipality, 'raw')
INTERIM_PATH = os.path.join(DATA_PATH, municipality, 'interim')
PROCESSED_PATH = os.path.join(DATA_PATH, municipality, 'processed')

# path to folder containg .log files 
LOG_PATH = os.path.join(LOCAL_GIT, "src", "log")
