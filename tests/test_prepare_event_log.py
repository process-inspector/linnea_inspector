from linnea_inspector.event_log.prepare_event_log import prepare_event_log
import sys

if __name__ == "__main__":
    trace_file = sys.argv[1]
    
    event_log, alg_data = prepare_event_log(trace_file)
    
    print(event_log)
    print(alg_data)
