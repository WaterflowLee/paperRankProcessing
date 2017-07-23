from pymongo import MongoClient
import json
client = MongoClient()
db = client.paper_rank
collection = db.papers

intervals = range(1, 31, 1)
journals = collection.distinct("normalized_journal")



contributions = []
for interval in intervals:
	contribution = {}
	# contribution["interval"] = interval
	for journal in journals:
		loss_value_field = "loss_value." + str(interval)
		pipeline = [
			{"$match": {"normalized_journal": journal, loss_value_field: {"$exists": 1}}},
			{"$group":{
				"_id": "nihaoya",
				"total_loss_value":{
					"$sum": "$" + loss_value_field
				}
			}}
		]
		ret = list(collection.aggregate(pipeline))
		try:
			contribution[journal] = ret[0]["total_loss_value"]
		except Exception as e:
			print e
			contribution[journal] = 0
	contributions.append(contribution)
json.dump(contributions, open("contributions.json", "w"), indent=2)
