    
from .. import config
from linnea_inspector.store.synthesis_store import SynthesisReader
import os

def prepare_facts_table_algs(df):
    col_schema = [
        {"id": "language", "label": "Language", "type": "string"},
        {"id": "expr", "label": "Expression", "type": "string"},
        {"id": "cluster_name", "label": "Cluster", "type": "string"},
        {"id": "arch", "label": "Arch", "type": "string"},
        {"id": "precision", "label": "Precision", "type": "string"},
        {"id": "nthreads", "label": "N. Threads", "type": "integer"},
        {"id": "prob_size", "label": "Problem Size", "type": "string"},
    ]
    
    df = df.copy()
    df = df[[col['id'] for col in col_schema] + ['store_path']]
    # Remove duplicates
    df = df.drop_duplicates()
    
    records = df.to_dict('records')
    for record in records:
        store_path = record.get('store_path')
        synth_reader = SynthesisReader(os.path.join(store_path,"synthesis"), record)
        stats_data = synth_reader.get_stats()
        record['anomaly'] = int(stats_data.get('anomaly', -1))
    
    col_schema.append({"id": "anomaly", "label": "Anomaly Class", "type": "integer"})
    
    ret = {
        'records': records,
        'col_schema': col_schema
    }
    return ret
        

def get_alg_code(alg_name, language, expr, cluster_name, arch, precision, n_threads, problem_size):
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

    code, gen_steps = reader.get_alg_code(alg_name, confs[0])
    
    return code, gen_steps    