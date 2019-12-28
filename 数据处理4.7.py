import os
import csv
import time
import pandas
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import mpl_toolkits.axisartist as axis

alias = {'date': '年月日',
         'year': '年',
         'mon' : '月',
         'mday': '日',
         'wday': '星期',
         'yday': '月日',
         'odd' : '单双日',
         'area': '地区',
         'hday': '节假日',
         }

qixi = ['2011-08-06',
        '2011-08-23',
        '2012-08-23',
        '2013-08-13',
        '2014-08-02',
        '2015-08-20',
        '2016-08-09',
        '2017-08-28',
        '2018-08-17',
        '2019-08-07',
        ]

os.makedirs('result', exist_ok=1)

#----------------------------------------------------------------------------
# 通用统计
#----------------------------------------------------------------------------

from matplotlib.ticker import FuncFormatter
FormatPercent = FuncFormatter(lambda temp, position: '%.1f%%'%(100 * temp))


def Percent(a, b, ndigits=2):
    return ('%d / %d = %.' + str(ndigits) + 'f%%')%(a, b, 100*a/b)


def Preprocess(file, weekday_file):
    with open(weekday_file) as f:
        reader = csv.reader(f)
        weekday_data = {}
        for date, holiday, weekday in reader:
            date = time.strftime('%Y-%m-%d', time.strptime(date, '%Y/%m/%d'))
            weekday_data[date] = int(holiday) # 0: 正常 1: 调休 2: 调班

    with open(file) as f:
        reader = csv.reader(f)
        data = []
        for area, date, num in reader:
            if num:
                res = SplitDate(date)
                res['area'] = area
                res['cnt']  = int(num)
                res['hday'] = ['工作日', '调休', '调班'][weekday_data.get(date, 0)]
                data.append(res)

    print('Finsh Preprocess: %s'%len(data))
    return data, weekday_data


def SplitDate(date):
    res = {}
    day = time.strptime(date, '%Y-%m-%d')
    res['date'] = date
    res['year'] = day[0]
    res['mon']  = day[1]
    res['mday'] = day[2]
    # res['wday'] = day[6] + 1
    res['wday'] = '星期%d'%(day[6] + 1)
    res['yday'] = time.strftime('%m-%d', day)
    # res['odd']  = day[2] % 2
    res['odd']  = ['双数', '单数'][day[2] % 2]
    return res


def SortAndCut(data, tag, top):
    '''top: 0(no sort) -1(sort all)'''
    result, tags = Analyse1(data, tag)
    if top:
        tags_sorted = sorted(zip(tags, result), key=lambda item: item[1], reverse=True)
        if top + 1:
            tags_sorted = tags_sorted[:top]
        tags   = [tag for tag, num in tags_sorted]
        result = [num for tag, num in tags_sorted]
    return result, tags


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


def DrawPlot(data, title='', collects=None, samples=None, show=True, savefile=None):
    for res, sample_name in zip(data, samples):
        plt.plot(res, label=sample_name)

    if len(collects) <= 12 or len(collects) == 31:
        rotation = 0
    elif len(collects) == 16:
        rotation = 45
    else:
        rotation = 90
    plt.xticks(np.arange(len(collects)), collects, rotation=rotation)

    if max(data[0]) < 1:
##        plt.gca().yaxis.set_major_formatter(FuncFormatter(FormatPercent))
        plt.gca().yaxis.set_major_formatter(FormatPercent)
    plt.ylim(0)
    plt.legend()
    plt.grid()
    DrawGeneral(title, show, savefile)


def DrawPlotPie(data, title='', collects=None, explode=None, show=True, savefile=None):
    data_sorted = sorted(zip(data, collects))
    x      = [a for a, b in data_sorted]
    labels = [b for a, b in data_sorted]
    plt.pie(x, explode, labels,
            autopct='%.1f%%',   # 显示百分比
            startangle=90,      # 起始角度
            # counterclock=False, # 逆时针否
            wedgeprops=dict(width=0.6,edgecolor='w'))
    DrawGeneral(title, show, savefile)


