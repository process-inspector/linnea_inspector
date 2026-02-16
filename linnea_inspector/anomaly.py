import pandas as pd

def is_anomaly(ranking_method, obj_context_data):
    assert ranking_method in ['m1', 'm2', 'm3'], f"Unsupported ranking method: {ranking_method}"
    
    df = pd.DataFrame(obj_context_data.records)
    
    assert df.empty == False, "No records found in object context data"
    rank_col = f'rank_{ranking_method}'
    
    min_flops_mean = df['flops_mean'].min()
    min_flops_records = df[df['flops_mean'] == min_flops_mean][['obj', rank_col]]
    # best_rank_records = df[df['rank'] == 0][['obj', 'rank', 'flops_mean']]
    
    #if all objs with min_flops have the rank == 0, then anomaly =0
    anomaly = 0
    if len(min_flops_records[rank_col].unique()) == 1:
        if min_flops_records[rank_col].iloc[0] != 0:
            # if none of the algs with min flops obtain the best rank
            anomaly = 2
    else:
        # if not all algs with min flops get the best rank
        anomaly = 1
        
    return int(anomaly)        
            
            