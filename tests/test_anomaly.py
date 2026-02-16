# Linnea Inspector
# Copyright (c) 2021-2026 Aravind Sankaran
#
# SPDX-License-Identifier: AGPL-3.0-or-later
# See LICENSE file in the project root for full license information.


from linnea_inspector.store.experiment_store import ExperimentReader

from process_inspector.activity_log import ActivityLog
from linnea_inspector.classifiers.f_call import f_call

from linnea_inspector.object_context import ObjectContext
from linnea_inspector.dfg.context import DFGContext
from linnea_inspector.dfg.ranks_perspective import DFGRanksPerspective
from linnea_inspector.anomaly import is_anomaly


import os

    
def test_store(store_path):
    reader = ExperimentReader(store_path)
    confs = reader.get_confs(
        expr="GLS_XX",
        prob_size="[1000, 1000]")
    
    if not confs:
        print("No configurations found.")
        return
    
    case_md = reader.get_case_md(confs, add_objs_from_config=['expr', 'prob_size'])
    obj_context = ObjectContext(case_md, obj_key='alg', compute_ranks=True)
    
    import pandas as pd
    print(pd.DataFrame(obj_context.data.records))
    print("Anomaly:")
    ranking_method = 'm1'
    print(is_anomaly(ranking_method, obj_context.data))
    
    df = pd.DataFrame(obj_context.data.records)
    df.loc[df['obj'] == 'algorithm10', 'flops_mean'] = 444886666.6666667
    print(df)
    print("Anomaly:")
    obj_context.data.records = df.to_dict(orient='records')
    print(is_anomaly(ranking_method, obj_context.data))
    
    df = pd.DataFrame(obj_context.data.records)
    df.loc[df['obj'] == 'algorithm0', 'flops_mean'] = 445886666.6666667
    print(df)
    print("Anomaly:")
    obj_context.data.records = df.to_dict(orient='records')
    print(is_anomaly(ranking_method, obj_context.data))
    
    print("SUCCESS")
    
if __name__ == "__main__":

    store_path = ["tests/store/test.rs",]
    test_store(store_path)