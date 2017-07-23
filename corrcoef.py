import numpy as np
import pandas as pd
import seaborn as sns
from pymongo import MongoClient
from matplotlib import pyplot as plt

client = MongoClient()
db = client.paper_rank
collection_1 = db.papers
collection_2 = db.traditional
k = 10
rank_field = "rank." + str(k)
x1 = []
x2 = []
cnt = 0
for p in collection_2.find({rank_field: {"$exists": 1}}):
	x1.append(p["rank"][str(k)])
	x2.append(collection_1.find_one({"_id": p["_id"]})["rank"][str(k)])
	if cnt == 1000:
		break
		# pass
	cnt += 1
sns.set(style="white")

x1 = pd.Series(x1, name="$X_1$")
x2 = pd.Series(x2, name="$X_2$")
x2 = ((x2 / x2.max())* x1.max()).apply(int) + 1
index = np.random.choice(range(len(x1)), 2000)
# Show the joint distribution using kernel density estimation
# g = sns.jointplot(x1[index], x2[index], kind="kde", size=7, space=0)
# plt.scatter(x1, x2)
# plt.show()
print np.corrcoef([x1, x2])
print pd.DataFrame([x1[:10],x2[:10]]).T
