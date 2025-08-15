from process_inspector.activity_log import ActivityLog
from linnea_inspector.event_data import prepare
from linnea_inspector.classifiers.f_call import f_call
import sys

if __name__ == "__main__":
    # python -m tests.test_prepare_activity_log examples/traces/gls_v1/experiments/traces/algorithm9.traces
    trace_file = sys.argv[1]
    
    event_log, meta_data = prepare(trace_file)
    activity_log = ActivityLog(event_log, 1, f_call)
    
    inv_map = activity_log.inv_mapping
    
    for activity, df in inv_map.items():
        print(f"Activity: {activity}, DataFrame:\n {df}")
        break
    
    al = activity_log.activity_log
    for case in al:
        print(case)
        break
    
    print(f"Number of variants: {activity_log.n_variants}")
    print(f"Number of activities: {activity_log.n_activities}")
    for i, (activity,df) in enumerate(inv_map.items()):
        print(f" {i+1}) {activity} count: {len(df)}")


