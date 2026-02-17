#!/bin/bash
cd "$(dirname "$0")/.."

python -m linnea_inspector.cli clean --store_dir tests/store/test.cli
python -m linnea_inspector.cli clean --store_dir tests/store/test.cli --experiment
