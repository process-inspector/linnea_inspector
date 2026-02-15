import pandas as pd
import os
import logging
logger = logging.getLogger(__name__)

class ConfigManager:
    def __init__(self, store_path):
        self.store_path = store_path
        self.run_configs_path = os.path.join(self.store_path, "run_configs.csv")
        
        self.primary_keys = ['language', 'expr', 'cluster_name', 'arch', 'prob_size', 'nthreads', 'precision', 'batch_id']
        self.run_id = "job_id"

        self._df = pd.DataFrame()  # Initialize an empty DataFrame with primary keys as columns
        
    def write_config(self, config):
        assert all(key in config for key in self.primary_keys), f"Config must contain primary keys: {self.primary_keys}"
        assert self.run_id in config, f"Config must contain key: {self.run_id}"
        
        record = {f"{key}": f"{str(value)}" for key, value in config.items()}
        
        if os.path.exists(self.run_configs_path):
            df = pd.read_csv(self.run_configs_path, dtype=str)
            
            #check if a record with same run_id exists, if yes, update the run_id with .0 or .1.. etc
            mask = (df[self.run_id] == record[self.run_id])
            if mask.any():
                existing_ids = df.loc[mask, self.run_id].tolist()
                suffixes = [id.split(".")[-1] for id in existing_ids if id.startswith(record[self.run_id])]
                suffixes = [int(s) for s in suffixes if s.isdigit()]
                next_suffix = max(suffixes) + 1 if suffixes else 0
                record[self.run_id] = f"{record[self.run_id]}.{next_suffix}"
                logger.warning(f"Duplicate run_id found. Updated run_id to {record[self.run_id]} to avoid conflict.")
            
            # Check for duplicates based on primary keys, and rewrite the record if a duplicate is found
            mask = pd.Series(True, index=df.index)
            for key in self.primary_keys:
                mask &= (df[key] == record[key])
            if mask.any():
                for col, val in record.items():
                    df.loc[mask, col] = val
            else:
                # No duplicate found, append the new record
                df = pd.concat([df, pd.DataFrame([record])], ignore_index=True)
        else:
            df = pd.DataFrame([record])

        try:
            df.to_csv(self.run_configs_path, index=False)
            logger.info(f"Config written to {self.run_configs_path}")    
        except Exception as e:
            raise IOError(f"Failed to write config to {self.run_configs_path}: {e}")
        
    def get_all_configs(self):
        if self._df.empty:
            if not os.path.exists(self.run_configs_path):
                raise FileNotFoundError(f"run_configs.csv not found at {self.run_configs_path}")
        
            try:
                self._df = pd.read_csv(self.run_configs_path, dtype=str)
            except Exception as e:
                raise IOError(f"Failed to read configs from {self.run_configs_path}: {e}")

            logger.info(f"Configs loaded from {self.run_configs_path}: {len(self._df)} records")
            
        return self._df
        
    def get_configs(self, **conditions):
        df = self.get_all_configs()
        mask = pd.Series(True, index=df.index)
        try:
            for key, value in conditions.items():
                mask &= (df[key] == str(value))
            return df[mask].to_dict(orient='records')
        except KeyError as e:
            raise KeyError(f"One or more condition keys not found in configs: {e}")
    
    def update(self,col, value, where={}):
        df = self.get_all_configs()
        mask = pd.Series(True, index=df.index)
        try:
            for key, cond_value in where.items():
                mask &= (df[key] == str(cond_value))
                
            df.loc[mask, col] = value
        except KeyError as e:
            raise KeyError(f"One or more condition keys not found in configs: {e}")
        
        
        try:
            df.to_csv(self.run_configs_path, index=False)
        except Exception as e:
            raise IOError(f"Failed to update config in {self.run_configs_path}: {e}")
        
    def delete(self, **conditions):
        # can delete records only by primary keys
        if not os.path.exists(self.run_configs_path):
            raise FileNotFoundError(f"run_configs.csv not found at {self.run_configs_path}")
        
        try:
            df = pd.read_csv(self.run_configs_path, dtype=str)
            mask = True
            
            try:
                for key, cond_value in conditions.items():
                    if key in self.primary_keys:
                        mask &= (df[key] == str(cond_value))
            except KeyError as e:
                raise KeyError(f"One or more condition keys not found in configs: {e}")
            
            # only delete if mask if of instance pd.series
            if isinstance(mask, pd.Series):
                df = df[~mask].reset_index(drop=True)
            df.to_csv(self.run_configs_path, index=False)
        except Exception as e:
            raise IOError(f"Failed to delete config from {self.run_configs_path}: {e}")