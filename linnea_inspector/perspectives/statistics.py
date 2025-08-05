import numpy as np
import pandas as pd

def compute_perf(inv_mapping):
    stats = []
    for activity, df in inv_mapping.items():
        df['perf'] = np.where(df['duration'] ==0 , np.nan, df['flops'] / df['duration'])
        avg_perf = df['perf'].mean()
        avg_flops = df['flops'].mean()
        count = len(df)
        nvariants = None
        try:
            nvariants = df['id'].nunique()
        except KeyError:
            pass
        
        stats.append({
            'activity': activity,
            'avg_perf': avg_perf,
            'avg_flops': avg_flops,
            'count': count,
            'nvariants': nvariants 
        })
        
    stats_df = pd.DataFrame(stats)
    return stats_df


def compute_perf_rank_score(inv_mapping, alg_ranks, total_variants):
    stats = []
    for activity, df in inv_mapping.items():
        df['perf'] = np.where(df['duration'] ==0 , np.nan, df['flops'] / df['duration'])
        avg_perf = df['perf'].mean()
        avg_flops = df['flops'].mean()
        nvariants = df['id'].nunique()
        count = len(df)
        if nvariants == total_variants:
            rank_score = 0
        else:  
            variants = df['id'].unique().tolist()
            m1 = 0
            m2 = 0
            m3 = 0
            for variant in variants:
                m1 += alg_ranks['m1'][variant]
                m2 += alg_ranks['m2'][variant]
                m3 += alg_ranks['m3'][variant]
            
            m1 /= len(variants)
            m2 /= len(variants)
            m3 /= len(variants)
            rank_score = m1
        
        
        stats.append({
            'activity': activity,
            'avg_perf': avg_perf,
            'avg_flops': avg_flops,
            'nvariants': nvariants,
            'count': count,
            'rank_score': rank_score,
        })
    
    stats_df = pd.DataFrame(stats)
    return stats_df
