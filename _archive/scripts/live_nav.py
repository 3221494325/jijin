import urllib.request,json,io,sys,time,re
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
H={'User-Agent':'Mozilla/5.0','Referer':'https://fund.eastmoney.com/'}

funds={'华夏绿电':'018735','全球成长':'018354','标普500':'017641','纳斯达克100':'019173','半导体':'020684','信息产业':'019024','科创50联接':'011608','科技智选':'022365'}

print('FundOS Live -', __import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M'))
print('='*65)
print(f'{"基金":12s} {"最新净值":>8s} {"日期":>10s} {"状态":>8s}')
print('-'*50)

for name,code in funds.items():
    time.sleep(0.3)
    try:
        url = 'https://fund.eastmoney.com/pingzhongdata/' + code + '.js'
        req = urllib.request.Request(url, headers=H)
        resp = urllib.request.urlopen(req, timeout=10).read().decode('utf-8')
        
        # Extract the latest NAV from Data_netWorthTrend
        nav_match = re.search(r'var Data_netWorthTrend = (\[.+?\]);', resp, re.DOTALL)
        if nav_match:
            nav_data = json.loads(nav_match.group(1))
            if nav_data:
                latest = nav_data[-1]
                nav = latest.get('y', 0)
                date_raw = latest.get('x', '')
                if date_raw:
                    from datetime import datetime as dt
                    date = dt.fromtimestamp(date_raw/1000).strftime('%Y-%m-%d') if date_raw > 1e10 else str(date_raw)
                else:
                    date = 'N/A'
                print(f'{name:12s} {nav:>8.4f} {date:>10s} {"OK":>8s}')
            else:
                print(f'{name:12s} {"N/A":>8s} {"N/A":>10s} empty')
        else:
            print(f'{name:12s} {"N/A":>8s} {"N/A":>10s} no data')
    except Exception as e:
        print(f'{name:12s} {"ERR":>8s} {"ERR":>10s} {str(e)[:30]}')
