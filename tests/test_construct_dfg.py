from process_inspector.activity_log import ActivityLog
from process_inspector.dfg.dfg import DFG
from linnea_inspector.data_processor import LogsProcessor
from linnea_inspector.classifiers.f_call import f_call
from linnea_inspector.rocks_store import RSReader

def test_lp(log_dir):
    
    processor = LogsProcessor(log_dir=log_dir, parse_run_config=True, sep=';')   
    processor.process()
    activity_log = ActivityLog(processor.event_log, f_call)
    
    dfg = DFG(activity_log)
    print(dfg.nodes)
    print(dfg.edges)
    print("SUCCESS")
    
def test_rs(store_path):
    rs_reader = RSReader(store_path)
    confs = rs_reader.get_confs(
        expr="GLS_XX",
        prob_size="[1000, 1000]")
    
    if not confs:
        print("No configurations found.")
        return
    
    al = rs_reader.get_activity_log(confs, add_objs_from_config=['expr', 'prob_size'])
    dfg = DFG(al)
    print(dfg.nodes)
    print(dfg.edges)
    print("SUCCESS")
    
    
    
 
if __name__ == "__main__":
    log_dir = "tests/traces/b0"
    test_lp(log_dir)
    
    store_path = ["tests/store/test.rs",]
    test_rs(store_path)
    
