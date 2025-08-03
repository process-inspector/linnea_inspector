import numpy as np
import pandas as pd

def compute_perf(inv_mapping):
    stats = []
    for activity, df in inv_mapping.items():
        df['perf'] = np.where(df['duration'] ==0 , np.nan, df['flops'] / df['duration'])
        avg_perf = df['perf'].mean()
        avg_flops = df['flops'].mean()
        count = len(df)
        stats.append({
            'activity': activity,
            'avg_perf': avg_perf,
            'avg_flops': avg_flops,
            'count': count  
        })
        
    stats_df = pd.DataFrame(stats)
    return stats_df
