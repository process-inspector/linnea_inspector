import pandas as pd

def parse_line(line):
    if line.strip() == "":
        return None
    parts = line.strip().split(' ')
    if len(parts) != 5:
        raise ValueError(f"Invalid line format: {line}")
    
    event_record = {
        'case': parts[0],
        'time': parts[1],
        'call': parts[2],
        'flops': float(parts[3]),
        'duration': float(parts[4])
    }
        
    return event_record
    

def prepare_event_log(trace_file):
    event_data = []
    alg_data = {'algorithm': None, 'durations': [], 'flops': None}
    with open(trace_file, 'r') as file:
        for line in file:
            record = parse_line(line)
            if record:
                if "algorithm" in record['call']:
                    if alg_data['algorithm'] is None:
                        alg_data['algorithm'] = record['call']
                        alg_data['flops'] = record['flops']
                    alg_data['durations'].append(record['duration'])
                else:
                    event_data.append(record)
                    
    if event_data:
        event_log = pd.DataFrame(event_data)
        event_log['time'] = pd.to_datetime(event_log['time'].astype(float), unit='ns')
    else:
        event_log = pd.DataFrame()
        
    return event_log, alg_data         