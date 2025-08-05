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
            'count': count,  
        })
        
    stats_df = pd.DataFrame(stats)
    return stats_df


def compute_perf_rank_score(inv_mapping, variant_ranks):
    stats = []
    for activity, df in inv_mapping.items():
        df['perf'] = np.where(df['duration'] ==0 , np.nan, df['flops'] / df['duration'])
        avg_perf = df['perf'].mean()
        avg_flops = df['flops'].mean()
        nvariants = df['id'].nunique()
        count = len(df)
        
        variants = df['id'].unique().tolist()
        m1 = 0
        m2 = 0
        m3 = 0
        for variant in variants:
            m1 += variant_ranks['m1'][variant]
            m2 += variant_ranks['m2'][variant]
            m3 += variant_ranks['m3'][variant]
        
        m1 /= len(variants)
        m2 /= len(variants)
        m3 /= len(variants)
        
        stats.append({
            'activity': activity,
            'avg_perf': avg_perf,
            'avg_flops': avg_flops,
            'nvariants': nvariants,
            'count': count,
            'rank_score': m1
        })
    
    stats_df = pd.DataFrame(stats)
    return stats_df
