"""
Minimize Fleet Size using Network Flow (Simplified Constraints).

This module uses simplified time constraints for trip compatibility:
only checks if driver can reach the next pickup before its start time.
"""

import time

import networkx as nx

from utils import (
    parse_args,
    file_processing,
    pre_processing,
    set_distance_matrix,
)


def solve_minimize_fleet(edges, nodes, number_of_trips):
    """
    Solve the minimum fleet size problem using network simplex.

    Args:
        edges: Dict containing network edges
        nodes: List of trip nodes
        number_of_trips: Total number of trips

    Returns:
        G: NetworkX DiGraph
        flowCost: Optimal flow cost
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

    # Solvve network model
    flowCost, flowDict = nx.network_simplex(G)
    # print(flowDict)
    print("FlowCost: ", flowCost)
    print('------------------------------------')
    print('used taxi:', number_of_trips + flowCost)
    # print(flowDict)
    # print (flow_cost)
    return G, flowCost


def main():
    args = parse_args("Minimize Fleet Size (Simple Constraints)")

    trips, distances, number_of_trips, left_nodes, right_nodes = file_processing(
        args.trips, args.distance
    )
    set_distance_matrix(distances)

    edges, nodes = pre_processing(trips, constraint_mode='simple')

    start = time.time()
    G, flowCost = solve_minimize_fleet(edges, nodes, number_of_trips)
    end = time.time()

    print('------------------------------------')
    print('Execution Time: ', end - start, 's')
    print('------------------------------------')


if __name__ == "__main__":
    main()
