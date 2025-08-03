using LinearAlgebra.BLAS
using LinearAlgebra

"""
    algorithm3(ml0::Array{Float64,2}, ml1::Array{Float64,2}, ml2::Array{Float64,1})

Compute
b = ((X^T M^-1 X)^-1 X^T M^-1 y).

Requires at least Julia v1.0.

# Arguments
- `ml0::Array{Float64,2}`: Matrix X of size 1000 x 100 with property FullRank.
- `ml1::Array{Float64,2}`: Matrix M of size 1000 x 1000 with property SPD.
- `ml2::Array{Float64,1}`: Vector y of size 1000.
"""                    
function algorithm3(ml0::Array{Float64,2}, ml1::Array{Float64,2}, ml2::Array{Float64,1})
    # cost: 4.55e+08 FLOPs
    run_id = get(ENV, "LINNEA_RUN_ID", -1)
    t_start = time_ns()
    # X: ml0, full, M: ml1, full, y: ml2, full
    # (L2 L2^T) = M
    t1 = time_ns()
    LAPACK.potrf!('L', ml1)
    t2 = time_ns()
    println("$(run_id) $(t1) LAPACK.potrf 333333333.3333333 $(t2-t1)")

    # X: ml0, full, y: ml2, full, L2: ml1, lower_triangular
    # tmp67 = (L2^-1 y)
    t1 = time_ns()
    trsv!('L', 'N', 'N', ml1, ml2)
    t2 = time_ns()
    println("$(run_id) $(t1) trsv 1000000 $(t2-t1)")

    # X: ml0, full, L2: ml1, lower_triangular, tmp67: ml2, full
    # tmp12 = (L2^-1 X)
    t1 = time_ns()
    trsm!('L', 'L', 'N', 'N', 1.0, ml1, ml0)
    t2 = time_ns()
    println("$(run_id) $(t1) trsm 100000000 $(t2-t1)")

    # tmp67: ml2, full, tmp12: ml0, full
    ml3 = Array{Float64}(undef, 100, 100)
    # tmp14 = (tmp12^T tmp12)
    t1 = time_ns()
    gemm!('T', 'N', 1.0, ml0, ml0, 0.0, ml3)
    t2 = time_ns()
    println("$(run_id) $(t1) gemm 20000000 $(t2-t1)")

    # tmp67: ml2, full, tmp12: ml0, full, tmp14: ml3, full
    # (L15 L15^T) = tmp14
    t1 = time_ns()
    LAPACK.potrf!('L', ml3)
    t2 = time_ns()
    println("$(run_id) $(t1) LAPACK.potrf 333333.3333333333 $(t2-t1)")

    # tmp67: ml2, full, tmp12: ml0, full, L15: ml3, lower_triangular
    ml4 = Array{Float64}(undef, 100)
    # tmp21 = (tmp12^T tmp67)
    t1 = time_ns()
    gemv!('T', 1.0, ml0, ml2, 0.0, ml4)
    t2 = time_ns()
    println("$(run_id) $(t1) gemv 200000 $(t2-t1)")

    # L15: ml3, lower_triangular, tmp21: ml4, full
    # tmp23 = (L15^-1 tmp21)
    t1 = time_ns()
    trsv!('L', 'N', 'N', ml3, ml4)
    t2 = time_ns()
    println("$(run_id) $(t1) trsv 10000 $(t2-t1)")

    # L15: ml3, lower_triangular, tmp23: ml4, full
    # tmp24 = (L15^-T tmp23)
    t1 = time_ns()
    trsv!('L', 'T', 'N', ml3, ml4)
    t2 = time_ns()
    println("$(run_id) $(t1) trsv 10000 $(t2-t1)")

    t_end = time_ns()
    println("$(run_id) $(t_end) algorithm3 454886666.6666666 $(t_end-t_start)")
    # tmp24: ml4, full
    # b = tmp24
    return (ml4)
end