from linnea_inspector.event_data import prepare
from linnea_inspector.classifiers.f_call import f_call
from process_inspector.event_log import EventLog
from process_inspector.activity_log import ActivityLog

import sys
import os

def test():
    trace_file = "tests/traces/algorithm0.traces"
    event_data, meta_data = prepare(trace_file)
    event_log = EventLog(event_data, case_key=['alg','iter'], order_key='time', obj_key='alg')
    print(f"Num events: {event_log.n_events}, Num cases: {event_log.n_cases}")
    
    activity_log = ActivityLog(event_log, f_call) 
    
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