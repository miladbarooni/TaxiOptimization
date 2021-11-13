import networkx as nx
import time
# import matplotlib.pyplot as plt


matrixD = list()
trips_converter = dict()

def file_processing():
    trips = list()
    distances = list()
    with open("./Dataset/d3.txt") as fp:
        number_of_trips = fp.readline()
        for i in range(int(number_of_trips)):
            trip = fp.readline()[:-1]
            trip_datas = trip.split(',')
            trip_datas[0], trip_datas[1] = int(trip_datas[0])//100 * 60 + (int(trip_datas[0])%100), int(trip_datas[1])//100 * 60 + (int(trip_datas[1])%100)

            trips_converter["trip_"+str(i+1)+"_start"], trips_converter["trip_"+str(i+1)+"_end"] = int(trip_datas[2]), int(trip_datas[3])

            # trip_datas = list(map(int, trip_datas))
            trips.append(trip_datas)
    with open("./MarixD_dataset1_General.txt") as fp:
        lines = fp.readlines()
        zero_for_matrixD = -1
        for line in lines:
            splited_line = list(map(int, line.split()))
            if zero_for_matrixD >= 0:
                splited_line = zero_for_matrixD * [0] + splited_line
            distances.append(splited_line)
            zero_for_matrixD += 1

    return trips, distances, int(number_of_trips)


def get_distance(i, j):
    # return matrixD[i][j]
    if i > j:
        return matrixD[j][i]
    return matrixD[i][j]


def valid_difference_time(time_end_trip1, time_end_trip2, trip_time2, distance_time):
    if time_end_trip1 + distance_time + trip_time2 > time_end_trip2:
        return False
    return True


def valid_difference_time2(time_start_trip1, time_start_trip2, trip_time1, distance_time):
    if time_start_trip1 + distance_time + trip_time1 > time_start_trip2:
        return False
    return True


def simple_valid_difference_time(time_end_trip1, time_start_trip2, distance_time):
    if time_end_trip1 + distance_time <= time_start_trip2:
        return True
    return False


def pre_processing(trips):
    edges = {"back_edge":[], "trip_edge":[], "start_edge":[], "end_edge":[], "garbage_edge":[]}
    nodes = list()
    for i in range(len(trips)):
        for j in range(len(trips)):
            if trips[i] == trips[j]:
                continue
            if simple_valid_difference_time(
                trips[i][1],
                trips[j][0],
                get_distance(int(trips[i][3]), int(trips[j][2]))
            ):
                edges["back_edge"].append(["trip_"+str(i+1)+"_end", "trip_"+str(j+1)+"_start"])
    for i in range(len(trips)):
        # create nodes
        nodes.append("trip_"+str(i+1)+"_start")
        nodes.append("trip_"+str(i+1)+"_end")
        # nodes.append("parking_start")
        # nodes.append("parking_end")
        # create edges
        # edges["trip_edge"].append(["trip_"+str(i+1)+"_start", "trip_"+str(i+1)+"_end"])
        edges["start_edge"].append(["parking_start", "trip_"+str(i+1)+"_start"])
        edges["end_edge"].append(["trip_"+str(i+1)+"_end", "parking_end"])
    edges["garbage_edge"].append(["parking_start", "parking_end"])
    return edges, nodes


def get_trip_number(name: str):
    start_index = name.find('_')
    name = name[start_index+1:]
    end_index = name.find('_')
    return int(name[:end_index]), name[end_index+1:]


def get_state_number(name: str):
    return trips_converter[name]


def solve_phase1(edges, nodes, number_of_trips):
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



if __name__ == "__main__":
    trips, distances, number_of_trips = file_processing()
    matrixD = distances
    edges, nodes = pre_processing(trips)
    start = time.time()
    G, flowCost = solve_phase1(edges, nodes, number_of_trips)
    end = time.time()
    print('------------------------------------')
    print('Execution Time: ', end - start, 's')
    print('------------------------------------')
    # print('used taxi:', number_of_trips - flowCost2)
    # print(get_distance(distances, 9, 4))
    # subax1 = plt.subplot(121)
    # nx.draw(G, with_labels=True, font_weight='bold')
    # plt.show()
    # subax2 = plt.subplot(122)
    # nx.draw_shell(G, nlist=[range(5, 10), range(5)], with_labels=True, font_weight='bold')
    # plt.show()
    # ax = plt.axes()
    # pos = nx.spring_layout(G)
    # print(pos)
