from process_inspector.model_data_utils import load_model_data
from process_inspector.dfg.dfg import DFG
import pandas as pd
from partial_ranker import MeasurementsVisualizer
from partial_ranker import QuantileComparer, PartialRanker, Method

def bp_algs(data_dir):
    dfg = DFG()
    dfg, activity_events, meta_data = load_model_data(data_dir,dfg)
    
    df_ = meta_data.get_case_data()
    df_ = df_[(df_['alg'] == 'algorithm1') | (df_['alg'] == 'algorithm15')]
    measurements = df_.groupby('alg')['duration'].apply(lambda x: [float(v) for v in x if pd.notna(v)]).to_dict()
    
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
    fig = mv.show_measurements_boxplots(obj_list=algs_seq, scale=0.5, unit='time (ns)')
    fig.savefig('bp_algs2.png', dpi=300, bbox_inches="tight")
    
    print(ranks_m1)
    print(ranks_m2)
    print(ranks_m3)
    print(f"{len(ranks_m1)}-{len(ranks_m2)}-{len(ranks_m3)}")
        

if __name__ == "__main__":
    data_dir = '../50algorithms_1000_100/Julia/experimentsKEB/traces/synthesis/model_data'
    bp_algs(data_dir)
    