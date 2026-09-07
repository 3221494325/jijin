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
console.log("Dashboard rendering contract checks passed");
