import os
import shutil
import json

def add_parser(subparsers):
    p = subparsers.add_parser('runner', help='Generate run scripts for the generated algs.')
    p.add_argument("--gen_dir", required=True, help="Path to the generation directory containing gen_config.json and generated algorithms.")
    p.add_argument("--run_template", required=True, help="Path to the run script template file.")
    p.add_argument("--nthreads", required=True, help="Number of threads to use when running the algorithms.")
    p.add_argument("--nreps", required=False, default=10, help="Number of repetitions for each algorithm run.")
    
def runner(args):
    gen_dir = args.gen_dir
    run_template = args.run_template
    nthreads = args.nthreads
    nreps = args.nreps
    
    
    try:      
        gen_config = json.load(open(os.path.join(gen_dir, "gen_config.json"), 'r'))
        prob_size = gen_config.get("prob_size", {})    
        #read the template file
        with open(run_template, 'r') as f:
            template_str = f.read()
            
        algorithm_files = [
            f for f in os.listdir(os.path.join(gen_dir, "Julia/generated"))
            if f.startswith("algorithm") and f.endswith(".jl")
        ]
        
    except Exception as e:
        raise ValueError(f"Error reading generation configuration: {e}")
    
    run_dir = os.path.join(gen_dir, "runs")
    if os.path.exists(run_dir):
        shutil.rmtree(run_dir)
    os.makedirs(run_dir)
    
    template_args = prob_size.copy()
    template_args["nthreads"] = nthreads
    template_args["nreps"] = nreps
    
    run_commands = []
    for filename in sorted(algorithm_files):
        algorithm_id = filename.rsplit('.', 1)[0]

        # Fill in template
        filled = template_str.format(
            algorithm_id=algorithm_id,
            **template_args
        )
        
        output_file = os.path.join(run_dir, f"run_{algorithm_id}.jl")
        with open(output_file, "w") as outf:
            outf.write(filled)
            
        run_command = f"julia run_{algorithm_id}.jl > traces/{algorithm_id}.traces"
        run_commands.append(run_command)
     
    os.makedirs(os.path.join(run_dir, "traces"), exist_ok=True)
    
    # Write the run.sh script
    run_script_path = os.path.join(run_dir, "run.sh")
    
    with open(run_script_path, "w") as runfile:
        runfile.write("#!/bin/bash\n\n")
        for cmd in run_commands:
            runfile.write(cmd + "\n")

    # Make run.sh executable
    os.chmod(run_script_path, 0o755)
    
    run_config = {
        "expr": gen_config["expr_name"],
        "prob_size": "+".join([f"{k}_eq_{v}" for k, v in prob_size.items()]),
        "nthreads": nthreads,
        "niter": nreps,
        "alg_codes_path": os.path.abspath(os.path.join(gen_dir, "Julia/generated")),
    }
    
    with open(os.path.join(run_dir, "_run_config.json"), 'w') as f:
        json.dump(run_config, f, indent=4)

    print(f"Generated {len(algorithm_files)} run scripts in '{run_dir}/'")
    
