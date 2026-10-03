---
name: feedback-assert-silent-skip
description: 断言/检查用 for 循环 + if 条件匹配时，条件永不匹配会静默假绿（断言没执行也不报错）
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 0a5586ed-6aaf-4c7d-bf0b-ec610b190d95
  modified: 2026-08-20T14:15:51.053Z
---

断言/验证脚本里，凡是「for 遍历候选 + if 条件命中才执行断言」的写法，**条件永不匹配时断言静默跳过**——脚本正常 exit 0，看起来全绿，实际该断言根本没跑。这是假绿的最大来源之一。

2026-08-10 事故：S1a verify_paper_numbers.py 里 G-SM f3 效应量断言写 `for k,v in pairwise_wilcoxon.items(): if "G-BL_vs_G-SM" in k and "f3" in k:`。但 `statistical_results.json` 的 pairwise 键只有 `G-BL_vs_G-SM`（HV 维度，无 f3 后缀），条件永不匹配 → 断言 0 次执行 → 论文 §6.2 的 δ=0.91（应为 1.0）没被断言抓到，是我手动重算发现。同脚本早期还有 `k[2:3]` 截串错位导致 stats 空但报错（崩溃式，反而显眼）；静默跳过比崩溃更危险——不报错。

**Why**：断言引擎的价值在「必须执行」。一个没执行的断言等于没有断言，但脚本输出"全绿"给了虚假安全感，且后续轮次会继续信任它。
**How to apply**：
1. 断言脚本显式统计「预期断言数 vs 实际执行数」，两者不等 → FAIL（exit 非0）。例如注册表式断言（每条 record 自带执行标记），跑完比对计数。
2. 用 `if key in data` 精确判键，别用 `substr in key` 猜键（键名带后缀维度时尤其容易漏）。
3. 修完断言后做一次「反向测试」：故意把期望值改错，确认断言真的会 FAIL——断言能被错误触发，才证明它在执行。见 [[feedback-verify-hardcoded-numbers]] 的 M-F1。
4. 审查脚本输出时 grep 断言 ID 是否真实出现在结果集（verify_paper_numbers_report.json 的 results 数组每个断言一条）。
5. 「文件缺失」分支禁走带容差的数值 check()：verify 的 p4 控制曾写 `else: check(paper=1, data=0, tol=1)` → `|0-1|<=1` 假 PASS，删文件/路径错/拼写错都绿灯。缺失输入必须 `N_FAIL+=1` + 显式 FAIL（f0c80d8 已修，反向测试：删文件确认 exit 1）。原则：分支判定存在性用布尔/FAIL，不要把"缺失"编码成一个能落进容差带的数值。

**变体追加（2026-09-30 paper2 审查轮实证）**：审计/验证脚本「打印汇总但不设退出码」是同一故障族——rederive_check.py 85 检查 print 后裸结束恒 exit 0，subagent 报"exit 0"作证据是空信号（5 个 FAILED 照样 exit 0）；且 subagent 自述「fixups 已解决全部 FAIL」与实跑不符（2 FAIL 残留 + 一处脚本自身 format 崩溃）。防线：①检查脚本结尾 `sys.exit(1 if FAIL else 0)`；②消费子代理验证结论时主线程必自跑计数（grep -c FAILED/PASS），不信自述 tallies；③发现计数与自述矛盾时逐脚本读退出逻辑。见 feedback-root-cause-and-lateral-sweep 主线程验证纪律。

**变体追加（2026-10-01 记忆 GC 工具审查实证）**：断言/守卫**构造上不可能失败**时，与"不执行"等价。
`assert sec in original`（sec 本身从 original 切出）就是恒真式，独立复核一眼判 "unreachable"；同批还有
"只护一半资源"的半盲守卫——只护 `.bak` 不护归档件，重跑照样静默覆盖旧归档。防线：①每写一条守卫/断言，
自问"什么输入能让它 FAIL"，答不出就是恒真式，删掉换真校验（本轮改成写入后逐字节 read-back）；
②同一批资源要么全护、要么显式写明只护哪一个；③这类缺陷自审抓不到，靠独立复核 + 复现脚本兜底。

**变体追加（2026-10-01 文件锁实证）**：断言"结果对"，不等于验证了"机制跑过"。给记忆库写的竞态测试只断言
"追加的 marker 是否存活"，而"被锁挡住"这条分支**一次都没触发**——机制完全没生效，测试依然全绿；
是独立复核用自建窗口脚本才打出来。补法：**验证某机制的测试必须至少有一例断言该机制的直接证据**
（这里 = appender 收到 `PermissionError`），并显式检查"预期触发的分支是否真触发过"（计数或断言分支命中）。
