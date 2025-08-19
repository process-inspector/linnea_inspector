from linnea_inspector.event_data  import prepare
from linnea_inspector.classifiers.f_call import f_call

from process_inspector.event_log import EventLog
from process_inspector.activity_log import ActivityLog

from process_inspector.dfg.dfg import DFG
from process_inspector.dfg.add_dfgs import add_dfgs
from process_inspector.model_data_utils import concat_activity_events

from linnea_inspector.dfg.statistics_perspective import LinneaDFGStatisticsPerspective

import sys
import os

def test2():
    trace_file1 = "examples/traces/gls_v2/experiments/traces/algorithm0.traces"
    trace_file2 = "examples/traces/gls_v2/experiments/traces/algorithm10.traces"
    
    event_data, meta_data = prepare(trace_file1)
    event_log = EventLog(event_data, case_key=['alg','iter'], order_key='time', obj_key='alg')
    activity_log1 = ActivityLog(event_log, 4, f_call)    
    dfg1 = DFG(activity_log1)
    
    event_data, meta_data = prepare(trace_file2)
    event_log = EventLog(event_data, case_key=['alg','iter'], order_key='time', obj_key='alg')
    activity_log2 = ActivityLog(event_log, 4, f_call)    
    dfg2 = DFG(activity_log2)
    
    dfg = add_dfgs(dfg1, dfg2)
    activity_events = concat_activity_events(activity_log1.activity_events, activity_log2.activity_events)
    
    perspective = LinneaDFGStatisticsPerspective(dfg, activity_events)
    perspective.create_style()
    graph = perspective.prepare_digraph(rankdir='TD')
    print(graph)
    graph.render(os.path.join('tmp', 'dfg_stats2'), format='svg', cleanup=True)
    print("SUCCESS")

def test1():
    
    trace_file = "examples/traces/gls_v2/experiments/traces/algorithm0.traces"
    event_data, meta_data = prepare(trace_file)
    event_log = EventLog(event_data, case_key=['alg','iter'], order_key='time', obj_key='alg')
    
    activity_log = ActivityLog(event_log, 4, f_call)    
    dfg = DFG(activity_log)
    
    perspective = LinneaDFGStatisticsPerspective(dfg, activity_log.activity_events)
    perspective.create_style()
    graph = perspective.prepare_digraph(rankdir='TD')
    print(graph)
    graph.render(os.path.join('tmp', 'dfg_stats1'), format='svg', cleanup=True)
    print("SUCCESS")


if __name__ == "__main__":
    
    test1()
    test2()
    