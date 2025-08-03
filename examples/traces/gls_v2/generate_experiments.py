import os
import sys


base_folder = "algorithms/"
generated_folder = os.path.join(base_folder, "Julia", "generated")
# generated_folder = os.path.join(base_folder)
template_path = "run_template.jl"
output_folder = "experiments"

# Ensure paths exist
if not os.path.isdir(generated_folder):
    print(f"Error: '{generated_folder}' is not a valid directory.")
    sys.exit(1)

if not os.path.isfile(template_path):
    print(f"Error: '{template_path}' not found.")
    sys.exit(1)

os.makedirs(os.path.join(output_folder,"traces"), exist_ok=True)

# Load template
with open(template_path, "r") as tf:
    template_content = tf.read()

# Process each algorithm file
algorithm_files = [
    f for f in os.listdir(generated_folder)
    if f.startswith("algorithm") and f.endswith(".jl")
]

run_commands = []
for filename in sorted(algorithm_files):
    algorithm_id = filename.rsplit('.', 1)[0]

    # Fill in template
    filled = template_content.format(
        algorithm_id=algorithm_id
    )

    # Write to experiments/run_algorithmX.jl
    output_file = os.path.join(output_folder, f"run_{algorithm_id}.jl")
    with open(output_file, "w") as outf:
        outf.write(filled)
        
    run_command = f"julia run_{algorithm_id}.jl > traces/{algorithm_id}.traces"
    run_commands.append(run_command)

# Write the run.sh script
run_script_path = os.path.join(output_folder, "run.sh")
with open(run_script_path, "w") as runfile:
    runfile.write("#!/bin/bash\n\n")
    for cmd in run_commands:
        runfile.write(cmd + "\n")

# Make run.sh executable
os.chmod(run_script_path, 0o755)

print(f"Generated {len(algorithm_files)} run scripts in '{output_folder}/'")
