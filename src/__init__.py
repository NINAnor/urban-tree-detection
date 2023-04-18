
"""Top-level package for treeDetection."""

__author__ = """Willeke A'Campo"""
__email__ = 'willeke.acampo@nina.com'
__version__ = '0.1.0'


# import specific functions and classes to  
# they can be imported from other parts of the projects using the syntax "from src import ..." 
from .utils.checkExist import createGDB_ifNotExists
from .utils.checkExist import fieldExist
from .utils.checkExist import addField_ifNotExists
from .utils.checkExist import calculateField_ifEmpty
from .utils.checkExist import check_isNull
from .utils.joinLayer import join_and_copy

from .data import prepare_lidar
#from .models import watershed_tree