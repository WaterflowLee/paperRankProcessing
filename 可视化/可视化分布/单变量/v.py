from matplotlib import pyplot as plt 
import seaborn as sns
from pymongo import MongoClient
import numpy as np 
client = MongoClient()
db = client.paper_rank
collection = db.papers
# collection = db.traditional

# interval = 3
for interval in range(2, 31, 1):
	fig, ax = plt.subplots(nrows=1, ncols=1)
	loss_value_field = "loss_value." + str(interval)

	loss_values = list(collection.find({loss_value_field: {"$exists": 1}, "citations": {"$exists": 1}}, {loss_value_field: 1, "_id": 0}))
	loss_values = np.array(map(lambda x: x["loss_value"][str(interval)], loss_values))
	threshold = loss_values.mean()
	loss_values = loss_values[loss_values > threshold]

	# remove outlier
	std = loss_values.std()
	mean = loss_values.mean()
	sigma_num = 4
	mask = (loss_values < (mean + sigma_num*std)) & (loss_values > (mean - sigma_num*std))
	loss_values = loss_values[mask]

	sns.distplot(loss_values)
	xmax = (int(loss_values.max() / 5) + 1) * 5
	xmin = int(threshold)
	# plt.xlim(xmin, xmax)
	ax.set_xlim(xmin, xmax)
	# plt.xticks(np.linspace(xmin, xmax, 10).astype(int))
	ax.set_xticks(np.linspace(xmin, xmax, 10).astype(int))
	# plt.title(loss_value_field + " $>" + str(threshold) + "$ 's papers " + loss_value_field + " distributation")
	ax.set_title(loss_value_field + " $>" + str(threshold) + "$ 's papers " + loss_value_field + " distributation")
	# plt.show()
	fig.savefig("paper_rank_" + str(interval) + "_.png", bbox_inches='tight')
	plt.close(fig)


# I work around this by forcing the closing of the figure window in my giant loop, 
# so I don't have a million open figures during the loop:

# import matplotlib.pyplot as plt
# fig, ax = plt.subplots( nrows=1, ncols=1 )  # create figure & 1 axis
# ax.plot([0,1,2], [10,20,3])
# fig.savefig('path/to/save/image/to.png')   # save the figure to file
# plt.close(fig)    # close the figure