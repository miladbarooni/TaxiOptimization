import time

import matplotlib.pyplot as plt
import networkx as nx

matrixD = list()
trips_converter = dict()


def file_processing():
	trips = list()
	distances = list()
	left_nodes = list()
	right_nodes = list()
	with open("./Dataset/d1.txt") as fp:
		number_of_trips = fp.readline()
		for i in range(int(number_of_trips)):
			trip = fp.readline()[:-1]
			trip_datas = trip.split(',')
			trip_datas[0], trip_datas[1] = int(trip_datas[0]) // 100 * 60 + (int(trip_datas[0]) % 100), int(trip_datas[1]) // 100 * 60 + (int(trip_datas[1]) % 100)

			trips_converter["trip_" + str(i + 1) + "_start"], trips_converter["trip_" + str(i + 1) + "_end"] = int(trip_datas[2]), int(trip_datas[3])

			left_nodes.append("trip_" + str(i + 1) + "_start")
			right_nodes.append("trip_" + str(i + 1) + "_end")

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

	return trips, distances, int(number_of_trips), left_nodes, right_nodes


def get_distance(i, j):
	global matrixD
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
	edges = {"back_edge": [], "trip_edge": [], "start_edge": [], "end_edge": [], "garbage_edge": []}
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
				edges["back_edge"].append(["trip_" + str(i + 1) + "_end", "trip_" + str(j + 1) + "_start"])
	for i in range(len(trips)):
		# create nodes
		nodes.append("trip_" + str(i + 1) + "_start")
		nodes.append("trip_" + str(i + 1) + "_end")

		# create edges

		edges["start_edge"].append(["parking_start", "trip_" + str(i + 1) + "_start"])
		edges["end_edge"].append(["trip_" + str(i + 1) + "_end", "parking_end"])
	edges["garbage_edge"].append(["parking_start", "parking_end"])
	return edges, nodes


def get_trip_number(name: str):
	start_index = name.find('_')
	name = name[start_index + 1:]
	end_index = name.find('_')
	return int(name[:end_index]), name[end_index + 1:]


def get_state_number(name: str):
	return trips_converter[name]


def solve_phase2(edges, nodes, number_of_trips):
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


def main():
	global matrixD
	trips, distances, number_of_trips, left_nodes, right_nodes = file_processing()
	matrixD = distances
	edges, nodes = pre_processing(trips)
	start = time.time()
	G, flowCost, flowDict = solve_phase2(edges, nodes, number_of_trips)
	end = time.time()
	print('-------------------------')
	print('Execution Time: ', int(end - start), 's', "\t |")
	print('-------------------------')

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

	# Make complete graph
	# graph = nx.DiGraph()
	#
	# # edges = {"back_edge": [], "trip_edge": [], "start_edge": [], "end_edge": [], "garbage_edge": []}
	# for i in range(number_of_trips):
	# 	graph.add_edge('trip_' + str(i + 1) + '_start', 'trip_' + str(i + 1) + '_end')
	# 	graph.add_edge('parking_start', 'trip_' + str(i + 1) + '_start')
	# 	graph.add_edge('trip_' + str(i + 1) + '_end', 'parking_end')
	#
	# for edge in edges['back_edge']:
	# 	graph.add_edge(edge[0], edge[1])
	#
	# position = {}
	# position.update((node, (2, number_of_trips - index)) for index, node in enumerate(left_nodes))
	# position.update((node, (3, number_of_trips - index)) for index, node in enumerate(right_nodes))
	#
	# position.update({'parking_start': (1, number_of_trips / 2)})
	# position.update({'parking_end': (4, number_of_trips / 2)})
	#
	# nx.draw(G=graph, pos=position, with_labels=True)
	# plt.show()

if __name__ == "__main__":
	main()
