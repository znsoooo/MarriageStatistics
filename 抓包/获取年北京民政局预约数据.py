# Homepage: http://mzj.beijing.gov.cn/jhyy/marryout/marry/index_yy.jsp
# Homepage: http://mzjgfpt.caservice.cn/jhyy/marryout/marry/index_yy.jsp

import re
import time
import datetime
import urllib
import urllib.error
import urllib.request

span = 2 # months: 1/2/3/4 (bad: 5/6/7..)
cookie = 'JSESSIONID=rBCWRBtZXgYB9Ka9WWTEP0JJlZIou9aVmTQA.marry1; Hm_lvt_8d03d41be19b72d5f435f915b62779f6=1577144183; Hm_lpvt_8d03d41be19b72d5f435f915b62779f6=1577451827'
headers = {'Cookie': cookie}

url1 = 'http://mzjgfpt.caservice.cn/jhyy/marryout/marry/stepFour.do?method=stepFour'
url2 = 'http://mzjgfpt.caservice.cn/jhyy/report/view_report.jsp?reportName=jhyy&where1=&start_date=%s&end_date=%s&deptCode=%s'

request  = urllib.request.Request(url1, headers=headers)
response = urllib.request.urlopen(request, timeout=5)
content  = response.read().decode('gbk')
district = re.findall(r'<option value="(.*?)" >(.*?)民政局婚姻登记处</option>', content)

print('Author Lsx')
print(time.strftime('%Y-%m-%d %H:%M:%S'))
print('district: %s'%len(district))

with open('log.csv', 'w') as f:
    f.write('Start time: %s\n\n'%time.strftime('%Y-%m-%d %H:%M:%S'))

text = ''
oneday = datetime.timedelta(1)
for code, dept in district:
    print ('-- ' + dept)
    for m in range(int(12 / span) * 0, int(12 / span) * 10):
        y1, m1 = divmod(span * (m),     12)
        y2, m2 = divmod(span * (m + 1), 12)
        d1 = datetime.datetime.strftime(datetime.datetime(2010 + y1, m1 + 1, 1),         '%Y-%m-%d')
        d2 = datetime.datetime.strftime(datetime.datetime(2010 + y2, m2 + 1, 1) - oneday,'%Y-%m-%d')
        print(d1, d2)
        # 实测提交20190101-20191201, 能记录到跨度20190101-20190622, 共173天
        url = url2%(d1, d2, code)
        while 1: # while 1 + break : 有趣的循环重试方法
            try:
                request  = urllib.request.Request(url, headers=headers)
                response = urllib.request.urlopen(request, timeout=15)
                content  = response.read().decode('gbk')
                items = re.findall(r'title=".*? (.*?) (.*?)"', content)
                for item in items:
                    text += dept+','+d1[:5]+item[0]+','+item[1]+'\n'
                # time.sleep(2.7)
                break
            except Exception as e:
                print('Error:', e)
    with open('log.csv', 'a') as f:
        f.write(text)
    text = ''

with open('log.csv', 'a') as f:
    f.write('\nEnd time: %s\n'%time.strftime('%Y-%m-%d %H:%M:%S'))

