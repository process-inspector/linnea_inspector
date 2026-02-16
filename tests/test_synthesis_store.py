
# Linnea Inspector
# Copyright (c) 2021-2026 Aravind Sankaran
#
# SPDX-License-Identifier: AGPL-3.0-or-later
# See LICENSE file in the project root for full license information.

import json
import os
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

from linnea_inspector.store.experiment_store import ExperimentReader, find_store_paths
from linnea_inspector.store.synthesis_store import SynthesisWriter, SynthesisReader

from process_inspector.activity_log import ActivityLog
from linnea_inspector.classifiers.f_call import f_call

from linnea_inspector.object_context import ObjectContext
from linnea_inspector.dfg.context import DFGContext
from linnea_inspector.dfg.ranks_perspective import DFGRanksPerspective

from process_inspector.schemas import ObjectSchema, ActivitySchema, RelationSchema

from linnea_inspector.anomaly import is_anomaly

def test_write(store_root):
    store_paths = find_store_paths(store_root)
    reader = ExperimentReader(store_paths)
    
    confs = reader.get_confs(
        expr="GLS_XX",
        prob_size="[1000, 1000]")
    
    if not confs:
        print("No configurations found.")
        return
    
    # print(confs)
    case_md = reader.get_case_md(confs)
    obj_context = ObjectContext(case_md, obj_key='alg', compute_ranks=True)
    
    activity_log = reader.get_activity_log(confs, class_name="f_call")

    dfg_context = DFGContext(activity_log, obj_context.data, obj_key='alg', compute_ranks=True)
    
    
    # synth_store_path = get_experiment_db_path(confs[0], store_path[0], db_folder="synthesis")
    synth_store_path = os.path.join(store_paths[0], "synthesis")
    synth_conf = confs[0].copy()
    # remove obj_key if the obj is other than alg
    # synth_conf.pop('cluster_name', None)
    
    synthesis_writer = SynthesisWriter(synth_store_path, synth_conf)
    
    synthesis_writer.write_context(
        class_name="f_call",
        object_context_data=obj_context.data,
        activity_context_data=dfg_context.activity_data,
        relation_context_data=dfg_context.relation_data,
    )
    
    anomaly_m1 = is_anomaly('m1', obj_context.data)
    anomaly_m2 = is_anomaly('m2', obj_context.data)
    anomaly_m3 = is_anomaly('m3', obj_context.data)
    stats_data = {
        "anomaly_m1": anomaly_m1,
        "anomaly_m2": anomaly_m2,
        "anomaly_m3": anomaly_m3
    }
    synthesis_writer.write_stats(stats_data)
    
    print("SUCCESS") 
    
def test_read(store_root):
    store_paths = find_store_paths(store_root)
    reader = ExperimentReader(store_paths)
    confs = reader.get_confs(
        expr="GLS_XX",
        prob_size="[1000, 1000]")
    
    if not confs:
        print("No configurations found.")
        return
    
    config = confs[0]
    
    synth_store_path = os.path.join(store_paths[0], "synthesis")
    # remove obj_key from config if the obj is other than alg
    synthesis_reader = SynthesisReader(synth_store_path, config)
    
    context_data = synthesis_reader.get_context(
        class_name="f_call"
    )
    
    print("Object Context Data:")
    print(context_data['object'])
    
    activity_context_data = ActivitySchema.model_validate_json(context_data['activity'])
    relation_context_data = RelationSchema.model_validate_json(context_data['relation'])
    object_context_data = ObjectSchema.model_validate_json(context_data['object'])

    ranking_method = 'm1'
    dfg_perspective = DFGRanksPerspective(ranking_method,
                                          activity_context_data, 
                                          relation_context_data,
                                          object_context_data)
    
    dfg_perspective.create_style()
    graph = dfg_perspective.prepare_digraph(rankdir='TD')
    print(graph)
    
    graph.render(os.path.join('tests/dfgs/', 'dfg_ranks_synth_rs'), format='svg', cleanup=True)
    
    stats_data = synthesis_reader.get_stats()
    print("Stats Data:")
    print(stats_data)
    print("SUCCESS") 
    
if __name__ == "__main__":
    store_root = "tests/store/test.rs"
    
    test_write(store_root)
    test_read(store_root)