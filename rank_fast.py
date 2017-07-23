from pymongo import MongoClient
import pymongo
client = MongoClient()
db = client.paper_rank
collection_from = db.papers
collection_to = db.ranks

for k in range(1, 31,1):
	rets = []
	rank = 0
	for p in collection_from.find({"loss_value." + str(k): {"$exists": 1}}).sort("loss_value." + str(k), pymongo.DESCENDING):
		rank += 1
		doc = {
		"id": p["_id"],
		"rank": rank,
		"loss_value": p["loss_value"][str(k)]
		}
		rets.append(doc)
	print k
	collection_to.insert_one({"_id": str(k), "content": rets})
