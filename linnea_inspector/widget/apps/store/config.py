from linnea_inspector.store.experiment_store import ExperimentReader, find_store_paths

import logging
logger = logging.getLogger(__name__)

import os



READER = None

def init():
    global READER
    global FACTS_INDEX_ALGS
    app_data_paths = os.getenv('LI_STORE_ROOTS', '')
    assert app_data_paths, "Environment variable LI_STORE_ROOTS is not set or empty."
    
    store_roots = [path.strip() for path in app_data_paths.split(',') if path.strip()]
    try:
        store_paths = []
        for root in store_roots:
            paths = find_store_paths(root)
            if not paths:
                logger.warning(f"No valid store paths found in root: {root}")
            else:
                store_paths.extend(paths)
        if not store_paths:
            raise FileNotFoundError(f"No valid store paths found in any of the specified roots: {store_roots}") 
      
        READER = ExperimentReader(store_paths)
    except Exception as e:
        raise RuntimeError(f"Failed to initialize config with data path {store_paths}: {e}")
    
    df = READER.run_configs
    # add id col
    # df.insert(0, 'id', range(1, len(df) + 1))
      
    logger.info(f"Config initialized with data path: {store_paths}")
    
def get_reader():
    if READER is None:
        raise RuntimeError("Config not initialized. Call config.init() first.")
    return READER
