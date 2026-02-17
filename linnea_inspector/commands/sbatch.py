import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
import os
import pandas as pd
from ..store.config_manager import ConfigManager

def add_parser(subparsers):
    p = subparsers.add_parser("sbatch",
                              usage="linnea-inspector sbatch -p <parameter_file> [-r <store_dir>] [--limit <job_limit>] submit_script.sh [script_args]",
                              help="Wrapper around sbatch that accepts arguments from a parameter file") 
    p.add_argument("-p", "--parameters", required=True, help="Path to csv parameter file")
    p.add_argument("-r", "--resume", required=False, help="Path to the store on which the experiments have to be resumed.")
    p.add_argument("--limit", required=False, default=10, help="Limit the number of experiments to submit.")
    
def prepare_experiments(parameters_df, store_dir):
    config_manager = ConfigManager(store_dir)
    
    parameters_df = parameters_df.astype(str)
    _df = config_manager.get_all_configs()
    _df["m"] = _df["prob_size"].apply(lambda x: x.split("+")[0].split("_eq_")[1])
    _df["n"] = _df["prob_size"].apply(lambda x: x.split("+")[1].split("_eq_")[1])
    
    # remove records from parameters_df that are already present in _df["m", "n"]
    merged_df = parameters_df.merge(_df[["m", "n"]], on=["m", "n"], how="left", indicator=True)
    experiments_df = merged_df[merged_df["_merge"] == "left_only"].drop(columns=["_merge"])
    
    return experiments_df
    

def sbatch(args, params):
    if len(params) == 0:
        # print help message from argparse
        logger.error('No submit script provided.\n Usage: linnea-inspector sbatch -p <parameter_file> [-s <store_dir>] submit_script.sh [script_args]')
        return
    
    if not params[0].endswith(".sh"):
        logger.error(f"Invalid argument {params[0]}.")
        return    
        
    parameters_df = pd.DataFrame()
    try:
        parameters_df = pd.read_csv(args.parameters, sep=';')
    except Exception as e:
        logger.error(f"Error reading parameter file {args.parameters}: {e}")
        return
    
    if args.resume:
        try:
            parameters_df = prepare_experiments(parameters_df, args.resume)
        except Exception as e:
            logger.error(f"Error preparing experiments with store {args.resume}: {e}")
            return
    
    try:
        limit = int(args.limit)
    except ValueError:
        logger.error(f"Invalid limit value {args.limit}. Must be an integer.")
        return
    
    experiments = parameters_df.head(int(args.limit)).to_dict(orient='records')
    
    logger.info(f"Submitting {len(experiments)} jobs to sbatch.")
    
    for exp in experiments:
        arg_str = ""
        for key, value in exp.items():
            arg_str += f"-{key} {value} "
        command = f"sbatch {params[0]} {arg_str} {' '.join(params[1:])} "
        # execute
        logger.info(f"Submitting job: {command}")
        os.system(command)
    
    
    