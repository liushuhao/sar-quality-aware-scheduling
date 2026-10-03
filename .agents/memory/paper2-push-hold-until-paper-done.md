---
name: paper2-push-hold-until-paper-done
description: paper2 commits 一律不推 GitHub，等论文写完再推；收尾报告不再列 push 为待办或风险
metadata:
  type: project
---

**paper2 的 commits 不推 GitHub。等论文写完再推。收尾报告里不要再把 push 列为待办/风险/待决事项。**

**Why**：2026-10-01 用户明令。remote `sar-quality-aware-scheduling` 是**公开仓**，
现仅含 9 个 paper2 文件；32 个未推 commit 全是 `papers/sliding-spotlight-scheduling/`
下的未发表研究代码与实验工件。推 = 发布未发表工作。本地 git 已足够安全（树净、commit 在库），
无需异地备份的紧迫性。

**How to apply**：
- 收尾报告**不再出现**「N commits 未 push」「需用户终端 push」这类行——这是既定决策不是待办。
- 不主动问「要不要 push」，不在待办清单里列它。
- 论文写完（或用户另行指示）时才重启该话题。
- 沙箱对 `git push` 是策略级硬拒，本来也推不动——不必再试探。
- 相关背景（公开仓边界）见 github-push-hygiene-and-schannel、feedback-bash-push-permission-boundary。

**注**：paper1/Ch3 侧的 push 不受此令影响（那是已发表/已投稿工作，2026-09-25 已推）。
