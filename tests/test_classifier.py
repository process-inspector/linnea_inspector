from linnea_inspector.event_data import prepare
from linnea_inspector.classifiers.f_call import f_call
import os

def test1():
    # Example test (from root directory):
    
    trace_file = "tests/traces/algorithm0.traces"
    event_data, meta_data = prepare(trace_file)
    
    event_data['el:activity'] = event_data.apply(lambda row: f_call(row), axis=1)
    print(event_data.head())
    print("SUCCESS")
    
if __name__ == "__main__":
    test1()