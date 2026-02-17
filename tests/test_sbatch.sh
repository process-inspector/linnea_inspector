 #!/bin/bash
cd "$(dirname "$0")/.."

 python -m linnea_inspector.cli sbatch -p tests/generation/gls/parameters.csv -r tests/store/store.sb/ --limit 10 tests/submit.sh
