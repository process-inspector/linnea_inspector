from linnea_inspector.event_data  import prepare
from linnea_inspector.classifiers.f_call import f_call

from process_inspector.event_log import EventLog
from process_inspector.activity_log import ActivityLog

import pandas as pd

import sys
import os

def activity_events():
    # Example test (from root directory):
    trace_dir = "../50algorithms_1000_100/Julia/experimentsKEB/traces/"
    
    trace_file1 = os.path.join(trace_dir,"algorithm1.traces")
    trace_file2 = os.path.join(trace_dir, "algorithm15.traces")
    
    event_data1, meta_data = prepare(trace_file1)
    
    event_data2, meta_data = prepare(trace_file2)
    
    # concat the two dataframes
    event_data = pd.concat([event_data1, event_data2], ignore_index=True)
    
    event_log = EventLog(event_data, case_key=['alg','iter'], order_key='time', obj_key='alg')
    activity_log = ActivityLog(event_log, 4, f_call) 
    
    for activity, events in activity_log.activity_events.items():
        if activity == 'trsm' or activity == 'potrf':
            print(f"Activity: {activity}")
            print(events)
        
    print(activity_log.activity_log)
         
    


if __name__ == "__main__":
    activity_events()