import json
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
sns.set(style="darkgrid", color_codes=True)

interval = 30
percentage = 20
papers = json.load(open("estimate_loss_function.%s.%s.json" % (interval, percentage), "r"))
papers_ = papers[:1000]
x = range(1, 31, 1)
xs = []
ys = []
for paper in papers_:
	loss_value = paper["loss_value"]
	y = sorted(map(float, loss_value.values()))
	xs.append(x)
	ys.append(y)

xs = np.array(xs)
ys = np.array(ys)
xs_avg = xs.mean(axis=0)
ys_avg = ys.mean(axis=0)
# g = sns.jointplot(xs, ys, kind="reg", size=7)

x_input = xs
y_input = np.log(ys)
g = sns.JointGrid(x=x_input, y=y_input, xlim=(0, 31), ylim=(0, np.max(y_input.flatten())+10))
g = g.plot_joint(sns.regplot, color="r")
cof = np.polyfit(xs_avg, np.log2(ys_avg), 2)
p = np.poly1d(cof)
plt.plot(xs_avg, p(xs_avg), lw="2")
txt = "a:%s \nb:%s \nc:%s\n" % (cof[0], cof[1], cof[2])
plt.text(5, np.max(y_input.flatten()) - 60, txt)
g = g.plot_marginals(sns.distplot, kde=True, color="g")
plt.show()
