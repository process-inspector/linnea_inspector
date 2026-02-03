from linnea_inspector.data_processor import LogsProcessor
from process_inspector.activity_log import ActivityLog
from linnea_inspector.classifiers.f_call import f_call
from linnea_inspector.store.experiment_store import ExperimentReader

from linnea_inspector.dfg.context import DFGContext
from linnea_inspector.object_context import ObjectContext

def test_lp(log_dir):
    
    processor = LogsProcessor(log_dir=log_dir, parse_run_config=True, sep=';')   
    processor.process()
    
    obj_context = ObjectContext(processor.case_md, obj_key='alg', compute_ranks=True)
    
    activity_log = ActivityLog(processor.event_log, f_call) 
    
    dfg_context = DFGContext(activity_log, obj_context.data, obj_key='alg', compute_ranks=True)

    print("DFG Context Activity Records:")
    print(dfg_context.activity_data.records)
    print(dfg_context.activity_data.obj_rank)
    
    print("DFG Context Relation Records:")
    print(dfg_context.relation_data.records)
    
    # print(dfg_context.relation_data.model_dump_json(indent=1))
        
    print("SUCCESS")
    
def test_store(store_path):
    reader = ExperimentReader(store_path)
    confs = reader.get_confs(
        expr="GLS_XX",
        prob_size="[1000, 1000]")
    
    if not confs:
        print("No configurations found.")
        return
    
    case_md = reader.get_case_md(confs, add_objs_from_config=['expr', 'prob_size'])
    obj_context = ObjectContext(case_md, obj_key='alg', compute_ranks=True)
    
    activity_log = reader.get_activity_log(confs, add_objs_from_config=['expr', 'prob_size'])
    dfg_context = DFGContext(activity_log, obj_context.data, obj_key='alg', compute_ranks=True)
    
    print("DFG Context Activity Records:")
    print(dfg_context.activity_data.records)
    print(dfg_context.activity_data.obj_rank)
    
    print("DFG Context Relation Records:")
    print(dfg_context.relation_data.records)
        
    print("SUCCESS")
    
if __name__ == "__main__":
    log_dir = "tests/traces/b0"
    test_lp(log_dir)
    
    store_path = ["tests/store/test.rs",]
    test_store(store_path)