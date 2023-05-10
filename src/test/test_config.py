import logging 

# local packages
from src import setup_logger 
from src.utils.config import FKB_BUILDING_PATH, FKB_WATER_PATH, SSB_DISTRICT_PATH, AR5_LANDUSE_PATH
from src import DATA_PATH, RAW_PATH, INTERIM_PATH, PROCESSED_PATH
from src import LOG_PATH


# Test the configuration variables in your code
print(f"FKB_BUILDING_PATH: {FKB_BUILDING_PATH} \n",
      f"FKB_WATER_PATH: {FKB_WATER_PATH} \n", 
      f"SSB_DISTRICT_PATH: {SSB_DISTRICT_PATH} \n",
      f"AR5_LANDUSE_PATH: {SSB_DISTRICT_PATH} \n",
      f"DATA_PATH: {DATA_PATH} \n",
      f"RAW_PATH: {RAW_PATH} \n",
      f"INTERIM_PATH: {INTERIM_PATH} \n",
      f"PROCESSED_PATH: {PROCESSED_PATH} \n",
      f"LOG_PATH: {LOG_PATH} \n")
      
      
# configure logger
setup_logger(logfile=False)



logging.debug('Debug message')
logging.info('Info message')
logging.warning('Warning message')
logging.error('Error message')
logging.critical('Critical message')