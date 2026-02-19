from linnea_inspector.event_data  import prepare
from linnea_inspector.classifiers.f_call import f_call

from process_inspector.event_log import EventLog
from process_inspector.activity_log import ActivityLog

from process_inspector.dfg.dfg import DFG
from process_inspector.dfg.reverse_maps import DFGReverseMaps

from linnea_inspector.dfg.statistics_perspective import LinneaDFGStatisticsPerspective

import sys
import os

def test1():
    # Example test (from root directory):
    
    trace_dir = "../50algorithms_1000_100/Julia/experimentsKEB/traces/"
    
    trace_file1 = os.path.join(trace_dir,"algorithm1.traces")
    trace_file2 = os.path.join(trace_dir, "algorithm15.traces")
    
    event_data, meta_data1 = prepare(trace_file1)
    event_log = EventLog(event_data, case_key=['alg','iter'], order_key='time', obj_key='alg')
    activity_log1 = ActivityLog(event_log, f_call)    
    
    event_data, meta_data2 = prepare(trace_file2)
    event_log = EventLog(event_data, case_key=['alg','iter'], order_key='time', obj_key='alg')
    activity_log2 = ActivityLog(event_log, f_call)  
    
    activity_log = activity_log1 + activity_log2
    dfg = DFG(activity_log)  
    reverse_maps = DFGReverseMaps(activity_log)
    
    
    perspective = LinneaDFGStatisticsPerspective(dfg, reverse_maps)
    perspective.create_style()
    graph = perspective.prepare_digraph(rankdir='TD')
    print(graph)
    graph.render('dfg3', format='svg', cleanup=True)
    
    print("SUCCESS")

if __name__ == "__main__":
    test1()