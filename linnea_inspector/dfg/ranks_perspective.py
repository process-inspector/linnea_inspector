import pandas as pd
from process_inspector.dfg.ranks_perspective import DFGRanksPerspective
from process_inspector.compute_ranks import compute_activity_ranks
import numpy as np
# from .statistics import compute_perf

class LinneaDFGRanksPerspective(DFGRanksPerspective):
    def __init__(self,dfg, reverse_maps, meta_data):   
        super().__init__(dfg, reverse_maps, meta_data, obj_key='alg', obj_perf_key='duration')
        self.activities_stats = None
        self.activity_ranks = None      
        
    def _compute_activities_stats(self):
        stats = []
        
        for activity, df in self.reverse_maps.activities_map.items():
            df['perf'] = np.where(df['duration'] ==0 , np.nan, df['flops'] / df['duration'])
                    
        self.activity_ranks = compute_activity_ranks(self.reverse_maps.activities_map ,group_by='alg', on='perf')
        
        for activity, df in self.reverse_maps.activities_map.items():
            mean_perf = df['perf'].mean()
            mean_flops = df['flops'].mean()
            
            nvariants = df['alg'].nunique()
            nranks = self.activity_ranks[activity]['nranks']
             
            stats.append({
                'activity': activity,
                'mean_perf': mean_perf,
                'mean_flops': mean_flops,
                'nvariants': nvariants,
                'rank_score':  self.activity_rank_score[activity],
                'nranks': nranks,
            })
            
            if nvariants == self.total_variants:
                label_str = (
                    f"{activity} ({nvariants}/{self.total_variants})\n"
                    f"Num. Ranks:  {nranks}\n"            
                    f"Mean. FLOPs: {mean_flops:.2e}\n"
                    f"Mean. Perf: {mean_perf:.2f} F/ns"
                )
            else:   
                label_str = (
                    f"{activity} ({nvariants}/{self.total_variants})\n"
                    f"Rank score: {self.activity_rank_score[activity]:.1f}\n"
                    f"Num. Ranks:  {nranks}\n"            
                    f"Mean. FLOPs: {mean_flops:.2e}\n"
                    f"Mean. Perf: {mean_perf:.2f} F/ns"
                )
            self.activity_label[activity] = label_str          
            
        self.activities_stats = pd.DataFrame(stats)
        

    def create_style(self):
        
        self._compute_activities_stats() 
              
        max_rank_score = max(self.activity_rank_score.values())    
        for node in self.dfg.nodes:
            if not node == '__START__' and not node == '__END__':
                self.activity_color[node] = self._get_activity_color(self.activity_rank_score[node], 0.0, max_rank_score)
        

        max_rank_score = max(self.edge_rank_score.values())                
        for edge in self.dfg.edges:
            self.edge_color[edge] = self._get_edge_color(self.edge_rank_score[edge], 0.0, max_rank_score)
            self.edge_penwidth[edge] = 1.0
            self.edge_label[edge] = f'{self.edge_rank_score[edge]:.1f}'

       
        
