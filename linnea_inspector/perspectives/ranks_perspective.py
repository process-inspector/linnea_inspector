import pandas as pd
from process_inspector.dfg.statistics_perspective import DFGStatisticsPerspective
from process_inspector.compute_ranks import compute_activity_ranks, compute_meta_data_ranks
import numpy as np
# from .statistics import compute_perf

class LinneaDFGRanksPerspective(DFGStatisticsPerspective):
    def __init__(self,dfg, activity_events, case_data):
        self.total_variants = case_data['alg'].nunique()
        self.alg_ranks = None
        self.activity_ranks = None     
        super().__init__(dfg, activity_events, case_data)
        self.color_by = "rank_score"
        
        
    def _compute_stats(self, activity_events, case_data):
        stats = []
        
        for activity, df in activity_events.items():
            df['perf'] = np.where(df['duration'] ==0 , np.nan, df['flops'] / df['duration'])
                    
        self.alg_ranks = compute_meta_data_ranks(case_data, group_by='alg', on='duration')
        self.activity_ranks = compute_activity_ranks(activity_events ,group_by='alg', on='perf')
        
        for activity, df in activity_events.items():
            avg_perf = df['perf'].mean()
            avg_flops = df['flops'].mean()
            nvariants = df['alg'].nunique()
            
            if nvariants == self.total_variants:
                rank_score = 0
            else:  
                variants = df['alg'].unique().tolist()
                m1 = 0
                for variant in variants:
                    m1 += self.alg_ranks['m1'][variant]  
                m1 /= nvariants
                rank_score = m1
                
            nranks = self.activity_ranks[activity]['nranks']
             
            stats.append({
                'activity': activity,
                'avg_perf': avg_perf,
                'avg_flops': avg_flops,
                'nvariants': nvariants,
                'rank_score': rank_score,
                'nranks': nranks,
            })
            
        stats_df = pd.DataFrame(stats)
        return stats_df
        
    def _format_label_str(self, row):
       #label_str = f"{row['activity']} ({row['nvariants']}/{self.nvariants})\nAvg. FLOPs: {row['avg_flops']:.2e}\nAvg. Perf: {row['avg_perf']:.2f} FLOPs/ns\nnPR:  {self.ranks[row['activity']]['rank_str']}"
       
       rank_score = f"Rank score: {row['rank_score']:.1f}\n" 
       if row['nvariants'] == self.total_variants:
           rank_score = "" 
           
       
       label_str = (
            f"{row['activity']} ({row['nvariants']}/{self.total_variants})\n"
            f"{rank_score}"
            f"Num. Ranks:  {row['nranks']}\n"            
            f"Avg. FLOPs: {row['avg_flops']:.2e}\n"
            f"Avg. Perf: {row['avg_perf']:.2f} F/ns"
        )
       return label_str 

       
        
