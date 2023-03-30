from data import prepare_lidar
#from utils import Log

#from whitebox import control
#from whitebox import cli


## TODO add the other 4 files as subprocesses to make_data
kommune = input("Enter the municipality: ")
prepare_lidar.main(kommune)