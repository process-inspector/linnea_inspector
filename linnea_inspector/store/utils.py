# Linnea Inspector
# Copyright (c) 2021-2026 Aravind Sankaran
#
# SPDX-License-Identifier: AGPL-3.0-or-later
# See LICENSE file in the project root for full license information.

import os
import pandas as pd
from metascribe.rocks_store import RocksStore
from .experiment_store import ExperimentReader
from .synthesis_store import SynthesisWriter
from linnea_inspector.object_context import ObjectContext
from linnea_inspector.dfg.context import DFGContext



import logging
logger = logging.getLogger(__name__)


def delete_experiment(run_config):
    store_path = run_config['store_path']
    
    run_configs_path = os.path.join(store_path, "run_configs.csv")
    if not os.path.exists(run_configs_path):
        logger.warning(f"run_configs.csv not found at {run_configs_path}. Nothing to delete.")
        return
    
    try:
        n_threads = run_config['nthreads']
        problem_size = run_config['prob_size']
        batch_id = run_config['batch_id']
    except KeyError as e:
        raise KeyError(f"Missing expected keys in run_config: {e}")
    
    delete_algs = False
    #1) delete case_md and activity_log from RocksDB
    db_path = os.path.join(store_path, "logs")
    with RocksStore(db_path, lock=True, lock_timeout=300) as store:
        case_md_key = f"/case_md/{n_threads}/{problem_size}/{batch_id}"
        try:
            del store._store[case_md_key]
            logger.info(f"Deleted case metadata with key {case_md_key} from the store at {db_path}")
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
        
        logger.info(f"Deleted activity logs with prefix {prefix} from the store at {db_path}")        
        #check if /case_md/{n_threads}/{problem_size}/ has any other batch ids.. if not, delete that too.
        case_md_prefix = f"/case_md/{n_threads}/{problem_size}/"
        remaining_keys = [key for key in store._store.keys() if key.startswith(case_md_prefix)]
        if not remaining_keys:
            delete_algs = True
    
    #2) delete entry from run_configs.csv
    df = pd.read_csv(run_configs_path)
    
    mask = True
    for key, value in run_config.items():
        if key not in ['store_path', 'db_path', 'algs_db_path', 'niter']:
            mask &= (df[key] == value)
    
    df = df[~mask].reset_index(drop=True)
    
    df.to_csv(run_configs_path, index=False)
    
    synthesis_db_path = os.path.join(store_path, "synthesis")
    if delete_algs:
        lang = run_config['language']
        expr = run_config['expr']
        cluster_name = run_config['cluster_name']
        aarch = run_config['aarch']
        
        with RocksStore(synthesis_db_path, lock=True, lock_timeout=300) as store:
            
            prefix = f"/contexts/{class_name}/{lang}/{expr}/{cluster_name}/{aarch}/{str(n_threads)}/{str(problem_size)}/"
            keys_to_delete = [key for key in store._store.keys() if key.startswith(prefix)]
            for key in keys_to_delete:
                try:
                    del store._store[key]
                except KeyError:
                    logger.warning(f"Synthesis context key {key} not found in the store at {synthesis_db_path}")
            
            logger.info(f"Deleted synthesis contexts with prefix {prefix} from {synthesis_db_path}")    
        
        algs_db_path = os.path.join(store_path, "algorithms")
        
        with RocksStore(algs_db_path, lock=True, lock_timeout=300) as store:
            algs_prefix = f"/algorithms/{problem_size}"
            gen_steps_prefix = f"/generation_steps/{problem_size}"
            alg_keys_to_delete = [key for key in store._store.keys() if key.startswith(algs_prefix)]
            gen_steps_keys_to_delete = [key for key in store._store.keys() if key.startswith(gen_steps_prefix)] 
            for key in alg_keys_to_delete + gen_steps_keys_to_delete:
                try:
                    del store._store[key]
                except KeyError:
                    logger.warning(f"Algorithm or generation steps key {key} not found in the store at {algs_db_path}")
            
            logger.info(f"Deleted algorithms and generation steps with prefixes {algs_prefix} and {gen_steps_prefix} from {algs_db_path}")  
    
    
def update_synthesis(run_config):


    store_path = run_config['store_path']
    reader = ExperimentReader([store_path,])
    
    confs = reader.get_confs(
        language=run_config['language'],
        expr=run_config['expr'],
        cluster_name=run_config['cluster_name'],
        aarch=run_config['aarch'],
        nthreads=run_config['nthreads'],
        prob_size=run_config['prob_size'])
    
    if not confs:
        logger.warning("No configurations found for updating synthesis context.")
        return
    
    case_md = reader.get_case_md(confs)
    obj_context = ObjectContext(case_md, obj_key='alg', compute_ranks=True)
    
    activity_log = reader.get_activity_log(confs)

    dfg_context = DFGContext(activity_log, obj_context.data, obj_key='alg', compute_ranks=True)
    
    synthesis_db_path = os.path.join(store_path, "synthesis")
    synthesis_writer = SynthesisWriter(synthesis_db_path)
    synthesis_writer.write_context(
        class_name="f_call",
        object_context_data=obj_context.data,
        activity_context_data=dfg_context.activity_data,
        relation_context_data=dfg_context.relation_data,
        language=run_config['language'],
        expr=run_config['expr'],
        cluster_name=run_config['cluster_name'],
        aarch=run_config['aarch'],
        n_threads=run_config['nthreads'],
        problem_size=run_config['prob_size']
    )
    
    logger.info("Synthesis context updated successfully.")