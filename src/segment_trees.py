#  TODO 
# 1. watershed segmentation 
# 2. mask 
# 3. add laser attributes

import logging
import os
import subprocess
# local modules
from src import *  # Assuming there's a logger.py module in the src directory

# set up logger
#logger.setup_logger(logfile=True)

def run_model_chm():
    
    logger.info("Start main script")
     

    dir_path = os.path.dirname(os.path.realpath(__file__))
    script_path = os.path.join(dir_path, "segmentation", "model_chm.py")    
    
    try:
        command = ['python', script_path]
        subprocess.run(command, check=True, capture_output=True, text=True)

    except subprocess.CalledProcessError as e:
        script_name = os.path.basename(script_path)
        #logger.error(f"An error occured: {str(e)}")
        logger.error(f"An error occured in the script {script_name}.")
        logger.error(f"Subprocess stderr:\n{e.stderr}")    

    logger.info("End main script")

if __name__ == '__main__':
    
    # setup logger
    logger.setup_logger(logfile=False)
    logger = logging.getLogger(__name__)
    
    # check municipality
    confirm_municipality = input(f"Is '{MUNICIPALITY}' the correct municipality? (y/n): ").strip().lower()
    if confirm_municipality != 'y':
        logger.info("User disagreed with the municipality.")
        exit()
    
    run_model_chm()