def DrawPlotBar(data, title='', collects=None, show=True, savefile=None):
    plt.bar(collects, data, zorder=2)
    if len(collects) <= 12 or len(collects) == 31:
        rotation = 0
    elif len(collects) == 16:
        rotation = 45
    else:
        rotation = 90
    plt.xticks(collects, rotation=rotation)
    plt.grid(axis='y', zorder=1)
    DrawGeneral(title, show, savefile)


def Analyse1(data, collect, show=False):
    title = '各%s结婚预约人数统计'%alias[collect]

    collects = set()
    for one in data:
        collects.add(one[collect])
    collects = sorted(list(collects))
    samples  = [collect]

    result = [0]*len(collects)

    for one in data:
        result[collects.index(one[collect])] += one['cnt']

    DrawPlot([result], '%s '%title, collects, samples, show, '单参数-%s'%title)
    DrawPlotPie(result, '%s '%title, collects, None, show, '饼图-%s'%title)
    DrawPlotBar(result, '%s '%title, collects, show, '柱形图-%s'%title)

    data_sorted = sorted(list(zip(result, collects)), reverse=1)
    result2   = [num          for num, collect in data_sorted]
    collects2 = [str(collect) for num, collect in data_sorted] # 将标签str防止当标签为数字格式时无法达到排序效果
    DrawPlotBar(result2, '%s '%title, collects2, show, '排序-%s'%title)

    return result, collects


def Analyse2(data, collect, sample, show=False):
    title = '%s-%s的结婚预约人数统计'%(alias[sample], alias[collect])

    collects = set()
    samples  = set()
    for one in data:
        collects.add(one[collect])
        samples. add(one[sample])
    collects = sorted(list(collects))
    samples  = sorted(list(samples))

    result = [[0]*len(collects) for _ in samples]

    for one in data:
        result[samples.index(one[sample])][collects.index(one[collect])] += one['cnt']

    DrawPlot(result, '%s'%title, collects, samples, show, '双参数-%s'%title)

    return result, collects, samples


def Exhaustion(data): # 穷举组合方式
    # 排除强相关的标签
    except_tags = [['mday', 'yday', 'odd'], ['yday', 'mon']]
    tags = ['year', 'mon', 'mday', 'wday', 'yday', 'hday', 'odd', 'area']
    for tag1 in tags:
        Analyse1(data, tag1)
        print('Draw: %s'%tag1)
        for tag2 in tags:
            if tag1 != tag2:
                is_related = False
                for related in except_tags:
                    if tag1 in related and tag2 in related:
                        is_related = True
                        break
                if not is_related:
                    print('Draw: %s-%s'%(tag1, tag2))
                    Analyse2(data, tag1, tag2)


#----------------------------------------------------------------------------
# 特殊统计
#----------------------------------------------------------------------------

def Analyse2Top(data, collect, sample, collect_top=0, sample_top=0, show=False): # other=False, reverse=True, separate=False
    title = '%s-%s'%(alias[sample], alias[collect])

    num1, collects_sorted = SortAndCut(data, collect, collect_top)
    num2, samples_sorted  = SortAndCut(data, sample, sample_top)

    data_top = []
    result, collects, samples = Analyse2(data, collect, sample)
    for sample_name in samples_sorted:
        line = []
        for collect_name in collects_sorted:
            line.append(result[samples.index(sample_name)][collects.index(collect_name)])
        data_top.append(line)

    DrawPlot(data_top, 'Top: %s'%title , collects_sorted, samples_sorted, show, savefile='排序-'+title)
    return data_top


def Analyse2Ratio(data, collect, sample, show=False):
    title = '%s-%s的结婚预约人数占比统计'%(alias[sample], alias[collect])
    result, collects, samples = Analyse2(data, collect, sample)
    totals, collects = Analyse1(data, collect)
    result2 = []
    for nums, sample_name in zip(result, samples):
        row = []
        for num, total in zip(nums, totals):
            row.append(num / total)
        result2.append(row)
    DrawPlot(result2, title, collects, samples, show, savefile='占比-'+title)
    return result2, collects, samples


