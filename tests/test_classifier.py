from linnea_inspector.data_processor import LogsProcessor
from linnea_inspector.classifiers.f_call import f_call
import os

def test1():
    # Example test (from root directory):
    

    log_dir = "tests/traces/b0"
    processor = LogsProcessor(log_dir=log_dir, parse_run_config=True)
    processor.process()
    
    for trace, event_data in processor.event_log.items():
        event_data['el:activity'] = event_data.apply(lambda row: f_call(row), axis=1)
        print(event_data.head())
        print("SUCCESS")
        break
    
if __name__ == "__main__":
    test1()