import networkx as nx
import time
import matplotlib.pyplot as plt
from networkx.classes.function import number_of_edges


matrixD = list()
trips_converter = dict()
trips_mean_time = 0
def file_processing():
    trips = list()
    distances = list()
    left_nodes = list()
    right_nodes = list()
    trip_sum = 0
    with open("./Dataset/d1.txt") as fp:
        number_of_trips = fp.readline()
        
        for i in range(int(number_of_trips)):
            trip = fp.readline()[:-1]
            trip_datas = trip.split(',')
            trip_datas[0], trip_datas[1] = int(trip_datas[0])//100 * 60 + (int(trip_datas[0])%100), int(trip_datas[1])//100 * 60 + (int(trip_datas[1])%100)
            trip_sum += trip_datas[1]- trip_datas[0]
            trips_converter["trip_"+str(i+1)+"_start"], trips_converter["trip_"+str(i+1)+"_end"] = int(trip_datas[2]), int(trip_datas[3])
            left_nodes.append("trip_"+str(i+1)+"_start")
            right_nodes.append("trip_"+str(i+1)+"_end")
            # trip_datas = list(map(int, trip_datas))
            trips.append(trip_datas)
    
    trips_mean_time = trip_sum // int(number_of_trips)
    print (trips_mean_time)
    with open("./MarixD_dataset1_General.txt") as fp:
        lines = fp.readlines()
        zero_for_matrixD = -1
        for line in lines:
            splited_line = list(map(int, line.split()))
            if zero_for_matrixD >= 0:
                splited_line = zero_for_matrixD * [0] + splited_line
            distances.append(splited_line)
            zero_for_matrixD += 1

    return trips, distances, int(number_of_trips), left_nodes, right_nodes, trips_mean_time


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


def pre_processing1(trips):
	edges = {"back_edge":[], "trip_edge":[], "start_edge":[], "end_edge":[], "garbage_edge":[]}
	nodes = list()
	for i in range(len(trips)):
		for j in range(len(trips)):
			if trips[i] == trips[j]:
				continue
			if valid_difference_time(
					trips[i][1], 
					trips[j][1],
					get_distance(int(trips[j][2]), int(trips[j][3])),
					get_distance(int(trips[i][3]), int(trips[j][2]))
				) \
				or \
				valid_difference_time2(
					trips[i][0],
					trips[j][0],
					get_distance(int(trips[i][2]), int(trips[i][3])),
					get_distance(int(trips[i][3]), int(trips[j][2]))
				):
			# if simple_valid_difference_time(
			#     trips[i][1],
			#     trips[j][0],
			#     get_distance(int(trips[i][3]), int(trips[j][2]))
			# ):
				edges["back_edge"].append(["trip_"+str(i+1)+"_end", "trip_"+str(j+1)+"_start"])
	for i in range(len(trips)):
		# create nodes
		nodes.append("trip_"+str(i+1)+"_start")
		nodes.append("trip_"+str(i+1)+"_end")

		edges["start_edge"].append(["parking_start", "trip_"+str(i+1)+"_start"])
		edges["end_edge"].append(["trip_"+str(i+1)+"_end", "parking_end"])
	edges["garbage_edge"].append(["parking_start", "parking_end"])
	return edges, nodes

def pre_processing2(trips):
	edges = {"back_edge":[], "trip_edge":[], "start_edge":[], "end_edge":[], "garbage_edge":[]}
	nodes = list()
	for i in range(len(trips)):
		for j in range(len(trips)):
			if trips[i] == trips[j]:
				continue
			if valid_difference_time(
					trips[i][1], 
					trips[j][1],
					get_distance(int(trips[j][2]), int(trips[j][3])),
					get_distance(int(trips[i][3]), int(trips[j][2]))
				):
				edges["back_edge"].append(["trip_"+str(i+1)+"_end", "trip_"+str(j+1)+"_start"])
	for i in range(len(trips)):
		# create nodes
		nodes.append("trip_"+str(i+1)+"_start")
		nodes.append("trip_"+str(i+1)+"_end")

		edges["start_edge"].append(["parking_start", "trip_"+str(i+1)+"_start"])
		edges["end_edge"].append(["trip_"+str(i+1)+"_end", "parking_end"])
	edges["garbage_edge"].append(["parking_start", "parking_end"])
	return edges, nodes

def pre_processing3(trips):
	edges = {"back_edge":[], "trip_edge":[], "start_edge":[], "end_edge":[], "garbage_edge":[]}
	nodes = list()
	for i in range(len(trips)):
		for j in range(len(trips)):
			if trips[i] == trips[j]:
				continue
			if valid_difference_time2(
					trips[i][0],
					trips[j][0],
					get_distance(int(trips[i][2]), int(trips[i][3])),
					get_distance(int(trips[i][3]), int(trips[j][2]))
				):
				edges["back_edge"].append(["trip_"+str(i+1)+"_end", "trip_"+str(j+1)+"_start"])
	for i in range(len(trips)):
		# create nodes
		nodes.append("trip_"+str(i+1)+"_start")
		nodes.append("trip_"+str(i+1)+"_end")

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

	# Solve network model
	flowCost, flowDict = nx.network_simplex(G)
	# print(flowDict)
	# print("FlowCost: ", flowCost)
	# print('------------------------------------')
	# print('used taxi:', number_of_trips + flowCost)
	# print(flowDict)
	# print (flow_cost)
	return G, flowCost, flowDict





def solve_phase2(edges, nodes, number_of_trips):
    G = nx.DiGraph()
    # print("flow in out: ",number_of_trips)
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
    # print('-------------------------')
    # print("FlowCost: ", flowCost, "\t |")
    # print('-------------------------')
    # print('Used Taxi:', number_of_trips - flowDict['parking_start']['parking_end'], "\t |")
    # print(flowDict)
    return G, flowCost, flowDict


if __name__ == "__main__":
    trips, distances, number_of_trips, left_nodes, right_nodes, trips_mean_time = file_processing()
    matrixD = distances
    all_edges = []
    edges, nodes = pre_processing1(trips)
    all_edges.append([edges, nodes])
    edges, nodes = pre_processing2(trips)
    all_edges.append([edges, nodes])
    edges, nodes = pre_processing3(trips)
    all_edges.append([edges, nodes])

    all_flows_from_phase1 = []
    for edgenode in all_edges:
        G, flowCost, flowDict = solve_phase1(edgenode[0], edgenode[1], number_of_trips)
        all_flows_from_phase1.append(number_of_trips+flowCost)
    print (all_flows_from_phase1)
    edges, node = pre_processing1(trips)
    pre_costs = []
    for flowcost in all_flows_from_phase1:
        for edgenode in all_edges:
            print (flowcost)
            try:
                G, flow_cost, flow_dict = solve_phase2(edgenode[0], edgenode[1], flowcost)
            except:
                print("there is no such flow that satisfy the problem")
                flow_cost = 10000000
            pre_costs.append((flowcost, flow_cost))
    costs = dict()
    print (pre_costs)
    for (used_taxi, waste_time) in pre_costs:
        print (used_taxi*trips_mean_time)
        print (waste_time)
        costs[(used_taxi, waste_time)] = int((used_taxi*trips_mean_time) - (waste_time / number_of_trips))
    print(costs)

