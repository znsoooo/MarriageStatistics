import json
import datetime
import urllib.request

def GetApi(url):
    request = urllib.request.Request(url)
    response = urllib.request.urlopen(request)
    content = response.read()
    data = json.loads(content.decode('gbk'))
    return data

url1 = 'http://api.goseek.cn/Tools/holiday?date=%s'
url2 = 'http://www.easybots.cn/api/holiday.php?d=%s'


##d1   = datetime.timedelta(monthes=1)
##date = datetime.datetime(2010,1,1)
##end  = datetime.datetime(2020,1,1)


for year in range(2010, 2020):
    for month in range(1, 13):
        date = '%d%02d'%(year, month)

        url = 'https://sp0.baidu.com/8aQDcjqpAAV3otqbppnN2DJv/api.php?query=%s&co=&resource_id=6018'%date
        data = GetApi(url)['data'][0]
        if 'holiday' in data:
            holidaylist = data['holiday']
            ss = ''
            if not isinstance(holidaylist, list):
                holidaylist = [holidaylist]
            for holiday in holidaylist:
                days = holiday['list']
                for day in days:
                    ss += day['date'] + ',' + day['status'] + '\n'
            print('Holidaies: %s'%date)
            print(ss)
        else:
            print('Skip: %s'%date)

# 1调休 2调班(除了2个特殊项均为周6/7) 0正常上班(只有1项)