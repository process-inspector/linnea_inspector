from linnea.algebra.expression import Matrix, Vector, Equal, Times, Inverse, Transpose
from linnea.algebra.equations import Equations
from linnea.algebra.properties import Property

name = "GLS"

op_info = {
    "input": "X: (n, m)",
    "output": "b: (m, 1)",
}

def get_equations(m,n):
    
        m = int(m)
        n = int(n)
         
        X = Matrix("X", (n, m))
        X.set_property(Property.FULL_RANK)
        M = Matrix("M", (n, n))
        M.set_property(Property.SPD)
        y = Vector("y", (n, 1))
        b = Vector("b", (m, 1))

        equations = Equations(Equal(b, Times(Inverse(Times(Transpose(X), Inverse(M), X ) ), Transpose(X), Inverse(M), y)))
        return equations