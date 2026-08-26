import urllib.request, json, re, gzip, io, sys, time
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
H = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
     'Referer': 'https://fund.eastmoney.com/'}

# ============================================================
# FUND DEFINITIONS
# ============================================================
funds = [
    {'name':'华夏绿电','code':'018735','amount':462,'cost_nav':1.1570,'index':'绿色电力','type':'A股行业','corr_idx':'sh000688','corr_weight':0.3},
    {'name':'全球成长','code':'018354','amount':297,'cost_nav':1.5660,'index':'全球QDII','type':'QDII','corr_idx':'int_nasdaq','corr_weight':0.6},
    {'name':'标普500','code':'017641','amount':707,'cost_nav':1.6610,'index':'标普500','type':'QDII美股','corr_idx':'int_sp500','corr_weight':0.9},
    {'name':'纳斯达克100','code':'019173','amount':391,'cost_nav':1.7310,'index':'纳斯达克','type':'QDII美股','corr_idx':'int_nasdaq','corr_weight':0.9},
    {'name':'半导体','code':'020684','amount':215,'cost_nav':2.2450,'index':'半导体','type':'A股行业','corr_idx':'sh000688','corr_weight':0.7},
    {'name':'信息产业','code':'019024','amount':244,'cost_nav':2.5640,'index':'TMT','type':'A股混合','corr_idx':'sh000688','corr_weight':0.6},
    {'name':'科创50联接','code':'011608','amount':352,'cost_nav':1.3380,'index':'科创50','type':'A股指数','corr_idx':'sh000688','corr_weight':0.95},
    {'name':'科技智选','code':'022365','amount':567,'cost_nav':4.9900,'index':'AI科技','type':'A股混合','corr_idx':'sh000688','corr_weight':0.7},
]

# ============================================================
# 1. FETCH LIVE INDICES
# ============================================================
print('📡 正在获取市场数据...')
indices = {}
# Sina indices
try:
    url = 'https://hq.sinajs.cn/list=sh000001,sz399001,sz399006,sh000688,sh000300,sz399673,sh000016'
    req = urllib.request.Request(url, headers={**H, 'Referer': 'https://finance.sina.com.cn/'})
    resp = urllib.request.urlopen(req, timeout=10).read().decode('gbk')
    for line in resp.strip().split('\n'):
        parts = line.split('"')
        if len(parts) >= 2:
            code = line.split('var hq_str_')[1].split('=')[0]
            data = parts[1].split(',')
            if len(data) > 5:
                indices[code] = {
                    'name': data[0], 'open': float(data[1]), 'prev_close': float(data[2]),
                    'price': float(data[3]), 'high': float(data[4]), 'low': float(data[5]),
                    'chg_pct': (float(data[3])-float(data[2]))/float(data[2])*100
                }
except Exception as e:
    print(f'  ⚠️ 新浪指数获取失败: {e}')

# Fallback: also try pingzhongdata for latest NAV
for f in funds:
    time.sleep(0.3)
    try:
        url = f'https://fund.eastmoney.com/pingzhongdata/{f["code"]}.js'
        req = urllib.request.Request(url, headers=H)
        resp = urllib.request.urlopen(req, timeout=10).read().decode('utf-8')
        nav_m = re.search(r'var Data_netWorthTrend = (\[.+?\]);', resp, re.DOTALL)
        if nav_m:
            nav_data = json.loads(nav_m.group(1))
            if nav_data:
                latest = nav_data[-1]
                f['nav'] = latest['y']
                f['nav_date'] = datetime.fromtimestamp(latest['x']/1000).strftime('%Y-%m-%d')
    except:
        f['nav'] = 0
        f['nav_date'] = 'N/A'

# ============================================================
# 2. CALCULATE POSITION METRICS
# ============================================================
print('📊 正在计算持仓指标...\n')

total_cost = 0
total_value = 0
total_return = 0
for f in funds:
    cost = f['amount']
    nav = f.get('nav', 0)
    cost_nav = f['cost_nav']
    if nav > 0:
        shares = cost / cost_nav
        value = shares * nav
        ret = value - cost
        ret_pct = (nav - cost_nav) / cost_nav * 100
    else:
        shares = 0
        value = cost  # assume no change
        ret = 0
        ret_pct = 0

    f['shares'] = shares
    f['value'] = value
    f['return'] = ret
    f['return_pct'] = ret_pct
    f['weight'] = 0  # will be filled

    total_cost += cost
    total_value += value
    total_return += ret

for f in funds:
    f['weight'] = f['value'] / total_value * 100 if total_value > 0 else 0

# ============================================================
# 3. ESTIMATE TODAY IMPACT VIA INDEX MAPPING
# ============================================================
# Use the 科创50 index (sh000688) as primary proxy for A-share tech funds
idx_688 = indices.get('sh000688', {})
today_chg_688 = idx_688.get('chg_pct', 0) if idx_688 else 0

