"""
Shared utilities for Taxi Fleet Optimization.

This module contains common functions used across all optimization approaches:
- File I/O for trips and distance matrix
- Time validation functions for trip compatibility
- Graph preprocessing for network flow models
"""

import argparse


# Global state (preserved from original design)
matrixD = list()
trips_converter = {}  # type: dict


def parse_args(description="Taxi Fleet Optimization"):
    """Parse command line arguments for dataset and distance matrix paths."""
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        '--trips', '-t',
        type=str,
        default='./data/small/d1.txt',
        help='Path to trips dataset file'
    )
    parser.add_argument(
        '--distance', '-d',
        type=str,
        default='./data/distance_matrix.txt',
        help='Path to distance matrix file'
    )
    parser.add_argument(
        '--no-plot',
        action='store_true',
        help='Disable visualization (for benchmarking)'
    )
    return parser.parse_args()


def file_processing(trips_file, distance_file):
    """
    Load trips and distance matrix from files.

    Args:
        trips_file: Path to trips dataset
        distance_file: Path to distance matrix

    Returns:
        trips: List of trip data [start_time, end_time, pickup, dropoff]
        distances: Distance matrix (upper triangular)
        number_of_trips: Total number of trips
        left_nodes: List of trip start node names
        right_nodes: List of trip end node names
    """
    global trips_converter

    trips = list()
    distances = list()
    left_nodes = list()
    right_nodes = list()

    with open(trips_file) as fp:
        number_of_trips = fp.readline()
        for i in range(int(number_of_trips)):
            trip = fp.readline()[:-1]
            trip_datas = trip.split(',')
            # Convert HHMM to minutes
            trip_datas[0], trip_datas[1] = int(trip_datas[0]) // 100 * 60 + (int(trip_datas[0]) % 100), int(trip_datas[1]) // 100 * 60 + (int(trip_datas[1]) % 100)

            trips_converter["trip_" + str(i + 1) + "_start"], trips_converter["trip_" + str(i + 1) + "_end"] = int(trip_datas[2]), int(trip_datas[3])

            left_nodes.append("trip_" + str(i + 1) + "_start")
            right_nodes.append("trip_" + str(i + 1) + "_end")
            # trip_datas = list(map(int, trip_datas))
            trips.append(trip_datas)

    with open(distance_file) as fp:
        lines = fp.readlines()
        zero_for_matrixD = -1
        for line in lines:
            splited_line = list(map(int, line.split()))
            if zero_for_matrixD >= 0:
                splited_line = zero_for_matrixD * [0] + splited_line
            distances.append(splited_line)
            zero_for_matrixD += 1

    return trips, distances, int(number_of_trips), left_nodes, right_nodes


def get_distance(i, j):
    """Get distance between locations i and j from the global matrix."""
    global matrixD
    # return matrixD[i][j]
    if i > j:
        return matrixD[j][i]
    return matrixD[i][j]


def valid_difference_time(time_end_trip1, time_end_trip2, trip_time2, distance_time):
    """Check if trip2 can follow trip1 based on end times."""
    if time_end_trip1 + distance_time + trip_time2 > time_end_trip2:
        return False
    return True


def valid_difference_time2(time_start_trip1, time_start_trip2, trip_time1, distance_time):
    """Check if trip2 can follow trip1 based on start times."""
    if time_start_trip1 + distance_time + trip_time1 > time_start_trip2:
        return False
    return True


def simple_valid_difference_time(time_end_trip1, time_start_trip2, distance_time):
    """Simple check: can driver reach trip2 pickup before its start time."""
    if time_end_trip1 + distance_time <= time_start_trip2:
        return True
    return False


def pre_processing(trips, constraint_mode='combined'):
    """
    Build network edges and nodes for the optimization model.

    Args:
        trips: List of trip data
        constraint_mode: 'combined', 'end_time', 'start_time', or 'simple'

    Returns:
        edges: Dict with back_edge, trip_edge, start_edge, end_edge, garbage_edge
        nodes: List of node names
    """
    edges = {"back_edge": [], "trip_edge": [], "start_edge": [], "end_edge": [], "garbage_edge": []}
    nodes = list()

    for i in range(len(trips)):
        for j in range(len(trips)):
            if trips[i] == trips[j]:
                continue

            is_compatible = False

            if constraint_mode == 'simple':
                is_compatible = simple_valid_difference_time(
                    trips[i][1],
                    trips[j][0],
                    get_distance(int(trips[i][3]), int(trips[j][2]))
                )
            elif constraint_mode == 'end_time':
                is_compatible = valid_difference_time(
                    trips[i][1],
                    trips[j][1],
                    get_distance(int(trips[j][2]), int(trips[j][3])),
                    get_distance(int(trips[i][3]), int(trips[j][2]))
                )
            elif constraint_mode == 'start_time':
                is_compatible = valid_difference_time2(
                    trips[i][0],
                    trips[j][0],
                    get_distance(int(trips[i][2]), int(trips[i][3])),
                    get_distance(int(trips[i][3]), int(trips[j][2]))
                )
            else:  # combined (default)
                is_compatible = valid_difference_time(
                    trips[i][1],
                    trips[j][1],
                    get_distance(int(trips[j][2]), int(trips[j][3])),
                    get_distance(int(trips[i][3]), int(trips[j][2]))
                ) or valid_difference_time2(
                    trips[i][0],
                    trips[j][0],
                    get_distance(int(trips[i][2]), int(trips[i][3])),
                    get_distance(int(trips[i][3]), int(trips[j][2]))
                )

            if is_compatible:
                edges["back_edge"].append(["trip_" + str(i + 1) + "_end", "trip_" + str(j + 1) + "_start"])

    for i in range(len(trips)):
        # create nodes
        nodes.append("trip_" + str(i + 1) + "_start")
        nodes.append("trip_" + str(i + 1) + "_end")

        # create edges
        edges["trip_edge"].append(["trip_" + str(i + 1) + "_start", "trip_" + str(i + 1) + "_end"])
        edges["start_edge"].append(["parking_start", "trip_" + str(i + 1) + "_start"])
        edges["end_edge"].append(["trip_" + str(i + 1) + "_end", "parking_end"])

    edges["garbage_edge"].append(["parking_start", "parking_end"])
    return edges, nodes


def get_trip_number(name: str):
    """Extract trip number and type (start/end) from node name."""
    start_index = name.find('_')
    name = name[start_index + 1:]
    end_index = name.find('_')
    return int(name[:end_index]), name[end_index + 1:]


def get_state_number(name: str):
    """Get location number for a trip node."""
    return trips_converter[name]


def calculate_mean_trip_time(trips):
    """Calculate average trip duration in minutes."""
    if not trips:
        return 0
    trip_sum = sum(trip[1] - trip[0] for trip in trips)
    return trip_sum // len(trips)


def set_distance_matrix(distances):
    """Set the global distance matrix."""
    global matrixD
    matrixD = distances
