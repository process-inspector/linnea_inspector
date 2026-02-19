from linnea_inspector.event_data  import prepare
from linnea_inspector.classifiers.f_call import f_call

from process_inspector.event_log import EventLog
import pandas as pd

import sys
import os

def event_log():
    # Example test (from root directory):
    trace_dir = "../50algorithms_1000_100/Julia/experimentsKEB/traces/"
    
    trace_file1 = os.path.join(trace_dir,"algorithm1.traces")
    trace_file2 = os.path.join(trace_dir, "algorithm15.traces")
    
    event_data1, meta_data = prepare(trace_file1)
    
    event_data2, meta_data = prepare(trace_file2)
    
    # concat the two dataframes
    event_data = pd.concat([event_data1, event_data2], ignore_index=True)
    event_log = EventLog(event_data, case_key=['alg','iter'], order_key='time', obj_key='alg')
    
    for case, trace in event_log.event_log:
        if case[1] == '1' or case[1] == '2':
            print(f"Case: {case}")
            print(trace)

if __name__ == "__main__":
    event_log()