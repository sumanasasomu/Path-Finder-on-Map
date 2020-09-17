import requests
import json
import os
import pickle

with open("node_long_lat.pickle","rb") as f:
	node_long_lat=pickle.load(f)

BingMapsKey = 'AnVaaMHMF9my49P6fCK6DLKLem8FjV7p-b97AuqNe0zjd57fKz-QDF_qoa0IOVrh'
url = 'https://dev.virtualearth.net/REST/v1/Routes/DistanceMatrix'

end_lat = '17.2406919'
end_lon = '78.4329069'
end_way = 29113368
end_node_id = 69555

start_way = 262821911
start_lat = 17.5473641
start_lon = 78.5724988
start_node_id = 74037


l = len(node_long_lat)
distance_matrix = {} # node_id -> [traveldistance,traveltime]
if "distance_matrix.pickle" not in os.listdir("./"):
	parameters = {}
	parameters["destinations"] = end_lat+","+end_lon
	parameters["travelMode"] = "driving"
	parameters["key"] = BingMapsKey

	factor = 25
	for i in range(3018):
		print("Round",i)
		origin_str = ""
		for j in range(25):
			pos = i*25 + j + 1
			if j == 0:
				origin_str += node_long_lat[pos]
			else:
				origin_str += ';' + node_long_lat[pos]
		parameters["origins"] = origin_str
		r = requests.get(url,params=parameters)
		js = r.json()

		for k in range(25):
			pos_ = i*25 + k + 1
			distance_matrix[pos_] = [ js['resourceSets'][0]['resources'][0]['results'][k]['travelDistance'], js['resourceSets'][0]['resources'][0]['results'][k]['travelDuration'] ]

	print("Round3018")
	origin_str = ""
	for a in range(12):
		posi = 75451 + a
		if a==0:
			origin_str += node_long_lat[posi]
		else:
			origin_str += ';' + node_long_lat[posi]
	parameters["origins"] = origin_str
	r = requests.get(url,params=parameters)
	js = r.json()

	for b in range(12):
		posi_ = 75451 + b
		distance_matrix[posi_] = [ js['resourceSets'][0]['resources'][0]['results'][b]['travelDistance'], js['resourceSets'][0]['resources'][0]['results'][b]['travelDuration'] ]


	with open("distance_matrix.pickle","wb") as f:
	    pickle.dump(distance_matrix,f)

else:
	print("pickle file already exists")

# with open("distance_matrix.txt", "a") as myfile:
# 	for k in range(len(distance_matrix)):
# 		myfile.write(str(k+1) + str(distance_matrix[k+1]) + "\n")
