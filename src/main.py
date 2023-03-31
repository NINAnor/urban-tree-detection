from data import prepare_lidar
from models import watershed_tree
#from utils import Log

#from whitebox import control
#from whitebox import cli


## TODO add the other 4 files as subprocesses to make_data
kommune = input("Enter the municipality: ")

## PREPARE LIDAR DATA
prepare_lidar.main(kommune)

## PREPARE KOMMUNE DATA
#watershed_tree --> TODO create subproccess function
## RUN SEGMENTATION


## JOIN