from linnea_inspector.data_processor import LogsProcessor
from linnea_inspector.object_context import ObjectContext
from linnea_inspector.store.experiment_store import ExperimentReader

def test_lp(log_dir):
    
    processor = LogsProcessor(log_dir=log_dir, parse_run_config=True, sep=';')   
    processor.process()
    print("Case Metadata:", processor.case_md.head())

    obj_context = ObjectContext(processor.case_md, obj_key='alg', compute_ranks=True)
    print("Object Context Records:")
    # print(obj_context.data.to_dict())
    print(obj_context.data.model_dump_json(indent=1))
        
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
    print("Case Metadata:", case_md.head())

    obj_context = ObjectContext(case_md, obj_key='alg', compute_ranks=True)
    print("Object Context Records:")
    # print(obj_context.data.to_dict())
    print(obj_context.data.model_dump_json(indent=1))
        
    print("SUCCESS")
    
if __name__ == "__main__":
    # log_dir = "tests/traces/b0"
    # test_lp(log_dir)
    
    store_path = ["tests/store/test.rs",]
    test_store(store_path)