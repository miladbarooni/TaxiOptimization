# Mathematical Model Documentation

## Problem Formulation

### Input Data

**Sets:**
- **T** = {1, 2, ..., n}: Set of trips
- **L** = {1, 2, ..., m}: Set of locations (including depot at location 1)

**Parameters:**
- **a_i**: Start time of trip i (in minutes)
- **b_i**: End time of trip i (in minutes)
- **c_i**: Pickup location of trip i
- **d_i**: Dropoff location of trip i
- **D[i][j]**: Travel time/distance from location i to location j

---

## Phase 1: Minimum Fleet Size

### Objective
Minimize the number of taxis required to serve all trips.

### Network Flow Formulation

**Graph G = (V, E):**

**Nodes V:**
- Source node: `s` (parking_start)
- Sink node: `t` (parking_end)
- For each trip i: `u_i` (trip_i_start) and `v_i` (trip_i_end)

**Node Demands:**
```
demand(s) = -n        (supply node)
demand(t) = +n        (demand node)
demand(u_i) = +1      (each trip start consumes 1 unit)
demand(v_i) = -1      (each trip end produces 1 unit)
```

**Edges E:**

| Edge Type | From | To | Capacity | Cost |
|-----------|------|-----|----------|------|
| Start | s | u_i | 1 | 0 |
| End | v_i | t | 1 | 0 |
| Transfer | v_i | u_j | 1 | 0 |
| Garbage | s | t | n | -1 |

**Transfer Edge Condition (Trip Compatibility):**

An edge (v_i, u_j) exists if and only if trip j can feasibly follow trip i:

```
b_i + D[d_i][c_j] <= a_j
```

Or using the extended validation:
```
(b_i + D[d_i][c_j] + D[c_j][d_j] <= b_j)  OR  (a_i + D[c_i][d_i] + D[d_i][c_j] <= a_j)
```

**Objective Function:**
```
minimize: sum over all edges (flow * cost)
```

**Result Interpretation:**
```
Number of taxis used = n + flowCost
```

The garbage edge with cost -1 absorbs unused flow, so minimizing total cost maximizes flow through the garbage edge, thereby minimizing the number of actual taxis used.

---

## Phase 1: ILP Formulation

### Decision Variables

**x_e in {0, 1}** for each edge e in E: Binary flow variable

### Objective Function
```
minimize: sum_{e in E} c_e * x_e
```

Where c_e is the cost of edge e (all 0 except garbage edge = -1).

### Constraints

**Flow Conservation (for each node n):**
```
supply(n) + sum_{(i,n) in E} x_{(i,n)} >= demand(n) + sum_{(n,j) in E} x_{(n,j)}
```

**Capacity Constraints:**
```
min_e <= x_e <= max_e    for all e in E
```

Where:
- Trip edges: min=1, max=1 (mandatory)
- Other edges: min=0, max=1 (or n for garbage)

---

## Phase 2: Minimum Empty Travel Distance

### Objective
Minimize total distance traveled without passengers (empty kilometers).

### Network Modifications

Same network structure as Phase 1, but with distance-based edge costs:

| Edge Type | Cost |
|-----------|------|
| Start (s -> u_i) | D[depot][c_i] |
| End (v_i -> t) | D[d_i][depot] |
| Transfer (v_i -> u_j) | D[d_i][c_j] |
| Garbage (s -> t) | 0 |

**Objective Function:**
```
minimize: sum_{e in E} D_e * x_e
```

Where D_e is the empty travel distance for edge e.

---

## Phase 3: Bi-objective Optimization

### Objectives
1. Minimize fleet size (f)
2. Minimize empty travel distance (d)

### Approach: Hierarchical Optimization

**Step 1:** Solve Phase 1 to get minimum fleet size f*

**Step 2:** Solve Phase 2 with fixed fleet size constraint:
- Allow up to 10% increase in fleet: f <= f* * 1.1

### Alternative Constraint Formulations

Three preprocessing methods for trip compatibility:

**Method 1 (Combined):**
```
valid if: (b_i + D[d_i][c_j] + D[c_j][d_j] <= b_j) OR (a_i + D[c_i][d_i] + D[d_i][c_j] <= a_j)
```

**Method 2 (End-time only):**
```
valid if: b_i + D[d_i][c_j] + D[c_j][d_j] <= b_j
```

**Method 3 (Start-time only):**
```
valid if: a_i + D[c_i][d_i] + D[d_i][c_j] <= a_j
```

### Efficiency Metric
```
Efficiency = (used_taxis * mean_trip_time) - (waste_time / num_trips)
```

---

## Time Conversion

Trip times are given in HHMM format and converted to minutes:

```
minutes = (HHMM // 100) * 60 + (HHMM % 100)

Example: 806 -> 8*60 + 6 = 486 minutes
```

---

## Distance Matrix

The distance matrix D is stored in upper triangular format:

```
    1   2   3   4   ...
1   0   d12 d13 d14 ...
2       0   d23 d24 ...
3           0   d34 ...
...
```

Access function:
```python
def get_distance(i, j):
    if i > j:
        return D[j][i]
    return D[i][j]
```

---

## Complexity Analysis

**Graph Size:**
- Nodes: |V| = 2n + 2
- Edges: |E| = O(n^2) in worst case

**Algorithm Complexity:**
- Network Simplex: O(|V| * |E| * log|V|) = O(n^3 * log n)
- Preprocessing (compatibility check): O(n^2)

**Space Complexity:**
- Graph storage: O(n^2)
- Distance matrix: O(m^2) where m = number of locations
