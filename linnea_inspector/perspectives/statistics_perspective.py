import pandas as pd
from process_inspector.statistics_coloring import StatisticsColoring
from .statistics import compute_perf

class StatisticsPerspective(StatisticsColoring):
    def __init__(self,dfg):
        super().__init__(dfg)
        self.color_by = "avg_perf"
        
        
    def compute_stats(self, inv_mapping):
        self.stats = compute_perf(inv_mapping)
        if self.stats is None:
            raise ValueError("No statistics computed. Please run compute_stats first.")
        
    def _format_label_str(self, row):
       label_str = (f"{row['activity']}\n"
                    f"Avg. FLOPs: {row['avg_flops']:.2e}\n"
                    f"Avg. Perf: {row['avg_perf']:.2f} FLOPs/ns"
       )
       return label_str 