# Linnea Inspector
# Copyright (c) 2021-2026 Aravind Sankaran
#
# SPDX-License-Identifier: AGPL-3.0-or-later
# See LICENSE file in the project root for full license information.

from metascribe.rocks_store import RocksStore
import os
import glob
import pandas as pd
from process_inspector.activity_log import ActivityLog

import logging
logger = logging.getLogger(__name__)

def get_store_path(store_root, run_config):
    try:
        language = run_config['language']
        expr = run_config['expr']
        cluster_name = run_config['cluster_name']
        aarch = run_config['aarch']
    except KeyError as e:
        raise KeyError(f"Missing expected keys in run_config: {e}")
    
    store_path = os.path.join(store_root, expr, language, cluster_name, aarch)
    return store_path

def find_store_paths(store_root):
    # find all paths in sub dir of store_root that contain run_configs.csv
    store_paths = []
    for root, dirs, files in os.walk(store_root):
        if "run_configs.csv" in files:
            store_paths.append(root)
    return store_paths 


class ExperimentWriter:

    def __init__(self, store_root, run_config,  lock_timeout=300, force_open=False):
        
        self.store_root = store_root
        
        self.run_config = run_config
        self.store_path = get_store_path(store_root, run_config)
        
        if not os.path.exists(self.store_path):
            os.makedirs(self.store_path, exist_ok=True)
        
              
        try:
            self.n_threads = self.run_config['nthreads']
            self.problem_size = self.run_config['prob_size']
            self.run_timestamp = self.run_config['timestamp']
            self.batch_id = self.run_config['batch_id']
        except KeyError as e:
            raise KeyError(f"Missing expected keys in run_config: {e}")
        
        self.lock_timeout = lock_timeout
        self.force_open = force_open
        # Following data are added
        # /case_md/n_threads/problem_size/batch_id: df, each row-- alg, iter
        # /run_config, json dump of run_config without prob_size and n_threads keys
        # /activity_log/class_name/n_threads/prob_size/batch_id/[alg]/[iter]
        

    def write_run_config(self):
        assert self.run_config is not None, "run_config must be provided to write run configuration."
        
        config_record = {f"{key}":f"{str(value)}" for key, value in self.run_config.items()}
        config_record['store_path'] = self.store_path
        # config_record['db_path'] = get_experiment_db_path(self.run_config, self.store_root, db_folder="logs")
        # config_record['algs_db_path'] = get_experiment_db_path(self.run_config, self.store_root, db_folder="algorithms")
              
        #read run_configs.csv at store_path.. create if not exists
        run_configs_path = os.path.join(self.store_path, "run_configs.csv")
        if os.path.exists(run_configs_path):
            run_configs_df = pd.read_csv(run_configs_path)
            run_configs_df = pd.concat([run_configs_df, pd.DataFrame([config_record])], ignore_index=True)
            #run_configs_df = run_configs_df.drop_duplicates().reset_index(drop=True).. does not work..
        else:
            run_configs_df = pd.DataFrame([config_record])
        
        try:
            run_configs_df.to_csv(run_configs_path, index=False)
        except Exception as e:
            raise IOError(f"Could not write run_configs.csv at {run_configs_path}: {e}")
        
    def remove_duplicate_configs(self):
        run_configs_path = os.path.join(self.store_path, "run_configs.csv")
        if os.path.exists(run_configs_path):
            df = pd.read_csv(run_configs_path).drop_duplicates().reset_index(drop=True)
            df.to_csv(run_configs_path, index=False)
        
    def write_case(self, case_md):
        assert self.run_config is not None, "run_config must be provided to write case metadata."
        
        db_path = os.path.join(self.store_path, "logs")
        
        with RocksStore(db_path, lock=True, lock_timeout=self.lock_timeout, force_open=self.force_open) as store:         
            case_md_key = f"/case_md/{self.n_threads}/{self.problem_size}/{self.batch_id}"
            store.put_df(case_md_key, case_md)
        
    def write_activity_log(self, activity_log):
        assert self.run_config is not None, "run_config must be provided to write activity log."
        
        if not activity_log.classifier_fn:
            raise ValueError("ActivityLog must have a classifier function defined.")
        
        class_name = activity_log.classifier_fn.__name__
        
        db_path = os.path.join(self.store_path, "logs")
        store = RocksStore(db_path, lock=True, lock_timeout=self.lock_timeout, force_open=self.force_open)
        
        for key, trace in activity_log.c_event_log.items():
            alg = key[0]
            iter = key[1]
            log_key = f"/activity_log/{class_name}/{self.n_threads}/{self.problem_size}/{self.batch_id}/{alg}/{iter}"
            store.put_df(log_key, trace)
            
        store.close()
            
    def write_algorithms(self):
        try:
            alg_codes_path = self.run_config['alg_codes_path']
        except KeyError as e:
            raise KeyError(f"Missing expected key 'alg_codes_path' in run_config: {e}")
        
        if not os.path.exists(alg_codes_path):
            raise FileNotFoundError(f"Algorithm codes file not found at {alg_codes_path}")
        
        alg_codes = {}
        alg_generation_steps = {}
        alg_code_files = glob.glob(os.path.join(alg_codes_path, "algorithm*"))
        alg_gen_step_files = glob.glob(os.path.join(alg_codes_path, "generation_steps", "algorithm*"))
        
        for alg_file in alg_code_files:
            alg_name = os.path.basename(alg_file).split(".")[0]
            with open(alg_file, 'r') as f:
                alg_codes[alg_name] = f.read()
                
        for gen_step_file in alg_gen_step_files:
            alg_name = os.path.basename(gen_step_file).split(".")[0]
            with open(gen_step_file, 'r') as f:
                alg_generation_steps[alg_name] = f.read()
        
        
        db_path = os.path.join(self.store_path, "algorithms")        
        with RocksStore(db_path, lock=True, lock_timeout=self.lock_timeout, force_open=self.force_open) as store:
            prob_size = self.run_config['prob_size']
            for alg_name, code in alg_codes.items():
                code_key = f"/algorithms/{prob_size}/{alg_name}"
                store.put_string(code_key, code)
                
            for alg_name, gen_steps in alg_generation_steps.items():
                gen_steps_key = f"/generation_steps/{prob_size}/{alg_name}"
                store.put_string(gen_steps_key, gen_steps)
            