idx_001 = indices.get('sh000001', {})
today_chg_sh = idx_001.get('chg_pct', 0) if idx_001 else 0

idx_399006 = indices.get('sz399006', {})
today_chg_cyb = idx_399006.get('chg_pct', 0) if idx_399006 else 0

for f in funds:
    t = f['type']
    if t == 'A股指数':
        f['today_est'] = today_chg_688 * f['corr_weight']
    elif t == 'A股行业':
        f['today_est'] = today_chg_688 * f['corr_weight']
    elif t == 'A股混合':
        f['today_est'] = today_chg_688 * f['corr_weight']
    elif t == 'QDII美股':
        # US funds: NAV is T-1 or T-2, today's A-share doesn't affect
        f['today_est'] = 0  
    elif t == 'QDII':
        f['today_est'] = 0
    else:
        f['today_est'] = 0

    # Estimate today's value
    nav = f.get('nav', 0)
    if nav > 0 and f['today_est'] != 0:
        est_nav = nav * (1 + f['today_est'] / 100)
        est_value = f['shares'] * est_nav
        f['est_nav'] = est_nav
        f['est_value'] = est_value
        f['est_return'] = est_value - f['amount']
    else:
        f['est_nav'] = nav
        f['est_value'] = f['value']
        f['est_return'] = f['return']

est_total_value = sum(f.get('est_value', f['value']) for f in funds)
est_total_return = est_total_value - total_cost

# ============================================================
# 4. OUTPUT REPORT
# ============================================================
print('=' * 78)
print(f'  📊 FundOS 持仓分析报告 | {datetime.now().strftime("%Y-%m-%d %H:%M")}')
print('=' * 78)
print()

# Market snapshot
if idx_688:
    print(f'  🟢 科创50: {idx_688["price"]:.2f} (+{idx_688["chg_pct"]:+.2f}%)' if idx_688['chg_pct'] > 0 else f'  🔴 科创50: {idx_688["price"]:.2f} ({idx_688["chg_pct"]:+.2f}%)')
if idx_399006:
    print(f'  {"🟢" if idx_399006["chg_pct"]>0 else "🔴"} 创业板指: {idx_399006["price"]:.2f} ({idx_399006["chg_pct"]:+.2f}%)')
if idx_001:
    print(f'  {"🟢" if idx_001["chg_pct"]>0 else "🔴"} 上证指数: {idx_001["price"]:.2f} ({idx_001["chg_pct"]:+.2f}%)')
print(f'  📅 今日市场状态: {"大涨 🔥" if today_chg_688 > 3 else ("上涨 ✅" if today_chg_688 > 0 else "下跌")} (科创50 领涨)')
print()

# Fund table
print(f'  {"基金":10s} {"投入":>6s} {"市值":>8s} {"盈亏":>7s} {"盈亏%":>7s} {"占比":>6s} {"净值日":>10s} {"今估%":>7s}')
print(f'  {"-"*10} {"-"*6} {"-"*8} {"-"*7} {"-"*7} {"-"*6} {"-"*10} {"-"*7}')
for f in funds:
    ret_color = '🔴' if f['return'] < 0 else ('🟢' if f['return'] > 0 else '⚪')
    today_color = '🟢' if f.get('today_est', 0) > 0 else ('🔴' if f.get('today_est', 0) < 0 else '⚪')
    print(f'  {f["name"]:10s} {f["amount"]:>6.0f} {f["value"]:>8.0f} {ret_color}{f["return"]:>6.0f} {f["return_pct"]:>+6.2f}% {f["weight"]:>5.1f}% {f.get("nav_date","N/A"):>10s} {today_color}{f.get("today_est",0):>+6.2f}%')

print(f'  {"-"*10} {"-"*6} {"-"*8} {"-"*7} {"-"*7} {"-"*6} {"-"*10} {"-"*7}')
total_ret_color = '🔴' if total_return < 0 else '🟢'
total_ret_pct = total_return / total_cost * 100
print(f'  {"合计":10s} {total_cost:>6.0f} {total_value:>8.0f} {total_ret_color}{total_return:>6.0f} {total_ret_pct:>+6.2f}% {"100":>6}%')
print()
print(f'  📈 今日估算市值: ¥{est_total_value:,.0f} | 估算收益: ¥{est_total_return:+,.0f} ({est_total_return/total_cost*100:+.2f}%)')
print()

# ============================================================
# 5. ANALYSIS & DECISION FRAMEWORK
# ============================================================
print('=' * 78)
print('  🔍 盘面分析与观察提醒')
print('=' * 78)
print()

# Risk classification
deep_red = [f for f in funds if f['return_pct'] < -10]
red = [f for f in funds if -10 <= f['return_pct'] < -5]
yellow = [f for f in funds if -5 <= f['return_pct'] < 0]
green = [f for f in funds if f['return_pct'] >= 0]

print('  📋 持仓风险分层:')
if deep_red:
    print(f'     🔴 深度亏损 (>-10%): {len(deep_red)}只 - {", ".join(f["name"] for f in deep_red)}')
