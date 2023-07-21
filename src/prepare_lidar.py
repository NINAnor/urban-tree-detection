import subprocess 
import logging
import os

# local modules
from src import *


def main(kommune):
    """ Runs data processing scripts to turn raw data from (../raw) into
        cleaned data ready to be analyzed (saved in ../processed).
    """

    logger.info(f'Run data processing scripts for {kommune} municipality to turn raw lidar data from (..raw/laz/all) \ninto cleaned data ready to be analyzed (saved in ...interim/lidar) to convert raw lidar files (.laz) to .las final data set from raw data')

    dir_path = os.path.dirname(os.path.realpath(__file__))
    script_path = os.path.join(dir_path, 'data/prepare_lidar/1_moveFile_lookUp.py')

    ## TODO add the other 4 files as subprocesses!
    try:
        # subprocess - moveFile
        command = ['python', script_path, kommune]
        output = subprocess.run(command, check=True, capture_output=True, text=True)
        logger.info(f"Subprocess stdout:\n{output.stdout}")

    except subprocess.CalledProcessError as e:
        script_name = os.path.basename(script_path)
        #logger.error(f"An error occured: {str(e)}")
        logger.error(f"An error occured in the script {script_name}.")
        logger.error(f"Subprocess stderr:\n{e.stderr}")
        
if __name__ == '__main__':
    # setup logger
    logger.setup_logger(logfile=True)
    logger = logging.getLogger(__name__)
    
    # check municipality
    confirm_municipality = input(f"Is '{MUNICIPALITY}' the correct municipality? (y/n): ").strip().lower()
    if confirm_municipality != 'y':
        logger.info("User disagreed with the municipality.")
        exit()

    main(MUNICIPALITY)

