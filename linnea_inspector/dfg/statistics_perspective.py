import pandas as pd
from process_inspector.dfg.base_perspective import DFGBasePerspective
import numpy as np

class DFGStatisticsPerspective(DFGBasePerspective):
    def __init__(self, activity_context_data, relation_context_data, color_by="perf_mean"):   
        super().__init__(activity_context_data.activities, relation_context_data.relations)
        
        self.color_by = color_by
        
        self.activity_data = activity_context_data
        self.relation_data = relation_context_data
        # self.context = DFGContext(reverse_maps, None, obj_key=obj_key, compute_ranks=False)
        
        
    def create_style(self):
        
        for record in self.relation_data.records:
            edge = record['relation']
            self.edge_color[edge] = "#000000"
            self.edge_penwidth[edge] = 1.0
            self.edge_label[edge] = f"{record['obj_count']}"
            
        sum_ = sum(record[self.color_by] for record in self.activity_data.records)
        for record in self.activity_data.records:
            activity = record['activity']
            
            label = f"{activity}\n"
            label += f"Mean. FLOPs: {record['flops_mean']:.2e}\n"
            label += f"Mean. Perf: {record['perf_mean']:.2f} F/ns"
            
            self.activity_label[activity] = label
            color_score = record[self.color_by]/sum_ if sum_ > 0 else 0.0
            self.activity_color[activity] = self._get_activity_color(color_score, 0.0, 1.0)
            
            
        
    def _get_activity_color(self, trans_count, min_trans_count, max_trans_count):
        """
        Get color representation based on the transaction count.

        Args:
            trans_count (float): The transaction count.
            min_trans_count (float): The minimum transaction count.
            max_trans_count (float): The maximum transaction count.

        Returns:
            str: A hexadecimal color code representing the transaction count.
        """
        try:
            trans_base_color = int(255 - 100 * (trans_count - min_trans_count) / (max_trans_count - min_trans_count + 0.00001))
            trans_base_color_hex = str(hex(trans_base_color))[2:].upper()
            return "#" + trans_base_color_hex + trans_base_color_hex + "FF"
        except ValueError:
            # this happens if trans_count is NaN or _sum is 0
            return "#FFFFFF"
