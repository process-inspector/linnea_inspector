import pandas as pd
from process_inspector.dfg.difference_perspective import DFGDifferencePerspective

class LinneaDFGDifferencePerspective(DFGDifferencePerspective):
    def __init__(self, dfg1, dfg2):
        super().__init__(dfg1, dfg2)
        