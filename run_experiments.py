#!/usr/bin/env python
"""
Run all experiments and collect results.
This script runs Phase 1, 2, and 3 on all datasets and saves results.
"""

import os
import sys
import time
import json
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import networkx as nx

# Global variables used by the modules
matrixD = []
trips_converter = {}


def load_distance_matrix(filepath):
    """Load distance matrix from file."""
    distances = []
    with open(filepath) as fp:
        lines = fp.readlines()
        zero_for_matrixD = -1
        for line in lines:
            splited_line = list(map(int, line.split()))
            if zero_for_matrixD >= 0:
                splited_line = zero_for_matrixD * [0] + splited_line
            distances.append(splited_line)
            zero_for_matrixD += 1
    return distances


def load_trips(filepath):
    """Load trips from file."""
    trips = []
    left_nodes = []
    right_nodes = []
    local_converter = {}

    with open(filepath) as fp:
        number_of_trips = int(fp.readline())
        for i in range(number_of_trips):
            trip = fp.readline().strip()
            trip_datas = trip.split(',')
            # Convert HHMM to minutes
            trip_datas[0] = int(trip_datas[0]) // 100 * 60 + (int(trip_datas[0]) % 100)
            trip_datas[1] = int(trip_datas[1]) // 100 * 60 + (int(trip_datas[1]) % 100)

            local_converter[f"trip_{i+1}_start"] = int(trip_datas[2])
            local_converter[f"trip_{i+1}_end"] = int(trip_datas[3])

            left_nodes.append(f"trip_{i+1}_start")
            right_nodes.append(f"trip_{i+1}_end")
            trips.append(trip_datas)

    return trips, number_of_trips, left_nodes, right_nodes, local_converter


def get_distance(matrix, i, j):
    """Get distance between two locations."""
    if i > j:
        return matrix[j][i]
    return matrix[i][j]


def valid_difference_time(time_end_trip1, time_end_trip2, trip_time2, distance_time):
    if time_end_trip1 + distance_time + trip_time2 > time_end_trip2:
        return False
    return True


def valid_difference_time2(time_start_trip1, time_start_trip2, trip_time1, distance_time):
    if time_start_trip1 + distance_time + trip_time1 > time_start_trip2:
        return False
    return True


def pre_processing(trips, matrix):
    """Create edges for network flow."""
    edges = {"back_edge": [], "start_edge": [], "end_edge": [], "garbage_edge": []}
    nodes = []

    for i in range(len(trips)):
        for j in range(len(trips)):
            if trips[i] == trips[j]:
                continue
            if valid_difference_time(
                    trips[i][1],
                    trips[j][1],
                    get_distance(matrix, int(trips[j][2]), int(trips[j][3])),
                    get_distance(matrix, int(trips[i][3]), int(trips[j][2]))) \
                    or \
                    valid_difference_time2(
                        trips[i][0],
                        trips[j][0],
                        get_distance(matrix, int(trips[i][2]), int(trips[i][3])),
                        get_distance(matrix, int(trips[i][3]), int(trips[j][2]))):
                edges["back_edge"].append([f"trip_{i+1}_end", f"trip_{j+1}_start"])

    for i in range(len(trips)):
        nodes.append(f"trip_{i+1}_start")
        nodes.append(f"trip_{i+1}_end")
        edges["start_edge"].append(["parking_start", f"trip_{i+1}_start"])
        edges["end_edge"].append([f"trip_{i+1}_end", "parking_end"])

    edges["garbage_edge"].append(["parking_start", "parking_end"])
    return edges, nodes


def solve_phase1(edges, nodes, number_of_trips):
    """Solve minimum fleet size problem."""
    G = nx.DiGraph()

    G.add_node('parking_start', demand=-number_of_trips)
    G.add_node('parking_end', demand=number_of_trips)

    for node in nodes:
        if node[-3:] == 'end':
            G.add_node(node, demand=-1)
        else:
            G.add_node(node, demand=1)

    for edge in edges['garbage_edge']:
        G.add_edge(edge[0], edge[1], capacity=number_of_trips, weight=-1)
    for edge in edges['start_edge']:
        G.add_edge(edge[0], edge[1], capacity=1, weight=0)
    for edge in edges['end_edge']:
        G.add_edge(edge[0], edge[1], capacity=1, weight=0)
    for edge in edges['back_edge']:
        G.add_edge(edge[0], edge[1], capacity=1, weight=0)

    flowCost, flowDict = nx.network_simplex(G)
    used_taxis = number_of_trips + flowCost

    return used_taxis, flowCost, flowDict


