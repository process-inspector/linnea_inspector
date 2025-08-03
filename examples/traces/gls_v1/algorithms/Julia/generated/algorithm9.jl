using LinearAlgebra.BLAS
using LinearAlgebra

"""
    algorithm9(ml0::Array{Float64,2}, ml1::Array{Float64,2}, ml2::Array{Float64,1})

Compute
b = ((X^T M^-1 X)^-1 X^T M^-1 y).

Requires at least Julia v1.0.

# Arguments
- `ml0::Array{Float64,2}`: Matrix X of size 1000 x 100 with property FullRank.
- `ml1::Array{Float64,2}`: Matrix M of size 1000 x 1000 with property SPD.
- `ml2::Array{Float64,1}`: Vector y of size 1000.
"""                    
function algorithm9(ml0::Array{Float64,2}, ml1::Array{Float64,2}, ml2::Array{Float64,1})
    # cost: 4.56e+08 FLOPs
    run_id = get(ENV, "LINNEA_RUN_ID", -1)
    t_start = time_ns()
    # X: ml0, full, M: ml1, full, y: ml2, full
    ml3 = Array{Float64}(undef, 100, 1000)
    # tmp56 = X^T
    t1 = time_ns()
    transpose!(ml3, ml0)
    t2 = time_ns()
    println("$(run_id) $(t1) transpose 1 $(t2-t1)")

    # X: ml0, full, M: ml1, full, y: ml2, full, tmp56: ml3, full
    # (L2 L2^T) = M
    t1 = time_ns()
    LAPACK.potrf!('L', ml1)
    t2 = time_ns()
    println("$(run_id) $(t1) LAPACK.potrf 333333333.3333333 $(t2-t1)")

    # X: ml0, full, y: ml2, full, tmp56: ml3, full, L2: ml1, lower_triangular
    # tmp12 = (L2^-1 X)
    t1 = time_ns()
    trsm!('L', 'L', 'N', 'N', 1.0, ml1, ml0)
    t2 = time_ns()
    println("$(run_id) $(t1) trsm 100000000 $(t2-t1)")

    # y: ml2, full, tmp56: ml3, full, L2: ml1, lower_triangular, tmp12: ml0, full
    ml4 = Array{Float64}(undef, 100, 100)
    # tmp14 = (tmp12^T tmp12)
    t1 = time_ns()
    syrk!('L', 'T', 1.0, ml0, 0.0, ml4)
    t2 = time_ns()
    println("$(run_id) $(t1) syrk 10000000 $(t2-t1)")

    # y: ml2, full, tmp56: ml3, full, L2: ml1, lower_triangular, tmp14: ml4, symmetric_lower_triangular
    # (L15 L15^T) = tmp14
    t1 = time_ns()
    LAPACK.potrf!('L', ml4)
    t2 = time_ns()
    println("$(run_id) $(t1) LAPACK.potrf 333333.3333333333 $(t2-t1)")

    # y: ml2, full, tmp56: ml3, full, L2: ml1, lower_triangular, L15: ml4, lower_triangular
    # tmp67 = (L2^-1 y)
    t1 = time_ns()
    trsv!('L', 'N', 'N', ml1, ml2)
    t2 = time_ns()
    println("$(run_id) $(t1) trsv 1000000 $(t2-t1)")

    # tmp56: ml3, full, L2: ml1, lower_triangular, L15: ml4, lower_triangular, tmp67: ml2, full
    # tmp143 = (L15^-1 tmp56)
    t1 = time_ns()
    trsm!('L', 'L', 'N', 'N', 1.0, ml4, ml3)
    t2 = time_ns()
    println("$(run_id) $(t1) trsm 10000000 $(t2-t1)")

    # L2: ml1, lower_triangular, L15: ml4, lower_triangular, tmp67: ml2, full, tmp143: ml3, full
    # tmp70 = (L2^-T tmp67)
    t1 = time_ns()
    trsv!('L', 'T', 'N', ml1, ml2)
    t2 = time_ns()
    println("$(run_id) $(t1) trsv 1000000 $(t2-t1)")

    # L15: ml4, lower_triangular, tmp143: ml3, full, tmp70: ml2, full
    ml5 = Array{Float64}(undef, 100)
    # tmp23 = (tmp143 tmp70)
    t1 = time_ns()
    gemv!('N', 1.0, ml3, ml2, 0.0, ml5)
    t2 = time_ns()
    println("$(run_id) $(t1) gemv 200000 $(t2-t1)")

    # L15: ml4, lower_triangular, tmp23: ml5, full
    # tmp24 = (L15^-T tmp23)
    t1 = time_ns()
    trsv!('L', 'T', 'N', ml4, ml5)
    t2 = time_ns()
    println("$(run_id) $(t1) trsv 10000 $(t2-t1)")

    t_end = time_ns()
    println("$(run_id) $(t_end) algorithm9 455876667.6666666 $(t_end-t_start)")
    # tmp24: ml5, full
    # b = tmp24
    return (ml5)
end