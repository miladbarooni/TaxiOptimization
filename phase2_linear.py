from pulp import *
import time


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
        # nodes.append("parking_start")
        # nodes.append("parking_end")
        # create edges
        # edges["trip_edge"].append(["trip_"+str(i+1)+"_start", "trip_"+str(i+1)+"_end"])
        edges["trip_edge"].append(["trip_"+str(i+1)+"_start", "trip_"+str(i+1)+"_end"])
        edges["start_edge"].append(["parking_start", "trip_"+str(i+1)+"_start"])
        edges["end_edge"].append(["trip_"+str(i+1)+"_end", "parking_end"])
    edges["garbage_edge"].append(["parking_start", "parking_end"])
    return edges, nodes


def get_trip_number(name: str):
    start_index = name.find('_'),
    name = name[start_index+1:]
    end_index = name.find('_')
    return int(name[:end_index]), name[end_index+1:]


def get_state_number(name: str):
    return trips_converter[name]


def solve_lp_model(nodes, edges, number_of_trips):
    # Making all Nodes and adding the source and destination to other nodes
    nodeData = dict()
    # [supply, demand]
    for node in nodes:
        nodeData[node] = [0, 0]
    nodeData['parking_start'] = [number_of_trips, 0]
    nodeData['parking_end'] = [0, number_of_trips]
    nodes.append('parking_start')
    nodes.append('parking_end')

    # Building the arc and arcData that contains cost and more info.
    arcs = list()
    arcData = dict()
    # [cost, minFlow, maxFlow]
    for edge in edges['back_edge']:
        arcs.append((edge[0], edge[1]))
        arcData[(edge[0], edge[1])] = [get_distance(get_state_number(edge[0]), get_state_number(edge[1])), 0, 1]
    for edge in edges['start_edge']:
        arcs.append((edge[0], edge[1]))
        arcData[(edge[0], edge[1])] = [get_distance(1, get_state_number(edge[1])), 0, 1]
    for edge in edges['end_edge']:
        arcs.append((edge[0], edge[1]))
        arcData[(edge[0], edge[1])] = [get_distance(get_state_number(edge[0]), 1), 0, 1]
    for edge in edges['trip_edge']:
        arcs.append((edge[0], edge[1]))
        arcData[(edge[0], edge[1])] = [0, 1, 1]
    for edge in edges['garbage_edge']:
        arcs.append((edge[0], edge[1]))
        arcData[(edge[0], edge[1])] = [0, 0, number_of_trips]
    # print (arcs)
    # print (arcData)

    # Splits the dictionaries to be more understandable
    (supply, demand) = splitDict(nodeData)
    (costs, mins, maxs) = splitDict(arcData)
    vars = LpVariable.dicts("X",arcs,None,None,LpInteger)

    # # Creates the upper and lower bounds on the variables
    for arc in arcs:
        vars[arc].bounds(mins[arc], maxs[arc])

    # Creates the 'prob' variable to contain the problem data    
    prob = LpProblem("Minimum Cost Flow Linear Problem Phase1",LpMinimize)

    # Creates the objective function
    prob += lpSum([vars[a]* costs[a] for a in arcs]), "The Objective Function"

    # Creates all problem constraints - this ensures the amount going into each node is 
    # at least equal to the amount leaving
    for n in nodes:
        prob += (supply[n]+ lpSum([vars[(i,j)] for (i,j) in arcs if j == n]) >=
                 demand[n]+ lpSum([vars[(i,j)] for (i,j) in arcs if i == n])), \
                f"Flow balance in Node {n}"

    # The problem data is written to an .lp file
    prob.writeLP("simple_MCFP.lp")

    # The problem is solved using PuLP's choice of Solver
    prob.solve()
    # The optimised objective function value is printed to the screen    
    print ("Total Cost of MCFP = ", value(prob.objective))


if __name__ == "__main__":
    trips, distances, number_of_trips = file_processing()
    matrixD = distances
    edges, nodes = pre_processing(trips)
    start = time.time()
    solve_lp_model(nodes, edges, number_of_trips)
    end = time.time()
    print('-------------------------')
    print('Execution Time: ', end - start, 's', "\t |")
    print('-------------------------')