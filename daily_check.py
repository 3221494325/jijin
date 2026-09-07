#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FundOS 每日盘后检查 v2.0 (2026-08-28)
用法: 交易日 15:00 后运行  python daily_check.py
抓取最新已公布净值 -> 对比 止损/止盈/换A 触发线 -> 输出当日操作建议
输出: 控制台 + daily_check_YYYY-MM-DD.md + daily_check_result.json(原子写入)

v2.0 变更:
  - 持仓/成本基准/触发线统一走 fundos_config.FUND_META（9只，与快照对齐，
    修复 v1.0 缺 019759 导致 portfolio_data 静默回退旧快照的问题）
  - 净值获取走 fundos_data（重试+备源）
  - 结果 JSON 原子写入（临时文件+replace，避免引擎并行时的撕裂读）

交易规则要点:
- 15:00 前提交按当日净值, 15:00 后按下一交易日 -> 建议须次日 15:00 前执行
- A股 T+1 确认, QDII 净值滞后 1-2 天 -> 表内标注净值日期
- C类赎回: 绿电/纳指>=7天免, 其余>=30天免; A类标普1年内0.5%, 科创50>=180天免
"""
import datetime
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fundos_data
from fundos_config import FUND_META, THRESHOLDS

sys.stdout.reconfigure(encoding='utf-8')
BASE = Path(__file__).resolve().parent
TODAY = datetime.date.today()
REPORT = BASE / 'daily_check_{0}.md'.format(TODAY.strftime('%Y-%m-%d'))
RESULT = BASE / 'daily_check_result.json'


def fetch_nav(code):
    """净值获取（数据层带重试+备源）。返回 (date, nav, chg) 或 (None,)*3。"""
    try:
        nav = fundos_data.fetch_fund_nav(code, use_cache=False)
        return nav["date"], nav["nav"], nav["day_chg"]
    except fundos_data.DataError:
        return None, None, None


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

    for code, meta in FUND_META.items():
        cost_nav = meta['cost_nav']
        nav_date, nav, chg = fetch_nav(code)
        if nav is None:
            out('!! {0} {1} 净值获取失败'.format(meta['name'], code))
            continue
        ret = nav / cost_nav - 1
        est_value = meta['cost'] * (1 + ret)
        total_v += est_value
        if meta['sector'] == 'tech': tech_v += est_value
        elif meta['sector'] == 'qdii': qdii_v += est_value
        else: green_v += est_value

        flags = []
        if ret <= THRESHOLDS['hard_stop']:
            flags.append('HARD_STOP')
        elif ret <= THRESHOLDS['eval_line']:
            flags.append('EVAL_15')
        if ret >= THRESHOLDS['take_profit_2']:
            flags.append('TP20')
        elif ret >= THRESHOLDS['take_profit_1']:
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
        a_code = meta.get('a_code')
        switch_th = meta.get('switch_th')
        if a_code and switch_th is not None and ret >= switch_th:
            if not flags:
                advice = '换A {0} (分批<=1/3, 间隔>=1周)'.format(a_code)
            else:
                advice += '; 换A {0}'.format(a_code)
            penalty = meta.get('penalty')
            if penalty and TODAY < datetime.date.fromisoformat(penalty):
                advice += '; 近30天批次未满(赎回费0.5%), 换仓避开'

        flag_txt = '/'.join(flags) if flags else '-'
        rows.append({
            'name': meta['name'], 'code': code, 'class': meta['cls'],
            'nav_date': nav_date, 'daily_change_pct': chg,
            'ret_pct': ret * 100, 'flag': flag_txt, 'advice': advice,
            'cost': meta['cost'], 'weight': 0, 'sector': meta['sector'],
            'value': est_value,
        })
        if flags or (a_code and switch_th is not None and ret >= switch_th):
            actions.append('{0} {1} [{2}] {3}'.format(
                ('🔴' if 'STOP' in flag_txt else '🟢' if 'TP' in flag_txt else '🟡'),
                meta['name'], code, advice))

    # 权重按市值重算（9 只全量后才准确）
    for r in rows:
        r['weight'] = round(r['value'] / total_v * 100, 1) if total_v else 0

    total_cost = sum(m['cost'] for m in FUND_META.values())
    total_ret = total_v / total_cost - 1 if total_cost else 0
    tech_w = tech_v / total_v * 100 if total_v else 0
    qdii_w = qdii_v / total_v * 100 if total_v else 0

    out('## 一、净值与触发状态')
    out('')
    out('| 基金 | 代码 | 类别 | 净值(日期) | 日涨跌% | 收益率% | 触发 | 建议 |')
    out('|---|---|---|---|---|---|---|---|')
    for row in rows:
        nd, chg, ret = row['nav_date'], row['daily_change_pct'], row['ret_pct'] / 100
        ft, adv = row['flag'], row['advice']
        chg_t = '{0:+.2f}'.format(chg) if chg is not None else '-'
        out('| {0} | {1} | {2} | {3} | {4} | {5:+.2f}% | {6} | {7} |'.format(
            row['name'], row['code'], row['class'], nd, chg_t, ret * 100, ft, adv))
    out('')
    out('## 二、组合状态')
    out('')
    out('- 估算总市值: **¥{0:,.0f}** | 总盈亏: **{1:+.1f}%**'.format(total_v, total_ret * 100))
    out('- 科技/AI 占比: **{0:.1f}%** (目标<=40%) {1}'.format(tech_w, '⚠️超配' if tech_w > THRESHOLDS['tech_max'] else '✅'))
    out('- QDII 海外占比: **{0:.1f}%** (目标<=40%) {1}'.format(qdii_w, '⚠️超配' if qdii_w > THRESHOLDS['qdii_max'] else '✅'))
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

    payload = {
        'schema_version': 'fundos.daily_check.v1',
        'checked_at': datetime.datetime.now().astimezone().isoformat(),
        'holdings': rows,
        'total_value': total_v,
        'total_ret_pct': total_ret * 100,
        'tech_weight': tech_w,
        'qdii_weight': qdii_w,
        'actions': actions,
    }
    # 原子写入: 先写临时文件再 replace，引擎并行时不会读到半截 JSON
    tmp = RESULT.with_suffix('.json.tmp')
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
    os.replace(tmp, RESULT)
    REPORT.write_text('\n'.join(lines), encoding='utf-8')
    print('')
    print('报告已保存: {0}'.format(REPORT))


if __name__ == '__main__':
    main()
