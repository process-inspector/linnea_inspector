# Linnea Inspector
# Copyright (c) 2021-2026 Aravind Sankaran
#
# SPDX-License-Identifier: AGPL-3.0-or-later
# See LICENSE file in the project root for full license information.

from linnea_inspector.store.experiment_store import ExperimentReader
from linnea_inspector.store.utils import delete_experiment, update_synthesis

def test_delete():
    store_path = ["tests/store/test.rs",]
    reader = ExperimentReader(store_path)

    confs = reader.get_confs(prob_size="[1000, 1000]", batch_id=1)

    for conf in confs:
        delete_experiment(conf)
    
    confs = reader.get_confs(prob_size="[1000, 1000]")
    update_synthesis(confs[0])
    
    print("SUCCESS")
    
if __name__ == "__main__":
    test_delete()    
    