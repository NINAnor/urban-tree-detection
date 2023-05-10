import subprocess 
import logging
import os
import datetime

# you can use click or argpars command-line interface (CLI), which makes it easy to define and parse command line arguments and options. 
# no CLI used in this project

current_time = datetime.datetime.now()
formatted_time = current_time.strftime("%Y.%m.%d_%H.%M")

# print log to console if file is used as module
# create console handler and set level to info
ch_fmt = '%(name)s - %(levelname)s - %(message)s'
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(logging.Formatter(ch_fmt))

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(ch)

def main(kommune):
    """ Runs data processing scripts to turn raw data from (../raw) into
        cleaned data ready to be analyzed (saved in ../processed).
    """
    logger = logging.getLogger(__name__)
    logger.info(f'Run data processing scripts for {kommune} municipality to turn raw lidar data from (..raw/laz/all) \ninto cleaned data ready to be analyzed (saved in ...interim/lidar) to convert raw lidar files (.laz) to .las final data set from raw data')

    dir_path = os.path.dirname(os.path.realpath(__file__))
    script_path = os.path.join(dir_path, 'prepare_lidar/1_moveFile_lookUp.py')

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
    kommune = input("Enter the municipality: ")
    
    # create log file if the file is ran as stand-alone script 
    
    log_folder = os.path.join('log')
    
    if not os.path.exists(log_folder):
        os.mkdir(log_folder)
    
    log_file = os.path.join(log_folder, f'make_data_{kommune}_{formatted_time}.log')


    # create file handler and set level to info
    fh_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    fh = logging.FileHandler(log_file)
    fh.setLevel(logging.INFO)
    fh.setFormatter(logging.Formatter(fh_fmt))
    logger.addHandler(fh)

    main(kommune)

