using LinearAlgebra
using Random
using LinearAlgebra.BLAS
BLAS.set_num_threads({nthreads}) 

include("../generated/{algorithm_id}.jl")  # Import the function

const REP = {nreps}  # Number of repetitions for the algorithm run

# Generate inputs
Random.seed!(123)
X = randn({n}, {m})
A = randn({n}, {n})
M = A * A' + 1e-3 * I  # SPD matrix
y = randn({n})

# Call the algorithm
for i in 1:REP
    ENV["LINNEA_RUN_ID"] = string(i)  # Set the run ID for each iteration
    cache_scrub = randn(100_000_000)
    b = {algorithm_id}(copy(X), copy(M), copy(y))
end
