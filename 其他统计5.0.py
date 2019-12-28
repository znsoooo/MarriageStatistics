import os
import csv
import time
import pandas
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import mpl_toolkits.axisartist as axis

from matplotlib.ticker import FuncFormatter
FormatPercent = FuncFormatter(lambda temp, position: '%.1f%%'%(temp*100))

def DrawGeneral(title='', show=True, savefile=None):
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False
    plt.tight_layout()
    plt.subplots_adjust(top=0.94)
    plt.title(title)
    if savefile:
        plt.savefig('result/'+savefile+'.png')
    if show:
        plt.show()
    plt.clf()


# nums, areas = Analyse1(data, 'area')

nums = [69287, 43625, 19130, 3243, 6024, 2118, 3933, 16906, 15588, 133574, 183478, 15551, 99804, 22409, 4516, 17692]
areas1 = ['东城区', '丰台区', '大兴区', '密云区', '平谷区', '延庆区', '怀柔区', '房山区', '昌平区', '朝阳区', '海淀区', '石景山区', '西城区', '通州区', '门头沟区', '顺义区']

areas2      = ['东城区', '西城区', '朝阳区', '丰台区', '石景山区', '海淀区', '门头沟区', '房山区', '通州区', '顺义区', '昌平区', '大兴区', '怀柔区', '平谷区', '密云区', '延庆区']
population  = [85.10, 122.00, 373.90, 218.60, 61.20, 348.00, 32.20, 115.40, 150.80, 112.80, 206.30, 176.10, 40.50, 44.80, 49.00, 34.00 ]
mianji      = [4182.04, 5033.13, 45118.62, 30359.44, 8422.40, 42648.77, 140571.01, 190006.93, 88531.76, 98927.58, 132408.53, 101109.94, 210360.57, 93204.32, 218801.48, 196604.16]
gdp         = [2247.18, 3920.72, 5635.48, 1427.54, 535.39, 5942.79, 174.40, 681.68, 758.01, 1715.87, 839.67, 644.56, 285.80, 233.55, 278.24, 136.17]

print('area_same:', sorted(areas1)==sorted(areas2))

data_sorted1 = sorted(list(zip(areas1, nums)))
data_sorted2 = sorted(list(zip(areas2, population, gdp, mianji)))

areas       = [one[0] for one in data_sorted1]
population  = [one[1]*1e4 for one in data_sorted2]
nums_av     = [one[0][1]/one[1] for one in zip(data_sorted1, population)]
gdp_av      = [one[0][2]*1e4/one[1] for one in zip(data_sorted2, population)]
mianji_av   = [one[1]/one[0][3] for one in zip(data_sorted2, population)]

print(np.corrcoef(nums_av, gdp_av))


x1, y1, t1 = gdp_av, nums_av, areas

f1 = np.polyfit(x1+[0]*200, y1+[0]*200, 1)
p1 = np.poly1d(f1)
yvals1 = p1([0, 40])
plt.plot([0, 40], yvals1, c='silver', linestyle='--', label='%.6fx'%p1[1], zorder=1)

plt.scatter(x1, y1, marker='D', c='darkred', zorder=2)

for x, y, tag in zip(x1, y1, t1):
    plt.annotate(tag, (x+1, y+0.003), 
                 bbox=dict(boxstyle='square', fc='white', alpha=0.4),
                 )

plt.xlim(0, 40)
plt.ylim(0)
plt.grid(zorder=1)
plt.gca().yaxis.set_major_formatter(FuncFormatter(FormatPercent))
plt.xlabel('人均GDP(万元)')
plt.ylabel('预约结婚率(预约人数/常住人口)')
plt.legend()
title = '北京各区县预约结婚率与人均GDP拟合曲线'
DrawGeneral(title, 1, 'sp2-'+title)



