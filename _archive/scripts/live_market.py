import urllib.request,re,io,sys,time
from datetime import datetime
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
H={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

print('FundOS Live Market -', datetime.now().strftime('%H:%M'))
print()

# Method 1: Sina Finance API (different source, should not be rate-limited)
print('=== 大盘指数 (新浪财经) ===')
try:
    url='https://hq.sinajs.cn/list=sh000001,sz399001,sz399006,sh000688,sh000300'
    req=urllib.request.Request(url,headers={**H,'Referer':'https://finance.sina.com.cn/'})
    resp=urllib.request.urlopen(req,timeout=10).read().decode('gbk')
    lines=resp.strip().split('\n')
    name_map={'sh000001':'上证指数','sz399001':'深证成指','sz399006':'创业板指','sh000688':'科创50','sh000300':'沪深300'}
    for line in lines:
        parts=line.split('"')
        if len(parts)>=2:
            code=line.split('var hq_str_')[1].split('=')[0]
            data=parts[1].split(',')
            if len(data)>5:
                name=name_map.get(code,code)
                price=float(data[3]); prev=float(data[2]); chg=(price-prev)/prev*100 if prev>0 else 0
                a='+' if chg>=0 else ''
                print(f'  {name:6s}: {price:8.2f} {a}{chg:+.2f}%  O:{data[1]} H:{data[4]} L:{data[5]}')
except Exception as e:
    print(f'  Sina failed: {str(e)[:60]}')

print()

# Method 2: Try EastMoney with longer delay
print('=== 板块概念 (东方财富) ===')
sectors={'半导体':'90.BK0471','AI':'90.BK0999','绿电':'90.BK1086','光伏':'90.BK1084','芯片':'90.BK0890','科创50概念':'90.BK0708','信创':'90.BK1107','机器人':'90.BK1140'}
for name,code in sectors.items():
    time.sleep(2.5)
    try:
        url='https://push2.eastmoney.com/api/qt/stock/get?secid='+code+'&fields=f43,f170,f58'
        d=json.loads(urllib.request.urlopen(urllib.request.Request(url,headers=H),timeout=8).read()).get('data',{})
        p=d.get('f43',0)/100; chg=d.get('f170',0)/100
        a='+' if chg>=0 else ''
        bar=chr(9608)*min(15,int(abs(chg)*3))
        print(f'  {name:8s}: {p:8.0f} {a}{chg:+.2f}%  {bar}')
    except Exception as e:
        if 'closed' not in str(e):
            print(f'  {name:8s}: {str(e)[:40]}')
