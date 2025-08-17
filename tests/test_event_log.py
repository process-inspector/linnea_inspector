from linnea_inspector.event_data import prepare
from process_inspector.event_log import EventLog

import sys
import os

def test():
    # Example test (from root directory):
    
    trace_file = "examples/traces/gls_v2/experiments/traces/algorithm0.traces"
    event_data, meta_data = prepare(trace_file)
    event_log = EventLog(event_data, case_key=['alg','iter'], order_key='time', obj_key='alg')
    
    for case, trace in event_log.event_log:
        if case[1] == '1' or case[1] == '2':
            print(f"Case: {case}")
            print(trace)
                
        # print(f"Case: {case}")
        # print(trace)
        # break
    
    print(f"Num events: {event_log.n_events}, Num cases: {event_log.n_cases}, Num objects: {event_log.n_objs}")
    
    print("SUCCESS")

if __name__ == "__main__":
    test()
    