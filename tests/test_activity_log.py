from linnea_inspector.data_processor import LogsProcessor
from linnea_inspector.classifiers.f_call import f_call
from process_inspector.event_log import EventLog
from process_inspector.activity_log import ActivityLog

import sys
import os


def test():
    log_dir = "tests/traces"
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

if __name__ == "__main__":
    test()