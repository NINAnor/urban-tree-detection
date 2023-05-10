import logging 

# local packages
from src import setup_logger 
from src import FKB_BUILDING_PATH, FKB_WATER_PATH, SSB_DISTRICT_PATH, AR5_LANDUSE_PATH
from src import DATA_PATH, RAW_PATH, INTERIM_PATH, PROCESSED_PATH
from src import LOG_PATH


# configure logger
setup_logger(logfile=True)
logging.info('TEST PROJECT CONFIGURATION')
logging.info('TEST logger setup')
logging.debug('Debug message')
logging.info('Info message')
logging.warning('Warning message')
logging.error('Error message')
logging.critical('Critical message')


# Test the configuration variables in your code
logging.info('TEST project variables')
print(f" FKB_BUILDING_PATH: \t{FKB_BUILDING_PATH} \n",
      f"FKB_WATER_PATH: \t{FKB_WATER_PATH} \n", 
      f"SSB_DISTRICT_PATH: \t{SSB_DISTRICT_PATH} \n",
      f"AR5_LANDUSE_PATH: \t{SSB_DISTRICT_PATH} \n",
      f"DATA_PATH: \t{DATA_PATH} \n",
      f"RAW_PATH: \t{RAW_PATH} \n",
      f"INTERIM_PATH: \t{INTERIM_PATH} \n",
      f"PROCESSED_PATH: \t{PROCESSED_PATH} \n",
      f"LOG_PATH: \t{LOG_PATH} \n")
      