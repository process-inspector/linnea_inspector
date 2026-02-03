import os
import pandas as pd

import logging
logger = logging.getLogger(__name__)

def get_experiment_db_path(run_config, store_path, db_folder):
    try:
        language = run_config['language']
        expr = run_config['expr']
        cluster_name = run_config['cluster_name']
        aarch = run_config['aarch']
    except KeyError as e:
        raise KeyError(f"Missing expected keys in run_config: {e}")
    
    db_path = os.path.join(store_path, language, expr, cluster_name, aarch, db_folder)
    return db_path

def delete_experiment(run_config):
    store_path = run_config['store_path']
    
    run_configs_path = os.path.join(store_path, "run_configs.csv")
    if not os.path.exists(run_configs_path):
        logger.warning(f"run_configs.csv not found at {run_configs_path}. Nothing to delete.")
        return
    
    try:
        n_threads = run_config['n_threads']
        problem_size = run_config['prob_size']
        batch_id = run_config['batch_id']
    except KeyError as e:
        raise KeyError(f"Missing expected keys in run_config: {e}")
    
    #1) delete case_md and activity_log from RocksDB
    db_path = get_experiment_db_path(run_config, store_path, db_folder="logs")
    with RocksStore(db_path, lock=True, lock_timeout=300) as store:
        case_md_key = f"/case_md/{n_threads}/{problem_size}/{batch_id}"
        try:
            del store._store[case_md_key]
        except KeyError:
            logger.warning(f"Case metadata key {case_md_key} not found in the store at {db_path}")
        
        class_name = 'f_call'  # assuming f_call as default classifier
        prefix = f"/activity_log/{class_name}/{n_threads}/{problem_size}/{batch_id}/"
        keys_to_delete = [key for key in store._store.keys() if key.startswith(prefix)]
        for key in keys_to_delete:
            try:
                del store._store[key]
            except KeyError:
                logger.warning(f"Activity log key {key} not found in the store at {db_path}")
    
    
    #2) delete entry from run_configs.csv
    df = pd.read_csv(run_configs_path)
    
    mask = True
    for key, value in run_config.items():
        if key not in ['store_path', 'db_path', 'algs_db_path', 'niter']:
            mask &= (df[key] == value)
    
    df = df[~mask].reset_index(drop=True)
    
    df.to_csv(run_configs_path, index=False)
    
    
    #3) If no other case for exp and prob size exists.. delete alg codes too.
    
    #4) if no algs, delete synthesis.. otherwise, update synthesis..
    
def update_synthesis(run_config):
    pass