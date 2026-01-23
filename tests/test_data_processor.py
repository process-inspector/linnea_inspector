from linnea_inspector.data_processor import LogsProcessor, add_cols_from_config
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def test_data_processor_with_config():
    log_dir = "tests/traces"
    processor = LogsProcessor(log_dir=log_dir, parse_run_config=True)
    
    processor.process()
    
    print("Event Log:", processor.event_log)
    print("Case Metadata:", processor.case_md)
    print("Run Config:", processor.run_config)
    
    print("SUCCESS")
    
def test_add_cols_from_config():
    log_dir = "tests/traces"
    processor = LogsProcessor(log_dir=log_dir, parse_run_config=True)
    
    processor.process()
    
    configs_to_add = {
        'language': processor.run_config.get('language'),
        'nthreads': processor.run_config.get('nthreads'),
        'cluster_name': processor.run_config.get('cluster_name')
    }

    add_cols_from_config(processor.case_md, processor.event_log, configs_to_add)
    
    print("Event Log after adding config columns:", processor.event_log)
    print("Case Metadata after adding config columns:", processor.case_md)
    
    print("SUCCESS")
    


if __name__ == "__main__":
    # test_data_processor_with_config()
    # test_data_processor_with_no_config()
    test_add_cols_from_config()
    