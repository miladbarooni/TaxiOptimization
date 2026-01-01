"""
Minimize Fleet Size using Integer Linear Programming (PuLP).

This module solves the taxi fleet minimization problem using ILP formulation
with PuLP solver. It provides an alternative to the network flow approach.
"""

import time as timer

from pulp import *

from utils import (
    parse_args,
    file_processing,
    pre_processing,
    set_distance_matrix,
)


def solve_minimize_fleet_ilp(nodes, edges, number_of_trips):
    """
    Solve the minimum fleet size problem using ILP.

    Args:
        nodes: List of trip nodes
        edges: Dict containing network edges
        number_of_trips: Total number of trips
    """
    # adding the source and destination to other nodes

    nodeData = dict()
    # [supply, demand]
    for node in nodes:
        nodeData[node] = [0, 0]
    nodeData['parking_start'] = [number_of_trips, 0]
    nodeData['parking_end'] = [0, number_of_trips]
    nodes.append('parking_start')
    nodes.append('parking_end')
    # Building the arc and arcData
    arcs = list()
    arcData = dict()
    # [cost, minFlow, maxFlow]
    for edge in edges['back_edge']:
        arcs.append((edge[0], edge[1]))
        arcData[(edge[0], edge[1])] = [0, 0, 1]
    for edge in edges['start_edge']:
        arcs.append((edge[0], edge[1]))
        arcData[(edge[0], edge[1])] = [0, 0, 1]
    for edge in edges['end_edge']:
        arcs.append((edge[0], edge[1]))
        arcData[(edge[0], edge[1])] = [0, 0, 1]
    for edge in edges['trip_edge']:
        arcs.append((edge[0], edge[1]))
        arcData[(edge[0], edge[1])] = [0, 1, 1]
    for edge in edges['garbage_edge']:
        arcs.append((edge[0], edge[1]))
        arcData[(edge[0], edge[1])] = [-1, 0, number_of_trips]
    # print (arcs)
    # print (arcData)

    # Splits the dictionaries to be more understandable
    (supply, demand) = splitDict(nodeData)
    (costs, mins, maxs) = splitDict(arcData)
    vars = LpVariable.dicts("X",arcs,None,None,LpInteger)

    # print(vars)
    # # Creates the upper and lower bounds on the variables
    for arc in arcs:
        vars[arc].bounds(mins[arc], maxs[arc])

    # Creates the 'prob' variable to contain the problem data
    prob = LpProblem("Minimum Cost Flow Linear Problem Phase1",LpMinimize)

    # Creates the objective function
    prob += lpSum([vars[a]* costs[a] for a in arcs]), "The Objective Function"

    # Creates all problem constraints - this ensures the amount going into each node is
    # at least equal to the amount leaving
    for n in nodes:
        prob += (supply[n]+ lpSum([vars[(i,j)] for (i,j) in arcs if j == n]) >=
                 demand[n]+ lpSum([vars[(i,j)] for (i,j) in arcs if i == n])), \
                f"Flow balance in Node {n}"

    # The problem data is written to an .lp file
    prob.writeLP("results/minimize_fleet.lp")

    # The problem is solved using PuLP's choice of Solver
    prob.solve(PULP_CBC_CMD(msg=0))
    # The optimised objective function value is printed to the screen
    print ("Total Cost of MCFP = ", value(prob.objective))
    print ("Used Taxis = ", number_of_trips + int(value(prob.objective)))


def main():
    args = parse_args("Minimize Fleet Size (ILP)")

    trips, distances, number_of_trips, left_nodes, right_nodes = file_processing(
        args.trips, args.distance
    )
    set_distance_matrix(distances)

    edges, nodes = pre_processing(trips, constraint_mode='combined')

    start = timer.time()
    solve_minimize_fleet_ilp(nodes, edges, number_of_trips)
    end = timer.time()

    print('-------------------------')
    print('Execution Time: ', end - start, 's', "\t |")
    print('-------------------------')


if __name__ == "__main__":
    main()
