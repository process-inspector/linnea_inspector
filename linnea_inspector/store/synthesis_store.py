# Linnea Inspector
# Copyright (c) 2021-2026 Aravind Sankaran
#
# SPDX-License-Identifier: AGPL-3.0-or-later
# See LICENSE file in the project root for full license information.

import os
from metascribe.rocks_store import RocksStore

import logging
logger = logging.getLogger(__name__)

class SynthesisWriter:
    def __init__(self, store_path, synth_config, lock_timeout=300, force_open=False):
        
        self.store_path = store_path
        if not os.path.exists(self.store_path):
            os.makedirs(self.store_path, exist_ok=True)
         
        self.language = synth_config.get("language", "")
        self.expr = synth_config.get("expr", "")
        self.cluster_name = synth_config.get("cluster_name", "")
        self.arch = synth_config.get("arch", "")
        self.precision = synth_config.get("precision", "")
        self.nthreads = str(synth_config.get("nthreads", ""))
        self.prob_size = synth_config.get("prob_size", "")
        # self.synthesis_db_path = os.path.join(self.store_path, "synthesis")       
        self.lock_timeout = lock_timeout
        self.force_open = force_open
        
    def write_context(self, class_name,
                        object_context_data,
                        activity_context_data,
                        relation_context_data):
        
        
        with RocksStore(self.store_path, lock=True, lock_timeout=self.lock_timeout, force_open=self.force_open) as store:
            key = os.path.join("/contexts", class_name,  self.language, self.expr, self.cluster_name, self.arch, self.precision, self.nthreads, self.prob_size)
            
            obj_key = f"{key}/object"
            activity_key = f"{key}/activity"
            relation_key = f"{key}/relation"
            
            store.put_json(obj_key, object_context_data.model_dump_json())
            store.put_json(activity_key, activity_context_data.model_dump_json())
            store.put_json(relation_key, relation_context_data.model_dump_json())
    
    def write_stats(self, stats_data):
        with RocksStore(self.store_path, lock=True, lock_timeout=self.lock_timeout, force_open=self.force_open) as store:
            key = os.path.join("/stats", self.language, self.expr, self.cluster_name, self.arch, self.precision, self.nthreads, self.prob_size)
            store.put_json(key, stats_data)
            
class SynthesisReader:
    def __init__(self, store_path, synth_config, lock_timeout=300, force_open=False):

        # self.synthesis_db_path = os.path.join(store_path, "synthesis")
        self.store_path = store_path
        if not os.path.exists(self.store_path):
            raise FileNotFoundError(f"Synthesis RocksDB not found at {self.store_path}")
        
        self.language = synth_config.get("language", "")
        self.expr = synth_config.get("expr", "")
        self.cluster_name = synth_config.get("cluster_name", "")
        self.arch = synth_config.get("arch", "")
        self.precision = synth_config.get("precision", "")
        self.nthreads = str(synth_config.get("nthreads", ""))
        self.prob_size = synth_config.get("prob_size", "")
                    
        # args for opening RocksStore    
        self.lock_timeout = lock_timeout
        self.force_open = force_open
        
    def get_context(self, class_name):
        
        
        with RocksStore(self.store_path, lock=True) as store:
            key = os.path.join("/contexts", class_name, self.language, self.expr, self.cluster_name, self.arch, self.precision, self.nthreads, self.prob_size)
                        
            obj_key = f"{key}/object"
            activity_key = f"{key}/activity"
            relation_key = f"{key}/relation"
            try:
                object_context_data = store.get_json(obj_key)
                activity_context_data = store.get_json(activity_key)
                relation_context_data = store.get_json(relation_key)
            except KeyError:
                raise KeyError(f"Key {key} not found in the store at {self.store_path}")
            
            return {
                "object": object_context_data,
                "activity": activity_context_data,
                "relation": relation_context_data
            }
            
            
    def get_stats(self):
        with RocksStore(self.store_path, lock=True) as store:
            key = os.path.join("/stats", self.language, self.expr, self.cluster_name, self.arch, self.precision, self.nthreads, self.prob_size)
            try:
                stats_data = store.get_json(key)
                return stats_data
            except KeyError:
                raise KeyError(f"Stats key {key} not found in the store at {self.store_path}")    