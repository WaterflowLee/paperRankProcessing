from pymongo import MongoClient

client = MongoClient()
db = client.paper_rank

# collection_1 = db.papers
# collection_2 = db.loss_value_rank_table

collection_1 = db.traditional
collection_2 = db.traditional_rank_table
cnt = 0
for p in collection_1.find():
# for p in collection_1.find({"citations": {"$exists": 1}}):
	rank = {}
	for k in p["loss_value"].keys():
		loss_value = p["loss_value"][k]
		rank[k] = collection_2.find_one({"interval": int(k), "loss_value": loss_value})["rank"]
	collection_1.update({"_id": p["_id"]}, {"$set": {"rank": rank}})
	if cnt % 1000 == 0:
		print cnt
	cnt += 1
