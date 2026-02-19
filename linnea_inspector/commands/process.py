# generate both logs and synthesies store in the data dir..

import json
import os
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from linnea_inspector.data_processor import LogsProcessor
from linnea_inspector.classifiers.f_call import f_call
from process_inspector.activity_log import ActivityLog

from linnea_inspector.store.experiment_store import ExperimentReader, ExperimentWriter
from linnea_inspector.object_context import ObjectContext
from linnea_inspector.dfg.context import DFGContext
from linnea_inspector.store.synthesis_store import SynthesisWriter

from linnea_inspector.anomaly import is_anomaly

import pandas as pd


def add_parser(subparsers):
    p = subparsers.add_parser("process",
                              usage="linnea-inspector process --trace_dir <dir> --store_dir <dir>", 
                              help="Process the trace files from the experiment runs and store the results in the linnea store.")
    p.add_argument("--trace_dir", required=True, help="Path to the directory containing trace files along with run_config.json.")
    p.add_argument("--store_dir", required=True, help="Path to the linnea store directory where processed results will be stored.")
    
def sanity_check_and_config(args):
    trace_dir = args.trace_dir
    assert os.path.exists(trace_dir), f"Trace directory {trace_dir} does not exist."
    
    config_path = os.path.join(trace_dir, "run_config.json")
    assert os.path.exists(config_path), f"Run configuration file {config_path} does not exist in trace directory."
    
    config = json.load(open(config_path, 'r'))
    required_keys = ["cluster_name", "arch", "expr", "language", "precision", "prob_size", "nthreads"]
    for key in required_keys:
        assert key in config, f"Key {key} not found in run_config.json. Please ensure the generator command is run with the correct arguments to include all necessary information in the config."
        
    return config

def perform_synthesis(config, trace_dir, store_dir):

    processor = LogsProcessor(log_dir=trace_dir, parse_run_config=False)
    processor.process()
    activity_log = ActivityLog(processor.event_log, f_call) 
        
    writer = ExperimentWriter(store_dir, config)
    logger.info(f"Opened RS store at {store_dir}")
    writer.write_run_config()
    writer.write_case(processor.case_md)
    writer.write_activity_log(activity_log)
    writer.write_algorithms()
    logger.info(f"Finished writing processed results to RS store at {store_dir}")
    
    reader = ExperimentReader([store_dir,])
    
    confs = reader.get_confs(
        expr=config["expr"],
        prob_size=config["prob_size"],
        language=config["language"],
        cluster_name=config["cluster_name"],
        arch=config["arch"],
        precision=config["precision"],
        nthreads=int(config["nthreads"]),
    )
    
    config['store_path'] = store_dir # add store path to config  for experiment_reader
    confs = [config,] + confs 
    
    if not confs:
        logger.warning(f"No configurations found. Synthesis cannot be performed.")
        return
    
    # print(confs)
    case_md = reader.get_case_md(confs)
    # print(f"Case metadata: {case_md}")
    obj_context = ObjectContext(case_md, obj_key='alg', compute_ranks=True)
    
    anomaly_m1 = is_anomaly('m1', obj_context.data)
    anomaly_m2 = is_anomaly('m2', obj_context.data)
    anomaly_m3 = is_anomaly('m3', obj_context.data)
    
    if anomaly_m1 != 2:
        # only kee all alg with min flops in case_md and recompute object context
        min_flops = case_md['flops'].min()
        case_md = case_md[case_md['flops'] == min_flops]
        obj_context = ObjectContext(case_md, obj_key='alg', compute_ranks=True)
    
    if anomaly_m1 or anomaly_m2 or anomaly_m3:
        logger.info(f"Anomaly detected m1={anomaly_m1}, m2={anomaly_m2}, m3={anomaly_m3}")    
    
    activity_log = reader.get_activity_log(confs, class_name="f_call")
    ## keep only alg in object context
    activity_log = activity_log.apply_filter(lambda record: record['alg'] in obj_context.data.objects)

    dfg_context = DFGContext(activity_log, obj_context.data, obj_key='alg', compute_ranks=True)
    
    synth_store_path = os.path.join(writer.store_path, "synthesis")
    synthesis_writer = SynthesisWriter(synth_store_path, config)
    
    synthesis_writer.write_context(
        class_name="f_call",
        object_context_data=obj_context.data,
        activity_context_data=dfg_context.activity_data,
        relation_context_data=dfg_context.relation_data
    )
    

    stats_data = {
        "anomaly_m1": anomaly_m1,
        "anomaly_m2": anomaly_m2,
        "anomaly_m3": anomaly_m3
    }
    
    synthesis_writer.write_stats(stats_data)
    
    # config["anomaly"] = anomaly
    # # writer.write_run_config()
    # # writer.remove_duplicate_configs()
    # anomaly_path = os.path.join(writer.store_path, "run_stats.csv")
    # if os.path.exists(anomaly_path):
    #     df = pd.read_csv(anomaly_path)
    #     df = df.append(config, ignore_index=True)
    # else:
    #     df = pd.DataFrame([config])
    # df.to_csv(anomaly_path, index=False)
    
    # df = pd.read_csv(anomaly_path).drop_duplicates().reset_index(drop=True)
    # df.to_csv(anomaly_path, index=False)
    
    logger.info(f"Synthesis context written to synthesis store at {synth_store_path}")
    
def process(args):
    
    try:
        config = sanity_check_and_config(args)
        logger.info(f"Processing trace files in {args.trace_dir} with configuration: {config}")
        logger.info(f"Storing processed results in {args.store_dir}")
        perform_synthesis(config, args.trace_dir, args.store_dir)
        
    except AssertionError as ae:
        logger.error(f"Sanity check failed: {ae}")
        raise
    # except Exception as e:
    #     print(f"Error during processing: {e}")
    #     return
