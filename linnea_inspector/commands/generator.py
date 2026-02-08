import os
import linnea.config
from linnea.algorithm_generation.graph.search_graph import SearchGraph
import importlib.util
import json
import random
import argparse

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
    p = subparsers.add_parser('generator', help='Generate algorithms using Linnea.')
    p.add_argument("--config", required=True, help="Path to the configuration file. Usage: linnea-inspector generator --config=path/to/config.json --key1=value1 --key2=value2'")

def generator(args, params):
    random.seed(0)
    config_path = args.config
    prob_size = parse_kwargs(params)
    
    try:
        config = json.load(open(config_path, 'r'))
    except Exception as e:
        raise ValueError(f"Error loading configuration file: {e}")
    
    try:
        expr_name = config['expr_name']
        equations_file = config['equations_file']
        gen_dir = config['generation_dir']
        num_algs_limit = int(config.get('num_algs_limit', 10))
        time_limit_sec = int(config.get('gen_time_limit_sec', 60))
        pruning_factor = float(config.get('pruning_factor', 1.0))
    except KeyError as e:
        raise ValueError(f"Missing required configuration parameter: {e}")
    
    try:
        spec = importlib.util.spec_from_file_location("equations_module", equations_file)
        equations_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(equations_module)
        print(prob_size)
        equations = equations_module.get_equations(**prob_size)
    except Exception as e:
        raise ValueError(f"Error loading equations from file: {e}")
    
        
    gen_dir = os.path.abspath(gen_dir)
    if gen_dir.endswith("/"):
        gen_dir = gen_dir[:-1]
        
    if not os.path.exists(gen_dir):
        os.makedirs(gen_dir, exist_ok=True)
        
    linnea.config.set_output_code_path(os.path.dirname(gen_dir))
    linnea.config.init()
    linnea.config.instrument = True
    
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
    
    #write the config to alg_dir for later use
    config['prob_size'] = prob_size
    alg_config_path = os.path.join(gen_dir, "gen_config.json")
    with open(alg_config_path, 'w') as f:
        json.dump(config, f, indent=4)
        