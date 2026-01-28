from linnea_inspector.data_processor import LogsProcessor
from linnea_inspector.rocks_store import RSReader

from process_inspector.activity_log import ActivityLog
from linnea_inspector.classifiers.f_call import f_call
from process_inspector.dfg.dfg import DFG

from process_inspector.dfg.reverse_maps import DFGReverseMaps
from linnea_inspector.dfg.statistics_perspective import DFGStatisticsPerspective

import os

def test_lp(log_dir):
    
    processor = LogsProcessor(log_dir=log_dir, parse_run_config=True, sep=';')   
    processor.process()
    
    
    activity_log = ActivityLog(processor.event_log, f_call) 
    
    dfg = DFG(activity_log)
    reverse_map = DFGReverseMaps(activity_log, next_attrs=['alg'])
    
    perspective = DFGStatisticsPerspective(dfg, reverse_map, obj_key='alg')
    
    perspective.create_style()
    graph = perspective.prepare_digraph(rankdir='TD')
    print(graph)
    graph.render(os.path.join('tests/dfgs/', 'dfg_stats_lp'), format='svg', cleanup=True)
    print("SUCCESS")

    
def test_rs(store_path):
    rs_reader = RSReader(store_path)
    confs = rs_reader.get_confs(
        expr="GLS_XX",
        prob_size="[1000, 1000]")
    
    if not confs:
        print("No configurations found.")
        return
    
    case_md = rs_reader.get_case_md(confs, add_objs_from_config=['expr', 'prob_size'])
    
    activity_log = rs_reader.get_activity_log(confs, add_objs_from_config=['expr', 'prob_size'])
    dfg = DFG(activity_log)
    reverse_map = DFGReverseMaps(activity_log, next_attrs=['alg'])

    perspective = DFGStatisticsPerspective(dfg, reverse_map, obj_key='alg')
    perspective.create_style()
    graph = perspective.prepare_digraph(rankdir='TD')
    print(graph)
    graph.render(os.path.join('tests/dfgs/', 'dfg_stats_rs'), format='svg', cleanup=True)
    print("SUCCESS")
    
if __name__ == "__main__":
    log_dir = "tests/traces/b0"
    test_lp(log_dir)
    
    store_path = ["tests/store/test.rs",]
    test_rs(store_path)