def solve_phase2(edges, nodes, number_of_trips, matrix, converter):
    """Solve minimum distance problem."""
    G = nx.DiGraph()

    G.add_node('parking_start', demand=-number_of_trips)
    G.add_node('parking_end', demand=number_of_trips)

    for node in nodes:
        if node[-3:] == 'end':
            G.add_node(node, demand=-1)
        else:
            G.add_node(node, demand=1)

    for edge in edges['garbage_edge']:
        G.add_edge(edge[0], edge[1], capacity=number_of_trips, weight=0)
    for edge in edges['start_edge']:
        G.add_edge(edge[0], edge[1], capacity=1, weight=get_distance(matrix, 1, converter[edge[1]]))
    for edge in edges['end_edge']:
        G.add_edge(edge[0], edge[1], capacity=1, weight=get_distance(matrix, converter[edge[0]], 1))
    for edge in edges['back_edge']:
        G.add_edge(edge[0], edge[1], capacity=1, weight=get_distance(matrix, converter[edge[0]], converter[edge[1]]))

    flowCost, flowDict = nx.network_simplex(G)
    used_taxis = number_of_trips - flowDict['parking_start']['parking_end']

    return used_taxis, flowCost


def run_experiment(dataset_name, trip_file, matrix_file):
    """Run experiment on a single dataset."""
    print(f"\n{'='*60}")
    print(f"Dataset: {dataset_name}")
    print('='*60)

    # Load data
    matrix = load_distance_matrix(matrix_file)
    trips, num_trips, left_nodes, right_nodes, converter = load_trips(trip_file)

    print(f"Number of trips: {num_trips}")
    print(f"Number of locations: {len(matrix)}")

    # Preprocess
    edges, nodes = pre_processing(trips, matrix)
    print(f"Compatible trip pairs: {len(edges['back_edge'])}")

    results = {
        'dataset': dataset_name,
        'num_trips': num_trips,
        'num_locations': len(matrix),
        'compatible_pairs': len(edges['back_edge']),
    }

    # Phase 1: Minimum Fleet
    print("\n--- Phase 1: Minimum Fleet Size ---")
    start = time.time()
    used_taxis, flow_cost, _ = solve_phase1(edges, nodes, num_trips)
    phase1_time = time.time() - start
    print(f"Minimum taxis needed: {used_taxis}")
    print(f"Execution time: {phase1_time:.4f}s")

    results['phase1'] = {
        'min_taxis': used_taxis,
        'flow_cost': flow_cost,
        'time_seconds': round(phase1_time, 4)
    }

    # Phase 2: Minimum Distance
    print("\n--- Phase 2: Minimum Empty Distance ---")
    start = time.time()
    used_taxis_p2, total_distance = solve_phase2(edges, nodes, num_trips, matrix, converter)
    phase2_time = time.time() - start
    print(f"Taxis used: {used_taxis_p2}")
    print(f"Total empty distance: {total_distance}")
    print(f"Execution time: {phase2_time:.4f}s")

    results['phase2'] = {
        'taxis_used': used_taxis_p2,
        'total_empty_distance': total_distance,
        'time_seconds': round(phase2_time, 4)
    }

    return results


def main():
    """Run all experiments."""
    print("="*60)
    print("Taxi Fleet Optimization - Experiment Runner")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)

    # Define datasets
    datasets = [
        ("Small (9 trips)", "data/small/d1.txt"),
        ("Medium (115 trips)", "data/medium/d2.txt"),
        ("Large (839 trips)", "data/large/d3.txt"),
        ("Synthetic (1500 trips)", "data/large/synthetic_1500.txt"),
        ("Synthetic (2000 trips)", "data/large/synthetic_2000.txt"),
        ("Synthetic (3000 trips)", "data/large/synthetic_3000.txt"),
    ]

    matrix_file = "data/distance_matrix.txt"

    all_results = []

    for name, trip_file in datasets:
        if os.path.exists(trip_file):
            result = run_experiment(name, trip_file, matrix_file)
            all_results.append(result)
        else:
            print(f"Warning: {trip_file} not found, skipping...")

    # Save results
    os.makedirs("results", exist_ok=True)
    results_file = "results/experiment_results.json"
    with open(results_file, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'experiments': all_results
        }, f, indent=2)

    print(f"\n{'='*60}")
    print("SUMMARY")
    print('='*60)
    print(f"{'Dataset':<25} {'Trips':>8} {'Min Taxis':>10} {'Empty Dist':>12} {'Time (s)':>10}")
    print('-'*60)
    for r in all_results:
        print(f"{r['dataset']:<25} {r['num_trips']:>8} {r['phase1']['min_taxis']:>10} {r['phase2']['total_empty_distance']:>12} {r['phase1']['time_seconds']:>10.4f}")

    print(f"\nResults saved to: {results_file}")
    print(f"Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
