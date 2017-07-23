from pymongo import MongoClient
import numpy as np 
client = MongoClient()
db = client.paper_rank
collection = db.papers
from collections import defaultdict
import json
# Returns a new dictionary-like object. defaultdict is a subclass of the built-in dict class. 
# It overrides one method and adds one writable instance variable. 
# The remaining functionality is the same as for the dict class and is not documented here.
rets = []
for interval in range(1, 31, 1):
	lv_per_year = defaultdict(float)
	loss_value_field = "loss_value." + str(interval)
	for p in collection.find({loss_value_field: {"$exists": 1}}):
		lv_per_year[p["time"]] += p["loss_value"][str(interval)]

	total = sum(lv_per_year.values())
	years = []
	loss_values = []
	for year, lv in lv_per_year.items():
		years.append(int(year))
		loss_values.append(lv / total)
	indices = np.argsort(years)
	loss_values = np.array(loss_values)[indices]
	rets.append(list(loss_values))
	print interval
json.dump(rets, open("pie.json", "w"))