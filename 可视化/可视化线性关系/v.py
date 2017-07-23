#!coding: utf-8
from matplotlib import pyplot as plt 
import seaborn as sns
from pymongo import MongoClient
import numpy as np 
import pandas as pd 
import json
from collections import defaultdict

client = MongoClient()
db = client.paper_rank
collection = db.loss_value_function


percentages = [1, 5, 10, 15]
intervals = [15, 20, 25, 30]

formula_dict = defaultdict(dict)
for percentage in percentages:
	for interval in intervals:
		xs = []
		ys = []
		loss_value_func = db.loss_value_function.find_one({"interval": interval})
		num = int(loss_value_func["count"] * (percentage / (100 * loss_value_func["percentage"])))
		data = loss_value_func["loss_value_func"][:num]
		for d in data:
			for k, v in d["loss_value"].items():
				xs.append(int(k))
				ys.append(v)
		# {scatter,line}_kws : dictionaries
		# Additional keyword arguments to pass to plt.scatter and plt.plot.
		fig, ax = plt.subplots(figsize=(14, 7))
		sns.regplot(x=np.array(xs), y=np.array(ys), x_estimator=np.mean, order=2, color="g", truncate=True, ax=ax)
		ax.set_xlim([0, 31]);
		ax.set_ylim(0);
		ax.set_xticks(range(0, 32, 1));
		# ax.set_xticklabels(map(str, range(0, 32, 1)), fontsize="large", weight="bold")
		ax.get_xaxis().set_tick_params(labelsize="large")

		# Axis.set_tick_params(which='major', reset=False, **kw)
		# Set appearance parameters for ticks and ticklabels.
		ax.get_yaxis().set_tick_params(labelsize="large")

		ax.set_xlabel("interval", size="xx-large", weight="bold")
		ax.set_ylabel("loss_value", size="xx-large", weight="bold")
		# ax.set_title("Loss value function for papers (interval: {}; top:{}%)".format(interval, percentage))
		

		# 参数 Polynomial coefficients, highest power first
		z = np.polyfit(xs, ys, 2)
		# 多项式
		# p = np.poly1d(z)

		# xp = np.linspace(1, 31, 100)
		# ax.plot(xs, ys, 'o', alpha=0.5)
		def formula(z):
			ret = "$f(x) = {:.4f}x^2 ".format(z[0])
			if z[1] >= 0:
				ret += "+ {:.4f}x ".format(z[1])
			else:
				ret += "- {:.4f}x ".format(np.abs(z[1]))
			if z[2] >= 0:
				ret += "+ {:.4f}".format(z[2])
			else:
				ret += "- {:.4f}".format(np.abs(z[2]))
			return ret+"$"
		# ax.text(10, 1, formula(z), bbox=dict(facecolor='red', alpha=0.5))
		formula_dict[interval][percentage] = formula(z)[1:-1]
		fig.savefig("lv_func_{}_{}.png".format(interval, percentage), bbox_inches='tight')
		plt.close(fig)
		print percentage, interval
		# break
	# break

json.dump(formula_dict, open("formula_dict.json", "w"), indent=2)
