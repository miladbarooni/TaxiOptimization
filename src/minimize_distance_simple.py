"""
Minimize Empty Travel Distance using Network Flow (Simplified Constraints).

This module uses simplified time constraints for trip compatibility:
only checks if driver can reach the next pickup before its start time.
"""

import time

import matplotlib.pyplot as plt
import networkx as nx

from utils import (
    parse_args,
    file_processing,
    pre_processing,
    get_trip_number,
    get_state_number,
    set_distance_matrix,
    get_distance,
)


def solve_minimize_distance(edges, nodes, number_of_trips):
    """
    Solve the minimum empty travel distance problem using network simplex.

    Args:
        edges: Dict containing network edges
        nodes: List of trip nodes
        number_of_trips: Total number of trips

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
    print('-------------------------')
    print("FlowCost: ", flowCost, "\t |")
    print('-------------------------')
    print('Used Taxi:', number_of_trips - flowDict['parking_start']['parking_end'], "\t |")
    # print(flowDict)
    return G, flowCost, flowDict


def visualize_flow(flowDict, number_of_trips, left_nodes, right_nodes):
    """Create visualization of the flow solution."""
    bipartite_edges = list()

    for i in range(len(left_nodes)):
        bipartite_edges.append((left_nodes[i], right_nodes[i]))

    for node in flowDict:
        for node2 in flowDict[node]:
            if flowDict[node][node2] != 0:
                if node == 'parking_start' and node2 == 'parking_end':
                    continue
                bipartite_edges.append((node, node2))
    # print(bipartite_edges)
    graph = nx.DiGraph()

    graph.add_edges_from(bipartite_edges)


    position = {}
    position.update((node, (2, number_of_trips - index)) for index, node in enumerate(left_nodes))
    position.update((node, (3, number_of_trips - index)) for index, node in enumerate(right_nodes))

    position.update({'parking_start': (1, number_of_trips/2)})
    position.update({'parking_end': (4, number_of_trips/2)})


    nx.draw(graph, pos=position, with_labels=True)
    plt.show()


def main():
    args = parse_args("Minimize Empty Travel Distance (Simple Constraints)")

    trips, distances, number_of_trips, left_nodes, right_nodes = file_processing(
        args.trips, args.distance
    )
    set_distance_matrix(distances)

    edges, nodes = pre_processing(trips, constraint_mode='simple')

    start = time.time()
    G, flowCost, flowDict = solve_minimize_distance(edges, nodes, number_of_trips)
    end = time.time()

    print('-------------------------')
    print('Execution Time: ', end - start, 's', "\t |")
    print('-------------------------')

    if not args.no_plot:
        visualize_flow(flowDict, number_of_trips, left_nodes, right_nodes)


if __name__ == "__main__":
    main()
