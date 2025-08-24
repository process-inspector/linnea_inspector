from linnea_inspector.event_data import prepare

import sys
import os

def test():
    # Example test (from root directory):
    
    trace_file = "tests/traces/algorithm0.traces"
    event_data, meta_data = prepare(trace_file)
    
    print(event_data)
    print(meta_data.get_obj_data())
    print(meta_data.get_case_data())
    print("SUCCESS")
    
if __name__ == "__main__":
    test()