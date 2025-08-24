from linnea_inspector.event_data  import prepare
from linnea_inspector.classifiers.f_call import f_call

from process_inspector.event_log import EventLog
from process_inspector.activity_log import ActivityLog

from process_inspector.dfg.dfg import DFG
from process_inspector.dfg.add_dfgs import add_dfgs
from process_inspector.model_data_utils import concat_activity_events, concat_meta_data

from linnea_inspector.dfg.ranks_perspective import LinneaDFGRanksPerspective

import sys
import os

def test1():
    # Example test (from root directory):
    
    trace_file1 = "tests/traces/algorithm0.traces"
    trace_file2 = "tests/traces/algorithm45.traces"
    
    event_data, meta_data1 = prepare(trace_file1)
    event_log = EventLog(event_data, case_key=['alg','iter'], order_key='time', obj_key='alg')
    activity_log1 = ActivityLog(event_log, 4, f_call)    
    dfg1 = DFG(activity_log1)
    
    event_data, meta_data2 = prepare(trace_file2)
    event_log = EventLog(event_data, case_key=['alg','iter'], order_key='time', obj_key='alg')
    activity_log2 = ActivityLog(event_log, 4, f_call)    
    dfg2 = DFG(activity_log2)
    
    dfg = add_dfgs(dfg1, dfg2)
    activity_events = concat_activity_events(activity_log1.activity_events, activity_log2.activity_events)
    meta_data = concat_meta_data(meta_data1, meta_data2)
    
    perspective = LinneaDFGRanksPerspective(dfg, activity_events, meta_data.get_case_data())
    perspective.create_style()
    graph = perspective.prepare_digraph(rankdir='TD')
    print(graph)
    graph.render(os.path.join('tmp', 'dfg_ranks'), format='svg', cleanup=True)
    
    for key, value in perspective.alg_ranks.items():
        print(f"{key}: {value}")
    print("SUCCESS")

if __name__ == "__main__":
    test1()
    
    