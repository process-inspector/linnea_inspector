
from linnea_inspector.store.utils import delete_experiment, update_synthesis
import logging
logger = logging.getLogger(__name__)

def prepare_experiments_table(df):
    col_schema = [
        {"id": "id", "label": "ID", "type": "string"},
        {"id": "language", "label": "Language", "type": "string"},
        {"id": "expr", "label": "Expression", "type": "string"},
        {"id": "cluster_name", "label": "Cluster", "type": "string"},
        {"id": "arch", "label": "Arch", "type": "string"},
        {"id": "precision", "label": "Precision", "type": "string"},
        {"id": "nthreads", "label": "N. Threads", "type": "integer"},
        {"id": "prob_size", "label": "Problem Size", "type": "string"},
        {"id": "niter", "label": "N. Iterations", "type": "integer"},
        {"id": "batch_id", "label": "Batch", "type": "integer"},
        {"id": "timestamp", "label": "Timestamp", "type": "string"},
    ]
    
    df = df.copy()
    
    #keep only relevant columns
    df = df[[col['id'] for col in col_schema]]
    
    ret = {
        'records': df.to_dict('records'),
        'col_schema': col_schema,
        'pk': 'id'
    }
    return ret

def delete_runs(ids, df):
    
    ids = [int(i) for i in ids]
    to_delete = df[df['id'].isin(ids)]
    # drop column 'id' to match run_config structure
    to_delete = to_delete.drop(columns=['id'])
    confs = to_delete.to_dict('records')
    for conf in confs:
        delete_experiment(conf)
        update_synthesis(conf)
    logger.info(f"Deleted runs with IDs: {ids}")