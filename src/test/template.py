# -*- coding: utf-8 -*-
# --------------------------------------------------------------------------- #
# Name: template.py
# Date: 2023-07-27
# Description:
# Author: Willeke A'Campo
# Dependencies:
# --------------------------------------------------------------------------- #

import logging

from src import *

# --------------------------------------------------------------------------- #
# FUNCTIONS
# --------------------------------------------------------------------------- #


def main():
    logger.info("Starting main()")

    logger.info("Finished main()")


if __name__ == "__main__":
    # setup logger
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

    main()
