# Linnea Inspector
#
# Copyright (c) 2021-2026, High-Performance and Automatic Computing group
# at RWTH Aachen University and Umeå University.
# All rights reserved.
#
# Licensed under the BSD 3-Clause License.
# See LICENSE file in the project root for full license information.
#
# Contributors:
# - Aravind Sankaran

import os
from metascribe.rocks_store import RocksStore

import logging
logger = logging.getLogger(__name__)

class SynthesisWriter:
    def __init__(self, store_path,  lock_timeout=300, force_open=False):
        
        self.store_path = store_path
        if not os.path.exists(self.store_path):
            os.makedirs(self.store_path, exist_ok=True)
         
        self.synthesis_db_path = os.path.join(self.store_path, "synthesis")       
        self.lock_timeout = lock_timeout
        self.force_open = force_open
        
    def write_context(self, class_name,
                        object_context_data,
                        activity_context_data,
                        relation_context_data,
                        language="",
                        expr="",
                        cluster_name="",
                        aarch="",
                        n_threads="",
                        problem_size=""):
        
        
        with RocksStore(self.synthesis_db_path, lock=True, lock_timeout=self.lock_timeout, force_open=self.force_open) as store:
            key = os.path.join("/contexts", class_name,  language, expr, cluster_name, aarch, str(n_threads), str(problem_size))
            
            obj_key = f"{key}/object"
            activity_key = f"{key}/activity"
            relation_key = f"{key}/relation"
            
            store.put_json(obj_key, object_context_data.model_dump_json())
            store.put_json(activity_key, activity_context_data.model_dump_json())
            store.put_json(relation_key, relation_context_data.model_dump_json())
            
class SynthesisReader:
    def __init__(self, store_path, lock_timeout=300, force_open=False):

        self.synthesis_db_path = os.path.join(store_path, "synthesis")
        if not os.path.exists(self.synthesis_db_path):
            raise FileNotFoundError(f"Synthesis RocksDB not found at {self.synthesis_db_path}")
                    
        # args for opening RocksStore    
        self.lock_timeout = lock_timeout
        self.force_open = force_open
        
    def get_context(self, class_name,
                    language="",
                    expr="",
                    cluster_name="",
                    aarch="",
                    n_threads="",
                    problem_size=""):
        
        
        with RocksStore(self.synthesis_db_path, lock=False) as store:
            key = os.path.join("/contexts", class_name, language, expr, cluster_name, aarch, str(n_threads), str(problem_size))
                        
            obj_key = f"{key}/object"
            activity_key = f"{key}/activity"
            relation_key = f"{key}/relation"
            try:
                object_context_data = store.get_json(obj_key)
                activity_context_data = store.get_json(activity_key)
                relation_context_data = store.get_json(relation_key)
            except KeyError:
                raise KeyError(f"Key {key} not found in the store at {synthesis_db_path}")
            
            return {
                "object": object_context_data,
                "activity": activity_context_data,
                "relation": relation_context_data
            }
            
            
        