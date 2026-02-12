
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
    synthesis_writer = SynthesisWriter(synth_store_path)
    
    synthesis_writer.write_context(
        class_name="f_call",
        object_context_data=obj_context.data,
        activity_context_data=dfg_context.activity_data,
        relation_context_data=dfg_context.relation_data,
        language=confs[0]['language'],
        expr=confs[0]['expr'],
        cluster_name=confs[0]['cluster_name'],
        arch=confs[0]['arch'],
        n_threads=confs[0]['nthreads'],
        problem_size=confs[0]['prob_size']
    )
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
    synthesis_reader = SynthesisReader(synth_store_path)
    
    context_data = synthesis_reader.get_context(
        class_name="f_call",
        language=config['language'],
        expr=config['expr'],
        cluster_name=config['cluster_name'],
        arch=config['arch'],
        n_threads=config['nthreads'],
        problem_size=config['prob_size']
    )
    
    print("Object Context Data:")
    print(context_data['object'])
    
    activity_context_data = ActivitySchema.model_validate_json(context_data['activity'])
    relation_context_data = RelationSchema.model_validate_json(context_data['relation'])
    object_context_data = ObjectSchema.model_validate_json(context_data['object'])

    dfg_perspective = DFGRanksPerspective(activity_context_data, 
                                          relation_context_data,
                                          object_context_data)
    
    dfg_perspective.create_style()
    graph = dfg_perspective.prepare_digraph(rankdir='TD')
    print(graph)
    
    graph.render(os.path.join('tests/dfgs/', 'dfg_ranks_synth_rs'), format='svg', cleanup=True)
    print("SUCCESS") 
    
if __name__ == "__main__":
    store_root = "tests/store/test.rs"
    
    test_write(store_root)
    test_read(store_root)