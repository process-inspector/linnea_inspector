# Linnea Inspector

Linear algebra expressions are the building blocks of countless computational problems. Such expressions can often be computed in many different ways, each corresponding to a specific sequence of kernel calls provided by highly optimized libraries such as BLAS and LAPACK. Although these sequences (also referred to as algorithmic variants) are mathematically equivalent, they can differ significantly in performance.

Linnea Inspector is a tool for identifying patterns of kernel operations that lead to suboptimal algorithmic performance.

For a given linear algebra expression, Linnea inspector generates multiple algorithmic variants for different problem sizes using [Linnea](https://github.com/HPAC/linnea.git). The kernel sequences of these variants are traced, and their execution times are measured. The resulting traces are then used to construct process models that identify and predict kernel operation patterns associated with suboptimal performance.

## Setup

### Requirements

- Python (recommended: Python 3.9+)
- Graphviz  
- Julia (Only required for building new models)

The remaining requirements are taken care of in the installation step.  

### Installation

```bash
git clone https://github.com/process-inspector/linnea_inspector.git
cd linnea_inspector
pip install .
```

### Verify

```bash
linnea-inspector -h
```

Output:
```
usage: linnea-inspector <command>

Linnea Inspector CLI

options:
  -h, --help            show this help message and exit

commands:
  {generator,runner,register,process,clean,sbatch,widget,store}
    generator           Generate algorithms using Linnea.
    runner              Generate run scripts for the generated algs.
    register            Register a run by linnea inspector.
    process             Process the trace files from the experiment runs and store the results in the linnea store.
    clean               Clean up data from failed runs.
    sbatch              Wrapper around sbatch that accepts arguments from a parameter file
    widget              Launch the Linnea Inspector web application.
    store               Lauch the Linnea Inspector store web application.
```

## Preparation of Process Models

The typical workflow to prepare process models using Linnea Inspector involves the following steps:

### 1) Generate Algorithms

The input expression is provided as a python script following the same format as [Linnea](https://github.com/HPAC/linnea?tab=readme-ov-file#python-module). The path to the python script is provided as a parameter to the argument `--equations_file`. 

```bash
linnea-inspector generator --equations_file <file> --generation_dir <dir> --language [Julia,] --precision=[Float32, Float64]  [problem sizes kwargs] ...
```
An example equation file for the generalized least squares expressions is shown below:
```python
from linnea.algebra.expression import Matrix, Vector, Equal, Times, Inverse, Transpose
from linnea.algebra.equations import Equations
from linnea.algebra.properties import Property

name = "GLS"

op_info = {
    "input": "X: (n, m); M: (n, n); y: (n, 1)",
    "output": "b: (m, 1)",
}

def get_equations(m,n):
    
        m = int(m)
        n = int(n)
         
        X = Matrix("X", (n, m))
        X.set_property(Property.FULL_RANK)
        M = Matrix("M", (n, n))
        M.set_property(Property.SPD)
        y = Vector("y", (n, 1))
        b = Vector("b", (m, 1))

        equations = Equations(Equal(b, Times(Inverse(Times(Transpose(X), Inverse(M), X ) ), Transpose(X), Inverse(M), y)))
        return equations
```

The script should contain attributes `name` and `op_info` that specify the name of the expression and the input/output variable information respectively. These information are used only for reporting purposes. The generation uses the `get_equations` function that takes problem size parameters as input and returns a `linnea.algebra.equations.Equations` object, which is used by Linnea to search and generate algorithmic variants.

The generated algorithms are stored in the specified `generation_dir`. The problem size parameters are passed as keyword arguments. For example, 

```bash
linnea-inspector generator --equations_file examples/gls_equations.py --generation_dir gls_algorithms --language Julia --precision Float64 --n 1000 --m 500
```
Apart from the algorithms, the `generation_dir` also contains a `json` file which stores the argument values (such as the problem sizes) that could be passed to the later stages of the workflow.

### 2) Generate Run Scripts

The generated algorithms are provided as functions that can be plugged into an arbitrary Julia application. Therefore, a templated run script is required to run the algorithms for measurements. The Julia run script for the GLS expression is shown below. The template file should contain the placeholder `{algorithm_id}` which is replaced by the actual function name of the generated algorithm. The number of threads (`{nthreads}`) and repetitions (`{nreps}`) are passed as parameters to the runner command and are replaced in the template file as shown below. The problem size placeholders `{n}` and `{m}` are replaced by the values specified during the generation step, which are stored in the `json` file in the `generation_dir`. The environment variable `LINNEA_RUN_ID` is set for each repetition, which is used in the algorithm code to log the kernel traces with the corresponding run ID.

```julia
using LinearAlgebra
using Random
using LinearAlgebra.BLAS
BLAS.set_num_threads({nthreads}) 

include("../Julia/generated/{algorithm_id}.jl")  # Import the function

const REP = {nreps}  # Number of repetitions for the algorithm run

# Generate inputs
Random.seed!(123)
X = randn({n}, {m})
A = randn({n}, {n})
M = A * A' + 1e-3 * I  # SPD matrix
y = randn({n})

# Call the algorithm
for i in 1:REP
    ENV["LINNEA_RUN_ID"] = string(i)  # Set the run ID for each iteration
    cache_scrub = randn(100_000_000)
    b = {algorithm_id}(copy(X), copy(M), copy(y))
end
```

This template file is passed via the `--run_template` argument to the `runner` command.

Usage:

```bash
linnea-inspector runner --generation_dir <dir> --run_template <template_file> --nthreads <num_threads> [--nreps <num_repetitions>]
```
This command generates a folder named `runs_<nthreads>t_<nreps>r` inside the `generation_dir`, which contains the run script `run.sh`, which can be executed to run the algorithms and log the traces. Running this script will create a folder named `traces` in the same directory as `run.sh`, which contains the raw kernel traces.

### 3) Register Runs

Execute the run script `run.sh` created inthe previous step. A successful execution creates the trace directory with raw traces. The `register` command is used to register the run with metadata passed as arguments.

```bash
linnea-inspector register --cluster_name <cluster> --arch <architecture> --job_id=<job_id> --run_dir <run_directory> [--batch_id <batch_id>]
```
This command performs sanity checks on the trace dir, and if successful, creates a `run_config.json` file in the directory containing the traces. 

### 4) Process Traces

The traces created in the previous step are used as input to the `process` command, which then prepares the process model and stores them in a key-value store (rocksdb) indicated via the argument ``--store_dir``. 

```bash
linnea-inspector process --trace_dir <dir> --store_dir <dir>
```

After successful execution, the generated algorithms and the raw traces can be deleted. 


## SLURM template

The following script provides a template for process model preparation (steps 1-4) in a SLURM cluster environment. 

```bash
#!/bin/bash
#SBATCH --job-name=linnea.gls
#SBATCH --output=logs/%j.out
#SBATCH --account=<account>
#SBATCH --time=00:15:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=24


# makedir job_id
GEN_DIR="generation/$SLURM_JOB_ID" 
mkdir -p "$GEN_DIR"
EQUATION_FILE="../../../equation.py"
RUN_TEMPLATE="../../run_template.jl"

source <path_to_venv>/bin/activate

linnea-inspector generator \
        --generation_dir=${GEN_DIR} \
        --language=Julia \
        --precision=Float64 \
        --equations_file=${EQUATION_FILE} \
        --m 1500 --n 100 \
        --expr_name=GLS \
        --overwrite

linnea-inspector runner \
        --generation_dir=${GEN_DIR} \
        --run_template=${RUN_TEMPLATE} \
        --nthreads=24 \
        --nreps=10

THIS_DIR=$(pwd)
cd $GEN_DIR/runs_24threads_10reps/

module load Julia
srun -n 1 -c 24 ./run.sh

linnea-inspector register --job_id="$SLURM_JOB_ID" --cluster_name=kebnekaise --arch=x86 --run_dir=.

linnea-inspector process --trace_dir=./traces/ --store_dir=$THIS_DIR/data/store.rs

cd $THIS_DIR
rm -rf $GEN_DIR
```
In order to re-use this script for different problem sizes, consider parameterizing the problem sizes and passing them as arguments to the script such that they can be run as shown below:

```bash
sbatch submit.sh -m 1500 -n 100
```

### Commands for convenience

`linnea-inspector clean --store_dir <dir>`: This command can be used to clean up the data from failed runs. 

`linnea-inspector sbatch -p <csv_parameter_file> submit.sh`: For a submit script with parameterized problem sizes, this command can be used to submit multiple jobs with different problem sizes by providing a csv file with the parameter values. The csv file should have a header row with the parameter names and the subsequent rows should contain the corresponding parameter values. For example, for parameters `m` and `n`, the csv file can be as shown below:

```csv
m,n
1500,100
2000,500
```

By default, the number of submitted jobs is limited to 10. This can be changed by providing the argument `--limit <num_jobs>`. To resume runs from a previous submission, use the argument `--resume <store_dir>` with path to store containing the process models. 




## Identification of suboptimal kernel patterns

The process models generated in the previous step can be inspected using the `widget` command, which launches a local flask server. 

```bash
export LI_STORE_ROOTS=<store_dirs_separated_by_comma>
linnea-inspector widget
```
By default, the server runs on port 8081. This can be changed by setting the environment variale ``TVST_PORT=<value>``.









