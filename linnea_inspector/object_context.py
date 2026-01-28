from process_inspector.schemas import ObjectSchema
from process_inspector.contexts import ObjectContextBase

    
class ObjectContext(ObjectContextBase):
    def __init__(self, case_md, obj_key="alg", compute_ranks=True):
        assert obj_key in case_md.columns, f"Object key '{obj_key}' not found in case metadata columns."
        super().__init__()
        
        
        self.obj_key = obj_key
        self.compute_ranks = compute_ranks
        
        self.compute_object_stats(case_md)
        
        
        
    def compute_object_stats(self, case_md):
        records = []
        bp_data = {}
        for obj, df in case_md.groupby(self.obj_key):
            record = {}
            record['obj'] = obj
            record['duration_mean'] = df['duration'].mean()
            record['flops_mean'] = df['flops'].mean()
            record['perf_mean'] = df['perf'].mean()
            
            bp_data[obj] = df['duration'].tolist()
            records.append(record)
            
        if self.compute_ranks:
            obj_rank, perf_class = self._compute_partial_ranks(bp_data)
            for record in records:
                record['rank'] = obj_rank[record['obj']]
                       
        self.data.records = records
        self.data.bp_data = bp_data
        if self.compute_ranks:
            self.data.rank = obj_rank
            self.data.perf_class = perf_class
            