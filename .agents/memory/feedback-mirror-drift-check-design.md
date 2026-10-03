---
name: feedback-mirror-drift-check-design
description: closeout-sweep 镜像差检查的噪声根因与修法——比较前须归一化 frontmatter/链接括号，否则每轮 20+ 假 NOTE 训练人忽略告警
metadata:
  node_type: memory
  type: feedback
  originSessionId: d0f5ed3f-b55c-4299-bd18-892a682b9298
  modified: 2026-10-01T01:01:39.401Z
---

**镜像检查要在比较前归一化掉「设计差异」，否则告警会被噪声淹没。**

**Why**：2026-10-01 收工三扫长期报 26 条 `镜像差` NOTE。用户问「NOTE 是什么，是警告吗」
并说「不想看到总有 NOTE」。查根因：`closeout-sweep.py:mirror_drift` 裸比行数，
把两类**设计差异**算成漂移——

1. **YAML frontmatter 折行**（长 description 在某侧被折行；且各库 metadata 字段本就不同：
   `originSessionId`/`modified`）
2. **链接括号**：双工具双写约定下，镜像库对「本库不存在的目标」按惯例去括号
   （双方括号链接退化为裸文件名），故「双方括号包裹的名字」与「裸名字」必须归一为同一物

26 条里 16 条是纯噪声。**代价不是多看一眼，是训练人忽略告警**——真漂移会藏进去。
修后同一命令只剩 10 条，且全部是真差异（随后逐条修净 → 0）。

**修法**（`_mirror_body`）：剥 frontmatter → 把双方括号字符对替换为空串 → 折叠空白
→ 比正文。**注意踩过的坑**：一度改成「整体删双方括号词元」，结果包裹版变空串、
裸词版仍是裸词，两侧反而不等——**只剥括号字符才对**（两种形式都归一为裸名）。
链接**目标名**不同仍会报（正确：那是真分歧）。
另加 `<repo_mem>/.mirror-known-diff`（每行一个 basename）供声明纯设计差异。

**How to apply**：
- 任何「比对两个来源」的检查，先列出**预期差异类别**并在比较前归一化；只让未预期的差异报警。
- 告警分级要可解释：`[TAIL]`=FAIL 计退出码，`[NOTE]`=人工判读。**NOTE 长期不清零 =
  检查已失效**，要么归一化要么声明抑制，别让它常态化。
- 改全局工具（`~/.agents/scripts/`）前先备份；改后**在另一个项目跑一次回归**确认不崩。

**顺带修净的真漂移**（工具修好后暴露，非本次引入）：repo 侧 `paper2-spec-v05-cycle-20260930`
的 How-to-apply 停在「开工票 18」（实为票 15）；`paper2-implementation-batch-closed` 数字
118+1 旧于 124+1；zcode 侧 `paper2-deferred-debts` 第 5/6 项仍写「待决策」（2026-09-29 已裁）；
同一记忆 `next-paper-squint-duration`（repo）/`project-next-paper-squint-duration`（claude）
两库两名两内容 → 合并为 claude 超集版 + 统一名。

相关 [[feedback-rtk-pipeline-count-pollution]] [[feedback-instrument-measurement-traps]]。