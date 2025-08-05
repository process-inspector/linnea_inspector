import pandas as pd
from process_inspector.difference_coloring import DifferenceColoring
from process_inspector.compute_ranks import compute_activity_ranks
from .statistics import compute_perf


class DifferencePerspective(DifferenceColoring):
    def __init__(self, dfg1, dfg2, dfg_combined=None):
        super().__init__(dfg1, dfg2, dfg_combined)
        self.activity_ranks = None
        
    def compute_stats(self, inv_mapping):
        self.stats = compute_perf(inv_mapping)
        if self.stats is None:
            raise ValueError("No statistics computed. Please run compute_stats first.")
        self.activity_ranks = compute_activity_ranks(inv_mapping, group_by='id', on='perf')
        
    
    def _format_label_str(self, row):
        label_str = (f"{row['activity']} ({row['nvariants']})\n"
                    f"Num. Ranks:  {self.activity_ranks[row['activity']]['nranks']}\n" 
                    f"Avg. FLOPs: {row['avg_flops']:.2e}\n"
                    f"Avg. Perf: {row['avg_perf']:.2f} FLOPs/ns"
        )
        return label_str 