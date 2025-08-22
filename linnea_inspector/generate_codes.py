import os
import sys
import linnea.config
from linnea.algorithm_generation.graph.search_graph import SearchGraph
import shutil


def generate_algorithm_codes(equations, alg_codes_path, num_algs_limit=50, time_limit_sec=60):
    
    algs_codes_path = os.path.abspath(alg_codes_path)
    if alg_codes_path[-1] == '/':
        alg_codes_path = alg_codes_path[:-1]
        
    linnea.config.set_output_code_path(os.path.dirname(alg_codes_path))
    linnea.config.init()
    
    graph = SearchGraph(equations)
    graph.generate(time_limit=time_limit_sec,
                   merging=True,
                   dead_ends=True,
                   pruning_factor=1.2)

    graph.write_output(code=True,
                       generation_steps=True,
                       output_name=os.path.basename(alg_codes_path),
                       experiment_code=False,
                       algorithms_limit=num_algs_limit,
                       graph=False,
                       no_duplicates=True)
    

def generate_experiment_codes(alg_codes_path, exp_template_path,tag='', **kwargs):
    # Ensure paths exist
    alg_codes_path = os.path.abspath(alg_codes_path)
    if not os.path.isdir(alg_codes_path):
        print(f"Error: '{alg_codes_path}' is not a valid directory.")
        sys.exit(1)

    if not os.path.isfile(exp_template_path):
        print(f"Error: '{exp_template_path}' not found.")
        sys.exit(1)


    # Load template
    with open(exp_template_path, "r") as tf:
        template_content = tf.read()

    # Process each algorithm file
    algorithm_files = [
        f for f in os.listdir(os.path.join(alg_codes_path, "Julia/generated"))
        if f.startswith("algorithm") and f.endswith(".jl")
    ]

    exp_codes_path = os.path.join(alg_codes_path, f"Julia/experiments{tag}")
    if os.path.exists(exp_codes_path):
        #remove existing directory
        shutil.rmtree(exp_codes_path)
    os.makedirs(os.path.join(exp_codes_path,"traces"), exist_ok=True)
        
    run_commands = []
    for filename in sorted(algorithm_files):
        algorithm_id = filename.rsplit('.', 1)[0]

        # Fill in template
        filled = template_content.format(
            algorithm_id=algorithm_id,
            **kwargs
        )
        
        output_file = os.path.join(exp_codes_path, f"run_{algorithm_id}.jl")
        with open(output_file, "w") as outf:
            outf.write(filled)
            
        run_command = f"julia run_{algorithm_id}.jl > traces/{algorithm_id}.traces"
        run_commands.append(run_command)

    # Write the run.sh script
    run_script_path = os.path.join(exp_codes_path, "run.sh")
    with open(run_script_path, "w") as runfile:
        runfile.write("#!/bin/bash\n\n")
        for cmd in run_commands:
            runfile.write(cmd + "\n")
        runfile.write("python -m linnea_inspector.synthesis traces/")

    # Make run.sh executable
    os.chmod(run_script_path, 0o755)

    print(f"Generated {len(algorithm_files)} run scripts in '{exp_codes_path}/'")

    
    