def MaxAndMinDate(data, weekday_data):
    '''全时间轴最多和最少'''
    # 单一民政局人数最多的一天
    area_max_num = 0
    area_max_date = []
    for day in data:
        num = day['cnt']
        if num > area_max_num:
            area_max_num = num
            area_max_date = []
        if num == area_max_num:
            area_max_date.append([day['area'], day['date']])

    # 最多和最少的一天
    result, tags = SortAndCut(data, 'date', -1)
    max_num = result[0]
    min_num = result[-1]
    max_date = []
    min_date = []
    for num, date in zip(result, tags):
        if num == max_num:
            max_date.append(date)
        if num == min_num:
            min_date.append(date)
    min_date = sorted(min_date)

    # 最多的一天等于最少的多少天
    equal_cnt = 0
    for i, num in enumerate(reversed(result)):
        equal_cnt += num
        if equal_cnt > max_num:
            equal_day = i
            break

    # 没有人结婚的日子
    import datetime
    date = datetime.datetime(2011, 1, 1)
    oneday = datetime.timedelta(1)
    void_date = []
    while 1:
        str_date = datetime.datetime.strftime(date, '%Y-%m-%d')
        # (非调休调班但不是周日 or 调班日) and 该日期不在汇总中
        if ((weekday_data.get(str_date, 0) == 0 and date.weekday() + 1 != 7) or weekday_data.get(str_date, 0) == 2) and str_date not in tags:
            void_date.append(str_date)
        if str_date == '2019-12-31':
            break
        date += oneday

    return [max_num, max_date], [min_num, min_date], [area_max_num, area_max_date], void_date, equal_day


def MarryInHoliday(data, weekday_data):
    '''节假日仍然领证的人'''
    result2 = []
    result, collects, samples = Analyse2(data, 'date', 'area')
    for sample_name, row in zip(samples, result):
        for collect_name, cell in zip(collects, row):
            if weekday_data.get(collect_name, 0) == 1 and cell:
                result2.append([sample_name, collect_name, cell])
    return result2


def MarryInHolidayPercent(data, weekday_data):
    result = MarryInHoliday(data, weekday_data)
    cnt_2019 = 0
    cnt = 0
    for area, date, num in result:
        cnt += num
        if SplitDate(date)['year'] != 2019:
            cnt_2019 += num
    cnt_sunday = Analyse1(data, 'wday')[0][-1]
    total = sum(Analyse1(data, 'year')[0])
    print('修正前:', Percent(cnt_sunday, total, 3))
    print('修正1:', Percent(cnt, total, 3))
    print('修正2:', Percent(cnt_2019, total, 3))


#----------------------------------------------------------------------------

data, weekday_data = Preprocess('2010-2019.csv', 'holiday.csv')

#----------------------------------------------------------------------------


#----------------------------------------------------------------------------
# DONE
# 每年最高值
# 全部最多/最少的单日
# 取消晚婚假(2017-01-01)(https://v.66law.cn/yuyinask/26472.html)
# 开放二胎(2015-10-29)(http://wenda.bendibao.com/life/201956/1259.shtm)
# 每年最受欢迎的日期
# 在节假日仍然结婚的人
# 各地区和全北京的逐年增长率变化(以及后续的将增长率排除计算特殊影响)
# 各区县的逐年占比变化
# 节假日对wday的影响
# 饼图
# 增加排序的柱形图
# 全年的不同日期人数频率分布直方图(排序)
#----------------------------------------------------------------------------
# PASS
# 排除离群点的月份统计
# 节假日对特殊日期的影响(归零)
# 各区县在520 214上的态度
#----------------------------------------------------------------------------

#----------------------------------------------------------------------------
# TODO
# 2013年1月4日 201314 20121212的等
# 全部曲线及拟合(增加稀疏的横坐标)
# 单双日的盒图
# 领证和子女出生日期的相关性
# 二八原则
# 所有日期大排序(折叠滚动条)
# 取消晚婚假对比北京人口曲线
# 出生率和结婚人数关系(2018年2171*0.9%=19.5w, 10w人领证)(https://www.sohu.com/a/258486017_769943)
# 出生月份与领证时间的关系(http://www.chyxx.com/industry/201701/486628.html)
# 星期四的影响
# 原来10-01是最冷清的一天，但是后来不是了
# 百分比纵坐标
# 画图输出数据结果到csv
#----------------------------------------------------------------------------


