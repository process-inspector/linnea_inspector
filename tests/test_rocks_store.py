from linnea_inspector.rocks_store import RSWriter, RSReader
import json
import os
import shutil
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

from linnea_inspector.data_processor import LogsProcessor
from linnea_inspector.classifiers.f_call import f_call
from process_inspector.activity_log import ActivityLog

def test_write():
    log_dir = "tests/traces"
    processor = LogsProcessor(log_dir=log_dir, parse_run_config=True)
    processor.process()
    activity_log = ActivityLog(processor.event_log, f_call) 

    
    store_path = "tests/store/test.rs"
    # if os.path.exists(store_path):
    #     shutil.rmtree(store_path)
    #     logging.info(f"Removed existing store at {store_path}")
        
    with RSWriter(processor.run_config, store_path) as store:
        logging.info(f"Opened RS store at {store.db_path}")
        store.write_run_config()
        store.remove_duplicate_configs()
        store.write_case(processor.case_md)
        store.write_activity_log(activity_log)
            

def test_read():
    store_path = "tests/store/test.rs"
    rs_reader = RSReader(store_path)
    
    df = rs_reader.run_configs
    print(df)
    
    confs = rs_reader.get_confs(prob_size="[1000, 1000]")
    print(confs)    
    
    case_mds = []
    activity_logs = []
    for config in confs:
        case_md = rs_reader.get_case_md(config)
        case_mds.append(case_md)
        activity_log = rs_reader.get_activity_log(config)
        activity_logs.append(activity_log)
    
    print("Run Configs DataFrame:")
    print(case_mds)
    print("Activity Logs:")
    for al in activity_logs:
        print(al.activity_language)
        break
    
    
    # case_md = rs_reader.get_case_md(n_threads="24", problem_size="[1000, 1000]")
    # print(case_md)
    
if __name__ == "__main__":
    test_write()
    test_read()
    