
import json
import os
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

from linnea_inspector.rocks_store import RSReader
from linnea_inspector.rocks_store import RSSynthesisWriter, RSSynthesisReader

from process_inspector.activity_log import ActivityLog
from linnea_inspector.classifiers.f_call import f_call

from linnea_inspector.object_context import ObjectContext
from linnea_inspector.dfg.context import DFGContext
from linnea_inspector.dfg.ranks_perspective import DFGRanksPerspective

from process_inspector.schemas import ObjectSchema, ActivitySchema, RelationSchema

def test_write(store_path):
    rs_reader = RSReader(store_path)
    confs = rs_reader.get_confs(
        expr="GLS_XX",
        prob_size="[1000, 1000]")
    
    if not confs:
        print("No configurations found.")
        return
    
    case_md = rs_reader.get_case_md(confs)
    obj_context = ObjectContext(case_md, obj_key='alg', compute_ranks=True)
    
    activity_log = rs_reader.get_activity_log(confs, class_name="f_call")

    dfg_context = DFGContext(activity_log, obj_context.data, obj_key='alg', compute_ranks=True)
    
    
    
    synthesis_writer = RSSynthesisWriter(store_path[0]) # can be different from read store path
    
    synthesis_writer.write_context(
        class_name="f_call",
        object_context_data=obj_context.data,
        activity_context_data=dfg_context.activity_data,
        relation_context_data=dfg_context.relation_data,
        language=confs[0]['language'],
        expr=confs[0]['expr'],
        cluster_name=confs[0]['cluster_name'],
        aarch=confs[0]['aarch'],
        n_threads=confs[0]['nthreads'],
        problem_size=confs[0]['prob_size']
    )
    print("SUCCESS") 
    
def test_read(store_path):
    rs_reader = RSReader(store_path)
    confs = rs_reader.get_confs(
        expr="GLS_XX",
        prob_size="[1000, 1000]")
    
    if not confs:
        print("No configurations found.")
        return
    
    config = confs[0]
    
    synthesis_reader = RSSynthesisReader(store_path[0])
    
    context_data = synthesis_reader.get_context(
        class_name="f_call",
        language=config['language'],
        expr=config['expr'],
        cluster_name=config['cluster_name'],
        aarch=config['aarch'],
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
    store_path = ["tests/store/test.rs",]
    
    # test_write(store_path)
    test_read(store_path)