def General(data):
    cnt_qixi = 0
    for day in data:
        if day['date'] in qixi:
            cnt_qixi += day['cnt']
    print('in_qixi:', cnt_qixi)

    data2 = []
    for day in data:
        if day['year'] < 2019:
            data2.append(day)
    nums, ydays = Analyse1(data2, 'yday')
    data2_sorted = sorted(list(zip(nums, ydays)))
    print('min_yday_before_2019:', len(data2_sorted), data2_sorted[:5])
    
    nums, areas = Analyse1(data, 'area')
    data_sorted = sorted(list(zip(nums, areas)), reverse=1)
    print('total:', sum(nums), sum(nums)/365/10)
    print('max_area:', data_sorted[0])

    min_areas = []
    cnt = 0
    for num, area in reversed(data_sorted):
        if cnt < data_sorted[0][0]:
            cnt += num
            min_areas.append(area)

        if not cnt < data_sorted[0][0]:
            cnt -= num
            min_areas.pop()
            break
    print('equal_min_areas:', cnt, len(min_areas), '、'.join(reversed(min_areas)))


General(data)


Analyse1(data, 'area', 1)

Analyse2Ratio(data, 'year', 'area', 1)
Analyse2Ratio(data, 'year', 'odd', 1)
Analyse2Ratio(data, 'year', 'wday', 1)

def Analyse2RatioSorted(result2, collects, samples):
    saturday = result2[5]
    result3 = []
    for line in result2:
        line_sorted = sorted(list(zip(saturday, line)))
        line2 = [one for sat, one in line_sorted]
        result3.append(line2)
    collects_sorted = sorted(list(zip(saturday, collects)))
    collects2 = [one for sat, one in collects_sorted]

    title = '%s-%s的结婚预约人数占比统计'%(alias['wday'], alias['area'])
    DrawPlot(result3, title, collects2, samples, True, savefile='sp-'+title)

result2, collects, samples = Analyse2Ratio(data, 'area', 'wday', 1) # 本身也会画一张图
Analyse2RatioSorted(result2, collects, samples)



Exhaustion(data) # 穷举组合方式



def DrawPlotDist(data, collect, title, top1, top2):
    nums, collects = Analyse1(data, collect)
    data_sorted = sorted(list(zip(nums, collects)), reverse=1)
    nums_sorted = [num for num, collect_name in data_sorted]
    plt.bar(np.arange(len(nums_sorted)), nums_sorted, width=1, zorder=2)
    plt.ylim(-1, 22000)
    plt.xlim(-1, len(nums_sorted))
    plt.grid(axis='y', zorder=1)
    plt.xticks(np.arange(0, 365, 30))
    

    tags = [[(top1-1, nums_sorted[top1-1]), (20, nums_sorted[top1-1]+800), '%d天'%top1],
            [(top2-1, nums_sorted[top2-1]), (40, nums_sorted[top2-1]+800), '%d天'%top2]]
    for xy, xytext, s in tags:
        plt.axvline(xy[0]+0.5, 0, xy[1]/22000, ls='--', c='silver', linewidth=1, zorder=3)
        plt.annotate(s, xy,
                     xytext=xytext,
                     arrowprops=dict(arrowstyle='-|>', connectionstyle='arc3'),
                     bbox=dict(boxstyle='square', fc='white', alpha=0.4)
                     )

    DrawGeneral(title, 1, 'sp-'+title)
    print('top1/2/3:', nums_sorted[0], nums_sorted[1], nums_sorted[3])

    return sum(nums_sorted), sum(nums_sorted[:top1]), sum(nums_sorted[:top2])


total, sum_top1, sum_top2 = DrawPlotDist(data, 'yday', '一年中最受欢迎日期的结婚人数频数分布直方图', 2, 14)
print('Top2:',  Percent(sum_top1, total))
print('Top14:', Percent(sum_top2, total))


