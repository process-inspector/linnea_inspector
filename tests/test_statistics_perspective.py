from linnea_inspector.data_processor import LogsProcessor
from linnea_inspector.rocks_store import RSReader

from process_inspector.activity_log import ActivityLog
from linnea_inspector.classifiers.f_call import f_call

from linnea_inspector.dfg.context import DFGContext
from linnea_inspector.dfg.statistics_perspective import DFGStatisticsPerspective

import os

def test_lp(log_dir):
    
    processor = LogsProcessor(log_dir=log_dir, parse_run_config=True, sep=';')   
    processor.process()
    
    
    activity_log = ActivityLog(processor.event_log, f_call) 
    
    dfg_context = DFGContext(activity_log, None, obj_key='alg', compute_ranks=False)
    
    dfg_perspective = DFGStatisticsPerspective(dfg_context.activity_data, dfg_context.relation_data, color_by="perf_mean")
    
    dfg_perspective.create_style()
    graph = dfg_perspective.prepare_digraph(rankdir='TD')
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
    
    dfg_context = DFGContext(activity_log, None, obj_key='alg', compute_ranks=False)

    dfg_perspective = DFGStatisticsPerspective(dfg_context.activity_data, dfg_context.relation_data, color_by="perf_mean")
    dfg_perspective.create_style()
    graph = dfg_perspective.prepare_digraph(rankdir='TD')
    
    print(graph)
    graph.render(os.path.join('tests/dfgs/', 'dfg_stats_rs'), format='svg', cleanup=True)
    print("SUCCESS")
    
if __name__ == "__main__":
    log_dir = "tests/traces/b0"
    test_lp(log_dir)
    
    store_path = ["tests/store/test.rs",]
    test_rs(store_path)