from linnea_inspector.event_data  import prepare

import pandas as pd
from partial_ranker import MeasurementsVisualizer
from partial_ranker import QuantileComparer, PartialRanker, Method
from process_inspector.model_data_utils import concat_meta_data
import os


def bp_algs2():
        # Example test (from root directory):
    trace_dir = "../50algorithms_1000_100/Julia/experimentsKEB/traces/"
    
    trace_file1 = os.path.join(trace_dir,"algorithm1.traces")
    trace_file2 = os.path.join(trace_dir, "algorithm15.traces")
    
    event_data1, meta_data1 = prepare(trace_file1)
    
    event_data2, meta_data2 = prepare(trace_file2)
    
    meta_data = concat_meta_data(meta_data1, meta_data2)
    
    df_ = meta_data.get_case_data()
    df_ = df_[(df_['alg'] == 'algorithm1') | (df_['alg'] == 'algorithm15')]
    measurements = df_.groupby('alg')['duration'].apply(lambda x: [float(v) for v in x if pd.notna(v)]).to_dict()
    
    # measurements = {f"t({key.replace('algorithm', 'alg')})": value for key, value in measurements.items()}
    # measurements = {f"t({key})": value for key, value in measurements.items()}
        
    
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
    fig = mv.show_measurements_boxplots(obj_list=algs_seq, scale=1.2, unit='runtime (ns)')
    fig.savefig('bp_algs2.png', dpi=300, bbox_inches="tight")
    
    print(ranks_m1)
    print(ranks_m2)
    print(ranks_m3)
    print(f"{len(ranks_m1)}-{len(ranks_m2)}-{len(ranks_m3)}")

        

if __name__ == "__main__":
    #data_dir = '../50algorithms_1000_100/Julia/experimentsKEB/traces/synthesis/model_data'
    #bp_algs(data_dir)
    bp_algs2()
    