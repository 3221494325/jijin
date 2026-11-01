// Offline rendering contract checks: node tests/test_dashboard.cjs
const fs = require("node:fs");
const vm = require("node:vm");
const assert = require("node:assert/strict");
const path = require("node:path");
const html = fs.readFileSync(path.join(__dirname, "../dashboard.html"), "utf8");
const elements = {};
for (const [, id] of html.matchAll(/id="([^"]+)"/g)) {
  assert.ok(!elements[id], "duplicate id: " + id);
  elements[id] = {innerHTML:"", textContent:"", style:{}, value:"value"};
}
const context = vm.createContext({console, document:{getElementById:id=>{assert.ok(elements[id], id); return elements[id];}}, window:{addEventListener(){}}, setInterval(){}, fetch:async()=>({ok:true,json:async()=>({})})});
vm.runInContext(html.split('<script>')[1].split('</script>')[0], context);
vm.runInContext("draw({})", context);
assert.ok(elements.cards.innerHTML.includes("¥—"));
assert.ok(!elements.cards.innerHTML.includes("NaN"));
context.sample = {portfolio:{as_of:"2026-09-01",total_value:200.08}, holdings:[{name:"B",value:10,weight:10,ret_pct:3,sector:"<tech>",nav_date:"2026-09-01",today_source:"QDII滞后"},{name:"A",value:90,weight:90,ret_pct:-2,sector:"<tech>"}],guide:{directives:[{level:"观察",title:"watch"},{level:"指令",title:"priority",action:"act",evidence:"e",boundary:"b"}]}};
vm.runInContext("draw(sample)", context);
assert.equal(elements.focusTitle.textContent, "指令 · priority");
assert.ok(elements.dataStatus.textContent.includes("明示滞后 1 笔"));
assert.ok(elements.exposure.innerHTML.includes("&lt;tech&gt;"));
assert.ok(elements.cards.innerHTML.includes("200.08"));
assert.ok(elements.holdTable.innerHTML.indexOf("<b>A</b>") < elements.holdTable.innerHTML.indexOf("<b>B</b>"));
elements.holdSort.value = "ret_pct";
vm.runInContext("draw(sample)", context);
assert.ok(elements.holdTable.innerHTML.indexOf("<b>A</b>") < elements.holdTable.innerHTML.indexOf("<b>B</b>"));
vm.runInContext("draw({llm_status:{configured:true}})", context);

// ---- v4：体检 / 绩效 / 相关性 / 盈亏贡献 的渲染契约 ----
context.v4 = {
  build: "cockpit-xray-v4",
  market: {session:"weekend", label:"休市 · 周末", is_trading_day:false, in_session:false,
           data_day:"2026-10-30", data_day_label:"最近交易日 2026-10-30"},
  actions: ["🔴 示例标的 当日无条件出清"],
  actions_meta: {state:"stale", label:"2026-10-29 盘后核验", date:"2026-10-29"},
  portfolio: {total_value: 1000, est_ret_pct: -1, total_ret_pct: -5},
  holdings: [{name:"A", code:"1", value:600, weight:60, ret_pct:-30, breakeven_pct:42.9, sector:"tech", nav_date:"2026-10-30"}],
  xray: {score: 41, grade: "需处置", summary: "示例结论",
         counts: {total:2, evaluated:2, pass:1, warn:0, fail:1, na:0},
         rules: [{name:"QDII 海外敞口", status:"fail", status_label:"不通过", value_text:"47.6%",
                  limit_text:"≤ 40%", evaluation:"说明", action:"动作", weight:2},
                 {name:"有效基金数", status:"pass", status_label:"通过", value_text:"5.9 只",
                  limit_text:"≥ 4 只", evaluation:"说明", action:"动作", weight:1}]},
  perf: {window_days: 120,
         curve: {dates:["2026-10-29","2026-10-30"], nav:[0.99,0.97], drawdown_pct:[-1,-3]},
         monthly: [{month:"2026-09", ret_pct:-2.27},{month:"2026-10", ret_pct:-10.85}],
         corr_matrix: {labels:["A","B"], values:[[1,0.9],[0.9,1]]}},
  contribution: [{name:"A", code:"1", pl:-100},{name:"B", code:"2", pl:20}],
  contribution_total: -80,
};
vm.runInContext("draw(v4)", context);
assert.equal(elements.marketLabel.textContent, "休市 · 周末");
assert.ok(elements.marketDay.textContent.includes("最近交易日"));
assert.equal(elements.xrayScore.textContent, 41);
assert.equal(elements.xrayGrade.textContent, "需处置");
assert.ok(elements.xrayGrid.innerHTML.includes("QDII 海外敞口"));
assert.ok(elements.xrayGrid.innerHTML.includes("不通过"));
assert.ok(elements.xrayCounts.innerHTML.includes("不通过 1"));
assert.ok(elements.buildTag.textContent === "build cockpit-xray-v4");
assert.ok(elements.alertBox.innerHTML.includes("上一交易日"), "陈旧号外必须带日期提示");
assert.ok(elements.perfKpi.innerHTML.includes("最大回撤"));
assert.ok(elements.perfKpi.innerHTML.includes("-3.00%"), "当前回撤应取曲线末值");
assert.ok(elements.perfMeta.textContent.includes("2个交易日"));
assert.ok(elements.monthHeat.innerHTML.includes("2026-10"));
assert.ok(elements.corrNote.innerHTML.includes("0.90") || elements.corrNote.innerHTML.includes("≥0.85"));
assert.ok(elements.contribNote.innerHTML.includes("-80.00"));
assert.ok(!elements.xrayGrid.innerHTML.includes("undefined"));
assert.ok(!elements.perfKpi.innerHTML.includes("NaN"));

// ---- v5：粘性摘要条、回本距离、体检分趋势、环球市场栅格 ----
assert.equal(elements.sbValue.textContent, "¥1,000.00");
assert.equal(elements.sbRet.textContent, "-5.00%");
assert.equal(elements.sbScore.textContent, "41");
assert.ok(elements.sbMarket.textContent.includes("2026-10-30"));
assert.ok(elements.holdTable.innerHTML.includes("回本需 +42.9%"), "亏损标的应显示回本所需涨幅");
assert.ok(elements.idxTable.innerHTML.includes("idx-grid"));
// 体检分趋势：只有 1 天时只能显示"积累中"，不得画假曲线
context.hist1 = [{date:"2026-10-30", score:41}];
vm.runInContext("draw({xray:v4.xray, xray_history:hist1})", context);
assert.ok(elements.xrayTrend.innerHTML.includes("积累中"));
assert.ok(!elements.xrayTrend.innerHTML.includes("<svg"));
// 两天以上才出折线
context.hist2 = [{date:"2026-10-29", score:35}, {date:"2026-10-30", score:41}];
vm.runInContext("draw({xray:v4.xray, xray_history:hist2})", context);
assert.ok(elements.xrayTrend.innerHTML.includes("<svg"), "满两天应渲染趋势折线");
assert.ok(elements.xrayTrend.innerHTML.includes("35 → 41"));

// 空数据不得抛错，也不得渲染出 undefined
vm.runInContext("draw({xray:{},perf:{},contribution:[]})", context);
assert.ok(elements.xraySummary.textContent.includes("暂无体检数据"));
assert.ok(elements.perfKpi.innerHTML.includes("—"));
console.log("Dashboard rendering contract checks passed");
