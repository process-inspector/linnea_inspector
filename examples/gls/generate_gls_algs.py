from linnea.algebra.expression import Matrix, Vector, Equal, Times, Inverse, Transpose
from linnea.algebra.equations import Equations
from linnea.algebra.properties import Property
import linnea.config
from linnea.algorithm_generation.graph.search_graph import SearchGraph

import os
import random
from linnea_inspector.generate_codes import  generate_experiment_codes

def generate(n,m, n_algs, nthreads, nreps, regenerate=False):

    alg_codes_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"data/{n_algs}algorithms_{n}_{m}")

    if not os.path.exists(alg_codes_path) or regenerate:
        X = Matrix("X", (n, m))
        X.set_property(Property.FULL_RANK)
        M = Matrix("M", (n, n))
        M.set_property(Property.SPD)
        y = Vector("y", (n, 1))
        b = Vector("b", (m, 1))

        equations = Equations(Equal(b, Times(Inverse(Times(Transpose(X), Inverse(M), X ) ), Transpose(X), Inverse(M), y)))
            
        linnea.config.set_output_code_path(os.path.dirname(alg_codes_path))
        linnea.config.init()
        linnea.config.instrument = True
        
        graph = SearchGraph(equations)
        graph.generate(time_limit=60,
                    merging=True,
                    dead_ends=True,
                    pruning_factor=1.2)

        graph.write_output(code=True,
                        generation_steps=True,
                        output_name=os.path.basename(alg_codes_path),
                        experiment_code=False,
                        algorithms_limit=n_algs,
                        graph=False,
                        no_duplicates=True)
    
    exp_template_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "run_template.jl")
    template_args = {
        'n': n,
        'm': m,
        'nthreads': nthreads,
        'nreps': nreps  
    }
    generate_experiment_codes(alg_codes_path, exp_template_path, **template_args)
    

if __name__ == "__main__":
    
    random.seed(0)
    generate(1000, 100, n_algs=20, nthreads=12, nreps=10, regenerate=True)
    

    
    


    
    
