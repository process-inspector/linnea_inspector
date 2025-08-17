import pandas as pd
from process_inspector.dfg.statistics_perspective import DFGStatisticsPerspective
import numpy as np
# from .statistics import compute_perf

class LinneaDFGStatisticsPerspective(DFGStatisticsPerspective):
    def __init__(self,dfg, activity_events):    
        super().__init__(dfg, activity_events)
        self.color_by = "avg_perf"
        
        
    def _compute_stats(self, activity_events):
        stats = []
        for activity, df in activity_events.items():
            df['perf'] = np.where(df['duration'] ==0 , np.nan, df['flops'] / df['duration'])
            avg_perf = df['perf'].mean()
            avg_flops = df['flops'].mean()
            
            stats.append({
                'activity': activity,
                'avg_perf': avg_perf,
                'avg_flops': avg_flops,
            })
            
        stats_df = pd.DataFrame(stats)
        return stats_df
        
    def _format_label_str(self, row):
       label_str = (f"{row['activity']}\n"
                    f"Avg. FLOPs: {row['avg_flops']:.2e}\n"
                    f"Avg. Perf: {row['avg_perf']:.2f} FLOPs/ns"
       )
       return label_str 