import pickle
import heapq
import os
import requests
import json

with open("node_long_lat.pickle","rb") as f:
	node_long_lat = pickle.load(f)
with open("adj_list.pickle","rb") as f:
	adj_list = pickle.load(f)
with open("distance_matrix.pickle","rb") as f:
	distance_matrix = pickle.load(f)

end_lat = 17.2406919
end_lon = 78.4329069
end_way = 29113368

start_way = 262821911
start_lat = 17.5473641
start_lon = 78.5724988

def heuristic_func(node):
	return distance_matrix[node][0]

def children(node):
	return adj_list[node]

def findTransittime(finalpath):
	Total_distance = 0.0
	Total_time = 0.0

	if "dis_time.pickle" not in os.listdir("./"):
		BingMapsKey = 'AnVaaMHMF9my49P6fCK6DLKLem8FjV7p-b97AuqNe0zjd57fKz-QDF_qoa0IOVrh'
		dis_time = {}

		for i in range(0,len(finalpath)-20,20):
			print(str(finalpath[i])+" "+str(finalpath[i+20]))
			url = 'https://dev.virtualearth.net/REST/v1/Routes/DistanceMatrix?origins='+str(node_long_lat[finalpath[i]])+'&destinations='+str(node_long_lat[finalpath[i+20]])+'&travelMode=driving&key='+BingMapsKey
			js1 = requests.get(url).json()
			dis_time[(finalpath[i],finalpath[i+20])] = (js1['resourceSets'][0]['resources'][0]['results'][0]['travelDistance'],js1['resourceSets'][0]['resources'][0]['results'][0]['travelDuration'])
			Total_distance += js1['resourceSets'][0]['resources'][0]['results'][0]['travelDistance']
			Total_time += js1['resourceSets'][0]['resources'][0]['results'][0]['travelDuration']

		url = 'https://dev.virtualearth.net/REST/v1/Routes/DistanceMatrix?origins='+str(node_long_lat[finalpath[540]])+'&destinations='+str(node_long_lat[finalpath[len(finalpath)-1]])+'&travelMode=driving&key='+BingMapsKey
		js1 = requests.get(url).json()
		dis_time[(finalpath[540],finalpath[len(finalpath)-1])] = (js1['resourceSets'][0]['resources'][0]['results'][0]['travelDistance'],js1['resourceSets'][0]['resources'][0]['results'][0]['travelDuration'])
		Total_distance += js1['resourceSets'][0]['resources'][0]['results'][0]['travelDistance']
		Total_time += js1['resourceSets'][0]['resources'][0]['results'][0]['travelDuration']

		with open("dis_time.pickle","wb") as f:
			pickle.dump(dis_time,f)

	else:
		with open("dis_time.pickle","rb") as f:
			dis_time = pickle.load(f)
		for i in range(0,len(finalpath)-20,20):
			Total_distance += dis_time[(finalpath[i],finalpath[i+20])][0]
			Total_time += dis_time[(finalpath[i],finalpath[i+20])][1]
		Total_distance += dis_time[(finalpath[540],finalpath[len(finalpath)-1])][0]
		Total_time += dis_time[(finalpath[540],finalpath[len(finalpath)-1])][1]

	print("The following are the coordinates of the path from bits to Airport in order")
	print("")
	ans = {}
	for x in finalpath:
		ans[x] = [float(node_long_lat[x].split(',')[0]), float(node_long_lat[x].split(',')[1])]

	print(ans)
	print("")

	print("Distance from Bits Hyderabad to Airport : ",Total_distance)
	print("Time taken from Bits Hyderabad to Airport by driving : ",Total_time)
	
	return

def AStarfunction(start_node_id,end_node_id = 69555):
	if "complete_distance_matrix.pickle" not in os.listdir("./"):
		print("File not there, so creating complete_distance_matrix")
		complete_distance_matrix = {}

	else:
		with open("complete_distance_matrix.pickle","rb") as f:
			complete_distance_matrix = pickle.load(f)

	oldGscore = {}
	parent = {}

	open_list_copy = []
	open_list = []

	closed_list = {}

	d = 0

	heapq.heappush(open_list,(heuristic_func(start_node_id),start_node_id))
	open_list_copy.append(start_node_id)

	oldGscore[start_node_id]=0
	path = []

	while len(open_list)>0:

		_,curr_loc = heapq.heappop(open_list)

		if curr_loc == end_node_id:
			
			node = end_node_id
			path = [end_node_id]

			while True:
				if(node == start_node_id):
					with open("complete_distance_matrix.pickle","wb") as f:
						pickle.dump(complete_distance_matrix,f)
					with open("path.pickle","wb") as f:
						pickle.dump(path,f)
					findTransittime(path)
					return
				node = parent[node]
				path.insert(0, node)

		else:

			children_list = children(curr_loc)
			children_unique_list = set(children_list)
			children_list = list(children_unique_list)

			for child in children_list:

				curr_pair = (0,0)
				if curr_loc > child:
					curr_pair = (curr_loc,child)
				else:
					curr_pair = (child,curr_loc)

				if curr_pair not in complete_distance_matrix:
					url = 'https://dev.virtualearth.net/REST/v1/Routes/DistanceMatrix?origins='+str(node_long_lat[curr_loc])+'&destinations='+str(node_long_lat[child])+'&travelMode=driving&key='+BingMapsKey
					js = requests.get(url).json()
					complete_distance_matrix[curr_pair] = js['resourceSets'][0]['resources'][0]['results'][0]['travelDistance']

				cost = oldGscore[curr_loc] + complete_distance_matrix[curr_pair]
				h = heuristic_func(child)
				f = cost+h

				if child in oldGscore:
					if cost < oldGscore[child]:
						oldGscore[child] = cost
						parent[child] = curr_loc				

				elif child in closed_list:
					if cost < closed_list[child]:
						oldGscore[child] = cost
						del closed_list[child]
						heapq.heappush(open_list, (f,child))
						parent[child] = curr_loc

				else:
					heapq.heappush(open_list, (f,child))
					oldGscore[child] = cost
					parent[child] = curr_loc
		closed_list[curr_loc] = oldGscore[curr_loc]


def main():
	start_node_id = 74037
	AStarfunction(start_node_id)

if __name__ == '__main__':
	main()