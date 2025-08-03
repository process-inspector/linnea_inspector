from linnea.algebra.expression import Matrix, Vector, Equal, Times, Inverse, Transpose
from linnea.algebra.equations import Equations
from linnea.algebra.properties import Property
import linnea.config
from linnea.algorithm_generation.graph.search_graph import SearchGraph

if __name__ == "__main__":
    n = 1000
    m = 100

    X = Matrix("X", (n, m))
    X.set_property(Property.FULL_RANK)
    M = Matrix("M", (n, n))
    M.set_property(Property.SPD)
    y = Vector("y", (n, 1))
    b = Vector("b", (m, 1))

    equations = Equations(Equal(b, Times(Inverse(Times(Transpose(X), Inverse(M), X ) ), Transpose(X), Inverse(M), y)))

    print(equations)
    
    linnea.config.set_output_code_path(".")
    linnea.config.init()
    
    graph = SearchGraph(equations)
    graph.generate(time_limit=60,
                   merging=True,
                   dead_ends=True,
                   pruning_factor=1.4)

    graph.write_output(code=True,
                       generation_steps=True,
                       output_name="algorithms",
                       experiment_code=False,
                       algorithms_limit=200,
                       graph=False,
                       no_duplicates=True)
    
    
