from dataclasses import dataclass, field
from typing import Dict, List, Tuple
import pandas as pd
from process_inspector.compute_ranks import compute_partial_ranks

@dataclass
class ActivityContextData:
    records: List[dict] = field(default_factory=list)
    obj_records: Dict[str, List[dict]] = field(default_factory=dict)
    obj_bp: Dict[str, Dict[str, List[float]]] = field(default_factory=dict)
    obj_rank: Dict[str, Dict[str, int]] = field(default_factory=dict)
    
@dataclass
class RelationContextData:
    records: List[dict] = field(default_factory=list)
    obj_records: Dict[Tuple[str, str], List[dict]] = field(default_factory=dict)
    obj_bp: Dict[Tuple[str, str], Dict[str, List[float]]] = field(default_factory=dict)
    obj_rank: Dict[Tuple[str, str], Dict[str, int]] = field(default_factory=dict)

@dataclass
class ObjectContextData:
    records: List[dict] = field(default_factory=list)
    rank: Dict[str, int] = field(default_factory=dict)
    bp: Dict[str, List[float]] = field(default_factory=dict)
    

class ObjectContext:
    def __init__(self, case_md, obj_key="alg", compute_ranks=True):
        self.obj_key = obj_key
        self.context = ObjectContextData()
        
    def _compute_object_stats(self, case_md):
        pass


class DFGContext:
    def __init__(self, reverse_maps, object_context, obj_key="alg", compute_ranks=True):
        self.obj_key = obj_key
        self.reduction_group = [obj_key, 'iter']
        
        self.activity_context = ActivityContextData()
        self.relation_context = RelationContextData()
                
        if compute_ranks:
            self.total_objs = len(object_context.records)    
            self.obj_rank = object_context.rank
            
        self.compute_ranks = compute_ranks
        
        self._compute_activity_stats(reverse_maps)
        self._compute_relation_stats(reverse_maps)

                
    def _compute_activity_stats(self, reverse_maps):
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
                record['rank_score'] = self._compute_rank_score(self.obj_key, df)

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
                
            records.append(record)
            obj_records[activity] = _obj_records
            obj_bp[activity] = _obj_bp
            if self.compute_ranks:
                obj_rank[activity], perf_class = self._compute_partial_ranks(_obj_bp)
                record['perf_class'] = perf_class
                
        self.activity_context.records = records
        self.activity_context.obj_records = obj_records
        self.activity_context.obj_bp = obj_bp
        if self.compute_ranks:
            self.activity_context.obj_rank = obj_rank
            
    
    def _compute_relation_stats(self, reverse_maps):
        records = []

        for relation, df in reverse_maps.edges_map.items():
            _obj_key = self.obj_key
            if relation[0] == '__START__':
                _obj_key = f'next_{self.obj_key}'
                      
            record = {}
            record['relation'] = relation
            record['obj_count'] = df[_obj_key].nunique()
            if self.compute_ranks:
                record['rank_score'] = self._compute_rank_score(_obj_key, df)
                
            records.append(record)
                
        self.relation_context.records = records
                
    def _compute_rank_score(self, obj_key, df):
        
        objs_in_df = df[obj_key].unique().tolist()
        nobjs = len(objs_in_df)
        
        rank_score = -1.0
        if nobjs != self.total_objs:
            rank_score = 0.0
            for obj in objs_in_df:
                rank_score += self.obj_rank[obj]
            rank_score /= nobjs
            
        return rank_score            
        
    def _compute_partial_ranks(self, obj_bp):
        inverted_m = {k: -1*np.array(v) for k, v in obj_bp.items()}
        partial_ranks = compute_partial_ranks(inverted_m, remove_outliers=False)
        obj_rank = partial_ranks['m1']
        perf_class = partial_ranks['nranks']
        return obj_rank, perf_class 
