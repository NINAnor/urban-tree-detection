
"""Top-level package for treeDetection."""

__author__ = """Willeke A'Campo"""
__email__ = 'willeke.acampo@nina.com'
__version__ = '0.1.0'


# import specific functions and classes to  
# they can be imported from other parts of the projects using the syntax "from src import ..." 
from src.utils.checkExist import createGDB_ifNotExists
from src.utils.checkExist import fieldExist
from src.utils.checkExist import addField_ifNotExists
from src.utils.checkExist import calculateField_ifEmpty
from src.utils.checkExist import check_isNull
from src.utils.joinLayer import join_and_copy
from src.utils.logger import configure_logger 

from src.data import prepare_lidar
#from .models import watershed_tree