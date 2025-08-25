from linnea_inspector.event_data  import prepare
from linnea_inspector.classifiers.f_call import f_call

from process_inspector.event_log import EventLog
from process_inspector.activity_log import ActivityLog

from process_inspector.dfg.dfg import DFG
from process_inspector.dfg.add_dfgs import add_dfgs
from process_inspector.dfg.perspective import DFGPerspective

import sys
import os

def dfg1():
    # Example test (from root directory):
    trace_dir = "../50algorithms_1000_100/Julia/experimentsKEB/traces/"
    
    trace_file1 = os.path.join(trace_dir,"algorithm1.traces")
    trace_file2 = os.path.join(trace_dir, "algorithm15.traces")
    
    event_data, meta_data = prepare(trace_file1)
    event_log = EventLog(event_data, case_key=['alg','iter'], order_key='time', obj_key='alg')
    activity_log1 = ActivityLog(event_log, 4, f_call)    
    dfg1 = DFG(activity_log1)
    
    event_data, meta_data = prepare(trace_file2)
    event_log = EventLog(event_data, case_key=['alg','iter'], order_key='time', obj_key='alg')
    activity_log2 = ActivityLog(event_log, 4, f_call)    
    dfg2 = DFG(activity_log2)
    
    dfg = add_dfgs(dfg1, dfg2)
    # activity_events = concat_activity_events(activity_log1.activity_events, activity_log2.activity_events)
    
    perspective = DFGPerspective(dfg)
    perspective.create_style()
    graph = perspective.prepare_digraph(rankdir='LR')
    print(graph)
    graph.render('dfg1', format='svg', cleanup=True)
    print("SUCCESS")

if __name__ == "__main__":
    dfg1()