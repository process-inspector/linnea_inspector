import pandas as pd
import os
from process_inspector.meta_data import MetaData
import numpy as np

def parse_event(line, sep):
    if line.strip() == "":
        return None
    parts = line.strip().split(sep)
    if len(parts) != 5:
        raise ValueError(f"Invalid line format: {line}")
    
    event_record = {
        'iter': parts[0].strip(),
        'time': parts[1].strip(),
        'call': parts[2].strip(),
        'flops': float(parts[3].strip()),
        'duration': float(parts[4].strip())
    }
        
    return event_record
    

def prepare(trace_file, sep=';'):
    events_data = []
    meta_data = MetaData()
    alg = None
    
    
    with open(trace_file, 'r') as file:
        for line in file:
            record = parse_event(line, sep)
            if record:
                if "algorithm" in record['call']:
                    # Add object metadata
                    alg = record['call']
                    if not meta_data.obj_data:
                        meta_data.add_obj_record({'alg': alg, 'flops': record['flops']})   
                    perf = record['flops'] / record['duration'] if record['duration'] > 0 else np.nan
                    meta_data.add_case_record({'alg': alg, 'iter': record['iter'], 'perf': perf})
                else:
                    # Add event record
                    events_data.append(record)
                    
    if events_data:
        events_df = pd.DataFrame(events_data)
        events_df['time'] = pd.to_datetime(events_df['time'].astype(float), unit='ns')
        events_df['alg'] = alg
        # event_log = EventLog(events_df, case_key='iter', order_key='time', obj_key='alg')
    else:
        raise ValueError("No valid event records found in the trace file.")
        
        
    return events_df, meta_data         