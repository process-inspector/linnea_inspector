import sys
import glob
from pathlib import Path
import os
from process_inspector.activity_log import ActivityLog
from process_inspector.dfg import DFG
from linnea_inspector.event_log.prepare_event_log import prepare_event_log
from linnea_inspector.mappings.f_call import f_call
from linnea_inspector.perspectives.ranks_perspective import RanksPerspective
from partial_ranker import MeasurementsVisualizer

if __name__ == "__main__":
    
    #  python -m tests.test_ranks_perspective examples/traces/gls_v1.1/experiments/traces/
    
    data_dir = sys.argv[1]
    # get the list of all .traces files in the directory
    trace_files = glob.glob(str(Path(data_dir) / "*.traces"))
    
    dfgs = []
    for trace_file in trace_files:
        print(f"Processing {trace_file}")
        
        # Prepare the event log and algorithm data
        event_log, alg_data = prepare_event_log(trace_file)

        
        # Create an ActivityLog instance
        activity_log = ActivityLog(event_log, 1, f_call)
        
        # Construct the DFG from the ActivityLog
        dfg = DFG(activity_log)
        dfg.id = alg_data['algorithm']
        dfg.info = alg_data
        
        dfgs.append(dfg)
        
    perspective = RanksPerspective(*dfgs)
    perspective.create_style()
    graph = perspective.prepare_digraph(rankdir='LR')
    
    print(graph)
    
    outdir = "examples/dfgs/tmp"
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    
    graph.render(os.path.join(outdir,'dfg_ranks_perspective'), format='svg', cleanup=True)
    
    for activity, rank in perspective.activity_ranks.items():
        print(f'{activity}: {rank["nranks"]}')
        
    print(f"Num. VR: {perspective.alg_ranks['nranks']}")    
    
    print(f"M1: {perspective.alg_ranks['m1']}")
    print(f"M2: {perspective.alg_ranks['m2']}")
    print(f"M3: {perspective.alg_ranks['m3']}")
    
    obj_list = sorted(list(perspective.alg_measurements.keys()))
    # obj_list.remove('algorithm2')
    mv = MeasurementsVisualizer(perspective.alg_measurements)
    fig = mv.show_measurements_boxplots(unit='ns', obj_list=obj_list, scale = 0.5)
    fig.savefig(os.path.join(outdir, 'variants_bp.svg'), format="svg", bbox_inches='tight')
    
    measurements = perspective.activity_ranks['gemv']['measurements']
    mv = MeasurementsVisualizer(measurements)
    fig = mv.show_measurements_boxplots(unit='ns', scale=0.5)
    fig.savefig(os.path.join(outdir, 'gemv_bp.svg'), format="svg", bbox_inches='tight')    

    
    
