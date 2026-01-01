"""
Bi-objective Optimization: Fleet Size vs Empty Travel Distance.

This module performs multi-objective optimization comparing three different
trip compatibility constraint formulations and evaluates the trade-off between
minimizing fleet size and minimizing empty travel distance.
"""

import time

import networkx as nx

from utils import (
    parse_args,
    file_processing,
    pre_processing,
    get_state_number,
    set_distance_matrix,
    get_distance,
    calculate_mean_trip_time,
)


def solve_phase1(edges, nodes, number_of_trips):
    """
    Solve Phase 1: Minimize fleet size.

    Returns:
        G: NetworkX DiGraph
        flowCost: Optimal flow cost
        flowDict: Flow on each edge
    """
    # Defind directed graph
    G = nx.DiGraph()

    #Adding nodes
    G.add_node('parking_start', demand=-number_of_trips)
    G.add_node('parking_end', demand=number_of_trips)
    for node in nodes:
        if node[-3:] == 'end':
            G.add_node(node, demand=-1)
        else:
            G.add_node(node, demand=1)

    # Adding edges
    for edge in edges['garbage_edge']:
        G.add_edge(edge[0], edge[1], capacity=number_of_trips, weight=-1)
    for edge in edges['start_edge']:
        G.add_edge(edge[0], edge[1], capacity=1, weight=0)
    for edge in edges['end_edge']:
        G.add_edge(edge[0], edge[1], capacity=1, weight=0)
    for edge in edges['back_edge']:
        G.add_edge(edge[0], edge[1], capacity=1, weight=0)

    # Solve network model
    flowCost, flowDict = nx.network_simplex(G)
    return G, flowCost, flowDict


def solve_phase2(edges, nodes, number_of_trips):
    """
    Solve Phase 2: Minimize empty travel distance.

    Returns:
        G: NetworkX DiGraph
        flowCost: Optimal flow cost (total empty distance)
        flowDict: Flow on each edge
    """
    G = nx.DiGraph()

    #Adding nodes
    G.add_node('parking_start', demand=-number_of_trips)
    G.add_node('parking_end', demand=number_of_trips)
    for node in nodes:
        if node[-3:] == 'end':
            G.add_node(node, demand=-1)
        else:
            G.add_node(node, demand=1)

    # Adding edges
    for edge in edges['garbage_edge']:
        G.add_edge(edge[0], edge[1], capacity=number_of_trips, weight=0)
    for edge in edges['start_edge']:
        G.add_edge(edge[0], edge[1], capacity=1, weight=get_distance(1, get_state_number(edge[1])))
    for edge in edges['end_edge']:
        G.add_edge(edge[0], edge[1], capacity=1, weight=get_distance(get_state_number(edge[0]), 1))
    for edge in edges['back_edge']:
        G.add_edge(edge[0], edge[1], capacity=1, weight=get_distance(get_state_number(edge[0]), get_state_number(edge[1])))

    # Solvve network model
    flowCost, flowDict = nx.network_simplex(G)
    return G, flowCost, flowDict


def main():
    args = parse_args("Bi-objective Optimization")

    trips, distances, number_of_trips, left_nodes, right_nodes = file_processing(
        args.trips, args.distance
    )
    set_distance_matrix(distances)

    trips_mean_time = calculate_mean_trip_time(trips)
    print("Mean trip time:", trips_mean_time)

    # Test three different constraint formulations
    constraint_modes = ['combined', 'end_time', 'start_time']
    all_edges = []

    for mode in constraint_modes:
        edges, nodes = pre_processing(trips, constraint_mode=mode)
        all_edges.append([edges, nodes, mode])

    # Phase 1: Find minimum fleet sizes for each formulation
    print("\n=== Phase 1: Minimum Fleet Size ===")
    all_flows_from_phase1 = []
    for edges, nodes, mode in all_edges:
        G, flowCost, flowDict = solve_phase1(edges, nodes, number_of_trips)
        min_taxis = number_of_trips + flowCost
        all_flows_from_phase1.append(min_taxis)
        print(f"  {mode}: {min_taxis} taxis")

    # Phase 2: Find minimum distance for each fleet size / formulation combination
    print("\n=== Phase 2: Minimum Empty Distance ===")
    pre_costs = []
    for flowcost in all_flows_from_phase1:
        for edges, nodes, mode in all_edges:
            try:
                G, flow_cost, flow_dict = solve_phase2(edges, nodes, flowcost)
                print(f"  Fleet={flowcost}, {mode}: distance={flow_cost}")
            except:
                print(f"  Fleet={flowcost}, {mode}: infeasible")
                flow_cost = 10000000
            pre_costs.append((flowcost, flow_cost))

    # Calculate efficiency metrics
    print("\n=== Efficiency Analysis ===")
    costs = dict()
    for (used_taxi, waste_time) in pre_costs:
        efficiency = int((used_taxi * trips_mean_time) - (waste_time / number_of_trips))
        costs[(used_taxi, waste_time)] = efficiency

    print("(Used Taxis, Empty Distance) -> Efficiency Score")
    for key, value in sorted(costs.items(), key=lambda x: x[1], reverse=True):
        print(f"  {key} -> {value}")


if __name__ == "__main__":
    main()
