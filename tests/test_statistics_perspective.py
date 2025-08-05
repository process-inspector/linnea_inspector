from process_inspector.activity_log import ActivityLog
from process_inspector.dfg import DFG
from linnea_inspector.event_log.prepare_event_log import prepare_event_log
from linnea_inspector.mappings.f_call import f_call
from linnea_inspector.perspectives.statistics_perspective import StatisticsPerspective
import sys
import os

if __name__ == "__main__":
    
    # python -m tests.test_statistics_perspective examples/traces/gls_v1/experiments/traces/algorithm0.traces
    
    trace_file = sys.argv[1]
    event_log, alg_data = prepare_event_log(trace_file)
    activity_log = ActivityLog(event_log, 1, f_call)
    dfg = DFG(activity_log)
    dfg.id = alg_data['algorithm']
    dfg.info = alg_data

    
    perspective = StatisticsPerspective(dfg)
    perspective.create_style()
    graph = perspective.prepare_digraph(rankdir='TD')
    print(graph)
    
    outdir = "examples/dfgs/tmp"
    if not os.path.exists(outdir):
        os.makedirs(outdir)
        
    graph.render(os.path.join(outdir,'dfg_statistics_perspective'), format='svg', cleanup=True)
    