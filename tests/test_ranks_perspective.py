# Linnea Inspector
# Copyright (c) 2021-2026 Aravind Sankaran
#
# SPDX-License-Identifier: AGPL-3.0-or-later
# See LICENSE file in the project root for full license information.

from linnea_inspector.data_processor import LogsProcessor
from linnea_inspector.store.experiment_store import ExperimentReader

from process_inspector.activity_log import ActivityLog
from linnea_inspector.classifiers.f_call import f_call

from linnea_inspector.object_context import ObjectContext
from linnea_inspector.dfg.context import DFGContext
from linnea_inspector.dfg.ranks_perspective import DFGRanksPerspective

import os

def test_lp(log_dir):
    
    processor = LogsProcessor(log_dir=log_dir, parse_run_config=True, sep=';')   
    processor.process()
    
    obj_context = ObjectContext(processor.case_md, obj_key='alg', compute_ranks=True)
    
    activity_log = ActivityLog(processor.event_log, f_call) 
    
    dfg_context = DFGContext(activity_log, obj_context.data, obj_key='alg', compute_ranks=True)
    
    ranking_method = 'm1'
    dfg_perspective = DFGRanksPerspective(ranking_method,
                                          dfg_context.activity_data, 
                                          dfg_context.relation_data,
                                          obj_context.data)
    
    dfg_perspective.create_style()
    graph = dfg_perspective.prepare_digraph(rankdir='TD')
    print(graph)
    graph.render(os.path.join('tests/dfgs/', 'dfg_ranks_lp'), format='svg', cleanup=True)
    print("SUCCESS")

    
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
    
    activity_log = reader.get_activity_log(confs, add_objs_from_config=['expr', 'prob_size'])

    dfg_context = DFGContext(activity_log, obj_context.data, obj_key='alg', compute_ranks=True)
    
    ranking_method = 'm1'
    dfg_perspective = DFGRanksPerspective(ranking_method,
                                          dfg_context.activity_data, 
                                          dfg_context.relation_data,
                                          obj_context.data)
    
    dfg_perspective.create_style()
    graph = dfg_perspective.prepare_digraph(rankdir='TD')
    print(graph)
    
    graph.render(os.path.join('tests/dfgs/', 'dfg_ranks_rs'), format='svg', cleanup=True)
    print("SUCCESS")
    
if __name__ == "__main__":
    log_dir = "tests/traces/b0"
    test_lp(log_dir)
    
    store_path = ["tests/store/test.rs",]
    test_store(store_path)