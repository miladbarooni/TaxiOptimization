# Taxi Fleet Optimization using Network Flow and Integer Linear Programming

## Overview

University project for the **Fundamentals of Operations Research** course implementing vehicle scheduling optimization for a taxi agency in Shiraz. The project explores both graph-based (Network Flow) and algebraic (Integer Linear Programming) approaches to solve the taxi fleet scheduling problem.

## Problem Description

A taxi agency needs to plan daily operations for **n** reserved trips. Each trip **i** is defined by:

| Parameter | Description |
|-----------|-------------|
| a_i | Start time of the trip |
| b_i | End time of the trip |
| c_i | Starting location (pickup point) |
| d_i | Ending location (dropoff point) |

After completing a trip, a driver can either:
1. Return to the parking depot, or
2. Proceed directly to another feasible trip

A trip **j** can follow trip **i** if the driver can travel from d_i (dropoff of trip i) to c_j (pickup of trip j) before the start time a_j.

The **distance matrix D** contains travel times between all locations (symmetric, upper triangular format).

## Methodology

### Phase 1: Minimize Fleet Size (Network Flow)

**Objective:** Find the minimum number of taxis required to serve all trips.

**Approach:** Modeled as a **Minimum Cost Flow Problem** using NetworkX's network simplex algorithm.

**Network Structure:**
- **Nodes:**
  - `parking_start` (source with supply = n)
  - `parking_end` (sink with demand = n)
  - `trip_i_start` and `trip_i_end` for each trip
- **Edges:**
  - Start edges: `parking_start` -> `trip_i_start` (capacity=1, cost=0)
  - Trip edges: `trip_i_start` -> `trip_i_end` (implicit)
  - Back edges: `trip_i_end` -> `trip_j_start` if trip j can follow trip i (capacity=1, cost=0)
  - End edges: `trip_i_end` -> `parking_end` (capacity=1, cost=0)
  - Garbage edge: `parking_start` -> `parking_end` (capacity=n, cost=-1)

**Result:** `Used Taxis = n + flowCost`

### Phase 1: Minimize Fleet Size (Integer Linear Programming)

**Approach:** Same problem formulated using PuLP solver for Integer Linear Programming.

The ILP formulation uses binary decision variables for flow on each arc, with flow conservation constraints at each node.

### Phase 2: Minimize Empty Travel Distance

**Objective:** Minimize the total distance traveled without passengers (environmental optimization).

**Approach:** Same network structure as Phase 1, but with distance-based costs on edges:
- Start edges: cost = distance(depot, pickup_location)
- Back edges: cost = distance(dropoff_i, pickup_j)
- End edges: cost = distance(dropoff_location, depot)
- Garbage edge: cost = 0

### Phase 3: Bi-objective Optimization

**Objective:** Balance between fleet size and empty travel distance.

**Approach:** Comparative analysis of three different trip compatibility constraints:
1. Combined end-time and start-time constraints
2. End-time constraints only
3. Start-time constraints only

**Efficiency Metric:** `(used_taxis * mean_trip_time) - (waste_time / num_trips)`

## Datasets

| Dataset | Trips | Description |
|---------|-------|-------------|
| d1.txt / General-Dataset-1.txt | 9-10 | Small test dataset |
| d2.txt / General-Dataset-2.txt | 115-154 | Medium dataset |
| d3.txt / General-Dataset-3.txt | 632-839 | Large dataset |

**Data Format:**
```
<number_of_trips>
<start_time>,<end_time>,<pickup_location>,<dropoff_location>
...
```

Time format: HHMM (e.g., 806 = 8:06 AM, converted to minutes internally)

**Distance Matrix Format:** Upper triangular symmetric matrix with location indices.

## Project Structure

```
TaxiOptimization/
├── src/                                    # Source code
│   ├── minimize_fleet_networkflow.py       # Minimize taxis (Network Flow)
│   ├── minimize_fleet_simple.py            # Simplified time constraints
│   ├── minimize_fleet_ilp.py               # Minimize taxis (ILP/PuLP)
│   ├── minimize_distance_networkflow.py    # Minimize empty travel (Network Flow)
│   ├── minimize_distance_simple.py         # Simplified distance optimization
│   ├── minimize_distance_ilp.py            # Minimize empty travel (ILP/PuLP)
│   ├── multiobjective_optimizer.py         # Bi-objective optimization
│   └── utils.py                            # Shared utilities
├── data/
│   ├── small/
│   │   ├── d1.txt              # 9 trips
│   │   └── General-Dataset-1.txt
│   ├── medium/
│   │   ├── d2.txt              # 115 trips
│   │   └── General-Dataset-2.txt
│   ├── large/
│   │   ├── d3.txt              # 839 trips
│   │   ├── General-Dataset-3.txt
│   │   └── synthetic_*.txt     # Generated large datasets
│   └── distance_matrix.txt     # Distance matrix
├── docs/
│   ├── MODEL.md                # Mathematical model documentation
│   └── OR_Project.pdf          # Original project specification
├── images/                     # Visualization outputs
│   ├── p1.png
│   ├── p2.png
│   └── p3.png
├── results/                    # Experiment results
│   └── experiment_results.json
├── generate_dataset.py         # Dataset generation utility
├── run_experiments.py          # Batch experiment runner
├── requirements.txt
├── environment.yml             # Conda environment
└── LICENSE
```

