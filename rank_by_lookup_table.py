from pymongo import MongoClient

client = MongoClient()
db = client.paper_rank

# collection_from = db.papers
# collection_to = db.loss_value_rank_table

collection_from = db.traditional
collection_to = db.traditional_rank_table

for k in range(1, 31, 1):
	loss_value_field = "loss_value." + str(k)
	# loss_value_list = collection_from.distinct(loss_value_field, {"citations": {"$exists": 1}})
	loss_value_list = collection_from.distinct(loss_value_field)
	loss_value_list.sort(reverse=True)
	rets = [{"loss_value": lv, "rank": i, "interval": k} for i, lv in enumerate(loss_value_list)]
	collection_to.insert_many(rets)
	print k
