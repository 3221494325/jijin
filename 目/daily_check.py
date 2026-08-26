#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FundOS 每日盘后检查 v1.0 (2026-08-08)
用法: 交易日 15:00 后运行  python daily_check.py
抓取最新已公布净值 -> 对比 止损/止盈/换A 触发线 -> 输出当日操作建议
输出: 控制台 + daily_check_YYYY-MM-DD.md

交易规则要点:
- 15:00 前提交按当日净值, 15:00 后按下一交易日 -> 建议须次日 15:00 前执行
- A股 T+1 确认, QDII 净值滞后 1-2 天 -> 表内标注净值日期
- C类赎回: 绿电/纳指>=7天免, 其余>=30天免; A类标普1年内0.5%, 科创50>=180天免
"""
import requests, json, sys, datetime
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
BASE = Path(__file__).resolve().parent
TODAY = datetime.date.today()
REPORT = BASE / 'daily_check_{0}.md'.format(TODAY.strftime('%Y-%m-%d'))

H = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36',
     'Referer': 'https://fundf10.eastmoney.com/'}

# ---- 持仓配置 (成本净值基准 2026-08-08; 信息产业转A后按A类净值口径) ----
# switch_th: 换A触发收益率阈值; penalty: 该日之后满30天批次免赎回费
HOLDINGS = [
    dict(name='华夏绿电', cls='C', cost=479.99, weight=12.3, sector='green',
         codes=[dict(code='018735', cost_nav=1.1555)], a_code='018734',
         switch_th=-0.02, penalty=None,
         note='光伏反内卷利好; 反弹到 -2% 换A'),
    dict(name='全球成长', cls='C', cost=390.02, weight=8.5, sector='qdii',
         codes=[dict(code='012922', cost_nav=4.6448)], a_code='012920',
         switch_th=-0.10, penalty=None,
         note='已破-15%评估线; 硬止损-25%(3.4836); 禁摊平; 反弹-10%减1/3'),
    dict(name='标普500', cls='A', cost=719.97, weight=19.7, sector='qdii',
         codes=[dict(code='017641', cost_nav=1.6847)], a_code=None,
         switch_th=None, penalty=None, note='1年内赎回0.5%, 不急卖'),
    dict(name='纳斯达克100', cls='A', cost=419.99, weight=11.1, sector='qdii',
         codes=[dict(code='019172', cost_nav=1.7830)], a_code=None,
         switch_th=None, penalty=None, note='净值滞后1-2天; 不接飞刀'),
    dict(name='半导体', cls='C', cost=222.98, weight=6.0, sector='tech',
         codes=[dict(code='019764', cost_nav=2.3546)], a_code='019759',
         switch_th=0.0, penalty='2026-08-15',
         note='07-16批次满30天后换A更优'),
    dict(name='科创50联接', cls='A', cost=382.41, weight=9.8, sector='tech',
         codes=[dict(code='011608', cost_nav=1.4103)], a_code=None,
         switch_th=None, penalty=None, note='180天内赎回0.1%; 减仓优先'),
    dict(name='科技智选', cls='C', cost=633.53, weight=17.0, sector='tech',
         codes=[dict(code='022365', cost_nav=5.4455)], a_code='022364',
         switch_th=0.0, penalty='2026-08-27',
         note='07-28转换批次满30天后换A更优'),
    dict(name='信息产业', cls='A', cost=554.40, weight=15.6, sector='tech',
         codes=[dict(code='019018', cost_nav=7.8693, until='2026-08-10'),
                dict(code='001513', cost_nav=7.9833, from_='2026-08-10')],
         a_code=None, switch_th=None, penalty=None,
         note='已转A(08-10到账); 浮盈中, +15%止盈1/3'),
]

def pick_code(item):
    for c in item['codes']:
        if 'until' in c and TODAY >= datetime.date.fromisoformat(c['until']):
            continue
        if 'from_' in c and TODAY < datetime.date.fromisoformat(c['from_']):
            continue
        return c
    return item['codes'][-1]

def fetch_nav(code):
    u = 'https://api.fund.eastmoney.com/f10/lsjz?fundCode={0}&pageIndex=1&pageSize=2'.format(code)
    r = requests.get(u, headers=H, timeout=15)
    d = r.json()
    ls = (d.get('Data') or {}).get('LSJZList') or []
    if not ls:
        return None, None, None
    x = ls[0]
    return x['FSRQ'], float(x['DWJZ']), float(x['JZZZL'] or 0)

def main():
    lines = []
    def out(s=''):
        print(s)
        lines.append(s)

    out('# FundOS 每日盘后检查 | {0}'.format(TODAY.isoformat()))
    out('')
    out('> 净值来源: 天天基金 f10/lsjz (最新已公布). QDII 净值滞后 1-2 天, 请留意净值日期. 建议须于下一交易日 15:00 前执行.')
    out('')

    rows = []
    actions = []
    tech_v = qdii_v = green_v = total_v = 0.0

    for it in HOLDINGS:
        c = pick_code(it)
        code, cost_nav = c['code'], c['cost_nav']
        nav_date, nav, chg = fetch_nav(code)
        if nav is None:
            out('!! {0} {1} 净值获取失败'.format(it['name'], code))
            continue
        ret = nav / cost_nav - 1
        est_value = it['cost'] * (1 + ret)
        total_v += est_value
        if it['sector'] == 'tech': tech_v += est_value
        elif it['sector'] == 'qdii': qdii_v += est_value
        else: green_v += est_value

        flags = []
        if ret <= -0.25:
            flags.append('HARD_STOP')
        elif ret <= -0.15:
            flags.append('EVAL_15')
        if ret >= 0.20:
            flags.append('TP20')
        elif ret >= 0.15:
            flags.append('TP15')

        advice = '持有观察'
        if 'HARD_STOP' in flags:
            advice = '当日无条件出清'
        elif 'EVAL_15' in flags:
            advice = '体检逻辑, 反弹分批退出'
        elif 'TP20' in flags:
            advice = '止盈+20%: 再减1/3'
        elif 'TP15' in flags:
            advice = '止盈+15%: 减1/3'
        if it['a_code'] and it['switch_th'] is not None and ret >= it['switch_th']:
            if not flags:
                advice = '换A {0} (分批<=1/3, 间隔>=1周)'.format(it['a_code'])
            else:
                advice += '; 换A {0}'.format(it['a_code'])
            if it['penalty'] and TODAY < datetime.date.fromisoformat(it['penalty']):
                advice += '; 近30天批次未满(赎回费0.5%), 换仓避开'

        flag_txt = '/'.join(flags) if flags else '-'
        rows.append((it['name'], code, cls := it['cls'], nav_date, chg, ret, flag_txt, advice))
        if flags or (it['a_code'] and it['switch_th'] is not None and ret >= it['switch_th']):
            actions.append('{0} {1} [{2}] {3}'.format(('🔴' if 'STOP' in flag_txt else '🟢' if 'TP' in flag_txt else '🟡'), it['name'], code, advice))

    total_ret = total_v / sum(it['cost'] for it in HOLDINGS) - 1
    tech_w = tech_v / total_v * 100
    qdii_w = qdii_v / total_v * 100

    out('## 一、净值与触发状态')
    out('')
    out('| 基金 | 代码 | 类别 | 净值(日期) | 日涨跌% | 收益率% | 触发 | 建议 |')
    out('|---|---|---|---|---|---|---|---|')
    for name, code, cls, nd, chg, ret, ft, adv in rows:
        chg_t = '{0:+.2f}'.format(chg) if chg is not None else '-'
        out('| {0} | {1} | {2} | {3} | {4} | {5:+.2f}% | {6} | {7} |'.format(
            name, code, cls, nd, chg_t, ret * 100, ft, adv))
    out('')
    out('## 二、组合状态')
    out('')
    out('- 估算总市值: **¥{0:,.0f}** | 总盈亏: **{1:+.1f}%**'.format(total_v, total_ret * 100))
    out('- 科技/AI 占比: **{0:.1f}%** (目标<=40%) {1}'.format(tech_w, '⚠️超配' if tech_w > 40 else '✅'))
    out('- QDII 海外占比: **{0:.1f}%** (目标<=40%) {1}'.format(qdii_w, '⚠️超配' if qdii_w > 40 else '✅'))
    out('')
    out('## 三、操作建议 (下一交易日 15:00 前执行)')
    out('')
    if actions:
        for i, a in enumerate(actions, 1):
            out('{0}. {1}'.format(i, a))
    else:
        out('无触发, 全部持有观察.')
    out('')
    out('## 四、免责声明')
    out('')
    out('净值与触发价为自动化计算, 需人工复核; 决策框架仅供参考, 非收益承诺, 操作以 App 实际数据为准.')

    REPORT.write_text('\n'.join(lines), encoding='utf-8')
    print('')
    print('报告已保存: {0}'.format(REPORT))

if __name__ == '__main__':
    main()
