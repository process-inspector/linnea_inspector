from process_inspector.activity_log import ActivityLog
from process_inspector.dfg.builder import DFGBuilder
from linnea_inspector.data_processor import LogsProcessor
from linnea_inspector.classifiers.f_call import f_call
from linnea_inspector.store.experiment_store import ExperimentReader

def test_lp(log_dir):
    
    processor = LogsProcessor(log_dir=log_dir, parse_run_config=True, sep=';')   
    processor.process()
    activity_log = ActivityLog(processor.event_log, f_call)
    
    dfg = DFGBuilder(activity_log)
    print(dfg.nodes)
    print(dfg.edges)
    
    for node in dfg.node_data:
        print(dfg.node_data[node].head())
        break
    
    for edge in dfg.edge_data:
        print(dfg.edge_data[edge].head())
        break
        
    print("SUCCESS")
    
def test_store(store_path):
    reader = ExperimentReader(store_path)
    confs = reader.get_confs(
        expr="GLS_XX",
        prob_size="[1000, 1000]")
    
    if not confs:
        print("No configurations found.")
        return
    
    al = reader.get_activity_log(confs, add_objs_from_config=['expr', 'prob_size'])
    dfg = DFGBuilder(al)
    
    print(dfg.nodes)
    print(dfg.edges)
    
    for node in dfg.node_data:
        print(dfg.node_data[node].head())
        break
    
    for edge in dfg.edge_data:
        print(dfg.edge_data[edge].head())
        break
    print("SUCCESS")
    
     
if __name__ == "__main__":
    log_dir = "tests/traces/b0"
    test_lp(log_dir)
    
    store_path = ["tests/store/test.rs",]
    test_store(store_path)
    