## Dependencies

- Python 3.x
- NetworkX (graph algorithms and network simplex)
- PuLP (linear programming)
- Matplotlib (visualization)

Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

All scripts accept command-line arguments for specifying datasets:

```bash
python src/<script>.py --trips <path_to_trips> --distance <path_to_matrix> [--no-plot]
```

### Minimize Fleet Size
```bash
# Using Network Flow (default: small dataset)
python src/minimize_fleet_networkflow.py

# Using a larger dataset
python src/minimize_fleet_networkflow.py -t data/large/d3.txt -d data/distance_matrix.txt --no-plot

# Using Integer Linear Programming
python src/minimize_fleet_ilp.py -t data/medium/d2.txt
```

### Minimize Empty Travel Distance
```bash
# Using Network Flow
python src/minimize_distance_networkflow.py -t data/large/d3.txt --no-plot

# Using Integer Linear Programming
python src/minimize_distance_ilp.py
```

### Bi-objective Optimization
```bash
python src/multiobjective_optimizer.py -t data/medium/d2.txt
```

### Generate Synthetic Datasets
```bash
python generate_dataset.py --trips 1000 --locations 10 --output data/large/custom.txt
```

### Run All Experiments
```bash
python run_experiments.py
```

## Results

Performance benchmarks across different dataset sizes:

| Dataset | Trips | Compatible Pairs | Min Fleet | Empty Distance | Execution Time |
|---------|-------|------------------|-----------|----------------|----------------|
| Small   | 9     | 27               | 3 taxis   | 103 units      | < 1 ms         |
| Medium  | 115   | 4,153            | 24 taxis  | 891 units      | ~30 ms         |
| Large   | 839   | 225,590          | 98 taxis  | 2,918 units    | ~5 s           |
| Synthetic | 1,500 | 1,085,728      | 25 taxis  | 2,367 units    | ~22 s          |
| Synthetic | 2,000 | 1,929,768      | 24 taxis  | 3,165 units    | ~54 s          |
| Synthetic | 3,000 | 4,343,024      | 34 taxis  | 3,607 units    | ~198 s         |

**Key Observations:**
- The network flow algorithm scales reasonably, handling 3,000 trips in ~3 minutes
- Compatible pairs grow quadratically with trip count (O(n²))
- Phase 2 (minimize distance) may use slightly more taxis than Phase 1 minimum to reduce empty travel
- Preprocessing is the main bottleneck for very large datasets

## Sample Output

```
FlowCost: -6
------------------------------------
Used Taxi: 3
------------------------------------
Execution Time: 0.001s
```

## Visualization

The scripts generate network visualizations showing:
- Trip nodes arranged in bipartite layout
- Parking depot nodes (start/end)
- Color-coded taxi routes
- Flow paths through the network

## Algorithm Complexity

- **Network Simplex:** O(V * E * log(V)) where V = 2n + 2 nodes and E = O(n^2) edges
- **Preprocessing:** O(n^2) for computing all pairwise trip compatibilities

## Limitations

This is an educational implementation with the following limitations:

- **Scale**: Preprocessing is O(n²), limiting practical use to ~5,000 trips
- **Static scheduling**: All trips must be known in advance (no real-time updates)
- **Simplified model**: No traffic variation, driver shifts, or vehicle capacity
- **Single depot**: All taxis start and end at the same location

## Future Work

Potential improvements for production use:
- Parallel preprocessing using multiprocessing
- Approximate algorithms for larger instances
- Dynamic/online scheduling support
- Multi-depot extension
- Integration with real-time traffic APIs

## Academic Context

This project was completed as part of the **Fundamentals of Operations Research** course, demonstrating practical applications of:
- Network Flow Theory
- Integer Linear Programming
- Vehicle Routing Problem (VRP) variants
- Multi-objective Optimization

## References

- NetworkX Documentation: https://networkx.org/
- PuLP Documentation: https://coin-or.github.io/pulp/
- Vehicle Scheduling Problem literature
