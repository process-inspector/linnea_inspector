from linnea_inspector.event_data  import prepare
from linnea_inspector.classifiers.f_call import f_call

from process_inspector.event_log import EventLog
from process_inspector.activity_log import ActivityLog
from process_inspector.dfg.reverse_maps import DFGReverseMaps

import pandas as pd

import sys
import os

def edge_events():
    # Example test (from root directory):
    trace_dir = "../50algorithms_1000_100/Julia/experimentsKEB/traces/"
    
    trace_file1 = os.path.join(trace_dir,"algorithm1.traces")
    trace_file2 = os.path.join(trace_dir, "algorithm15.traces")
    
    event_data1, meta_data = prepare(trace_file1)
    
    event_data2, meta_data = prepare(trace_file2)
    
    # concat the two dataframes
    event_data = pd.concat([event_data1, event_data2], ignore_index=True)
    
    event_log = EventLog(event_data, case_key=['alg','iter'], order_key='time', obj_key='alg')
    activity_log = ActivityLog(event_log, f_call)
    reverse_maps = DFGReverseMaps(activity_log) 
    
    for edge, events in reverse_maps.edges_map.items():
        #only events where iter == 1 or 2
        # print(events)
        if edge == ('potrf', 'trsm') or edge == ('trsv', '__END__'):
            print(f"Edge: {edge}")
            # start_node dfs are empty because the iter is nan, and the next_iter holds the iter value
            print(events[events['iter'].isin(['1','2'])].reset_index(drop=True))
        
    #print(activity_log.activity_log)
         
    


if __name__ == "__main__":
    edge_events()