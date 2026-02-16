# Linnea Inspector
# Copyright (c) 2021-2026 Aravind Sankaran
#
# SPDX-License-Identifier: AGPL-3.0-or-later
# See LICENSE file in the project root for full license information.

import pandas as pd
from process_inspector.contexts import PMContextBase
from process_inspector.dfg.builder import DFGBuilder
import numpy as np

class DFGContext(PMContextBase):
    def __init__(self, activity_log, object_context_data, obj_key="alg", compute_ranks=True):
        super().__init__()
        
        dfg = DFGBuilder(activity_log)
          
        self.obj_key = obj_key
        self.reduction_group = [obj_key, 'iter']
        
        if compute_ranks:
            self.obj_rank = object_context_data.rank
            
        self.compute_ranks = compute_ranks
        
        self.compute_activity_stats(dfg.node_data)
        self.compute_relation_stats(dfg.edge_data)

                
    def compute_activity_stats(self, node_data):
        activities = []
        records = []
        obj_records = {}
        obj_bp = {}
        obj_rank = {'m1': {}, 'm2': {}, 'm3': {}}

        for activity, df in node_data.items():
            # node_data does not contain __START__ and __END__
            # otherwise, a check should be added here
            activities.append(activity) 
            record = {}
            record['activity'] = activity
            record['perf_mean'] = df['perf'].mean()
            
            g = df.groupby(self.reduction_group)        
            grouped = g.agg(duration_sum=('duration', 'sum'),
                            flops_sum=('flops', 'sum'),
                            perf_mean=('perf', 'mean') # for obj_bp
            )
            
            record['duration_mean'] = grouped['duration_sum'].mean()
            record['flops_mean'] = grouped['flops_sum'].mean()
            if self.compute_ranks:
                objs_in_activity = df[self.obj_key].unique().tolist()
                record['rank_score_m1'] = self._compute_rank_score(objs_in_activity, self.obj_rank['m1'])
                record['rank_score_m2'] = self._compute_rank_score(objs_in_activity, self.obj_rank['m2'])
                record['rank_score_m3'] = self._compute_rank_score(objs_in_activity, self.obj_rank['m3'])

            _obj_bp = {}
            _obj_records = []
            for obj, obj_df in grouped.groupby(self.obj_key):
                _obj_record = {}
                _obj_record['obj'] = obj
                _obj_record['duration_mean'] = obj_df['duration_sum'].mean()
                _obj_record['flops_mean'] = obj_df['flops_sum'].mean()
                _obj_record['perf_mean'] = obj_df['perf_mean'].mean()
                _obj_records.append(_obj_record)
                
                _obj_bp[obj] = obj_df['perf_mean'].to_list()
                
            if self.compute_ranks:
                pr = self._compute_partial_ranks(_obj_bp, invert=True)
                record['perf_class'] = pr['nranks']
                for obj_rec in _obj_records:
                    obj_rec['rank_m1'] = pr['m1'][obj_rec['obj']]
                    obj_rec['rank_m2'] = pr['m2'][obj_rec['obj']]
                    obj_rec['rank_m3'] = pr['m3'][obj_rec['obj']]
                obj_rank['m1'][activity] = pr['m1']
                obj_rank['m2'][activity] = pr['m2']
                obj_rank['m3'][activity] = pr['m3']
                
            obj_bp[activity] = _obj_bp            
            records.append(record)            
            obj_records[activity] = _obj_records
        
        self.activity_data.activities = set(activities)       
        self.activity_data.records = records
        self.activity_data.obj_records = obj_records
        self.activity_data.obj_bp_data = obj_bp
        if self.compute_ranks:
            self.activity_data.obj_rank = obj_rank
            
    
    def compute_relation_stats(self, edge_data):
        relations = []
        records = []

        for relation, df in edge_data.items():
            relations.append(relation)
            _obj_key = self.obj_key
            # if relation[0] == '__START__':
            #     _obj_key = f'next_{self.obj_key}'
                      
            record = {}
            record['relation'] = relation
            record['obj_count'] = df[_obj_key].nunique()
            if self.compute_ranks:
                objs_in_relation = df[_obj_key].unique().tolist()
                record['rank_score_m1'] = self._compute_rank_score(objs_in_relation, self.obj_rank['m1'])
                record['rank_score_m2'] = self._compute_rank_score(objs_in_relation, self.obj_rank['m2'])
                record['rank_score_m3'] = self._compute_rank_score(objs_in_relation, self.obj_rank['m3'])
                
            records.append(record)
       
        self.relation_data.relations = set(relations)         
        self.relation_data.records = records
                
