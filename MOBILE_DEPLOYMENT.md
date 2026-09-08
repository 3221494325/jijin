# FundOS 手机访问方案

## 推荐架构：GitHub Actions + 静态快照

这套方案不需要云服务器，也不要求电脑开机：GitHub Actions 在云端定时运行 FundOS，生成 mobile_site/data.json，GitHub Pages 提供手机页面。电脑关机后，手机仍能打开最近一次成功生成的快照。

### 成本与限制

- GitHub Actions 对公开仓库通常有免费额度；私有仓库也有额度，以 GitHub 当前账户规则为准。
- 这是定时快照，不是实时 API。手机刷新显示最近一次快照。
- GitHub Pages 不适合直接承载含金额的私人持仓，也不能安全提供任意访客调用的 AI 按钮。

### 当前隐私边界

当前仓库与 Pages 为公开部署，手机快照会发布组合市值、盈亏、基金代码和持仓金额。这不是私密方案；不接受公开个人财务数据时，应先改为私有数据服务。

### 配置步骤

1. 将 GitHub 仓库设为 Private，或先只手动运行 Actions，不打开 Pages。
2. 在 Settings → Secrets and variables → Actions 添加 FUNDOS_LLM_API_KEY；可选添加 FUNDOS_LLM_BASE_URL、FUNDOS_LLM_MODEL。
3. Actions 中手动运行 FundOS mobile snapshot；工作流会自动构建并部署 Pages artifact。第一次运行前，在 Settings → Pages 中将 Source 设为 GitHub Actions。
4. 用手机打开 Pages 地址。AI 研判是定时生成后展示，不是手机即时调用；密钥只在 Actions 服务端使用。

## 第二阶段：需要手机即时 AI 时

再增加一个带认证的在线函数（如 Cloudflare Workers/Pages Functions、Vercel Functions，或 NAS 上的 Tailscale 服务），只提供 /api/ai；密钥放函数环境变量，网页使用短期登录令牌。不要把密钥写入 dashboard.html、data.json 或 Git 历史。

## 本地验证

python export_mobile_snapshot.py
python -m http.server 8000 --directory mobile_site

## 电脑同步到手机

电脑看板刷新不会自动上传。确认本地数据无误后运行 sync_mobile_snapshot.py。只有数据发生变化时才提交并推送；推送失败不会覆盖手机端上一版快照。

本地验证只证明静态页面可用；电脑关机后可用必须先完成 GitHub Actions + Pages 部署。工作流失败时不会覆盖上一次成功部署。
