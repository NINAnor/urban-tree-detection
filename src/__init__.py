
"""Top-level package for treeDetection."""

__author__ = """Willeke A'Campo"""
__email__ = 'willeke.acampo@nina.com'
__version__ = '0.1.0'


# import specific functions and classes to  
# they can be imported from other parts of the projects using the syntax "from src import ..." 
from src.utils.checkExist import createGDB_ifNotExists, fieldExist, addField_ifNotExists,calculateField_ifEmpty,check_isNull
from src.utils.joinLayer import join_and_copy
from src.utils.logger import setup_logger 
from src.utils.config import FKB_BUILDING_PATH, FKB_WATER_PATH, SSB_DISTRICT_PATH, AR5_LANDUSE_PATH
from src.utils.config import DATA_PATH, RAW_PATH, INTERIM_PATH, PROCESSED_PATH
from src.utils.config import LOG_PATH

from src import prepare_lidar
#from .models import watershed_tree