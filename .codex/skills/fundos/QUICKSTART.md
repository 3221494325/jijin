# FundOS Quick Start（总裁版）

> 项目级技能：仅 `D:\基金项目` 使用。人格：**总裁**（详见 persona.md）。
> 所有分析按"总裁批示"输出：形势研判 → 持仓体检 → 执行指令 → 风控边界 → 免责声明。

## 5分钟上手

### 1. 导出持仓
支付宝 → 理财 → 基金 → 持仓 → 右上角导出Excel → 保存到桌面

### 2. 生成第一份报告
```powershell
python "D:\基金项目\.codex\skills\fundos\scripts\portfolio_report.py" --holdings "C:/Users/lzf13/Desktop/基金持仓与收益统计_2026.07.30.xlsx"
```

### 3. 搜板块新闻
```powershell
python "D:\基金项目\.codex\skills\fundos\scripts\news_fetch_v2.py" --mode quick
```

### 4. 一键日报
```powershell
python "D:\基金项目\.codex\skills\fundos\scripts\scheduler.py" --run
```

### 5. 交互式菜单
```powershell
python "D:\基金项目\fundos_console_v2.py"
```

## 日常命令速查

| 想做什么 | 命令 |
|----------|------|
| 持仓诊断 | `portfolio_report.py --holdings 持仓.xlsx` |
| 搜新闻 | `news_fetch_v2.py --mode quick` |
| 搜单板块 | `news_fetch_v2.py --sector 半导体` |
| 更新净值 | `nav_update.py` |
| 基金对比 | `fund_compare.py` |
| 定投计算 | `aip_calc.py --amount 1000 --period monthly --years 3` |
| 新建模块 | `scaffold.py data-provider my-source` |
| 一键日报 | `scheduler.py --run` |
| 定时任务 | `scheduler.py --setup` (需管理员权限) |

## Codex 对话

在 Codex 中直接说：
- "分析我的持仓"
- "搜半导体最新消息"
- "生成持仓诊断报告"
- "对比我的基金表现"
- "算一下定投收益"
- "配置止盈线到20%"

## 配置你的阈值

编辑 `C:\Users\lzf13\.fundos\config.json`:
```json
{
  "thresholds": {
    "profit_alert": 0.15,
    "loss_alert": -0.10,
    "valuation_percentile": 20,
    "single_fund_max_ratio": 0.30,
    "equity_ratio_min": 0.30,
    "equity_ratio_max": 0.80
  }
}
```

## 自动化 (可选)

```powershell
# Windows定时任务：每天18:00自动生成日报
python "D:\基金项目\.codex\skills\fundos\scripts\scheduler.py" --setup
```
