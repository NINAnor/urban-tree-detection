from src import *
#from src import join_and_copy

## TODO add the other 4 files as subprocesses to make_data
kommune = input("Enter the municipality: ")

## PREPARE LIDAR DATA
prepare_lidar.main(kommune)

## PREPARE KOMMUNE DATA
# check if filgdb exists with layers and fieldnames
# manualy prepare in arcgis 


## RUN SEGMENTATION AND MERGE
#watershed_tree --> TODO create subproccess function
## MASK BUILDINGS AND SEA AND ADD LIDAR ATTR.
#watershed_tree --> TODO create subproccess function

## JOIN