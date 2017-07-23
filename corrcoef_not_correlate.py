#!coding:utf-8
# correlate coefficient == corr coef
# correlate
# 相关和相关系数意义物理都不一样
import numpy as np
x = np.array([[1, 2, 3], [0, 1, 0.5]])
print "和卷积很类似"
print "滑动点积: 1*0 + 2*1 + 3*0.5"
print np.correlate(x[0], x[1])
print "滑动点积: 1*1 + 0.5*2; 1*0 + 2*1 + 3*0.5; 0*2 + 1*3"
print np.correlate(x[0], x[1], "same")

covariance = np.cov(x)
# 变量1 的取值 x[0]
# 变量2 的取值 x[1]
# Covariance indicates the level to which two variables vary together.
# 即变量1 取1时，变量2 取0
# 即变量1 取2时，变量2 取1
# 即变量1 取3时，变量2 取0.5
print x[0].var() * 1.5
print x[1].var() * 1.5
# 根据公式 E[(X - E(X))(Y - E(y))]
print ((x[0] - x[0].mean()) * (x[1] - x[1].mean())).mean() * 1.5

print "方差 协方差 \n协方差 方差"
print covariance

print "R(i,j) = C(i,j) / np.sqrt(C(i,i)* C(j,j))"
print "自相关系数 相关系数 \n相关系数 自相关系数"
print np.corrcoef(x)