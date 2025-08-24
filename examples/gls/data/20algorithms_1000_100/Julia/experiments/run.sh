#!/bin/bash

julia run_algorithm0.jl > traces/algorithm0.traces
julia run_algorithm1.jl > traces/algorithm1.traces
julia run_algorithm10.jl > traces/algorithm10.traces
julia run_algorithm11.jl > traces/algorithm11.traces
julia run_algorithm12.jl > traces/algorithm12.traces
julia run_algorithm13.jl > traces/algorithm13.traces
julia run_algorithm14.jl > traces/algorithm14.traces
julia run_algorithm15.jl > traces/algorithm15.traces
julia run_algorithm16.jl > traces/algorithm16.traces
julia run_algorithm17.jl > traces/algorithm17.traces
julia run_algorithm18.jl > traces/algorithm18.traces
julia run_algorithm19.jl > traces/algorithm19.traces
julia run_algorithm2.jl > traces/algorithm2.traces
julia run_algorithm3.jl > traces/algorithm3.traces
julia run_algorithm4.jl > traces/algorithm4.traces
julia run_algorithm5.jl > traces/algorithm5.traces
julia run_algorithm6.jl > traces/algorithm6.traces
julia run_algorithm7.jl > traces/algorithm7.traces
julia run_algorithm8.jl > traces/algorithm8.traces
julia run_algorithm9.jl > traces/algorithm9.traces
python -m linnea_inspector.synthesis traces/