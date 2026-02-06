# Linnea Inspector
#
# Copyright (c) 2021-2026 Aravind Sankaran
# SPDX-License-Identifier: AGPL-3.0-or-later
# See LICENSE file in the project root for full license information.


import pandas as pd
import os
import numpy as np
from pathlib import Path
import glob
import json
import logging
import time
logger = logging.getLogger(__name__)


class LogsProcessor:
    def __init__(self, log_dir, parse_run_config=True, sep=';'):
        self.log_dir = log_dir
        self.sep = sep
        
        self.run_config = {}
        if parse_run_config:
            run_config_path = os.path.join(self.log_dir, "run_config.json")
            assert os.path.isfile(run_config_path), f"Missing run_config.json in {self.log_dir}"
            self._prepare_run_config(run_config_path)
        
        self.num_logs = 0
        self.files = []
        self._prepare_files()            
        
        self.case_key = ['alg', 'iter']
        self.event_log = {}
        self.case_md = None   
        
    def _prepare_run_config(self, run_config_path):
        
        with open(run_config_path, 'r') as f:
            run_config = json.load(f)
            
            try:
                self.run_config['language'] = run_config['language']
                self.run_config['expr'] = run_config['expr']
                self.run_config['nthreads'] = run_config['nthreads']
                self.run_config['cluster_name'] = run_config['cluster_name']
                self.run_config['aarch'] = run_config['aarch']
                self.run_config['prob_size'] = run_config['prob_size']
                self.run_config['batch_id'] = run_config['batch_id']
                self.run_config['timestamp'] = run_config['timestamp']
                self.run_config['niter'] = run_config['niter']
                self.run_config['alg_codes_path'] = run_config['alg_codes_path']
            except KeyError as e:
                raise KeyError(f"Missing expected keys in run_config.json: {e}")         
            
            self.run_config['log_dir'] = self.log_dir

        
    def _prepare_files(self):
        
        log_files = glob.glob(os.path.join(self.log_dir, "algorithm*.traces"))
        
        assert len(log_files) > 0, f"No trace files found in log directory: {self.log_dir}"
        
        self.num_logs = len(log_files)
        self.files = log_files
        
        logger.info(f"Found {self.num_logs} log files in {len(self.log_dir)} directories.")
            

    def process(self):
        start_time = time.perf_counter()
        event_data = []
        case_md = []
        
        for file in self.files:
            file_event_data, file_case_md = self._parse_file(file, sep=self.sep)
            event_data.extend(file_event_data)
            case_md.extend(file_case_md)

        self.case_md = pd.DataFrame(case_md)
            
        assert len(event_data) > 0, f"No event data parsed from log directory: {log_dir}"
            
        event_df = pd.DataFrame(event_data)
        grouped = event_df.groupby(self.case_key)
        for case, event_trace in grouped:
            event_trace = event_trace.sort_values(by='timestamp')
            self.event_log[case] = event_trace
            
        end_time = time.perf_counter()
        
        logger.info(f"Processed {self.num_logs} log files in {end_time - start_time:.2f} seconds.")      
        
    
    def _parse_event_record(self, alg, line, sep):
        if not "[#LT]" in line:
            return None
        line = line.split("[#LT] ")[-1]
        if line.strip() == "":
            return None
        parts = line.strip().split(sep)
        if len(parts) != 5:
            raise ValueError(f"Invalid line format: {line}")
        
        event_record = {
            'iter': parts[0].strip(),
            'call': parts[2].strip(),
            'timestamp': parts[1].strip(),
            'flops': float(parts[3].strip()),
            'duration': float(parts[4].strip()),
            # Possible objects
            'alg': alg,
            # These should be filled before preparing activity log
            # 'expr': self.run_config['expr'],
            # 'prob_size': self.run_config['prob_size'],
            # 'nthreads': self.run_config['nthreads'],
            # 'cluster_name': self.run_config['cluster_name'],
            # 'aarch': self.run_config['aarch']          
        }
        
        perf = event_record['flops'] / event_record['duration'] if event_record['duration'] > 0 else np.nan
        event_record['perf'] = perf
            
        return event_record
    

    def _parse_file(self, log_file, sep=';'):
        alg = Path(log_file).name.split('.')[0]
        
        #assert alg starts with "algorithm "
        assert alg.startswith("algorithm"), f"Invalid algorithm name in log file: {alg}"
        
        event_data = []
        case_md = []        
        with open(log_file, 'r') as file:
            for line in file:
                record = self._parse_event_record(alg, line, sep)
                if record:                    
                    if "algorithm" in record['call']:
                        # Add case metadata record  
                        case_record = record.copy()
                        case_record.pop('call')
                        case_record['timestamp'] = pd.to_datetime(float(record['timestamp']), unit='ns', utc=True).tz_convert('Europe/Berlin').strftime('%Y-%m-%d %H:%M:%S.%f %Z')
                        case_md.append(case_record)
                    else:
                        # Add event record
                        event_data.append(record)
        return event_data, case_md

def add_cols_from_config(case_md, event_log, config):
    for key, value in config.items():
        case_md[key] = value
        for case, df in event_log.items():
            df[key] = value

            
            