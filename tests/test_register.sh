#!/bin/bash
cd "$(dirname "$0")/.."

JOB_ID=L$(date +"%m%d%H%M%S")

python -m linnea_inspector.cli  register --job_id="$JOB_ID" --cluster_name=kebnekaise --arch=x86 --run_dir=tests/generation/gls/linnea_codes1/runs_24threads_5reps/
