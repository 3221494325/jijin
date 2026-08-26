import urllib.request,json,io,sys,time,re
from datetime import datetime
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
H={'User-Agent':'Mozilla/5.0','Referer':'https://finance.eastmoney.com/'}

print('=== 板块概念实时 ===')
sectors={'半导体':'90.BK0471','AI人工':'90.BK0999','绿色电力':'90.BK1086','光伏设备':'90.BK1084','芯片':'90.BK0890','科创50':'90.BK0708','信创':'90.BK1107','机器人':'90.BK1140'}
for name,code in sectors.items():
    time.sleep(1.5)
    try:
        d=json.loads(urllib.request.urlopen(urllib.request.Request('https://push2.eastmoney.com/api/qt/stock/get?secid='+code+'&fields=f43,f170',headers=H),timeout=8).read()).get('data',{})
        if d:
            p=d.get('f43',0)/100; chg=d.get('f170',0)/100
            a='+' if chg>=0 else ''
            bar=chr(9608)*min(20,int(abs(chg)*3))
            print(f'  {name:6s}: {p:8.0f} {a}{chg:+.2f}% {bar}')
    except:
        pass

print()

# North-bound capital
print('=== 北向资金 ===')
try:
    url='https://push2.eastmoney.com/api/qt/kamt.kline/get?fields1=f1,f3&fields2=f51,f52&klt=101&lmt=1&secid=1.000300'
    d=json.loads(urllib.request.urlopen(urllib.request.Request(url,headers=H),timeout=8).read())
    klines=d.get('data',{}).get('klines',[])
    if klines:
        parts=klines[-1].split(',')
        net=float(parts[1])/1e8
        direction='净流入' if net>0 else '净流出'
        print(f'  今日北向资金: {direction} {abs(net):.1f}亿')
except:
    pass

# Market breadth
print()
print('=== 市场宽度 ===')
try:
    url='https://push2.eastmoney.com/api/qt/stock/get?secid=1.000001&fields=f43,f169,f170'
    d=json.loads(urllib.request.urlopen(urllib.request.Request(url,headers=H),timeout=8).read()).get('data',{})
    if d:
        up=d.get('f169',0)
        print(f'  上涨家数(沪): {int(up) if up else "N/A"}')
except:
    pass

print()
print('Data: Sina + EastMoney public APIs')
