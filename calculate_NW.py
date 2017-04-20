from pymongo import MongoClient
import pymongo
import numpy as np
import json
client = MongoClient()
conn = client.paper_rank
collection = conn.papers_top

# start = 0
# interval = 0 
# end = 0
# assert start + interval == end
# def papers_in_interval(start,end):
# 	return [doc for doc in collection.find({"time":{"$gte":start,"$lt":end}},{"_id":1})]
def calculate_weights(_id, hop=3):
	reference = collection.find_one({"_id":_id},{"_id":0, "reference":1})["reference"]
	pyramid = []
	pyramid.append(reference)
	for i in range(hop-1):
		layer = []
		for ref_id in pyramid[i]:
			ret = collection.find_one({"_id":ref_id},{"_id":0, "reference":1})
			if ret is not None:
				layer += ret["reference"]
		pyramid.append(layer)
	weights = {}
	for ref in pyramid[0]:
		weights[ref] = []
		for i in range(hop):
			weights[ref].append(pyramid[i].count(ref))
	return weights
def normalize_weights(weights, discount=0.5, hop=3):
	for key in weights.keys():
		ret = collection.find_one({"_id":key},{"_id":0, "eigen":1})
		if ret is not None:
			eigen = ret["eigen"]
		else:
			eigen = 1
		weights[key] = (np.array(weights[key]) * np.array([discount**i for i in range(hop)]) * eigen).sum()
	all_sum = np.sum(weights.values())
	normalized_weights = {}
	try:
		for key in weights.keys():
			normalized_weights[key.decode("utf-8")] = weights[key]/float(all_sum)
	except:
		for key in weights.keys():
			normalized_weights[key.decode("utf-8")] = weights[key]
	finally:
		return normalized_weights
c = 0;
docs = []
for paper in collection.find({},{"_id":1}):
	if c%1000==0:
		print c
	c += 1
	NW = normalize_weights(calculate_weights(paper["_id"]))
	docs.append({"_id":paper["_id"], "reference_normalized_weights":NW})
with open("NW.json", "w") as f:
	f.write(json.dumps(docs))
	# collection.update_one({"_id":paper["_id"]}, {"$set":{"reference_normalized_weights":NW}});
	# pymongo.errors.WriteError: The dotted field 'WOS:000203912500001.82' 
	# in 'reference_normalized_weights.WOS:000203912500001.82' is not valid for storage.
# def calculate_loss_values(start, end):
# 	need_to_cal = [dict((doc["_id"],doc["eigen"])) for doc in collection.find({"time":{"$gte":start,"$lt":end}, "citations":{"$exists":1}},{"_id":1, "eigen":1})]
# 	just_init = [doc for doc in collection.find({"time":{"$gte":start,"$lt":end}, "citations":{"$exists":0}},{"_id":1,"eigen":1})]
# 	print need_to_cal
# calculate_loss_values(1900, 1930)
# 
# dict(doc.values())