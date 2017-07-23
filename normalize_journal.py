#!coding: utf-8
from pymongo import MongoClient
import os
import pandas as pd 
from functools import reduce

client = MongoClient()
db = client.paper_rank
collection = db.papers

variants_dir = "F:\Paper_Rank\Paper_Rank\cleaner\clean\changed"
files = os.listdir(variants_dir)
files = [os.path.join(variants_dir, f) for f in files]

list_of_dicts = []
for f in files:
	df = pd.read_excel(f, sheetname=0, index_col=None)
	ret = df.to_dict(orient="list")
	ret = dict(zip(ret["variant"], ret["source"]))
	list_of_dicts.append(ret)

def concate(x, y):
	x.update(y)
	return x
# final_dict = reduce(lambda x,y: x.update(y), list_of_dicts, {})
final_dict = reduce(concate, list_of_dicts, {})

cursor = collection.find({"journal": {"$exists": 1}})
cnt = 0
for p in cursor:
	# p["journal"] 大小写混杂
	# final_dict key 小写;value 大写
	normalized_journal = final_dict.get(p["journal"].lower(), "NULL")
	collection.update_one({"_id": p["_id"]}, {"$set": {"normalized_journal": normalized_journal}})
	if cnt%1000 ==0:
		print cnt
	cnt += 1
