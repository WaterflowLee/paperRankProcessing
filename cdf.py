from pymongo import MongoClient
import numpy as np
client = MongoClient()
db = client.paper_rank
collection_from = db.papers
collection_to = db.cdf
rets = []
for interval in range(1, 31,1):
	lv_field = "loss_value." + str(interval)
	universal_set = collection_from.find({lv_field: {"$exists": 1}}, {"_id": 0, lv_field: 1})
	# universal_set = list(universal_set)
	universal_set = map(lambda p: p["loss_value"][str(interval)], universal_set)
	total = len(universal_set)
	fractiles = set(np.random.choice(universal_set, 100))
	fractiles.add(min(universal_set))
	fractiles.add(max(universal_set))
	ret = {}
	for fractile in fractiles:
		ret[str(fractile).replace(".", "_")] = collection_from.find({lv_field: {"$lt": fractile}}).count()/float(total)
	rets.append({"_id": str(interval),
				"cdf": ret})
collection_to.insert_many(rets)