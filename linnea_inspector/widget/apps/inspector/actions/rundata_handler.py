    
from .. import config

def prepare_facts_table_algs(df):
    col_schema = [
        {"id": "language", "label": "Language", "type": "string"},
        {"id": "expr", "label": "Expression", "type": "string"},
        {"id": "cluster_name", "label": "Cluster", "type": "string"},
        {"id": "aarch", "label": "Arch", "type": "string"},
        {"id": "nthreads", "label": "N. Threads", "type": "integer"},
        {"id": "prob_size", "label": "Problem Size", "type": "string"}
    ]
    
    df = df.copy()
    df = df[[col['id'] for col in col_schema]]
    # Remove duplicates
    df = df.drop_duplicates()
    
    ret = {
        'records': df.to_dict('records'),
        'col_schema': col_schema
    }
    return ret
        

def get_alg_code(alg_name, language, expr, cluster_name, aarch, n_threads, problem_size):
    reader = config.get_reader()
    confs = reader.get_confs(
        language=language,
        expr=expr,
        cluster_name=cluster_name,
        aarch=aarch,
        nthreads=int(n_threads),
        prob_size=problem_size
    )
    if not confs:
        raise ValueError("No configurations found for the given parameters.")

    code, gen_steps = reader.get_alg_code(alg_name, confs[0])
    
    return code, gen_steps    