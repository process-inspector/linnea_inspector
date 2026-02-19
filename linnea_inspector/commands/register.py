import os
import json
from datetime import datetime
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def add_parser(subparsers):
    p = subparsers.add_parser('register',
                              usage="linnea-inspector register --cluster_name <cluster> --arch <architecture> --run_dir <run_directory> [--batch_id <batch_id>]", 
                              help='Register a run by linnea inspector.')
    p.add_argument("--cluster_name", required=True, help="Name of the cluster where the run was executed.")
    p.add_argument("--arch", required=True, help="Architecture of the machine where the run was executed.")
    p.add_argument("--run_dir", required=True, help="Path to the run directory containing the _run_config.json and traces from experiment runs.")
    p.add_argument("--job_id", required=True, help="Job ID for the run.")
    p.add_argument("--batch_id", required=False, type=int, default=0, help="Batch ID for the run, if applicable.")

def sanity_check_and_register(args):
    #1) check if run_dir exists
    run_dir = args.run_dir
    assert os.path.exists(run_dir), f"Run directory {run_dir} does not exist."
    
    #2) check if _run_config.json exists in run_dir
    config_path = os.path.join(run_dir, "_run_config.json")
    assert os.path.exists(config_path), f"Run configuration file {config_path} does not exist in run directory."
    
    #3) check if traces directory exists in run_dir
    traces_dir = os.path.join(run_dir, "traces")
    assert os.path.exists(traces_dir), f"Traces directory {traces_dir} does not exist in run directory."
    
    #4) check if for each run_algorithm_id.jl in run_dir, there is a corresponding traces/algorithm_id.traces file that is not empty
    for filename in os.listdir(run_dir):
        if filename.startswith("run_algorithm") and filename.endswith(".jl"):
            algorithm_id = filename[len("run_"):-len(".jl")]
            trace_file = os.path.join(traces_dir, f"{algorithm_id}.traces")
            assert os.path.exists(trace_file), f"Trace file {trace_file} does not exist for algorithm {algorithm_id}."
            assert os.path.getsize(trace_file) > 0, f"Trace file {trace_file} for algorithm {algorithm_id} is empty."
            
    # If all checks pass, read _run_config.json, add key timestamp with current date time, and write the file as run_config.json to traces dir
    run_config = json.load(open(config_path, 'r'))
    
    run_config["cluster_name"] = args.cluster_name
    run_config["arch"] = args.arch
    run_config["job_id"] = args.job_id
    run_config["batch_id"] = args.batch_id
    run_config["timestamp"] = datetime.now().isoformat()
    try:
        with open(os.path.join(traces_dir, "run_config.json"), 'w') as f:
            json.dump(run_config, f, indent=4)
    except Exception as e:
        raise ValueError(f"Error writing run_config.json to traces directory: {e}")
        
def register(args):
    
    try:
        sanity_check_and_register(args)
        logger.info(f"Run registered successfully for cluster_name={args.cluster_name}, arch={args.arch}, batch_id={args.batch_id}")
    except AssertionError as ae:
        logger.error(f"Sanity check failed: {ae}")
        raise
    except Exception as e:
        logger.error(f"Error during registration: {e}")
        raise