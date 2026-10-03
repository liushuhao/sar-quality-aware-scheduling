---
name: feedback-verifier-shares-failure-surface
description: 交接/审计工件里每条「某文件有某内容」必须本轮打开文件 grep 到那一行——凭笔记填=二手快照（七轮审查 45 处发现全出在这）；含 rtk 假零绿与长句局部替换留残句两个同族
metadata:
  node_type: memory
  type: feedback
  originSessionId: 6eadc7ce-9c13-4ecb-96ec-a0d5e685e2bc
  modified: 2026-10-02T00:09:57.749Z
---

**规则**：写交接件（goal 卡 / brief / spec / 记忆）时，凡出现「某文件里有某内容 / 某键在某路径下」，必须**本轮打开该文件、grep 到那一行**才可写。凭上一轮笔记 / 记忆 / 上一版自己的措辞 = 重犯。

**Why**: 2026-10-02 paper2 goal 卡，七轮 11 路异源模型审查共 45 处发现，**全部**属「未核即写」及其变体。同根犯五次：
1. 抄计划步骤（首版把票链凭记忆写成 21→15→16→17，漏了票 22——而 `Blocked by` 字段明写 17 = 16 + 22）
2. 抄 prereg 键名 → 两条指针双双落空：`escalation_rule` 实际在 `scope` 下不在 `pre_declared_criteria`；`binding_rule` 实际在 `amendment_20260930_audit2_r1_redline` 下不在 `convergence_calibration`。**后者是全卡最吃重的安全锚**，挂错 amendment 名 = agent grep 落空
3. 抄 ADR 位置（凭印象写 `.scratch/`，实测在 `reference/adr/`）

**同族三变体**（一个根：**用来确认的东西和出错的东西是同一个**）：
- **验证器自身坏**：`rtk` 包装 `python`，整目录 pytest 被压成 `Pytest: No tests collected` + **exit 0**。实测 `python -m pytest src/tests/ --co -q` 假零 vs 绝对解释器 `145 tests collected`。agent 没撒谎，是被工具骗——**机器诱导的假绿比 agent 撒谎难防**。同族已有 [[feedback-rtk-pipeline-count-pollution]]（污染 `git status` 计数）
- **局部替换 = 半个修复**：长句 `Edit` 的 `old_string` 只覆盖新句片段，旧括号残留拼出 `X（…）X…` 双前缀。自查看的是 diff 视图不是改后整句 → **长文稿编辑后必须机器 grep 关键 token 计数**（`grep -o "五族\|六族" \| sort \| uniq -c`）

**How to apply**:
- 交接件写完，每条事实性引用回查一遍源文件；查不到的写 `「待核：…」` 占位，不许编
- **自检不能替代独立审**：七轮里每轮我都自查过，全部发现由外部审者抓出。且**单人审会漏**——两条独立命中才暴露指针错误（confirm-round 与 fresh-agent-sim 各抓一条不同键位）。**dry-run 模拟接收方**比静态审计值钱：它专报「我照卡 grep 落空了」这类静态审者不会构造的失效
- **审核计数类数字时先核验证路径**：本域测试实测 134 collected，而我早前实测「127 passed + 1 skipped」是**执行数**——两数都对但语义不同。卡里索性不写死数字，只写「计数以 `--co` 实测为准」+ 点名两个互不相交的测试面（`不写死数字 ≠ 不指名测试面`）
- 与 [[feedback-stale-snapshot-audit]] 同源（过期快照制造假发现）在交接工件上的新实例；与 [[feedback-negative-existence-claims]]、[[feedback-premise-laundering]] 同族
