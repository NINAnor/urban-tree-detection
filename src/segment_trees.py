#  TODO 
# 1. watershed segmentation 
# 2. mask 
# 3. add laser attributes

import logging
import os

# local modules
from src import *  # Assuming there's a logger.py module in the src directory

# set up logger
#logger.setup_logger(logfile=True)

def main():
    
    logger.info("Start main script")

    # Your main code goes here

    logger.info("End main script")

if __name__ == '__main__':
    
    logger.setup_logger(logfile=True)
    logger = logging.getLogger(__name__)
    
    # check municipality
    confirm_municipality = input(f"Is '{MUNICIPALITY}' the correct municipality? (y/n): ").strip().lower()
    if confirm_municipality != 'y':
        logger.info("User disagreed with the municipality.")
        exit()
    
