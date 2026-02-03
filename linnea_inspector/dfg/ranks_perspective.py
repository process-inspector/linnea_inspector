import pandas as pd
from process_inspector.dfg.base_perspective import DFGBasePerspective
import numpy as np

class DFGRanksPerspective(DFGBasePerspective):
    def __init__(self, activity_context_data, relation_context_data, object_context_data):   
        super().__init__(activity_context_data.activities, relation_context_data.relations)
        
        self.activity_data = activity_context_data
        self.relation_data = relation_context_data
        self.total_objs = len(object_context_data.objects)
        
    
    def create_style(self):
        # find max rank score for activities
        max_activity_rank_score = max(record['rank_score'] for record in self.activity_data.records)    
        max_edge_rank_score = max(record['rank_score'] for record in self.relation_data.records)
        
        for record in self.relation_data.records:
            edge = record['relation']
            score = record['rank_score']
            self.edge_color[edge] = self._get_edge_color(max(0, score), 0.0, max_edge_rank_score)
            self.edge_penwidth[edge] = 1.0
            
            if score != -1.0:
                self.edge_label[edge] = f"{score:.1f}"
            else:
                self.edge_label[edge] = ""
                
        for record in self.activity_data.records:
            num_objs = len(self.activity_data.obj_records[record['activity']])
            score = record['rank_score']
            
            label = f"{record['activity']} ({num_objs}/{self.total_objs})\n"
            if score != -1.0:
                label += f"Rank Score: {score:.1f}\n"
            label += f"Perf. class: {record['perf_class']}\n"
            label += f"{record['flops_mean']:.2e} F @ {record['perf_mean']:.2f} GF/s"
            
            self.activity_label[record['activity']] = label
            self.activity_color[record['activity']] = self._get_activity_color(max(0, record['rank_score']), 0.0, max_activity_rank_score)
             
                 
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
            return "#FF" + trans_base_color_hex + trans_base_color_hex
        except ValueError:
            # this happens if trans_count is NaN or _sum is 0
            return "#FFFFFF"
        
        
    def _get_edge_color(self, trans_count, min_trans_count, max_trans_count):
        try:
            trans_base_color = int(255 * (trans_count - min_trans_count) / (max_trans_count - min_trans_count + 1e-9))
            trans_base_color_hex = str(hex(trans_base_color))[2:].upper().zfill(2)
            return "#" + trans_base_color_hex + "0000"
        except ValueError:
            # this happens if trans_count is NaN or _sum is 0
            return "#000000"


        

       
        
