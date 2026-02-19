from process_inspector.model_data_utils import load_model_data
from process_inspector.dfg.dfg import DFG
import pandas as pd
from linnea_inspector.dfg.ranks_perspective import LinneaDFGRanksPerspective


def dfg_stats(data_dir):
    dfg = DFG()
    dfg, activity_events, meta_data = load_model_data(data_dir,dfg)
    
    perspective = LinneaDFGRanksPerspective(dfg, activity_events, meta_data.get_case_data())
    perspective.create_style()
    graph = perspective.prepare_digraph(rankdir='TD')
    print(graph)
    graph.render('dfg_stats', format='svg', cleanup=True)
    
     

if __name__ == "__main__":
    data_dir = '../50algorithms_1000_100/Julia/experimentsKEB/traces/synthesis/model_data'
    dfg_stats(data_dir)
    