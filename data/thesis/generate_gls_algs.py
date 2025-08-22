from linnea.algebra.expression import Matrix, Vector, Equal, Times, Inverse, Transpose
from linnea.algebra.equations import Equations
from linnea.algebra.properties import Property

import os
import random
from linnea_inspector.generate_codes import generate_algorithm_codes, generate_experiment_codes

def generate(n,m, n_algs, nthreads, nreps,tag, regenerate=False):

    alg_codes_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"{n_algs}algorithms_{n}_{m}")

    if not os.path.exists(alg_codes_path) or regenerate:
        X = Matrix("X", (n, m))
        X.set_property(Property.FULL_RANK)
        M = Matrix("M", (n, n))
        M.set_property(Property.SPD)
        y = Vector("y", (n, 1))
        b = Vector("b", (m, 1))

        equations = Equations(Equal(b, Times(Inverse(Times(Transpose(X), Inverse(M), X ) ), Transpose(X), Inverse(M), y)))
        
        generate_algorithm_codes(equations, alg_codes_path=alg_codes_path, num_algs_limit=n_algs, time_limit_sec=60)
    
    exp_template_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "run_template.jl")
    template_args = {
        'n': n,
        'm': m,
        'nthreads': nthreads,
        'nreps': nreps  
    }
    generate_experiment_codes(alg_codes_path, exp_template_path, tag=tag, **template_args)
    

if __name__ == "__main__":
    
    random.seed(0)
    generate(1000, 100, n_algs=50, nthreads=12, nreps=10, tag='KEB', regenerate=False)
    

    
    


    
    

