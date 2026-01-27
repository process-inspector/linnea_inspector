from process_inspector.activity_log import ActivityLog
from process_inspector.dfg.reverse_maps import DFGReverseMaps
from linnea_inspector.data_processor import LogsProcessor
from linnea_inspector.classifiers.f_call import f_call
from linnea_inspector.rocks_store import RSReader

def test_lp(log_dir):
    
    processor = LogsProcessor(log_dir=log_dir, parse_run_config=True, sep=';')   
    processor.process()
    activity_log = ActivityLog(processor.event_log, f_call)
    
    reverse_map = DFGReverseMaps(activity_log, next_attrs=['alg', 'perf']) # possible objs, expr and prob_size are unavailable here
    
    
    for node, df in reverse_map.activities_map.items():
        print(f"Node: {node}, DataFrame:\n {df.head()}")
        break
    
    for edge, df in reverse_map.edges_map.items():
        print(f"Edge: {edge}, DataFrame:\n {df.head()}")
        break
    
    print('Edge DataFrame for (__START__, potrf):')
    print(reverse_map.edges_map[('__START__', 'potrf')].head())
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
    reverse_map = DFGReverseMaps(activity_log, next_attrs=['alg', 'expr', 'prob_size', 'perf']) # possible objs
    
    for node, df in reverse_map.activities_map.items():
        print(f"Node: {node}, DataFrame:\n {df.head()}")
        break
    
    for edge, df in reverse_map.edges_map.items():
        print(f"Edge: {edge}, DataFrame:\n {df.head()}")
        break
    
    print('Edge DataFrame for (__START__, potrf):')
    print(reverse_map.edges_map[('__START__', 'potrf')].head())
    print("SUCCESS")
    
if __name__ == "__main__":
    log_dir = "tests/traces/b0"
    test_lp(log_dir)
    
    store_path = ["tests/store/test.rs",]
    test_rs(store_path)