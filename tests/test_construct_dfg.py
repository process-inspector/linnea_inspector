from process_inspector.activity_log import ActivityLog
from process_inspector.dfg import DFG
from linnea_inspector.event_data import prepare
from linnea_inspector.classifiers.f_call import f_call
import sys
import os
import pickle

if __name__ == "__main__":
    # python -m tests.test_construct_dfg examples/traces/gls_v1/experiments/traces/algorithm9.traces
    trace_file = sys.argv[1]
    
    event_log, meta_data = prepare(trace_file)
    activity_log = ActivityLog(event_log, 1, f_call)
    dfg = DFG(activity_log)
    
    print(dfg.dfg)
    
    outdir = "examples/dfgs/tmp"
    if not os.path.exists(outdir):
        os.makedirs(outdir)
        
    dfg.save(outdir)
    with open(os.path.join(outdir, "meta_data.pkl"), "wb") as f:
        pickle.dump(meta_data, f)
        
    