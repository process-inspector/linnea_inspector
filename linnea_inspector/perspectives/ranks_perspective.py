from process_inspector.statistics_coloring import StatisticsColoring
from process_inspector.add_dfgs import add_dfgs
from process_inspector.compute_ranks import compute_activity_ranks, compute_partial_ranks
from .statistics import  compute_perf_rank_score


class RanksPerspective(StatisticsColoring):
    def __init__(self, *dfgs):
        dfg = add_dfgs(*dfgs)
        super().__init__(dfg)
        self.color_by = "rank_score"
        self.activity_ranks = None
        self.alg_ranks = None
        self.nvariants = len(dfgs)
        
        self.alg_measurements = {}
        for dfg in dfgs:
            self.alg_measurements[dfg.id] = dfg.info['durations']
            
        self.alg_ranks = compute_partial_ranks(self.alg_measurements)
        
    def compute_stats(self, inv_mapping):
        self.stats = compute_perf_rank_score(inv_mapping, self.alg_ranks) # adds column 'perf' to inv_mapping
        if self.stats is None:
            raise ValueError("No statistics computed. Please run compute_stats first.")
        self.activity_ranks = compute_activity_ranks(inv_mapping, group_by='id', on='perf')
        
             
        
    def _format_label_str(self, row):
       #label_str = f"{row['activity']} ({row['nvariants']}/{self.nvariants})\nAvg. FLOPs: {row['avg_flops']:.2e}\nAvg. Perf: {row['avg_perf']:.2f} FLOPs/ns\nnPR:  {self.ranks[row['activity']]['rank_str']}"
       label_str = (
            f"{row['activity']} ({row['nvariants']}/{self.nvariants})\n"
            f"Rank score: {row['rank_score']:.1f}\n"
            f"Num. Ranks:  {self.activity_ranks[row['activity']]['nranks']}\n"            
            f"Avg. FLOPs: {row['avg_flops']:.2e}\n"
            f"Avg. Perf: {row['avg_perf']:.2f} F/ns"
        )
       return label_str 
       
        
