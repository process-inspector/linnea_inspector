# Linnea Inspector
# Copyright (c) 2021-2026 Aravind Sankaran
#
# SPDX-License-Identifier: AGPL-3.0-or-later
# See LICENSE file in the project root for full license information.

from linnea_inspector.store.experiment_store import ExperimentWriter, ExperimentReader
import json
import os
import shutil
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

from linnea_inspector.data_processor import LogsProcessor
from linnea_inspector.classifiers.f_call import f_call
from process_inspector.activity_log import ActivityLog

def test_write(log_dir):
    processor = LogsProcessor(log_dir=log_dir, parse_run_config=True)
    processor.process()
    activity_log = ActivityLog(processor.event_log, f_call) 

    
    store_path = "tests/store/test.rs"
    # if os.path.exists(store_path):
    #     shutil.rmtree(store_path)
    #     logging.info(f"Removed existing store at {store_path}")
        
    writer = ExperimentWriter(processor.run_config, store_path)
    logging.info(f"Opened RS store at {writer.store_path}")
    writer.write_run_config()
    writer.remove_duplicate_configs()
    writer.write_case(processor.case_md)
    writer.write_activity_log(activity_log)
    writer.write_algorithms()
            

def test_read():
    store_path = ["tests/store/test.rs",]
    reader = ExperimentReader(store_path)
    
    df = reader.run_configs
    print(df)
    
    confs = reader.get_confs(prob_size="[1000, 1000]")
    
    print(confs)
    
    if not confs:
        print("No configurations found.")
        return    
    
    case_md = reader.get_case_md(confs, add_objs_from_config=['cluster_name', 'prob_size'])
    al = reader.get_activity_log(confs, add_objs_from_config=['cluster_name', 'prob_size'])

    print("Run Configs DataFrame:")
    print(case_md)
    print("Activity Logs:")
    print(al.activity_language)

    for trace, df in al.c_event_log.items():
        print(f"Trace: {trace}")
        print(df)
        break    
    
def test_read_alg_code():
    store_path = ["tests/store/test.rs",]
    reader = ExperimentReader(store_path)
    
    confs = reader.get_confs(prob_size="[1000, 1000]")
    alg_name = "algorithm0"
    code, gen_steps = reader.get_alg_code(alg_name, confs[0])
    
    print(f"Algorithm Code for {alg_name}:\n{code}")
    print(f"Generation Steps for {alg_name}:\n{gen_steps}")
    
    
# def test_delete_context():
#     store_path = ["tests/store/test.rs",]
#     rs_reader = RSReader(store_path)
    
#     confs = rs_reader.get_confs(prob_size="[1000, 1000]", batch_id=1)
    
#     for conf in confs:
#         rs_writer = RSWriter(conf, conf['store_path'])
#         rs_writer.delete_config_entry()
    
#     print(f"Deleting contexts:")
#     print(confs)
    
  
if __name__ == "__main__":
    test_write("tests/traces/b0")
    test_write("tests/traces/b1")
    test_read()
    test_read_alg_code()
    