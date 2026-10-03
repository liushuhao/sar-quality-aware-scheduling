---
name: bash-classifier-backend-gotcha
description: "Bash 全卡 = 安全分类器后端挂, 非本地问题; 换 _NAME 或代理热改"
metadata: 
  node_type: memory
  type: reference
  originSessionId: f428cc33-b71d-4225-8d10-001382e03f92
---

Bash 在 auto 权限模式下每条命令先过**安全分类器**(硬门槛)。分类器跑 Opus 层模型，经本地代理 `127.0.0.1:15721` 路由到实际后端(由 `~/.claude/settings.json` 的 `ANTHROPIC_DEFAULT_OPUS_MODEL_NAME` 决定)。

**症状**: 任何 Bash 调用报 `claude-opus-4-8[1m] is temporarily unavailable, so auto mode cannot determine the safety`。只读工具(Read/Grep/Glob)正常(不走分类器)。

**根因**: 分类器后端瞬时故障/限流。**非本地配置问题**。

**已验证**: allowlist 里的命令(如 `Bash(git *)`)照样卡 → **加白名单不绕分类器**, 别浪费时间改 allowlist。

**换法**(2026-07-21 实战: qwen3.8-max-preview 挂 → 换 glm-5.2 起死):
1. 改 `ANTHROPIC_DEFAULT_OPUS_MODEL_NAME` 指健康后端 → 重启 Claude Code(env 启动读, mid-session 改不生效)。
2. 代理若动态路由, 热改代理把 `_NAME` 指健康后端 → 立即生效, 不用重启(更快)。

四 tier(Opus/Sonnet/Haiku/Fable)的 `_NAME` 常全指同一后端, 一并换更稳。`_MODEL` 是 harness 认为用的逻辑名, `_NAME` 是代理实际路由的后端名。关联 [[figure-tooling-setup]]。

### 2026-08-02 实战: qwen3.8-max-preview 单独抖，换 3.7-plus 根治

**现象重现**: auto 模式 `claude-opus-4-8[1m] is temporarily unavailable ...` 间歇报，doubao/deepseek 走同 gateway 无事。

**诊断**:
- 用户 A/B 锁：问题在 qwen 路径，不在 gateway / relay 架构。
- gateway 15721 探测：无论请求模型传什么（`deepseek-v4-flash` / `doubao-seed-evolving` / `glm-5.2` / `sensenova` / `qwen3.8-max-preview`），响应都返回 `"model":"qwen3.8-max-preview"` → **gateway 按 cc-switch 配置的当前后端路由，不按请求模型名**。
- 所以 Claude Code 端单改 `_NAME` 是摆设；必须 **通过 cc-switch 切 provider** 才真正换 gateway 后端。
- `-preview` 后缀 = 预览版，过载/限流高发区。

**修法**:
1. cc-switch 切 Opus 到非 preview 的 qwen（实测 `qwen3.7-plus`）。
2. 验证：连续 6 次 `/v1/messages` 请求 + auto 模式下 6 条 Bash（含 `rm`、`python`、`&&`、`|`）→ 全 200，分类器不抖。

**结论**: 抖是**型号级**（-preview 不稳），非 provider 级（qwen 整 key 没事）。留 qwen + auto 双全。

**复用规则**:
- 分类器报 unavailable，先 A/B：整个 provider 抖 vs 单个型号抖。
- provider 整体抖 → 必须换 provider（doubao/deepseek 等）。
- 单型号抖（带 `-preview` / `-beta` / `-thinking` 等不稳定后缀）→ cc-switch 换同 provider 稳定型号即可。
- 别绕弯：直接改 cc-switch 配置，不要试图只改 Claude Code 端 `_NAME`（那层是摆设，gateway 不按它路由）。
