import urllib.request,json,io,sys,time,re
from datetime import datetime
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
H={'User-Agent':'Mozilla/5.0','Referer':'https://fund.eastmoney.com/'}

funds={'华夏绿电':'018735','全球成长':'018354','标普500':'017641','纳斯达克100':'019173','半导体':'020684','信息产业':'019024','科创50联接':'011608','科技智选':'022365'}

print('FundOS TODAY Change -', datetime.now().strftime('%Y-%m-%d %H:%M'))
print('='*65)
print(f'{"Fund":14s} {"PrevNAV":>8s} {"TodayNAV":>8s} {"DAY%":>8s} {"Date":>10s}')
print('-'*55)

for name,code in funds.items():
    time.sleep(0.4)
    try:
        url = 'https://fund.eastmoney.com/pingzhongdata/' + code + '.js'
        req = urllib.request.Request(url, headers=H)
        resp = urllib.request.urlopen(req, timeout=10).read().decode('utf-8')
        nav_match = re.search(r'var Data_netWorthTrend = (\[.+?\]);', resp, re.DOTALL)
        if nav_match:
            nav_data = json.loads(nav_match.group(1))
            if len(nav_data) >= 2:
                prev = nav_data[-2]['y']
                today = nav_data[-1]['y']
                day_chg = (today - prev) / prev * 100 if prev > 0 else 0
                date_raw = nav_data[-1]['x']
                dt = datetime.fromtimestamp(date_raw/1000) if date_raw > 1e10 else datetime.now()
                date_str = dt.strftime('%m-%d')
                arrow = '+' if day_chg >= 0 else ''
                bar = chr(9608)*min(20, int(abs(day_chg)*2))
                direction = 'RED' if day_chg > 0 else ('GREEN' if day_chg < 0 else '--')
                print(f'{name:14s} {prev:>8.4f} {today:>8.4f} {arrow}{day_chg:>+7.2f}% {date_str:>10s}  {direction} {bar}')
            else:
                print(f'{name:14s} not enough data')
    except Exception as e:
        print(f'{name:14s} ERR: {str(e)[:30]}')

print('='*65)
print('TODAY = latest available NAV day (QDII may be 1-2 days behind)')
