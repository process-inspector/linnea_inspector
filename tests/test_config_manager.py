from linnea_inspector.store.config_manager import ConfigManager
import os
import json
import shutil
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def read_config(trace_dir):
    config_json = os.path.join(trace_dir, "run_config.json")
    if not os.path.exists(config_json):
        raise FileNotFoundError(f"run_config.json not found in {trace_dir}")
    with open(config_json, 'r') as f:
        config = json.load(f)
    return config

def test_write(config, store_path):
    
    print("Writing..")
    
    config_manager = ConfigManager(store_path)
    config_manager.write_config(config)
    
    # Read back the configs and verify
    configs_df = config_manager.get_all_configs()
    assert not configs_df.empty, "No configs found in the store after writing."
    
    print(configs_df)
    
def test_update(store_path):
    print("Updating..")
    config_manager = ConfigManager(store_path)
    config_manager.update(col="expr", value="GLS", where={"language": "julia"})
    # config_manager.update(col="expr", value="GLS", where={}) # should update all records with expr=GLS
    df = config_manager.get_all_configs()
    print(df)
    
def test_delete(store_path):
    print("Deleting..")
    config_manager = ConfigManager(store_path)
    config_manager.delete(language="julia", expr="GLS", batch_id=1, niter="SSS") # niter is not a primary key, so it should be ignored
    # config_manager.delete(niter=10) # should not delete anything as niter is not a primary key
    df = config_manager.get_all_configs()
    print(df)
    
def test_get_configs(store_path):
    print("Getting configs with conditions..")
    config_manager = ConfigManager(store_path)
    configs = config_manager.get_configs(language="julia", expr="GLS")
    configs = config_manager.get_configs(language="julia", expr="GLS") # should not read from file again
    print(configs)
    
if __name__ == "__main__":
    store_path = "tests/store/test.conf"
    
    if os.path.exists(store_path):
        shutil.rmtree(store_path)
        
    os.makedirs(store_path, exist_ok=True)
    
    trace_dir = "tests/traces/b0"    
    config = read_config(trace_dir)
    test_write(config, store_path)
    
    trace_dir = "tests/traces/b1"
    config = read_config(trace_dir)
    test_write(config, store_path)
    
    test_update(store_path)
    
    test_delete(store_path)
    
    trace_dir = "tests/traces/b1"
    config = read_config(trace_dir)
    test_write(config, store_path)
    
    trace_dir = "tests/traces/b1"
    config = read_config(trace_dir)
    test_write(config, store_path)
    
    test_get_configs(store_path)
    
    print("SUCCESS")
    