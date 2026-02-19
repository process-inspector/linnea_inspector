from linnea_inspector.event_data  import prepare
from linnea_inspector.classifiers.f_call import f_call

from process_inspector.event_log import EventLog
from process_inspector.activity_log import ActivityLog

from process_inspector.dfg.dfg import DFG
from process_inspector.dfg.reverse_maps import DFGReverseMaps
from process_inspector.model_data_utils import concat_meta_data

from linnea_inspector.dfg.ranks_perspective import LinneaDFGRanksPerspective

import sys
import os
import glob

def test1(data_dir):
    # Example test (from root directory):
    
    
    #find all files in the directory that start with algorithm and end with .traces using glob
    trace_files = glob.glob(os.path.join(data_dir, "algorithm*.traces")) 
    
    
    meta_data_logs = []
    for i, trace_file in enumerate(trace_files):
        event_data, meta_data = prepare(trace_file)
        event_log = EventLog(event_data, case_key=['alg','iter'], order_key='time', obj_key='alg')
        if i == 0:
            activity_log = ActivityLog(event_log, f_call)
        else:
            activity_log += ActivityLog(event_log, f_call)   
         
        meta_data_logs.append(meta_data)
        
    meta_data = concat_meta_data(*meta_data_logs)
        
    dfg = DFG(activity_log)  
    reverse_maps = DFGReverseMaps(activity_log)
    
    perspective = LinneaDFGRanksPerspective(dfg, reverse_maps, meta_data)    
    perspective.create_style()
    graph = perspective.prepare_digraph(rankdir='TD')
    print(graph)
    graph.render('dfg_ranks2', format='svg', cleanup=True)
    
    print("SUCCESS")

if __name__ == "__main__":
    data_dir = '../50algorithms_1000_100/Julia/experimentsKEB/traces/'
    test1(data_dir)