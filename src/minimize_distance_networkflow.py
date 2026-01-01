"""
Minimize Empty Travel Distance using Network Flow (NetworkX).

This module solves the taxi fleet optimization problem to minimize the total
distance traveled without passengers (empty kilometers).
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
    """Create visualization of the flow solution with colored taxi routes."""
    graph = nx.DiGraph()

    def dfs(node, flowDict, edges, color):
        if node == 'parking_end':
            return edges
        dst_node = None
        if node[-5:] == 'start':
            trip_number, _ = get_trip_number(node)
            dst_node = 'trip_' + str(trip_number) + '_end'
            graph.add_edge(node, dst_node, color=color)
            return dfs(dst_node, flowDict, edges, color)
        for d_node in flowDict[node]:
            if flowDict[node][d_node] != 0:
                dst_node = d_node
                break
        graph.add_edge(node, dst_node, color=color)
        return dfs(dst_node, flowDict, edges, color)

    colors = ['green', 'red', 'blue', 'black', 'brown', 'purple', 'pink', 'cyan', 'gray']

    i = 0
    for node in flowDict['parking_start']:
        if node == 'parking_end':
            continue
        if flowDict['parking_start'][node] != 0:
            graph.add_edge('parking_start', node, color=colors[i % len(colors)])
            colored_edges = dfs(node, flowDict, [], colors[i % len(colors)])

            i += 1

    position = {}
    position.update((node, (2, number_of_trips - index)) for index, node in enumerate(left_nodes))
    position.update((node, (3, number_of_trips - index)) for index, node in enumerate(right_nodes))

    position.update({'parking_start': (1, number_of_trips / 2)})
    position.update({'parking_end': (4, number_of_trips / 2)})

    graph_edges = graph.edges()
    colors = [graph[u][v]['color'] for u, v in graph_edges]
    nx.draw(G=graph, pos=position, edge_color=colors, with_labels=True)
    plt.show()


def main():
    args = parse_args("Minimize Empty Travel Distance (Network Flow)")

    trips, distances, number_of_trips, left_nodes, right_nodes = file_processing(
        args.trips, args.distance
    )
    set_distance_matrix(distances)

    edges, nodes = pre_processing(trips, constraint_mode='combined')

    start = time.time()
    G, flowCost, flowDict = solve_minimize_distance(edges, nodes, number_of_trips)
    end = time.time()

    print('-------------------------')
    print('Execution Time: ', int(end - start), 's', "\t |")
    print('-------------------------')

    if not args.no_plot:
        visualize_flow(flowDict, number_of_trips, left_nodes, right_nodes)


if __name__ == "__main__":
    main()
