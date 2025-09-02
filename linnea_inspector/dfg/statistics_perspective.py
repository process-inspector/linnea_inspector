import pandas as pd
from process_inspector.dfg.statistics_perspective import DFGStatisticsPerspective
import numpy as np
# from .statistics import compute_perf

class LinneaDFGStatisticsPerspective(DFGStatisticsPerspective):
    def __init__(self,dfg, reverse_maps):    
        super().__init__(dfg, reverse_maps)
        self.color_by = "mean_perf"
        
        
    def _compute_activities_stats(self, reverse_maps):
        stats = []
        for activity, df in reverse_maps.activities_map.items():
            df['perf'] = np.where(df['duration'] ==0 , np.nan, df['flops'] / df['duration'])
            mean_perf = df['perf'].mean()
            mean_flops = df['flops'].mean()
            
            stats.append({
                'activity': activity,
                'mean_perf': mean_perf,
                'mean_flops': mean_flops,
            })
            
        stats_df = pd.DataFrame(stats)
        return stats_df
        
    def _format_activity_label_str(self, row):
       label_str = (f"{row['activity']}\n"
                    f"Mean. FLOPs: {row['mean_flops']:.2e}\n"
                    f"Mean. Perf: {row['mean_perf']:.2f} FLOPs/ns"
       )
       return label_str 