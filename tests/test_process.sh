#!/bin/bash
cd "$(dirname "$0")/.."

python -m linnea_inspector.cli process --trace_dir=tests/generation/gls/linnea_codes1/runs_24threads_5reps/traces/ --store_dir=tests/store/test.cli
