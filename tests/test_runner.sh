#!/bin/bash
cd "$(dirname "$0")/.."

 python -m linnea_inspector.cli runner \
        --generation_dir=tests/generation/gls/linnea_codes1/ \
        --run_template=tests/generation/gls/run_template.jl \
        --nthreads=24 \
        --nreps=5
