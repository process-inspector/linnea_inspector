#!/bin/bash
cd "$(dirname "$0")/.."

python -m linnea_inspector.cli generator \
        --generation_dir=tests/generation/gls/linnea_codes1/ \
        --language=Julia \
        --precision=Float64 \
        --equations_file=tests/generation/gls/equations.py \
        --m 1000 -n 200 \
        --expr_name=GLS \
        --overwrite