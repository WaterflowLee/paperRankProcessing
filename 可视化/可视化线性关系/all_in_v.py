from matplotlib import pyplot as plt 
import seaborn as sns
from pymongo import MongoClient
import numpy as np 
import pandas as pd 

client = MongoClient()
db = client.paper_rank
collection = db.loss_value_function

xs = []
ys = []
percentages = []
intervals = []
for interval in [15, 20, 25, 30]:
	loss_value_func = db.loss_value_function.find_one({"interval": interval})
	for percentage in [1, 5, 10, 15]:
		num = int(loss_value_func["count"] * (percentage / (100 * loss_value_func["percentage"])))
		data = loss_value_func["loss_value_func"][:num]
		for d in data:
			for k, v in d["loss_value"].items():
				xs.append(int(k))
				ys.append(v)
				percentages.append(percentage)
				intervals.append(interval)

df = pd.DataFrame(data={
	"interval": xs,
	"loss_value": ys,
	"percentages": percentages,
	"intervals": intervals
	})
df.to_csv("t.csv", index=False)
sns.lmplot(x="interval", y="loss_value", row="intervals", col="percentages", data=df, x_estimator=np.mean, order=2, size=3)
plt.show()