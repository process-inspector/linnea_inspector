#!/bin/bash
cd "$(dirname "$0")/.."

python -m linnea_inspector.cli  register --cluster_name=kebnekaise --arch=x86 --run_dir=tests/generation/gls/linnea_codes1/runs_24threads_5reps/
