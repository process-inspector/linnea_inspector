#!/bin/bash
#SBATCH --job-name=linnea.gls
#SBATCH --output=logs/%j.out
#SBATCH --account=hpc2n2025-096
#SBATCH --time=00:20:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=24
#SBATCH --gpus-per-node=2


########################################
# Parse command line arguments
########################################

M=""
N=""

while getopts ":m:n:" opt; do
  case $opt in
    m) M="$OPTARG" ;;
    n) N="$OPTARG" ;;
    \?)
      echo "Invalid option: -$OPTARG" >&2
      exit 1
      ;;
    :)
      echo "Option -$OPTARG requires an argument." >&2
      exit 1
      ;;
  esac
done

########################################
# Check required arguments
########################################

if [[ -z "$M" || -z "$N" ]]; then
    echo "ERROR: You must provide -m and -n arguments."
    echo "Usage: sbatch script.sh -m <rows> -n <cols>"
    exit 1
fi

# makedir job_id
GEN_DIR="tests/generation/$SLURM_JOB_ID" 
EQUATION_FILE="tests/generation/gls/equations.py"
RUN_TEMPLATE="tests/generation/gls/run_template.jl"
mkdir -p "$GEN_DIR"

source /proj/nobackup/aravind/LAAB/venvs/kebnekaise/activate.sh

linnea-inspector generator \
        --generation_dir=${GEN_DIR} \
        --language=Julia \
        --precision=Float64 \
        --equations_file=${EQUATION_FILE} \
        --m "$M" -n "$N" \
        --expr_name=GLS \
        --num_algs_limit 15 \
        --gen_time_limit_sec 60 \
        --pruning_factor 1.2 \
        --overwrite

linnea-inspector runner \
        --generation_dir=${GEN_DIR} \
        --run_template=${RUN_TEMPLATE} \
        --nthreads=24 \
        --nreps=10

THIS_DIR=$(pwd)

module load Julia

cd $GEN_DIR/runs_24threads_10reps/
srun -n 1 -c 24 ./run.sh

linnea-inspector register --job_id="$SLURM_JOB_ID" --cluster_name=kebnekaise --arch=x86 --run_dir=.

linnea-inspector process --trace_dir=./traces/ --store_dir=$THIS_DIR/tests/store/store.sb

cd $THIS_DIR
rm -rf $GEN_DIR

