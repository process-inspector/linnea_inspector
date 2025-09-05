
from process_inspector.event_log import EventLog
from process_inspector.activity_log import ActivityLog
from process_inspector.dfg.reverse_maps import DFGReverseMaps
from linnea_inspector.event_data  import prepare
from linnea_inspector.classifiers.f_call import f_call
import pandas as pd
from partial_ranker import MeasurementsVisualizer
from partial_ranker import QuantileComparer, PartialRanker, Method
import os
import numpy as np

def bp_algs(data_dir, activity):
    trace_dir = "../50algorithms_1000_100/Julia/experimentsKEB/traces/"
    
    trace_file1 = os.path.join(trace_dir,"algorithm1.traces")
    trace_file2 = os.path.join(trace_dir, "algorithm15.traces")
    
    event_data1, meta_data1 = prepare(trace_file1)
    event_log1 = EventLog(event_data1, case_key=['alg','iter'], order_key='time', obj_key='alg')
    
    event_data2, meta_data2 = prepare(trace_file2)
    event_log2 = EventLog(event_data2, case_key=['alg','iter'], order_key='time', obj_key='alg')
    
    activity_log1 = ActivityLog(event_log1, f_call)
    activity_log2 = ActivityLog(event_log2, f_call)
    activity_log = activity_log1 + activity_log2
    reverse_maps = DFGReverseMaps(activity_log) 
    
    
    df_ = reverse_maps.activities_map[activity]
    df_ = df_[(df_['alg'] == 'algorithm1') | (df_['alg'] == 'algorithm15')]
    df_['perf'] = np.where(df_['duration'] ==0 , np.nan, df_['flops'] / df_['duration'])
    measurements = df_.groupby('alg')['perf'].apply(lambda x: [float(v) for v in x if pd.notna(v)]).to_dict()
    
    
    cm = QuantileComparer(measurements)
    cm.compute_quantiles(q_max=75, q_min=25, outliers=True)
    cm.compare()
    pr = PartialRanker(cm)
    
    pr.compute_ranks(Method.DFG)
    ranks_m1 = pr.get_ranks()
    
    pr.compute_ranks(Method.DFGReduced)
    ranks_m2 = pr.get_ranks()
    algs_seq = pr. get_separable_arrangement()
    
    pr.compute_ranks(Method.Min)
    ranks_m3 = pr.get_ranks()
    
    mv = MeasurementsVisualizer(measurements)
    fig = mv.show_measurements_boxplots(obj_list=algs_seq, scale=1.2, unit=f'{activity} perf (FLOPS/ns)')
    fig.savefig(f'bp_{activity}.pdf', dpi=300, bbox_inches="tight")
    
    print(f"{len(ranks_m1)}-{len(ranks_m2)}-{len(ranks_m3)}")
    
        

if __name__ == "__main__":
    data_dir = '../50algorithms_1000_100/Julia/experimentsKEB/traces/synthesis/model_data'
    bp_algs(data_dir,'trsm')
    bp_algs(data_dir,'potrf')
    bp_algs(data_dir,'syrk')
    bp_algs(data_dir,'trsv')
    