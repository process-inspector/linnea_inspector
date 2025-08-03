from process_inspector.dfg import DFG
from linnea_inspector.perspectives.statistics_perspective import StatisticsPerspective
import sys
import os

if __name__ == "__main__":
    
    data_dir = sys.argv[1]
    dfg = DFG()
    dfg.restore(data_dir)
    
    perspective = StatisticsPerspective(dfg)
    perspective.create_style()
    graph = perspective.prepare_digraph(rankdir='TD')
    print(graph)
    graph.render(os.path.join(data_dir,'dfg'), format='svg', cleanup=True)
    