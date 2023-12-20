import logging

from src import *
from src.logger import setup_custom_logging, setup_logging  # noqa

# set up logger
setup_custom_logging()
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
# prepare_lidar.main(MUNICIPALITY)
# create main()
# segment_trees.main()

logger.info("Done.")
