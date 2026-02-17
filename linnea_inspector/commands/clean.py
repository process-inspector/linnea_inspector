import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

import os
import pandas as pd
import fnmatch

from linnea_inspector.store.config_manager import ConfigManager
# from linnea_inspector.store.synthesis_store import SynthesisReader
from metascribe.rocks_store import RocksStore

from linnea_inspector.store.utils import delete_experiment

def add_parser(subparsers):
    p = subparsers.add_parser("clean",
                              usage="linnea-inspector clean --store_dir <dir>", 
                              help="Clean up data from failed runs.")
    p.add_argument("--store_dir", required=True, help="Path to the store containing the run_configs.csv file")
    p.add_argument("--object", required=False, default="alg", help="Synthesis object. Possible values [alg,]")
    #add boolean arg --delete_experiment default false
    p.add_argument("--experiment", action='store_true', help="Whether to delete the entire experiment from the store if any key is missing. If false, only the synthesis context and stats for the missing keys will be deleted.") 
    
def sanity_check_and_config(args):
    store_dir = args.store_dir
    assert os.path.exists(os.path.join(store_dir, "synthesis")), f"Store directory {store_dir} does not exists or does not contain synthesis."
    
    run_configs_path = os.path.join(store_dir, "run_configs.csv")
    assert os.path.exists(run_configs_path), f"Run configuration file {run_configs_path} does not exist in store directory."

    assert args.object in ["alg",], f"Invalid object {args.object}. Currently only alg is supported."

    config_manager = ConfigManager(store_dir)
    
    return config_manager


def get_store_keys_from_configs_algs(df):
    df["rs_key"] = df.apply(lambda row: f"{row['language']}/{row['expr']}/{row['cluster_name']}/{row['arch']}/{row['precision']}/{row['nthreads']}/{row['prob_size']}", axis=1)
    config_keys = set(df["rs_key"].tolist())
    return config_keys


def get_config_from_store_key_algs(key, start):
    config = {}
    parts = key.split("/")
    config["language"] = parts[start]
    config["expr"] = parts[start+1]
    config["cluster_name"] = parts[start+2]
    config["arch"] = parts[start+3]
    config["precision"] = parts[start+4]
    config["nthreads"] = parts[start+5]
    config["prob_size"] = parts[start+6]
    
    pk = [config["language"], config["expr"], config["cluster_name"], config["arch"], config["precision"], config["nthreads"], config["prob_size"]]
    pk = "/".join(pk)
    
    return config, pk

def update_conf_df(df, col, value, where):
    mask = pd.Series(True, index=df.index)
    try:
        for key, cond_value in where.items():
            mask &= (df[key] == str(cond_value))
            
        df.loc[mask, col] = value
    except KeyError as e:
        raise KeyError(f"One or more condition keys not found in configs: {e}")
    
def clean_synthesis_store(config_manager, args):
    synthesis_db_path = os.path.join(args.store_dir, "synthesis")
    
    logger.info(f"Opening synthesis store at {synthesis_db_path} to retrieve context and stats keys.")
    with RocksStore(synthesis_db_path, lock=False) as store:
        context_pattern = "/contexts/**/activity"
        stats_pattern = "/stats/*"
        context_keys = {}
        stats_keys = {}
        for key in store._store.keys():
            if fnmatch.fnmatch(key, context_pattern):
                conf, pk = get_config_from_store_key_algs(key, start=3)
                context_keys[pk] = {
                    "store_key": key,
                    "config": conf
                }
            elif fnmatch.fnmatch(key, stats_pattern):
                conf, pk = get_config_from_store_key_algs(key, start=2)
                stats_keys[pk] = {
                    "store_key": key,
                    "config": conf
                }
    
    df = config_manager.get_all_configs()
    df['OK'] = False         
    
    for key in stats_keys:
        confs = config_manager.get_configs(**stats_keys[key]["config"])
        if not confs:
            logger.warning(f"[!STORE.SYNTHESIS] {key} has stats but no matching config in run_configs.csv")
            with RocksStore(synthesis_db_path, lock=True, lock_timeout=300) as store:
                if context_keys[key]["store_key"] in store._store:
                    logger.warning(f"Deleting context key {context_keys[key]['store_key']} from synthesis store.")
                    del store._store[context_keys[key]["store_key"]]
            
                if stats_keys[key]["store_key"] in store._store:
                    logger.warning(f"Deleting stats key {stats_keys[key]['store_key']} from synthesis store.")
                    del store._store[stats_keys[key]["store_key"]]
        else:
            logger.info(f"[OK] {key}")
            update_conf_df(df, col='OK', value=True, where=stats_keys[key]["config"])
            
    # remove records from config csv for which synthesis context or stats is missing in the store
    dead_confs = df[df['OK'] == False].to_dict(orient='records')
    for conf in dead_confs:
        _conf = {k: conf[k] for k in config_manager.primary_keys}
        logger.warning(f"[!CONFIG.CSV] Deleting config from run_configs.csv as matching synthesis context or stats is missing in the store.")
        config_manager.delete(**_conf)
        
    logger.info("[COMPLETE] Synthesis store cleanup completed.")
            
                
def clean_experiment_store(config_manager, args):
    logs_db_path = os.path.join(args.store_dir, "logs")
    
    df = config_manager.get_all_configs()
    
    config = {}
    config["language"] = df['language'].iloc[0]
    config["expr"] = df['expr'].iloc[0]
    config["cluster_name"] = df['cluster_name'].iloc[0]
    config["arch"] = df['arch'].iloc[0]
    config["precision"] = df['precision'].iloc[0]
    
    
    with RocksStore(logs_db_path, lock=False) as store:
        case_pattern = "/case_md/**"
        al_keys_to_delete = []
        for key in store._store.keys():
            if fnmatch.fnmatch(key, case_pattern):
                parts = key.split("/")
                # prepare conf..
                conf = config.copy()
                conf["nthreads"] = parts[2]
                conf["prob_size"] = parts[3]
                conf["batch_id"] = parts[4]
                # check if retrievalble from config_manager... if not, delete from store (also al)
                _confs = config_manager.get_configs(**conf)
                if not _confs:
                    del store._store[key]
                    logger.warning(f"[!STORE.EXPERIMENT] {key} has no matching config in run_configs.csv. Deleting case.")
                                        
                    al_keys_to_delete.append(f"/{conf['nthreads']}/{conf['prob_size']}/{conf['batch_id']}/")
                    
                else:
                    logger.info(f"[OK]  experiment: {key}")
        if al_keys_to_delete:       
            for key in store._store.keys():
                if fnmatch.fnmatch(key, f"/activity_log/*"):
                    for al_key in al_keys_to_delete:
                        if al_key in key:
                            del store._store[key]
                            logger.warning(f"[!STORE.EXPERIMENT] Deleting activity log key for exp {key}.")
    
    
        # do not delete configs that do not have exp. It is possible that synthesis is available.
        logger.info("[COMPLETE] Experiment store cleanup completed.")
        
def clean(args):
    
    try:
        config_manager = sanity_check_and_config(args)
    except Exception as e:
        logger.error(f"Sanity check failed: {e}")
        return
    
    delete_experiment = args.experiment
    
    if not delete_experiment:
        clean_synthesis_store(config_manager, args)
    else:
        clean_experiment_store(config_manager, args)
    
    
    
    
        

    