class ExperimentReader:
    def __init__(self, store_paths, lock_timeout=300, force_open=False):

        run_configs = []
        for store_path in store_paths:
            run_configs_path = os.path.join(store_path, "run_configs.csv")
            if not os.path.exists(run_configs_path):
                raise FileNotFoundError(f"run_configs.csv not found at {run_configs_path}")

            df = pd.read_csv(run_configs_path)
            # df['store_path'] = store_path
            run_configs.append(df)            
        
        self.run_configs = pd.DataFrame()
        if run_configs:
            self.run_configs = pd.concat(run_configs, ignore_index=True)
        else:
            logger.warning("Run_configs is empty. No experiments available.")
                    
        # args for opening RocksStore    
        self.lock_timeout = lock_timeout
        self.force_open = force_open
        
    def get_confs(self, **conditions):
        
        if not conditions:
            return self.run_configs.to_dict(orient='records')
        
        mask = True
        df = self.run_configs
        for col, val in conditions.items():
            if isinstance( val, (list, tuple, set) ):
                mask &= df[col].isin(val)
            else:
                mask &= (df[col] == val)
        
                
        return df[mask].to_dict(orient='records')
        
    def get_case_md(self, configs, add_objs_from_config=[]):
        
        case_mds = []
        for config in configs:
            store_path = config['store_path']
            db_path = os.path.join(store_path, "logs")
        
            if not os.path.exists(db_path):
                raise FileNotFoundError(f"RocksDB not found at {db_path}")
        
            n_threads = config['nthreads']
            problem_size = config['prob_size']
            batch_id = config['batch_id']
            
            key = f"/case_md/{n_threads}/{problem_size}/{batch_id}"
        
            with RocksStore(db_path, lock=False) as store:
                case_md = store.get_df(key)
            
            if case_md.empty:
                logger.warning(f"No case metadata found for config: {config}")
                continue
            
            case_md['iter'] = f"{batch_id}." + case_md['iter'] 

            for obj in add_objs_from_config:
                try:
                    val = config[obj]
                except KeyError:
                    raise KeyError(f"Object {obj} not found in config.")    
                case_md[obj] = val
            
               
            case_mds.append(case_md)
        
        case_md_df = pd.DataFrame()
        if case_mds:
            case_md_df = pd.concat(case_mds, ignore_index=True)
            
        return case_md_df
    
    def get_activity_log(self, configs, class_name='f_call', add_objs_from_config=[]):
        
        c_event_log = {}
        language_log = {}
        
        for config in configs:
            store_path = config['store_path']
            db_path = os.path.join(store_path, "logs")
            
            if not os.path.exists(db_path):
                raise FileNotFoundError(f"RocksDB not found at {db_path}")
          
            n_threads = config['nthreads']
            problem_size = config['prob_size']
            batch_id = config['batch_id']
              
            with RocksStore(db_path, lock=False) as store:
                prefix = f"/activity_log/{class_name}/{n_threads}/{problem_size}/{batch_id}"
                rs_keys = [key for key in store._store.keys() if key.startswith(prefix)]
                for key in rs_keys:
                    parts = key.split('/')
                    alg = parts[-2]
                    iter = parts[-1]
                    df = store.get_df(key)
                    
                    iter = f"{batch_id}." + iter
                    df['iter'] = iter
                    
                    for obj in add_objs_from_config:
                        try:
                            df[obj] = config[obj]
                        except KeyError:
                            raise KeyError(f"Object {obj} not found in obj_vals.")
                    
                    trace_key = tuple(add_objs_from_config + [alg, iter])
                    c_event_log[trace_key] = df
                    activity_trace = tuple(df['el:activity'])
                    try:
                        language_log[activity_trace] += 1
                    except KeyError:
                        language_log[activity_trace] = 1
        
        if not c_event_log:
            logger.warning(f"No activity logs found for the given configurations.")
            return ActivityLog({}, {})
                    
        al = ActivityLog()
        al.restore(c_event_log, language_log)
                
        return al
    
    def get_alg_code(self, alg_name, config):
        alg_db_path = os.path.join(config['store_path'], "algorithms")
        
        if not os.path.exists(alg_db_path):
            logger.warning(f"Algorithms RocksDB not found at {alg_db_path}")
            raise FileNotFoundError(f"Algorithms RocksDB not found at {alg_db_path}")
        
        prob_size = config['prob_size']
        with RocksStore(alg_db_path, lock=False) as store:
            code_key = f"/algorithms/{prob_size}/{alg_name}"
            gen_steps_key = f"/generation_steps/{prob_size}/{alg_name}"
            try:
                alg_code = store.get_string(code_key)
                gen_steps = store.get_string(gen_steps_key)
            except KeyError:
                raise KeyError(f"Algorithm {alg_name} not found in the store at {alg_db_path}")
            
        return alg_code, gen_steps
    