from .actions import rundata_handler
from linnea_inspector.rocks_store import RSReader

import logging
logger = logging.getLogger(__name__)

import os



READER = None
FACTS_INDEX_ALGS = None

def init():
    global READER
    global FACTS_INDEX_ALGS
    app_data_paths = os.getenv('LI_STORE_PATHS', '')
    assert app_data_paths, "Environment variable LI_STORE_PATHS is not set or empty."
    
    store_paths = [path.strip() for path in app_data_paths.split(',') if path.strip()]
    try:
        READER = RSReader(store_paths)
    except Exception as e:
        raise RuntimeError(f"Failed to initialize config with data path {store_paths}: {e}")
    
    df = READER.run_configs
    # add id col
    df.insert(0, 'id', range(1, len(df) + 1))
    
    FACTS_INDEX_ALGS = rundata_handler.prepare_facts_table_algs(READER.run_configs)
    
    logger.info(f"Config initialized with data path: {store_paths}")
    
def get_reader():
    if READER is None:
        raise RuntimeError("Config not initialized. Call config.init() first.")
    return READER
