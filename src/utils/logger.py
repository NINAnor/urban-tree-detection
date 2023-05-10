"""Logging configuration"""

import logging
import datetime
import os
import sys

from src.utils.yaml_utils import yaml_load
from dotenv import load_dotenv

# for .env file in USER directory 
# user_dir = C:\\USERS\\<<firstname.lastname>>
user_dir = os.path.join(os.path.expanduser("~"))
dotenv_path = os.path.join(user_dir, 'trekroner.env')
load_dotenv(dotenv_path)

# path to yaml project configuration file 
LOCAL_GIT = os.getenv('LOCAL_GIT')  
config_file = os.path.join(LOCAL_GIT, "NINAnor", "urban-treeDetection", "config.yaml")


LOGGER = logging.getLogger(__name__)

def setup_logger(logfile=False):
    """
    Setup logging configuration

    :returns: void (creates logging instance)
    """
    
    with open(config_file, 'r') as f:
        config = yaml_load(f)
        log_level = config['logging']['level']
        log_format = config['logging']['log_format']
        date_format = config['logging']['date_format']
        date_format_os = config['logging']['date_format_os']
        file_path = config['logging']['file_path']


    # Remove all existing handlers from the logger
    for handler in LOGGER.handlers:
        LOGGER.removeHandler(handler)
    
    if logfile:
        try:
            log_file_name = datetime.datetime.now().strftime(date_format_os) + '_' + \
                            os.path.splitext(os.path.basename(sys.argv[0]))[0] + '.log'
            log_file_path = os.path.join(file_path, log_file_name)
            # set file handler 
            logging.basicConfig(level=log_level, datefmt=date_format,
                                format=log_format,
                                filename=log_file_path)
            
            # Add console handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(log_level)
            console_handler.setFormatter(logging.Formatter(log_format))
            LOGGER.addHandler(console_handler)
        except FileNotFoundError:
            LOGGER.error(f'Failed to create log file: {log_file_name}')
            # set consoler handler
            logging.basicConfig(level=log_level, datefmt=date_format,
                                format=log_format, stream=sys.stdout)
    else:
        # set consoler handler
        logging.basicConfig(level=log_level, datefmt=date_format,
                            format=log_format, stream=sys.stdout)
    LOGGER.setLevel(log_level)
    LOGGER.debug('Logging initialized')
    return


