from pymongo import MongoClient
from collections import Counter
client = MongoClient()
db = client.paper_rank
collection_from = db.papers
sub_collection_from = db.papers.find({"citations": {"$exists":1}})
collection_to = db.traditional
cnt = 0
c_list = []

for p in sub_collection_from:
	# p_id = p["_id"].replace(".", "_")
	p_id = p["_id"]
	p_time = p["time"]
	citation_interval = []
	for c_id in p["citations"]:
		c = collection_from.find_one({"_id": c_id})
		c_time = c["time"]
		citation_interval.append(c_time - p_time + 1)
	citation_interval_cnt = Counter(citation_interval)
	citation_interval_dict = {}
	for k in dict(citation_interval_cnt).keys():
		citation_interval_dict[str(k)] = citation_interval_cnt[k]
	c_list.append({"_id": p_id, "traditional": citation_interval_dict})
	if cnt%1000 == 0:
		# collection_to.insert_many(c_list)
		c_list = []
		print cnt
	cnt += 1
collection_to.insert_many(c_list)


collection = db.papers
collection_from = db.traditional
cnt = 0
for p in collection_from.find({"rank": {"$exists": 0}}):
	cumulative = 0
	loss_value = {}

	keys = collection.find_one({"_id": p["_id"]})["loss_value"].keys()
	keys = map(int, keys)
	keys.sort()
	for k in keys:
		cumulative += p["traditional"].get(str(k), 0)
		loss_value[str(k)] = cumulative
	collection_from.update({"_id": p["_id"]}, {"$set": {"loss_value": loss_value}})
	if cnt%1000 ==0:
		print cnt 
	cnt += 1
