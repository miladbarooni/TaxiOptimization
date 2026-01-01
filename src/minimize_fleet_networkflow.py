"""
Minimize Fleet Size using Network Flow (NetworkX).

This module solves the taxi fleet minimization problem using the network simplex
algorithm from NetworkX. It finds the minimum number of taxis required to serve
all trips.
"""

import time

import matplotlib.pyplot as plt
import networkx as nx

from utils import (
    parse_args,
    file_processing,
    pre_processing,
    get_trip_number,
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
        flowDict: Flow on each edge
    """
    # Defind directed graph
    G = nx.DiGraph()

    # Adding nodes
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
    # print(flowDict)
    print("FlowCost: ", flowCost)
    print('------------------------------------')
    print('Used Taxi:', number_of_trips + flowCost)
    # print(flowDict)
    # print (flow_cost)
    return G, flowCost, flowDict


def visualize_network(edges, number_of_trips, left_nodes, right_nodes):
    """Create visualization of the network flow graph."""
    # Make complete graph
    graph = nx.DiGraph()

    # edges = {"back_edge": [], "trip_edge": [], "start_edge": [], "end_edge": [], "garbage_edge": []}
    for i in range(number_of_trips):
        graph.add_edge('trip_' + str(i + 1) + '_start', 'trip_' + str(i + 1) + '_end')
        graph.add_edge('parking_start', 'trip_' + str(i + 1) + '_start')
        graph.add_edge('trip_' + str(i + 1) + '_end', 'parking_end')

    for edge in edges['back_edge']:
        graph.add_edge(edge[0], edge[1])

    position = {}
    position.update((node, (2, number_of_trips - index)) for index, node in enumerate(left_nodes))
    position.update((node, (3, number_of_trips - index)) for index, node in enumerate(right_nodes))

    position.update({'parking_start': (1, number_of_trips / 2)})
    position.update({'parking_end': (4, number_of_trips / 2)})

    nx.draw(G=graph, pos=position, with_labels=True)
    plt.show()


def main():
    args = parse_args("Minimize Fleet Size (Network Flow)")

    trips, distances, number_of_trips, left_nodes, right_nodes = file_processing(
        args.trips, args.distance
    )
    set_distance_matrix(distances)

    edges, nodes = pre_processing(trips, constraint_mode='combined')

    start = time.time()
    G, flowCost, flowDict = solve_minimize_fleet(edges, nodes, number_of_trips)
    end = time.time()

    print('------------------------------------')
    print('Execution Time: ', end - start, 's')
    print('------------------------------------')

    if not args.no_plot:
        visualize_network(edges, number_of_trips, left_nodes, right_nodes)


if __name__ == "__main__":
    main()
