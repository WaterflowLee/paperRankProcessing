from pymongo import MongoClient
import pymongo
client = MongoClient()
db = client.paper_rank
# collection_from = db.papers
collection_from = db.traditional

for k in range(1, 31,1):
	rank = 0
	for p in collection_from.find({"loss_value." + str(k): {"$exists": 1}}).sort("loss_value." + str(k), pymongo.DESCENDING):
		rank += 1
		collection_from.update_one({"_id": p["_id"]}, {
			"$set": {
			"rank." + str(k): rank
			}
		})
	print k

for k in range(1, 31,1):
	for p in collection_from.find({"loss_value." + str(k): {"$exists": 1}}).sort("loss_value." + str(k), pymongo.DESCENDING):
		p_id = p["_id"]
		lv = p["loss_value"][str(k)]
		loss_value_field = "loss_value." + str(k)
		rank_field = "rank." + str(k)
		rank_1 = collection_from.find_one({loss_value_field: lv}, {"_id": 0, rank_field: 1})["rank"][str(k)]
		rank_2 = collection_from.find_one({"_id": p_id}, {"_id": 0, rank_field: 1})["rank"][str(k)]
		if rank_1 < rank_2:
			collection_from.update_one({"_id": p_id}, {"$set": {rank_field: rank_1}})
	print k
