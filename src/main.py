import logging

from src import *
import prepare_lidar
import segment_trees


# set up logger
logger.setup_logger(logfile=True)
logger = logging.getLogger(__name__)

# check municipality
confirm_municipality = (
    input(f"Is '{MUNICIPALITY}' the correct municipality? (y/n): ")
    .strip()
    .lower()
)
if confirm_municipality != "y":
    logger.info("User disagreed with the municipality.")
    exit()

# run scripts
# TODO add subroutines
prepare_lidar.main(MUNICIPALITY)
# create main()
segment_trees.main()