def MostPopularDate(data, top=30):
    '''取中位数排序一年中最受欢迎的结婚日期
       取中位数而不是平均数排序,是为了排除诸如201314的特殊年月日日期,和节假日导致0人结婚结婚造成的影响'''
    result, collects, samples = Analyse2(data, 'year', 'yday')
    result2 = []
    for nums, date in zip(result, samples):
        half = len(nums) // 2 # 因为所有数据均为奇数(9)个项目, 所以中位数只有一个不需要中间的两个除2
        result2.append([sorted(nums)[half], date, nums])

    result3 = sorted(result2, reverse=1)
    data1 = []
    samples = []
    for median, date, nums in result3[:top]:
        data1.append(median)
        samples.append(date)

    title = '最受欢迎的日期结婚人数(单日)(中位数)(前%s)'%top

    # 曲线图
    # DrawPlot([data1], title, samples, ['date'], show=True, savefile='sp-'+title)

    # 散点图
    plt.scatter(np.arange(len(data1)), data1, marker='*', zorder=2)
    plt.xticks(np.arange(len(data1)), samples, rotation=90)
    plt.xlim(-1, top)
    plt.ylim(0, 2200)
    plt.grid(axis='y')
    for x, y in enumerate(data1):
        plt.axvline(x, 0, y/2200, ls='--', c='silver', linewidth=1, zorder=1)
    plt.axhspan(0, 500,     alpha=0.3)
    plt.axhspan(500, 1375,  alpha=0.2)
    plt.axhspan(1375, 2200, alpha=0.1)
    DrawGeneral(title, 1, 'sp-%s(散点)'%title)

    return result3

result1 = MostPopularDate(data, top=40)



def MostPopularDateEveryYear(data):
    result, collects, samples = Analyse2(data, 'yday', 'year')
    result2 = []
    for nums, years in zip(result, samples):
        result2.append(sorted(list(zip(nums, collects)), reverse=1))
    return result2



def SpecialDateButNotSpecialYday(data, top):
    from scipy import stats

    result, collects, samples = Analyse2(data, 'year', 'yday')
    totals, years = Analyse1(data, 'year')
    totals = [one / 20 for one in totals]
    result2 = []
    for nums, date in zip(result, samples):

        nums2 = []
        for i, num in enumerate(nums):
            # if num: # 排除不可抗力造成的0点
            if num:
                nums2.append([num / 20, totals[i]])

        res = stats.chi2_contingency(nums2)
        result2.append([res[1], date, nums])

    result3 = sorted(result2)

    ps = []
    collects = []
    colors = []
    for p, yday, nums in reversed(result3[:top]):
        if p == 0.0:
            p = 1e-308
        year = years[nums.index(max(nums))]
        date = '%s-%s'%(year, yday)
        if date in qixi:
            colors.append('pink')
        else:
            colors.append('#1F77B4') # 默认的蓝色
        # print(date, p, nums)
        ps.append(-np.log(p)/np.log(10)) # 绘制对数柱形图
        collects.append(date)

    plt.barh(np.arange(len(ps)), ps, color=colors, zorder=2)
    plt.xticks(np.arange(0, 250, 50), [1, '10^-50', '10^-100', '10^-150', '10^-200'])
    plt.yticks(np.arange(len(ps)), collects)
    plt.xlim(0, 240)
    plt.ylim(-1, top)
    plt.grid(axis='x', zorder=1)
    title = '日期在不同年份间结婚人数的卡方检验p-value(前%s)'%top
    DrawGeneral(title, 1, 'sp-'+title)

    return ps, collects

SpecialDateButNotSpecialYday(data, 20)



##def MostPopularDateEveryYearRatio(data):
##    result = MostPopularDateEveryYear(data)
##    # for year in result:
##    #     print(year[:20])
##    totals, years = Analyse1(data, 'year')
##    result2 = []
##    for dates, total in zip(result, totals):
##        row = [0]
##        for num, date in dates:
##            row.append(row[-1] + num / total)
##        result2.append(row)
##        
##    DrawPlot(result2, '123', np.arange(366), years, 1)
##
##MostPopularDateEveryYearRatio(data)



