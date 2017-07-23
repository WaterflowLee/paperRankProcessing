#!coding:utf-8
from pymongo import MongoClient
import pymongo

client = MongoClient()
db = client.paper_rank
collection_from = db.papers
collection_to = db.loss_value_function

# db.papers.find({"loss_value.30":{"$exists":1}}).count()
paper_num = {"15": 136325, "20": 123635, "25": 110502, "30": 97481}
# 为了让拟合出的曲线不因为数据缺失而失真, 应该应用"30"对应的数据
for interval in [15, 20, 25, 30]:
	percentage = 0.20
	cursor = collection_from.find({"loss_value.30": {"$exists": 1}}, {"_id": 1, "loss_value": 1})\
		.sort("loss_value." + str(interval), pymongo.DESCENDING)\
		.limit(int(paper_num["30"] * percentage))
	collection_to.insert_one({
		"interval": interval,
		"percentage": percentage,
		"count": int(paper_num["30"] * percentage),
		"loss_value_func": list(cursor)
		})