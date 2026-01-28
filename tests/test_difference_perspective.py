from linnea_inspector.data_processor import LogsProcessor
from linnea_inspector.rocks_store import RSReader

from process_inspector.activity_log import ActivityLog
from linnea_inspector.classifiers.f_call import f_call
from process_inspector.dfg.dfg import DFG

from process_inspector.dfg.difference_perspective import DFGDifferencePerspective

import os


def test_lp(log_dir):
    
    processor = LogsProcessor(log_dir=log_dir, parse_run_config=True, sep=';')   
    processor.process()
    
    activity_log = ActivityLog(processor.event_log, f_call)
    al_1 = activity_log.apply_filter(lambda event: event['alg'] == 'algorithm0')
    dfg_1 = DFG(al_1)
    
    al_2 = activity_log.apply_filter(lambda event: event['alg'] == 'algorithm10')
    dfg_2 = DFG(al_2)
    
    
    perspective = DFGDifferencePerspective(dfg_1, dfg_2)
    
    perspective.create_style()
    graph = perspective.prepare_digraph(rankdir='TD')
    print(graph)
    graph.render(os.path.join('tests/dfgs/', 'dfg_diff_lp'), format='svg', cleanup=True)
    print("SUCCESS")

def test_rs(store_path):
    rs_reader = RSReader(store_path)
    confs = rs_reader.get_confs(
        expr="GLS_XX",
        prob_size="[1000, 1000]")
    
    if not confs:
        print("No configurations found.")
        return
    
    
    activity_log = rs_reader.get_activity_log(confs, add_objs_from_config=['expr', 'prob_size'])
    
    al_1 = activity_log.apply_filter(lambda event: event['alg'] == 'algorithm0')
    dfg_1 = DFG(al_1)
    al_2 = activity_log.apply_filter(lambda event: event['alg'] == 'algorithm10')
    dfg_2 = DFG(al_2)
    
    perspective = DFGDifferencePerspective(dfg_1, dfg_2)
    perspective.create_style()
    graph = perspective.prepare_digraph(rankdir='TD')
    print(graph)
    graph.render(os.path.join('tests/dfgs/', 'dfg_diff_rs'), format='svg', cleanup=True)
    print("SUCCESS")
    
if __name__ == "__main__":
    log_dir = "tests/traces/b0"
    test_lp(log_dir)
    
    store_path = ["tests/store/test.rs",]
    test_rs(store_path)