using LinearAlgebra
using Random

include("../algorithms/Julia/generated/algorithm0.jl")  # Import the function

const REP = 10  # Number of repetitions for the algorithm run

# Generate inputs
Random.seed!(123)
X = randn(1000, 100)
A = randn(1000, 1000)
M = A * A' + 1e-3 * I  # SPD matrix
y = randn(1000)

# Call the algorithm
for i in 1:REP
    ENV["LINNEA_RUN_ID"] = string(i)  # Set the run ID for each iteration
    cache_scrub = randn(100_000_000)
    b = algorithm0(copy(X), copy(M), copy(y))
end
