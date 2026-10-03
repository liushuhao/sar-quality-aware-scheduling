---
name: paper2-ticket12-double-chain-catch
description: 票 12 双链对账实抓票 10 评估器 C2 链 index 序缺陷（幻影违规 gap −200 s）——锚种子
  交叉核对方法论与修复记录（2026-09-27）
metadata:
  node_type: memory
  type: project
  originSessionId: sess_784932fb-489f-4579-aae8-de9efb9c1a72
---

票 12 verify 门禁的锚交叉核对（rule 11 双链）实抓票 10 真缺陷：evaluator 的 C2/冲突链按 plan **index** 序迭代而非 **start 时间**序——索引相邻 ≠ 时间相邻，对时间倒置的选中对产生幻影违规（gap = −200 s 量级，种子个体 CV=729）。锚按时间序检查所以自洽，评估器不一致——两个独立解路径（贪婪插入 vs GA 演化）对账使缺陷可见。修复：C2/冲突链按 start 时间序迭代（evaluator.py）；修复后 pilot 前沿 max f1* 0.2824 → 0.8931 == 锚值，search-only 0.6641 留档。

**Why:** (1) 跨链对账不是仪式：同源谓词 + 不同搜索机制的两条解路径对账，恰好质询了单链测试测不到的「解语义」层（单链测试全绿、缺陷藏在遍历序）。(2) 锚种子进初始种群（measure-accumulated 反解 + round-trip 断言 + CV/f1 双检 fail-loud）同时完成三件事：对账上限、机制验证、缺陷探针。(3) 幻影违规曾把 NSGA-II 搜索压到 0.2824——「优化器弱」与「评估器错」表象相同，无独立锚就无法归因。

**How to apply:** 任何「优化器 + 贪婪/构造锚」双实现组合，锚解必须编码进初始种群并在构造时断言（a）反解 round-trip（b）锚解在评估器下 CV=0（c）前沿 max f1* ≥ 锚 − ε；三条任一红即评估器语义缺陷信号，先查遍历序与需求计算基准。相关 [[paper2-implementation-batch-closed]]、[[paper2-deferred-debts]]。
