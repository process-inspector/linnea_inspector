from process_inspector.statistics_coloring import StatisticsColoring
from process_inspector.add_dfgs import add_dfgs
from process_inspector.compute_partial_ranks import compute_partial_ranks
from .compute_perf import compute_perf, compute_perf_avg_ranks
from partial_ranker import QuantileComparer, PartialRanker, Method

def compute_variant_ranks(variants_measurements):
    cm = QuantileComparer(variants_measurements)
    cm.compute_quantiles(q_max=75, q_min=25)
    cm.compare()
    pr = PartialRanker(cm)
    
    pr.compute_ranks(Method.DFG)
    nranks_m1 = len(pr.get_ranks())
    ranks_m1 = pr.ranker._obj_rank
    
    pr.compute_ranks(Method.DFGReduced)
    nranks_m2 = len(pr.get_ranks())
    ranks_m2 = pr.ranker._obj_rank
    
    pr.compute_ranks(Method.Min)
    nranks_m3 = len(pr.get_ranks())
    ranks_m3 = pr.ranker._obj_rank
    
    rank_str = f'{nranks_m1}-{nranks_m2}-{nranks_m3}'
    
    
    return {
        'm1': ranks_m1,
        'm2': ranks_m2,
        'm3': ranks_m3,
        'rank_str': rank_str
    }

class RanksPerspective(StatisticsColoring):
    def __init__(self, *dfgs):
        dfg = add_dfgs(*dfgs)
        super().__init__(dfg)
        self.color_by = "rank_val"
        self.activity_ranks = None
        self.variant_ranks = None
        self.nvariants = len(dfgs)
        
        self.variants_measurements = {}
        for dfg in dfgs:
            self.variants_measurements[dfg.id] = dfg.info['durations']
            
        self.variant_ranks = compute_variant_ranks(self.variants_measurements)
        
    def compute_stats(self, inv_mapping):
        self.stats = compute_perf_avg_ranks(inv_mapping, self.variant_ranks) # adds column 'perf' to inv_mapping
        if self.stats is None:
            raise ValueError("No statistics computed. Please run compute_stats first.")
        self.activity_ranks = compute_partial_ranks(inv_mapping, group_by='id', on='perf')
        
             
        
    def _format_label_str(self, row):
       #label_str = f"{row['activity']} ({row['nvariants']}/{self.nvariants})\nAvg. FLOPs: {row['avg_flops']:.2e}\nAvg. Perf: {row['avg_perf']:.2f} FLOPs/ns\nnPR:  {self.ranks[row['activity']]['rank_str']}"
       label_str = (
            f"{row['activity']} ({row['nvariants']}/{self.nvariants})\n"
            f"Avg. FLOPs: {row['avg_flops']:.2e}\n"
            f"Avg. Perf: {row['avg_perf']:.2f} F/ns\n"
            f"Num. AR:  {self.activity_ranks[row['activity']]['rank_str']}"
            f"\nAvg. VR: {row['avg_ranks']}"
        )
       return label_str 
       
        
