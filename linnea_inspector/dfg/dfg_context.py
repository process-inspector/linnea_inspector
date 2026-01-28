import pandas as pd
from process_inspector.schemas import ActivitySchema, RelationSchema
from process_inspector.contexts import PMContextBase
import numpy as np



class DFGContext(PMContextBase):
    def __init__(self, reverse_maps, object_context, obj_key="alg", compute_ranks=True):
        super().__init__()
        
        self.obj_key = obj_key
        self.reduction_group = [obj_key, 'iter']
        
        if compute_ranks:
            self.total_objs = len(object_context.data.records)     
            self.obj_rank = object_context.data.rank
            
        self.compute_ranks = compute_ranks
        
        self.compute_activity_stats(reverse_maps)
        self.compute_relation_stats(reverse_maps)

                
    def compute_activity_stats(self, reverse_maps):
        records = []
        obj_records = {}
        obj_bp = {}
        obj_rank = {}

        for activity, df in reverse_maps.activities_map.items():
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
                record['rank_score'] = self._compute_rank_score(df[self.obj_key].unique().tolist(), self.obj_rank)

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
                obj_rank[activity], perf_class = self._compute_partial_ranks(_obj_bp, invert=True)
                record['perf_class'] = perf_class
                for obj_rec in _obj_records:
                    obj_rec['rank'] = obj_rank[activity][obj_rec['obj']]
                
            obj_bp[activity] = _obj_bp            
            records.append(record)            
            obj_records[activity] = _obj_records
               
        self.activity_data.records = records
        self.activity_data.obj_records = obj_records
        self.activity_data.obj_bp_data = obj_bp
        if self.compute_ranks:
            self.activity_data.obj_rank = obj_rank
            
    
    def compute_relation_stats(self, reverse_maps):
        records = []

        for relation, df in reverse_maps.edges_map.items():
            _obj_key = self.obj_key
            if relation[0] == '__START__':
                _obj_key = f'next_{self.obj_key}'
                      
            record = {}
            record['relation'] = relation
            record['obj_count'] = df[_obj_key].nunique()
            if self.compute_ranks:
                record['rank_score'] = self._compute_rank_score(df[_obj_key].unique().tolist(), self.obj_rank)
                
            records.append(record)
                
        self.relation_data.records = records
                