if red:
    print(f'     🟠 中度亏损 (-5~-10%): {len(red)}只 - {", ".join(f["name"] for f in red)}')
if yellow:
    print(f'     🟡 轻度亏损 (0~-5%): {len(yellow)}只 - {", ".join(f["name"] for f in yellow)}')
if green:
    print(f'     🟢 盈利: {len(green)}只 - {", ".join(f["name"] for f in green)}')
print()

# Concentration risk
print('  📋 集中度分析:')
for f in sorted(funds, key=lambda x: x['weight'], reverse=True):
    bar_len = int(f['weight'] * 2)
    bar = '█' * bar_len
    print(f'     {f["name"]:10s}: {f["weight"]:5.1f}% {bar}')
print()

# Sector exposure
tech_funds = [f for f in funds if f['type'] in ('A股行业','A股混合','A股指数') and '科技' in f['index'] or '半导体' in f['index'] or '科创' in f['index'] or '信息' in f['index'] or 'AI' in f['index']]
tech_weight = sum(f['weight'] for f in tech_funds)
qdii_weight = sum(f['weight'] for f in funds if f['type'].startswith('QDII'))
print(f'  📋 板块敞口: 科技/TMT {tech_weight:.0f}% | QDII海外 {qdii_weight:.0f}% | 绿电 {sum(f["weight"] for f in funds if "绿电" in f["name"]):.0f}%')
print()

# Today-specific analysis
print('=' * 78)
print('  💡 今日决策框架 (客观观察，非操作建议)')
print('=' * 78)
print()
print(f'  今日市场特征: A股全面大涨，科创50 +{today_chg_688:+.2f}%，创业板 +{today_chg_cyb:+.2f}%')
print(f'  你的持仓高度集中于科技/AI/半导体 ({tech_weight:.0f}%)，今天大概率大幅回血')
print()
print('  📊 观察清单 (基于当前数据):')
print()

# Per-fund observations
for f in funds:
    ret = f['return_pct']
    est = f.get('today_est', 0)
    print(f'  ▸ {f["name"]} [{f["code"]}]')
    
    # Status
    if ret < -20:
        print(f'    状态: 严重亏损 ({ret:+.1f}%)，考虑是否止损或等待反弹')
    elif ret < -10:
        print(f'    状态: 大幅亏损 ({ret:+.1f}%)，关注是否跌破心理底线')
    elif ret < -5:
        print(f'    状态: 中度亏损 ({ret:+.1f}%)')
    elif ret < 0:
        print(f'    状态: 轻微亏损 ({ret:+.1f}%)')
    else:
        print(f'    状态: 盈利 ({ret:+.1f}%)')
    
    # Today estimate
    if est > 5:
        print(f'    今日: 大涨预估 ~{est:+.1f}% (跟随科创50/创业板)')
    elif est > 2:
        print(f'    今日: 上涨预估 ~{est:+.1f}%')
    elif est > 0:
        print(f'    今日: 微涨预估 ~{est:+.1f}%')
    elif est == 0 and f['type'].startswith('QDII'):
        print(f'    今日: QDII海外 - 净值滞后1-2天，今日A股大涨不影响')
    else:
        print(f'    今日: 预估 ~{est:+.1f}%')
    
    # Observation
    if ret < -15 and est > 0:
        print(f'    ⚠️ 观察: 今日反弹但仍在深度亏损区，关注是否持续')
    elif ret < -5 and est > 3:
        print(f'    ℹ️ 观察: 大幅反弹中，关注回本进度')
    print()

# Threshold checks
print('-' * 78)
print('  🎯 策略阈值检查:')
print()

# Loss alert
loss_funds = [f for f in funds if f['return_pct'] < -10]
if loss_funds:
    print(f'  ⚠️ 回撤阈值 (-10%): {len(loss_funds)}只基金触发 - {", ".join(f["name"] for f in loss_funds)}')
else:
    print(f'  ✅ 回撤阈值 (-10%): 无触发')

# Single industry concentration
if tech_weight > 40:
    print(f'  ⚠️ 行业集中度 (>40%): 科技板块 {tech_weight:.0f}%，过于集中')
elif tech_weight > 30:
    print(f'  ℹ️ 行业集中度 (30-40%): 科技板块 {tech_weight:.0f}%，注意分散')
else:
    print(f'  ✅ 行业集中度: {tech_weight:.0f}%，合理范围')

# QDII proportion
if qdii_weight > 50:
    print(f'  ℹ️ QDII占比: {qdii_weight:.0f}%，海外敞口较高')
else:
    print(f'  ✅ QDII占比: {qdii_weight:.0f}%')

print()
print('=' * 78)
print('  📌 免责声明: 以上为客观数据展示与策略阈值检查，不构成投资建议')
print('  📌 所有交易决策请自行判断，投资有风险，市场有波动')
print('=' * 78)

