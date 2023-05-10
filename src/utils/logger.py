"""Logging configuration"""

import logging
import datetime
import os
import sys

from src.utils.yaml_utils import yaml_load


LOGGER = logging.getLogger(__name__)


def setup_logger(logfile=False):
    """
    Setup logging configuration

    :returns: void (creates logging instance)
    """
    
    with open(r'P:\152022_itree_eco_ifront_synliggjore_trars_rolle_i_okosyst\urban-treeDetection\config.yaml', 'r') as f:
        config = yaml_load(f)
        
    
    log_level = config['logging']['level']
    log_format = config['logging']['log_format']
    date_format = config['logging']['date_format']
    date_format_os = config['logging']['date_format_os']
    file_path = config['logging']['file_path']

    
    if logfile:
        try:
            log_file_name = os.path.splitext(os.path.basename(sys.argv[0]))[0] + '_' + \
                            datetime.datetime.now().strftime(date_format_os) + '.log'
            log_file_path = os.path.join(file_path, log_file_name)
            logging.basicConfig(level=log_level, datefmt=date_format,
                                format=log_format,
                                filename=log_file_path)
        except FileNotFoundError:
            LOGGER.error(f'Failed to create log file: {log_file_name}')
            logging.basicConfig(level=log_level, datefmt=date_format,
                                format=log_format, stream=sys.stdout)
    else:
        logging.basicConfig(level=log_level, datefmt=date_format,
                            format=log_format, stream=sys.stdout)

    LOGGER.debug('Logging initialized')
    return


