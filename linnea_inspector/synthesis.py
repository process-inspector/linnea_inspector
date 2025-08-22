from linnea_inspector.event_data  import prepare
from linnea_inspector.classifiers.f_call import f_call

from process_inspector.event_log import EventLog
from process_inspector.activity_log import ActivityLog

from process_inspector.dfg.dfg import DFG
from process_inspector.dfg.add_dfgs import add_dfgs
from process_inspector.model_data_utils import concat_activity_events, concat_meta_data, save_model_data

from linnea_inspector.dfg.ranks_perspective import LinneaDFGRanksPerspective

import sys
import os
import glob


def dfg_synthesis(trace_dir, save_model=False):
    # trace_dir = os.path.join(exp_dir, "Julia/experiments/traces")
    
    if not os.path.isdir(trace_dir):
        print(f"Error: '{trace_dir}' is not a valid directory.")
        sys.exit(1)
    
    trace_files = glob.glob(os.path.join(trace_dir, "*.traces"))
    if not trace_files:
        print(f"Error: No trace files found in '{trace_dir}'.")
        sys.exit(1)
    
    dfgs = []
    activity_events = []
    meta_data_list = []
    
    for trace_file in trace_files:
        event_data, meta_data = prepare(trace_file)
        event_log = EventLog(event_data, case_key=['alg', 'iter'], order_key='time', obj_key='alg')
        activity_log = ActivityLog(event_log, 1, f_call)

        dfg = DFG(activity_log)
        
        dfgs.append(dfg)
        activity_events.append(activity_log.activity_events)
        meta_data_list.append(meta_data)
        
    full_dfg = add_dfgs(*dfgs)
    full_activity_events = concat_activity_events(*activity_events)
    full_meta_data = concat_meta_data(*meta_data_list)
    
    perspective = LinneaDFGRanksPerspective(full_dfg, full_activity_events, full_meta_data.get_case_data())
    perspective.create_style()
    graph = perspective.prepare_digraph(rankdir='TD')
    
        
    print(f"M1: {perspective.alg_ranks['m1']}")
    print(f"M2: {perspective.alg_ranks['m2']}")
    print(f"M3: {perspective.alg_ranks['m3']}")
    print(perspective.alg_ranks['nranks'])
    
    synthesis_dir = os.path.join(trace_dir, "synthesis")
    os.makedirs(synthesis_dir, exist_ok=True)
    graph.render(os.path.join(synthesis_dir, 'dfg'), format='svg', cleanup=True)
    if save_model:
        save_model_data(os.path.join(synthesis_dir, "model_data"), full_dfg, full_activity_events, full_meta_data)
    
    
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python dfg_synthesis.py <experiment_directory>")
        sys.exit(1)
    
    exp_dir = sys.argv[1]
    dfg_synthesis(exp_dir, save_model=True)
    print("DFG synthesis completed successfully.")
    sys.exit(0)