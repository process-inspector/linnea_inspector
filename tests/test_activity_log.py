from linnea_inspector.data_processor import LogsProcessor
from linnea_inspector.classifiers.f_call import f_call
from process_inspector.event_log import EventLog
from process_inspector.activity_log import ActivityLog
from linnea_inspector.rocks_store import RSReader

import sys
import os


def test_lp(log_dir):

    processor = LogsProcessor(log_dir=log_dir, parse_run_config=True, sep=';')
    
    processor.process()
    
    activity_log = ActivityLog(processor.event_log, f_call) 
    
    for case, classified_trace in activity_log.c_event_log.items():
        print(case)
        print(classified_trace)
        break
    
    print(activity_log.activity_language)
    print(activity_log.activities)
    
        
    print(f"Num activities: {len(activity_log.activities)}, Num variants: {activity_log.n_variants}")

    
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
    
    for case, classified_trace in activity_log.c_event_log.items():
        print(case)
        print(classified_trace)
        break
    
    print(activity_log.activity_language)
    print(activity_log.activities)
    
        
    print(f"Num activities: {len(activity_log.activities)}, Num variants: {activity_log.n_variants}")

    
    print("SUCCESS")

if __name__ == "__main__":
    test_lp("tests/traces/b0")
    test_rs(["tests/store/test.rs",])