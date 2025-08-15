from linnea_inspector.event_data import prepare
import sys

if __name__ == "__main__":
    
    # python -m tests.test_prepare_event_data examples/traces/gls_v1/experiments/traces/algorithm9.traces
    trace_file = sys.argv[1]
    
    event_log, meta_data = prepare(trace_file)
    
    print(event_log.df)
    print(f"Num events: {event_log.n_events}, Num cases: {event_log.n_cases}, Num objects: {event_log.n_objs}")
    print(meta_data.case_attr)
    print(meta_data.obj_attr)
