# Linnea Inspector
#
# Copyright (c) 2021-2025, High-Performance and Automatic Computing group
# at RWTH Aachen University and Umeå University.
# All rights reserved.
#
# Licensed under the BSD 3-Clause License.
# See LICENSE file in the project root for full license information.
#
# Contributors:
# - Aravind Sankaran


from metascribe.rocks_store import RocksStore
import os
import pandas as pd
from process_inspector.activity_log import ActivityLog

def get_db_path(run_config, store_path):
    try:
        language = run_config['language']
        expr = run_config['expr']
        cluster_name = run_config['cluster_name']
        aarch = run_config['aarch']
    except KeyError as e:
        raise KeyError(f"Missing expected keys in run_config: {e}")
    
    db_path = os.path.join(store_path, language, expr, cluster_name, aarch, 'inspector.rs')
    return db_path


class RSWriter(RocksStore):

    def __init__(self, run_config, store_path, lock_timeout=300, force_open=False):
        
        self.store_path = store_path
        db_path = get_db_path(run_config, store_path)
        self.run_config = run_config
               
        super().__init__(db_path, lock=True, lock_timeout=lock_timeout, force_open=force_open)
        
        try:
            self.n_threads = self.run_config['nthreads']
            self.problem_size = self.run_config['prob_size']
            self.run_timestamp = self.run_config['timestamp']
            self.batch_id = self.run_config['batch_id']
        except KeyError as e:
            raise KeyError(f"Missing expected keys in run_config: {e}")
        
        # Following data are added
        # /case_md/n_threads/problem_size/batch_id: df, each row-- alg, iter
        # /run_config, json dump of run_config without prob_size and n_threads keys
        # /activity_log/class_name/n_threads/prob_size/batch_id/[alg]/[iter]
        

    def write_run_config(self):
        
        config_record = {f"{key}":f"{str(value)}" for key, value in self.run_config.items()}
        config_record['db_path'] = self.db_path
              
        #read run_configs.csv at store_path.. create if not exists
        run_configs_path = os.path.join(self.store_path, "run_configs.csv")
        if os.path.exists(run_configs_path):
            run_configs_df = pd.read_csv(run_configs_path)
            run_configs_df = pd.concat([run_configs_df, pd.DataFrame([config_record])], ignore_index=True)
        else:
            run_configs_df = pd.DataFrame([config_record])
        
        try:
            run_configs_df.to_csv(run_configs_path, index=False)
        except Exception as e:
            raise IOError(f"Could not write run_configs.csv at {run_configs_path}: {e}")
        
        config_key = "/run_config"
        self.put_json(config_key, self.run_config)
        
    def remove_duplicate_configs(self):
        run_configs_path = os.path.join(self.store_path, "run_configs.csv")
        if os.path.exists(run_configs_path):
            df = pd.read_csv(run_configs_path).drop_duplicates().reset_index(drop=True)
            df.to_csv(run_configs_path, index=False)
        
    def write_case(self, case_md):       
        case_md_key = f"/case_md/{self.n_threads}/{self.problem_size}/{self.batch_id}"
        self.put_df(case_md_key, case_md)
        
    def write_activity_log(self, activity_log):
        if not activity_log.classifier_fn:
            raise ValueError("ActivityLog must have a classifier function defined.")
        
        class_name = activity_log.classifier_fn.__name__
        
        for key, trace in activity_log.c_event_log.items():
            alg = key[0]
            iter = key[1]
            log_key = f"/activity_log/{class_name}/{self.n_threads}/{self.problem_size}/{self.batch_id}/{alg}/{iter}"
            self.put_df(log_key, trace)
        
        
class RSReader:
    def __init__(self, store_path, lock_timeout=300, force_open=False):
        self.store_path = store_path
        self.lock_timeout = lock_timeout
        self.force_open = force_open
        
        run_configs_path = os.path.join(self.store_path, "run_configs.csv")
        if not os.path.exists(run_configs_path):
            raise FileNotFoundError(f"run_configs.csv not found at {run_configs_path}")
        
        self.run_configs = pd.read_csv(run_configs_path)
        
    def get_confs(self, **conditions):
        mask = True
        df = self.run_configs
        for col, val in conditions.items():
            if isinstance( val, (list, tuple, set) ):
                mask &= df[col].isin(val)
            else:
                mask &= (df[col] == val)
                
        return df[mask].to_dict(orient='records')
        
    def get_case_md(self, config):
        
        db_path = get_db_path(config, self.store_path)
        
        if not os.path.exists(db_path):
            raise FileNotFoundError(f"RocksDB not found at {db_path}")
        
        n_threads = config['nthreads']
        problem_size = config['prob_size']
        batch_id = config['batch_id']
        key = f"/case_md/{n_threads}/{problem_size}/{batch_id}"
        
        with RocksStore(db_path, lock=False, lock_timeout=self.lock_timeout, force_open=self.force_open) as store:
            case_md = store.get_df(key)
            
        return case_md
    
    def get_activity_log(self, config, class_name='f_call'):
        db_path = get_db_path(config, self.store_path)
        
        if not os.path.exists(db_path):
            raise FileNotFoundError(f"RocksDB not found at {db_path}")
        
        n_threads = config['nthreads']
        problem_size = config['prob_size']
        batch_id = config['batch_id']
        
        c_event_log = {}
        language_log = {}
        
        with RocksStore(db_path, lock=False, lock_timeout=self.lock_timeout, force_open=self.force_open) as store:
            prefix = f"/activity_log/{class_name}/{n_threads}/{problem_size}/{batch_id}"
            keys = [key for key in store._store.keys() if key.startswith(prefix)]
            for key in keys:
                parts = key.split('/')
                alg = parts[-2]
                iter = parts[-1]
                df = store.get_df(key)
                c_event_log[(alg, iter)] = df
                activity_trace = tuple(df['el:activity'])
                try:
                    language_log[activity_trace] += 1
                except KeyError:
                    language_log[activity_trace] = 1
                    
        al = ActivityLog()
        al.restore(c_event_log, language_log)
                
        return al
    
    
            

        

        
                