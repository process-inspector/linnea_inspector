from .. import config
from linnea_inspector.store.synthesis_store import SynthesisReader
from linnea_inspector.dfg.ranks_perspective import DFGRanksPerspective
from process_inspector.schemas import ObjectSchema, ActivitySchema, RelationSchema
import re
import os


def get_facts_algs(ranking_method, language, expr, cluster_name, arch, precision, n_threads, problem_size):
    reader = config.get_reader()
    confs = reader.get_confs(
        language=language,
        expr=expr,
        cluster_name=cluster_name,
        arch=arch,
        precision=precision,
        nthreads=int(n_threads),
        prob_size=problem_size
    )
    if not confs:
        raise ValueError("No configurations found for the given parameters.")
    
    store_path = confs[0]['store_path']
    synth_store_path = os.path.join(store_path, "synthesis")
    synthesis_reader = SynthesisReader(synth_store_path, confs[0])
    
  
    context_data = synthesis_reader.get_context(
        class_name="f_call"
    )
    
    activity_context_data = ActivitySchema.model_validate_json(context_data['activity'])
    relation_context_data = RelationSchema.model_validate_json(context_data['relation'])
    object_context_data = ObjectSchema.model_validate_json(context_data['object'])

    dfg_perspective = DFGRanksPerspective(ranking_method,
                                          activity_context_data, 
                                          relation_context_data,
                                          object_context_data)
    
    dfg_perspective.create_style()
    graph = dfg_perspective.prepare_digraph(rankdir='LR')
    
    dfg_svg = graph.pipe(format='svg').decode('utf-8')
    
    node_info = _prepare_node_info_for_rendering(ranking_method, activity_context_data, obj_label="Algorithm")
    object_info = _prepare_object_info_for_rendering(ranking_method, object_context_data, obj_label="Algorithm")
    
    fact_details = {}
    fact_details['language'] = language
    fact_details['expr'] = expr
    fact_details['cluster_name'] = cluster_name
    fact_details['arch'] = arch
    fact_details['precision'] = precision
    fact_details['nthreads'] = n_threads
    fact_details['prob_size'] = problem_size
    
    fact_details['equation'] = confs[0].get('equation', 'N/A')
    fact_details['eqn_input'] = confs[0].get('eqn_input', 'N/A')
    fact_details['eqn_output'] = confs[0].get('eqn_output', 'N/A')
    
    stats_data = synthesis_reader.get_stats()
    anomoaly_m1 = stats_data.get('anomaly_m1', -1)
    anomoaly_m3 = stats_data.get('anomaly_m3', -1)

    fact_details['ranking_method'] = ranking_method        
    fact_details['anomaly'] = f"m1: {anomoaly_m1} / m3: {anomoaly_m3}"
    fact_details['num_objs'] = len(object_context_data.objects)

    return dfg_svg, node_info, object_info, fact_details

            
    
def _prepare_node_info_for_rendering(ranking_method, activity_context_data, obj_label):
    col_schema = [
        {"id": f"rank_{ranking_method}", "label": f"Rank ({ranking_method})", "type": "integer"},
        {"id": "obj", "label": obj_label, "type": "string"},
        {"id": "flops_mean", "label": "FLOPS", "type": "decimal"},
        {"id": "perf_mean", "label": "Avg Performance (GFLOPS/s)", "type": "decimal"},
    ]
        
    node_info = {
        "nodes": activity_context_data.activities,
        "col_schema": col_schema,
        "node_records": activity_context_data.obj_records,
        "pk": "obj",
        "bp_data": activity_context_data.obj_bp_data,
        "ranks": activity_context_data.obj_rank[ranking_method],
        "bp_title": "Performance",
        "bp_x_label": "GFLOPS/s",
    }
    
    return node_info

def _prepare_object_info_for_rendering(ranking_method, object_context_data, obj_label):
    col_schema = [
        {"id": f"rank_{ranking_method}", "label": f"Rank ({ranking_method})", "type": "integer"},
        {"id": "obj", "label": obj_label, "type": "string"},
        {"id": "flops_mean", "label": "FLOPS", "type": "decimal"},
        {"id": "perf_mean", "label": "Avg Performance (GFLOPS/s)", "type": "decimal"},
    ]
    
    bp_data = object_context_data.bp_data
    # convert ns to s for box plot
    for obj in bp_data:
        bp_data[obj] = [d / 1e9 for d in bp_data[obj]]
        
    # in records, convert flops to GFLOPS
    for record in object_context_data.records:
        # record['flops_mean'] = record['flops_mean'] / 1e9
        record['flops_mean'] = int(record['flops_mean'])
        
    object_info = {
        "objects": object_context_data.objects,
        "col_schema": col_schema,
        "records": object_context_data.records,
        "pk": "obj",
        "bp_data": bp_data,
        "ranks": object_context_data.rank[ranking_method],
        "bp_x_label": "Duration (s)",
    }
    
    return object_info