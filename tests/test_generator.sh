#!/bin/bash
cd "$(dirname "$0")/.."

python -m linnea_inspector.cli generator \
        --generation_dir=tests/generation/gls/linnea_codes1/ \
        --language=Julia \
        --precision=Float64 \
        --equations_file=tests/generation/gls/equations.py \
        --m 2048 -n 128 \
        --expr_name=GLS \
        --overwrite \
        # --store_dir=tests/store/test.cli