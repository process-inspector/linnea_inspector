from .actions import data_handler

import logging
logger = logging.getLogger(__name__)

import os



DATA = None

def init():
    global DATA
    app_data_path = os.getenv('TVST_APP1_DATA', '/path_to_data')
    #sanity checks for existsence of path can be added here
    try:
        DATA = data_handler.prepare_data(app_data_path)
    except Exception as e:
        raise RuntimeError(f"Failed to initialize APP1 config with data path {app_data_path}: {e}")
    
    logger.info(f"APP1 config initialized with data path: {app_data_path}")
    
    