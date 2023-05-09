import os
import logging
from datetime import datetime

def configure_logger(log_file=None, set_level=logging.DEBUG):
    """ 
    Configures a console logger or a file logger if to path to  the logfile is given. 


    Args:
        log_file (str, optional): path to log_file. Defaults to None.
        
        set_level (logging.level, optional): logging.level . Defaults to logging.DEBUG.

    Returns:
        logging.Logger: logger object
    """

    # Create logger object and set its level
    logger = logging.getLogger()
    logger.setLevel(set_level)
    
    # Remove all existing handlers from the logger
    for handler in logger.handlers:
        logger.removeHandler(handler)

    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Create console handler and set its level
    console_handler = logging.StreamHandler()
    console_handler.setLevel(set_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    logger.info("Logger is configured.")
    
    # Create file handler if log file is specified
    if log_file:
        try:
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(set_level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
            logger.info(f"Logfile '{log_file}' is created.")
        except FileNotFoundError:
            logger.error(f"Failed to create log file '{log_file}")
        
    return logger


if __name__ == '__main__':
    # ask for path to log folder
    log_folder = input("Enter path to log folder: ")
    
    # format log file name 
    formatted_time = datetime.now().strftime("%Y.%m.%d_%H.%M")
    log_file = os.path.join(log_folder, f"log_{formatted_time}.log")

    # init file handler logger 
    logger = configure_logger(log_file=log_file)

    # init console_logger 
    # logger = configure_logger(set_level=logging.INFO)