from linnea_inspector.data_processor import LogsProcessor
from linnea_inspector.store.experiment_store import ExperimentReader

from process_inspector.activity_log import ActivityLog
from linnea_inspector.classifiers.f_call import f_call

from linnea_inspector.dfg.context import DFGContext
from process_inspector.dfg.difference_perspective import DFGDifferencePerspective

import os


def test_lp(log_dir):
    
    processor = LogsProcessor(log_dir=log_dir, parse_run_config=True, sep=';')   
    processor.process()
    
    activity_log = ActivityLog(processor.event_log, f_call)
    al_1 = activity_log.apply_filter(lambda event: event['alg'] == 'algorithm0')
    context1 = DFGContext(al_1, None, obj_key='alg', compute_ranks=False)
    
    al_2 = activity_log.apply_filter(lambda event: event['alg'] == 'algorithm10')
    context2 = DFGContext(al_2, None, obj_key='alg', compute_ranks=False)
    
    
    perspective = DFGDifferencePerspective(context1.activity_data.activities,
                                           context1.relation_data.relations,
                                           context2.activity_data.activities,
                                           context2.relation_data.relations)
    
    perspective.create_style()
    graph = perspective.prepare_digraph(rankdir='TD')
    print(graph)
    graph.render(os.path.join('tests/dfgs/', 'dfg_diff_lp'), format='svg', cleanup=True)
    print("SUCCESS")

def test_store(store_path):
    reader = ExperimentReader(store_path)
    confs = reader.get_confs(
        expr="GLS_XX",
        prob_size="[1000, 1000]")
    
    if not confs:
        print("No configurations found.")
        return
    
    
    activity_log = reader.get_activity_log(confs, add_objs_from_config=['expr', 'prob_size'])
    
    al_1 = activity_log.apply_filter(lambda event: event['alg'] == 'algorithm0')
    context1 = DFGContext(al_1, None, obj_key='alg', compute_ranks=False)
    
    al_2 = activity_log.apply_filter(lambda event: event['alg'] == 'algorithm10')
    context2 = DFGContext(al_2, None, obj_key='alg', compute_ranks=False)
    
    perspective = DFGDifferencePerspective(context1.activity_data.activities,
                                           context1.relation_data.relations,
                                           context2.activity_data.activities,
                                           context2.relation_data.relations)
    perspective.create_style()
    graph = perspective.prepare_digraph(rankdir='TD')
    print(graph)
    graph.render(os.path.join('tests/dfgs/', 'dfg_diff_rs'), format='svg', cleanup=True)
    print("SUCCESS")
    
if __name__ == "__main__":
    log_dir = "tests/traces/b0"
    test_lp(log_dir)
    
    store_path = ["tests/store/test.rs",]
    test_store(store_path)