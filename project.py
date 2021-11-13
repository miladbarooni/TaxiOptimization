import networkx as nx
from numpy import number

matrixD = [
            [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            [1, 0, 11, 19, 6, 4, 20, 16, 18, 20, 19],
            [2, 11, 0, 15, 17, 15, 13, 9, 10, 18, 13],
            [3, 19, 15, 0, 17, 16, 17, 11, 15, 16, 17],
            [4, 6, 17, 17, 0, 5, 15, 16, 16, 16, 15],
            [5, 4, 15, 16, 5, 0, 11, 8, 10, 14, 12],
            [6, 20, 13, 17, 15, 11, 0, 12, 13, 18, 4],
            [7, 16, 9, 11, 16, 8, 12, 0, 10, 8, 11],
            [8, 18, 10, 15, 16, 10, 13, 10, 0, 9, 8],
            [9, 20, 18, 16, 16, 14, 18, 8, 9, 0, 7],
            [10,19, 13, 17, 15, 12, 4, 11, 8, 7, 0]
        ]

def file_processing():
    trips = list()
    distances = list()
    with open("./General-Dataset-1.txt") as file:
        number_of_trips = file.readline()
        for i in range(int(number_of_trips)):
            trip = file.readline()[:-1]
            trip_datas = trip.split(',')
            trip_datas[0], trip_datas[1] = int(trip_datas[0])//100 * 60 + (int(trip_datas[0])%100), int(trip_datas[1])//100 * 60 + (int(trip_datas[1])%100)
            # trip_datas = list(map(int, trip_datas))
            trips.append(trip_datas)
    with open("./MarixD_dataset1_General.txt") as file:
        lines = file.readlines()
        idx = 0
        for line in lines:
            splited_line = list(map(int, line.split()))
            distances.append(splited_line)
            idx += 1

    return trips, distances

def get_distance(i, j):
    return matrixD[i][j]

def valid_difference_time(time_end, time_start, distance_time):
    if time_end + distance_time > time_start:
        return False
    return True


    

def pre_processing(trips, distances):
    edges = {"backedge":[], "trip_edge":[], "start_edge":[], "end_edge":[], "garbage_edge":[]}
    nodes = list()
    for i in range(len(trips)):
        for j in range(len(trips)):
            if trips[i] == trips[j]:
                continue
            if (valid_difference_time(trips[i][1], trips[j][0], get_distance(int(trips[i][3]), int(trips[j][2])))):
                edges["backedge"].append(["trip_"+str(i+1)+"_end", "trip_"+str(j+1)+"_start"])
    for i in range(len(trips)):
        # create nodes
        nodes.append("trip_"+str(i+1)+"_start")
        nodes.append("trip_"+str(i+1)+"_end")
        nodes.append("parking_start")
        nodes.append("parking_end")
        # create edges
        edges["trip_edge"].append(["trip_"+str(i+1)+"_start", "trip_"+str(i+1)+"_end"])
        edges["start_edge"].append(["parking_start", "trip_"+str(i+1)+"_start"])
        edges["end_edge"].append(["trip_"+str(i+1)+"_end", "parking_end"])
    edges["garbage_edge"].append([["parking_start", "parking_end"]])
    return edges, nodes


def main(edges, nodes):
    G = nx.DiGraph()
    
    

if __name__ == "__main__":
    trips, distances = file_processing()
    edges, nodes = pre_processing(trips, distances)
    main(edges, nodes)