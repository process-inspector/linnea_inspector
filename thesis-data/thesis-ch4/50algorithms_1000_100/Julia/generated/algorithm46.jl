using LinearAlgebra.BLAS
using LinearAlgebra

"""
    algorithm46(ml0::Array{Float64,2}, ml1::Array{Float64,2}, ml2::Array{Float64,1})

Compute
b = ((X^T M^-1 X)^-1 X^T M^-1 y).

Requires at least Julia v1.0.

# Arguments
- `ml0::Array{Float64,2}`: Matrix X of size 1000 x 100 with property FullRank.
- `ml1::Array{Float64,2}`: Matrix M of size 1000 x 1000 with property SPD.
- `ml2::Array{Float64,1}`: Vector y of size 1000.
"""                    
function algorithm46(ml0::Array{Float64,2}, ml1::Array{Float64,2}, ml2::Array{Float64,1})
    # cost: 4.48e+08 FLOPs
    run_id = get(ENV, "LINNEA_RUN_ID", -1)
    t_start = time_ns()
    # X: ml0, full, M: ml1, full, y: ml2, full
    # (L2 L2^T) = M
    t1 = time_ns()
    LAPACK.potrf!('L', ml1)
    t2 = time_ns()
    println("[#LT] $(run_id); $(t1); LAPACK.potrf; 333333333.3333333; $(t2-t1)")

    # X: ml0, full, y: ml2, full, L2: ml1, lower_triangular
    # tmp67 = (L2^-1 y)
    t1 = time_ns()
    trsv!('L', 'N', 'N', ml1, ml2)
    t2 = time_ns()
    println("[#LT] $(run_id); $(t1); trsv; 1000000; $(t2-t1)")

    # X: ml0, full, L2: ml1, lower_triangular, tmp67: ml2, full
    # tmp12 = (L2^-1 X)
    t1 = time_ns()
    trsm!('L', 'L', 'N', 'N', 1.0, ml1, ml0)
    t2 = time_ns()
    println("[#LT] $(run_id); $(t1); trsm; 100000000; $(t2-t1)")

    # tmp67: ml2, full, tmp12: ml0, full
    ml3 = Array{Float64}(undef, 100)
    # tmp21 = (tmp12^T tmp67)
    t1 = time_ns()
    gemv!('T', 1.0, ml0, ml2, 0.0, ml3)
    t2 = time_ns()
    println("[#LT] $(run_id); $(t1); gemv; 200000; $(t2-t1)")

    # tmp12: ml0, full, tmp21: ml3, full
    ml4 = Array{Float64}(undef, 100, 100)
    # tmp14 = (tmp12^T tmp12)
    t1 = time_ns()
    syrk!('L', 'T', 1.0, ml0, 0.0, ml4)
    t2 = time_ns()
    println("[#LT] $(run_id); $(t1); syrk; 10000000; $(t2-t1)")

    # tmp21: ml3, full, tmp14: ml4, symmetric_lower_triangular
    ml5 = Array{Float64}(undef, 100)
    # (Z18 W19 Z18^T) = tmp14
    t1 = time_ns()
    ml5, ml4 = LAPACK.syev!('V', 'L', ml4)
    t2 = time_ns()
    println("[#LT] $(run_id); $(t1); W, A = LAPACK.syev; 3343333.333333333; $(t2-t1)")

    # tmp21: ml3, full, W19: ml5, diagonal_vector, Z18: ml4, full
    ml6 = Array{Float64}(undef, 100)
    # tmp95 = (Z18^T tmp21)
    t1 = time_ns()
    gemv!('T', 1.0, ml4, ml3, 0.0, ml6)
    t2 = time_ns()
    println("[#LT] $(run_id); $(t1); gemv; 20000; $(t2-t1)")

    # W19: ml5, diagonal_vector, Z18: ml4, full, tmp95: ml6, full
    # tmp96 = (W19^-1 tmp95)
    t1 = time_ns()
    ml6 ./= ml5
    t2 = time_ns()
    println("[#LT] $(run_id); $(t1); x ./= A; 100; $(t2-t1)")

    # Z18: ml4, full, tmp96: ml6, full
    ml7 = Array{Float64}(undef, 100)
    # tmp24 = (Z18 tmp96)
    t1 = time_ns()
    gemv!('N', 1.0, ml4, ml6, 0.0, ml7)
    t2 = time_ns()
    println("[#LT] $(run_id); $(t1); gemv; 20000; $(t2-t1)")

    t_end = time_ns()
    println("[#LT] $(run_id); $(t_end); algorithm46; 447916766.6666666; $(t_end-t_start)")
    # tmp24: ml7, full
    # b = tmp24
    return (ml7)
end