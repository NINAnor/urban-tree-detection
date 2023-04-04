from src import *
#from src import join_and_copy

## TODO add the other 4 files as subprocesses to make_data
kommune = input("Enter the municipality: ")

## PREPARE LIDAR DATA
prepare_lidar.main(kommune)

## PREPARE KOMMUNE DATA
#watershed_tree --> TODO create subproccess function


## RUN SEGMENTATION


## JOIN