def AllTrail(data, middle, show=False):
    trail = [0]
    nums, dates = Analyse1(data, 'date')
    for num in nums:
        trail.append(trail[-1] + num)
##    for num, date in zip(nums, dates):
##        day = SplitDate(date)
##        if day['wday'] != 6 and weekday_data.get(date, 0) == 0:
##            trail.append(trail[-1] + num)
    print('Fin Accumulation')

    x1 = np.arange(middle+1)
    x2 = np.arange(middle, len(trail))
    y1 = np.array(trail[:middle+1])
    y2 = np.array(trail[middle:])
    f1 = np.polyfit(x1, y1, 1)
    f2 = np.polyfit(x2, y2, 1)
    p1 = np.poly1d(f1)
    p2 = np.poly1d(f2)
    print(p1, p2)
    yvals1 = p1(x1)
    yvals2 = p2(x2)
    plt.plot(x1, y1, zorder=1)
    plt.plot(x2, y2, zorder=1)
    plt.plot(x1, yvals1, label=str(p1), zorder=1)
    plt.plot(x2, yvals2, label=str(p2), zorder=1)

    plt.grid()
    plt.legend()

    dxy = [len(trail)/20, -trail[-1]/10]
    events = [['2011-11-01', '开放双独二孩', dxy],
              ['2013-11-01', '开放单独二孩', dxy],
              ['2015-12-01', '允许跨区登记', (-5*dxy[0], -0.5*dxy[1])],
              ['2016-01-01', '全面二孩',    (-3*dxy[0], -2*dxy[1])],
              ['2016-07-01', '周六必须预约', (dxy[0], 1.5*dxy[1])],
              ['2017-01-01', '取消晚婚假',  dxy],
              ]
    events = list(reversed(events))
    date2, event, dxy = events.pop()
    for i, date in enumerate(dates):
        if date > date2:
            print(i, date, date2)
            xy = (i-1, trail[i-1])
            plt.scatter(*xy, c='b', marker='D', zorder=2)
            plt.annotate(date2+'\n'+event, xy,
                         xytext=(xy[0]+dxy[0], xy[1]+dxy[1]),
                         arrowprops=dict(arrowstyle='-|>', connectionstyle='arc3'),
                         bbox=dict(boxstyle='square', fc='yellow', alpha=0.4)
                         )
            if len(events):
                date2, event, dxy = events.pop()
            else:
                break

    plt.xticks([0, middle, len(trail)-1], [dates[0], dates[middle], dates[-1]])
    title = '历史累加预约结婚人数及拟合曲线和拐点'
    DrawGeneral(title, show, 'sp-'+title)

    return trail, p1[1], p2[1]


trail, k1, k2 = AllTrail(data, 1486, 1) # 2015-12-18

# trail, k1, k2 = AllTrail(data, 1286, 1) # 2015-04-17 排除周六和节假日后的曲线(因为周六必须预约才能办理)
##print(k1, k2) # 148, 380

# 查询百度“结婚 2015年12月 2015年11月”等



max_date, min_date, area_max_date, void_date, equal_day = MaxAndMinDate(data, weekday_data)

print('max_date:', max_date)
print('min_date:', min_date)
print('area_max_date:', area_max_date)
print('void_date:', void_date)
print('equal_day:', equal_day)




# TODO 这个数据可以提一下
# 2013-01-04(5): 90.48% 6498/7182



def MostTopPopularDateEveryYearInBar(data, top):
    cmap = cm.Blues_r
    result = MostPopularDateEveryYear(data)
    year_total, years = Analyse1(data, 'year')
    bottom = [0] * len(years)
    for rank in range(top):
        nums = [year_sorted[rank][0]/total for total, year_sorted in zip(year_total, result)]
        plt.bar(np.arange(len(years)), nums, bottom=bottom, color=cmap(rank/top*0.9), zorder=2)
        bottom = [base + num for base, num in zip(bottom, nums)]    
    plt.xticks(np.arange(len(years)), years)
    plt.grid(axis='y', zorder=1)
    plt.gca().yaxis.set_major_formatter(FormatPercent)
    plt.legend(['Top%d'%(i + 1) for i in range(top)])

    title = '每年中结婚人数最多的单日的全年占比堆积柱形图(前%s)'%top
    DrawGeneral(title, 1, 'sp-'+title)

