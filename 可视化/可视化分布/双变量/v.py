#!coding:utf-8
from matplotlib import pyplot as plt 
import seaborn as sns
from pymongo import MongoClient
import numpy as np 
from scipy import stats
from collections import defaultdict
import json

client = MongoClient()
db = client.paper_rank
collection_1 = db.papers
collection_2 = db.traditional
sns.set_style("white")

meta_dict = defaultdict(dict)
for interval in range(2, 31, 1):
	# with sns.axes_style("white"):
	if True:
		# fig, ax = plt.subplots(nrows=1, ncols=1)
		loss_value_field = "loss_value." + str(interval)
		traditional_count_field= "traditional_count." + str(interval)

		rets = list(collection_1.find({loss_value_field: {"$exists": 1}, "citations": {"$exists": 1}}, 
			{loss_value_field: 1, "_id": 1}))
		ids = np.array(map(lambda x: x["_id"], rets))
		loss_values = np.array(map(lambda x: x["loss_value"][str(interval)], rets))
		threshold = loss_values.mean() * 2
		threshold_mask = loss_values > threshold
		loss_values = loss_values[threshold_mask]
		ids = ids[threshold_mask]

		# remove outlier
		std = loss_values.std()
		mean = loss_values.mean()
		sigma_num = 4
		mask = (loss_values < (mean + sigma_num*std)) & (loss_values > (mean - sigma_num*std))
		loss_values = loss_values[mask]
		ids = ids[mask]
		loss_values_traditional = []
		for _id in ids:
			loss_values_traditional.append(collection_2.find_one({"_id": _id}, 
				{loss_value_field: 1, "_id": 0})["loss_value"][str(interval)])
		Pearson_corrcoef, two_tailed_p_value = stats.pearsonr(loss_values, loss_values_traditional)

		loss_values = np.log(loss_values + 1)
		loss_values_traditional = np.log(np.array(loss_values_traditional) + 1)
		
		# jointplot 会自己新建一个 figure
		grid = sns.jointplot(x=loss_values, y=loss_values_traditional, stat_func=None, size=12,
			kind="hex", color="r", space=0, joint_kws={"gridsize": 40}, xlim=(min(loss_values), max(loss_values)), 
			ylim=(min(loss_values_traditional), max(loss_values_traditional)));
		# grid.set_axis_labels(loss_value_field, traditional_count_field)
		grid.ax_joint.get_xaxis().set_tick_params(labelsize="large")
		grid.ax_joint.get_yaxis().set_tick_params(labelsize="large")
		grid.ax_joint.set_xlabel(loss_value_field, size="xx-large", weight="bold")
		grid.ax_joint.set_ylabel(traditional_count_field, size="xx-large", weight="bold")
		# print dir(grid)
		# 'annotate', 'ax_joint', 'ax_marg_x', 'ax_marg_y', 'fig', 'plot', 'plot_joint', 'plot_marginals', 'savefig', 'set_axis_labels', 'x', 'y'
		# grid.fig 就和 matplotlib 的 Figure 一样了
		# grid.fig.text(0.2, 0.8, "{} > (mean * 2)'s papers no log Pearson_corrcoef: {};two_tailed_p_value: {}"
		# 	.format(loss_value_field, Pearson_corrcoef, two_tailed_p_value))
		# grid.fig.suptitle("{} $> {}$ (mean * 2)'s papers log({}) vs log({}) bivariate distributation".format(loss_value_field, 
		# 	threshold, loss_value_field, traditional_count_field))
		grid.savefig("bivariate_{}.png".format(interval))
		plt.close(grid.fig)
		# plt.show()
		meta_dict[interval]["corrcoef"] = "{:.4f}".format(Pearson_corrcoef)
		meta_dict[interval]["two_tailed_p_value"] = "{:.4e}".format(two_tailed_p_value)
		meta_dict[interval]["threshold"] = "{:.4f}".format(threshold)
	# break
json.dump(meta_dict, open("bivariate.json", "w"), indent=2)
