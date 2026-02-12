import os
import linnea.config
from linnea.algorithm_generation.graph.search_graph import SearchGraph
import importlib.util
import json
import random
import argparse
import shutil

def parse_kwargs(tokens):
    out = {}
    i = 0
    while i < len(tokens):
        t = tokens[i]

        if t == "--":
            i += 1
            continue

        if not t.startswith("-"):
            raise ValueError(f"Unexpected bare argument: {t}")

        # Handle --k=v or -k=v
        if "=" in t:
            k, v = t.split("=", 1)
            out[k.lstrip("-")] = v
            i += 1
            continue

        key = t.lstrip("-")

        # Handle flag with no value
        if i + 1 >= len(tokens) or tokens[i + 1].startswith("-"):
            out[key] = True
            i += 1
            continue

        # Handle --k v or -k v
        out[key] = tokens[i + 1]
        i += 2

    return out

def add_parser(subparsers):
    # may be gen_dir should be arg
    p = subparsers.add_parser('generator',
                              usage="linnea-inspector generator --generation_dir <dir> --language [Julia,] --precision=[Float32, Float64] --equations_file <file> [--config <config_file>] [--expr_name <name>] [problem sizes kwargs] [--overwrite]",
                              help='Generate algorithms using Linnea.')
    p.add_argument("--generation_dir", required=True, help="Directory to store generated algorithms.")
    p.add_argument("--language", required=True, help="Programming language for the generated code (currently supports: Julia, ).")
    p.add_argument("--equations_file", required=True, help="Path to the equations file.")
    p.add_argument("--config", required=False, help="Path to the configuration file.")
    p.add_argument("--expr_name", required=False, help="Name of the expression being generated. Default is to look for name variable in equations file.")
    p.add_argument("--precision", required=True, help="Precision for the generated code (currently supports: Float64, Float32).")
    p.add_argument("--overwrite", action='store_true', help="Whether to overwrite the generation directory if it already exists. Default is False.")

def sanity_check_and_configure(args, params):
    config = {}
    if args.config:
        config_path = args.config
        if not os.path.exists(config_path):
            raise ValueError(f"Configuration file {config_path} does not exist.")
        try:
            config = json.load(open(config_path, 'r'))
        except Exception as e:
            raise ValueError(f"Error loading configuration file: {e}")
    
    language = args.language
    if language not in ["Julia"]:
        raise ValueError(f"Unsupported language: {language}. Currently only Julia is supported.")
    
    linnea.config.set_language(linnea.config.Language.Julia)
    
    precision = args.precision
    
    if precision not in ["Float64", "Float32"]:
        raise ValueError(f"Unsupported precision: {precision}. Currently only Float64 and Float32 are supported.")
    
    if precision == "Float64":
        linnea.config.set_data_type(linnea.config.JuliaDataType.Float64)
    elif precision == "Float32":
        linnea.config.set_precision(linnea.config.JuliaDataType.Float32)
        
    equations_file = args.equations_file
    if not os.path.exists(equations_file):
        raise ValueError(f"Equations file {equations_file} does not exist.")
    
    prob_size = parse_kwargs(params)
    try:
        spec = importlib.util.spec_from_file_location("equations_module", equations_file)
        equations_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(equations_module)
        equations = equations_module.get_equations(**prob_size)
    except Exception as e:
        raise ValueError(f"Error loading equations from file: {e}")
    
    if args.expr_name:
        expr_name = args.expr_name
    elif hasattr(equations, 'name'):
        expr_name = equations_module.name
    else:
        raise ValueError("Expression name not found in equations file. Please provide --expr_name argument.")
    
    if not hasattr(equations_module, 'op_info'):
        raise ValueError("Equations file must define op_info variable with operands information.")
    
    try:
        eqn_input = equations_module.op_info["input"]
        eqn_output = equations_module.op_info["output"]
    except Exception as e:
        raise ValueError(f"Error extracting input/output operator information from equations file: {e}")
      
    config['language'] = language
    config['precision'] = precision
    
    if not "num_algs_limit" in config:
        config["num_algs_limit"] = 10
    if not "gen_time_limit_sec" in config:
        config["gen_time_limit_sec"] = 60
    if not "pruning_factor" in config:
        config["pruning_factor"] = 1.0
        
    config['expr_name'] = expr_name
    config['generation_dir'] = args.generation_dir
    config['equations_file'] = equations_file
    config['equation'] = equations.__str__()
    config['eqn_input'] = eqn_input
    config['eqn_output'] = eqn_output
    config['prob_size'] = prob_size
    config['generation_dir'] = args.generation_dir
    
    
    if os.path.exists(config['generation_dir']):
        if args.overwrite:
            print(f"Warning: Generation directory {config['generation_dir']} already exists. Overwriting as --overwrite flag is set.")
            shutil.rmtree(config['generation_dir'])
            os.makedirs(config['generation_dir'], exist_ok=True)
        else:
            raise ValueError(f"Generation directory {config['generation_dir']} already exists and may contain trace data. Remove this director or Use --overwrite flag to overwrite.")
        
    return expr_name, equations, prob_size, config
    

def generator(args, params):
    random.seed(0)
    
    try:
        expr_name, equations, prob_size, config = sanity_check_and_configure(args, params)
    except AssertionError as ae:
        print(f"Sanity check failed: {ae}")
        return
    except ValueError as ve:
        print(f"Configuration error: {ve}")
        return
    
        
    gen_dir = os.path.abspath(config["generation_dir"])
    if gen_dir.endswith("/"):
        gen_dir = gen_dir[:-1]
    
    #configure linnea    
    linnea.config.set_output_code_path(os.path.dirname(gen_dir))
    linnea.config.init()
    linnea.config.instrument = True
    
    time_limit_sec = config["gen_time_limit_sec"]
    pruning_factor = config["pruning_factor"]
    num_algs_limit = config["num_algs_limit"]
    
    graph = SearchGraph(equations)
    graph.generate(time_limit=time_limit_sec,
                   merging=True,
                   dead_ends=True,
                   pruning_factor=pruning_factor)

    graph.write_output(code=True,
                       generation_steps=True,
                       output_name=os.path.basename(gen_dir),
                       experiment_code=False,
                       algorithms_limit=num_algs_limit,
                       graph=False,
                       no_duplicates=True)
    
    alg_config_path = os.path.join(gen_dir, "gen_config.json")
    with open(alg_config_path, 'w') as f:
        json.dump(config, f, indent=4)
        