MostTopPopularDateEveryYearInBar(data, 6)




def DistributionInYear(data):
    result, collects, samples = Analyse2(data, 'yday', 'mon') # TODO 此处生成了一张"月-月日"图
    result2 = []
    for res in result:
        result2.append(list(filter(None, res)))
            
    fig = plt.boxplot(result2, sym='x')

    for x, box in enumerate(fig['fliers']):
        for y in box.get_data()[1]:
            date = collects[result[x].index(y)]
            plt.annotate(date, (x+1.1, y+700), fontsize=9,
                         bbox=dict(boxstyle='square', fc='white', alpha=0.4),
                         )

    plt.xticks(np.arange(1, len(samples) + 1), samples)
    plt.grid()
    plt.ylim(-500, 23000)

    title = '各月份不同日期结婚人数盒图统计图(标记离群点)'
    DrawGeneral(title, 1, 'sp-'+title)

DistributionInYear(data)




MarryInHolidayPercent(data, weekday_data)



Analyse2Top(data, 'year', 'yday', sample_top=15, show=1)

# SKIP 对横坐标年份按照该年份的曲线总数值之和进行了排序
##Analyse2Top(data, 'year', 'yday', sample_top=10, collect_top=-1, show=1)



#----------------------------------------------------------------------------


##Analyse2(data, 'area', 'year')
##Analyse1(data, 'mon', 1)
##Analyse1(data, 'year', 1)
##Analyse1(data, 'yday', 1)
##
##Analyse2(data, 'year', 'yday', 1)
##Analyse2(data, 'year', 'hday', 1)
##Analyse2(data, 'hday', 'wday', 1)
##Analyse2(data, 'mon', 'mday', 1)
##Analyse2(data, 'year', 'mon', 1)
##
##Analyse2(data, 'area', 'mon')
##Analyse2(data, 'area', 'year')
##Analyse2(data, 'year', 'mon')
##Analyse2(data, 'year', 'odd')
##Analyse2(data, 'year', 'wday')




# 非节假日的最少登记人数日期(月日和年月日)
##Analyse2(data, 'hday', 'wday', 1)
##Analyse2(data, 'hday', 'area', 1)



#----------------------------------------------------------------------------

# SKIP 逐年前13个日期的总占比逐年呈下降的趋势但波动较大不作列出
##result1 = MostPopularDate(data, top=40)
##result2, collects = Analyse1(data, 'year')
##result3 = [0] * len(collects)
##for median, date, nums in result1[:13]: # 前13个日期最多
##    res = date
##    for num, total in zip(nums, result2):
##        res += ' %.2f%%'%(100*num/total)
##    print(res)



# SKIP 前后一天的人数也不多
##result, dates = Analyse1(data, 'date')
##for num, date in zip(result, dates):
##    if date.startswith('2014-11-1'):
##        print(date, num)
# TODO void_date前后一天的结婚人数
# 2014-11-11 9
# 2014-11-13 33



# SKIP 使用卡方检验更有效
##def TopDatesInYday(data):
##    dates_sorted = SortAndCut(data, 'date', -1)
##    ydays_sorted = SortAndCut(data, 'yday', -1)
##    result = []
##    for num1, date in zip(*dates_sorted):
##        res = SplitDate(date)
##        yday1 = res['yday']
##        wday1 = res['wday']
##        for num2, yday2 in zip(*ydays_sorted):
##            if yday2 == yday1:
##                result.append('%s(%s): %.2f%% %s/%s'%(date, wday1, 100*num1/num2, num1, num2))
##    return result
##
##result = TopDatesInYday(data)
##print('\n'.join(result[:100]))

