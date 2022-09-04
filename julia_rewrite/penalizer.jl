include("utils.jl")

export INVALID_POINTS

#count

INVALID_POINTS = []

function penalizer_init()
    #pass
end

function penalize(points, valid_points::Array{Float64, 2}, grid, penalty = 100; overflown...)

    # Use the grid or compute it
    _grid = grid === nothing ? grid_compute(points) : grid

    invalid = 0
    empty!(INVALID_POINTS)

    for _p in eachrow(points)

        if any(all(abs.(valid_points .- _p[1:2]') .< _grid, dims = 2)) == false
            invalid += 1
            
            # Store invalid point
            push!(INVALID_POINTS, _p)
        end
    end

    # invalid = sum(.!any(all(abs.(valid_points .- _p[1:2]') .< _grid, dims = 2)) for _p in eachrow(points))
    invalid * penalty
end

if (abspath(PROGRAM_FILE) == @__FILE__)
    a = [ 0.16433    0.524746;
        0.730177   0.787651;
        0.646905   0.0135035;
        0.796598   0.0387711;
        0.442782   0.753235;
        0.832315   0.483352;
        0.442524   0.912381;
        0.336651   0.236891;
        0.0954936  0.303086;
        0.459189   0.374318]
    b = a .+ 0.1
    println(penalize(a, b, 0.03999999910593033))
    println(INVALID_POINTS)
end
