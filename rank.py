from pymongo import MongoClient
import time
client = MongoClient()
db = client.paper_rank
collection_from = db.papers
collection_to = db.rank
cnt = 0
rets = []
tic = time.time()
for p in collection_from.find():
	p_rank = {}
	for k in p["loss_value"].keys():
		lv = p["loss_value"][k]
		rank = collection_from.find({"loss_value." + k: {"$gt": lv}}).count() + 1
		# print len(list(collection_from.find({"loss_value." + k: {"$gt": lv}}, {"loss_value." + k: 1, "_id":0})))
		# collection_from.find({"loss_value." + k: {"$gt": lv}})
		# collection_from.aggregate([
		# 	{"$match": {"loss_value." + k: {"$gt": lv}}},
		# 	{"$group": { "_id": "null", "count": {"$sum": 1}}}
		# ])
		p_rank[k] = rank
	# collection_from.update_one({"_id": p["_id"]}, {"$set": {"rank": p_rank}})
	rets.append({"_id": p["_id"], "rank": p_rank})
	if cnt%2 == 0:
		collection_to.insert_many(rets)
		rets = []
		print cnt
		print time.time() - tic
	cnt += 1
	if cnt == 6:
		break
