from pymongo import MongoClient
import numpy as np 
import json 
client = MongoClient()
db = client.paper_rank
collection = db.papers
# collection = db.traditional

for interval in range(29, 30, 1):
	loss_value_field = "loss_value." + str(interval)
	loss_values = list(collection.find({loss_value_field: {"$exists": 1}, "citations": {"$exists": 1}}, {loss_value_field: 1, "_id": 0}))
	loss_values = np.array(map(lambda x: x["loss_value"][str(interval)], loss_values))
	hist, bin_edges = np.histogram(loss_values, bins=50, normed=True)
	ret = {
	"hist": list(hist),
	"bin_edges": list(bin_edges)
	}
	json.dump(ret, open("hist_{}.json".format(interval), "w"))
