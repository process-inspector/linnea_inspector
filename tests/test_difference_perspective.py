from process_inspector.activity_log import ActivityLog
from process_inspector.dfg import DFG
from linnea_inspector.event_log.prepare_event_log import prepare_event_log
from linnea_inspector.mappings.f_call import f_call
from linnea_inspector.perspectives.difference_perspective import DifferencePerspective
import sys
import os

if __name__ == "__main__":
    
    # python -m tests.test_difference_perspective examples/traces/gls_v1/experiments/traces/algorithm0.traces examples/traces/gls_v1/experiments/traces/algorithm2.traces
    # python -m tests.test_difference_perspective examples/traces/gls_v2/experiments/traces/algorithm40.traces examples/traces/gls_v2/experiments/traces/algorithm42.traces  
    
    trace_file1 = sys.argv[1]
    trace_file2 = sys.argv[2] 
    
    event_log1, alg_data1 = prepare_event_log(trace_file1)
    activity_log1 = ActivityLog(event_log1, 1, f_call)
    dfg1 = DFG(activity_log1)
    dfg1.id = alg_data1['algorithm']
    dfg1.info = alg_data1
    
    event_log2, alg_data2 = prepare_event_log(trace_file2)
    activity_log2 = ActivityLog(event_log2, 1, f_call)
    dfg2 = DFG(activity_log2)
    dfg2.id = alg_data2['algorithm']
    dfg2.info = alg_data2
    
    perspective = DifferencePerspective(dfg1, dfg2)
    perspective.create_style()
    graph = perspective.prepare_digraph(rankdir='TD')
    
    outdir = "examples/dfgs/tmp"
    if not os.path.exists(outdir):
        os.makedirs(outdir)
        
    graph.render(os.path.join(outdir,'dfg_difference_perspective'), format='svg', cleanup=True)
    
    