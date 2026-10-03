---
name: feedback-instrument-measurement-traps
description: 三个静默说谎的测量工具——管道后取 $?（拿到 tail 的码）、glob 空后缀匹配全部、跨记忆库拷贝不改编链接
metadata:
  node_type: memory
  type: feedback
  originSessionId: d0f5ed3f-b55c-4299-bd18-892a682b9298
  modified: 2026-10-01T00:38:20.023Z
---

**测量工具本身会静默说谎。下结论前先确认读数来自哪里。**

**Why**：2026-10-01 paper2 会话一次踩三个：

1. **管道后取 `$?`**：`cmd > out 2>&1 | tail; echo "exit=$?"` 里 `$?` 是 **tail** 的退出码。
   首次跑收尾三扫报「exit=0」而脚本其实 **exit=1**。正解：`PIPESTATUS[0]`，
   或先落文件再单独查 `$?`。
2. **glob 空后缀匹配全部**：`glob(f'...seed*{suffix}.json')` 在 `suffix=''` 时匹配**所有**
   预算档文件 ⇒ 把 p80/p160 两组混成一组（n=10 而非 5），得出「P7WH 跨预算持平、
   非单调」的**错误**结论，一度以为推翻了另一路审查的发现。正解：空后缀要显式分支
   （`'_base'` 之类），或先 `ls` 看命中集合再算。
3. **跨记忆库拷贝不改编链接**：把带双方括号 wiki 链接的记忆文件拷到另一套记忆库
   （claude auto-memory / repo `.agents/memory/` / zcode），被引文件不存在侧即产生
   **悬空链接**——收尾三扫的 FAIL 数 9→13。正解：拷完按目标库已有文件集**去括号**，
   再复跑三扫确认回到基线。


4. **在记忆/文档正文里写字面量双方括号当例子**：收尾三扫的悬空链接检查会把例子当成真链接
   （本会话踩两次：写了「双方括号 wiki 链接」的字面样例、以及 `.replace` 里的括号字符对）。
   正解：举例时用文字描述（「双方括号包裹的名字」），或写进代码块并接受被扫描。

**How to apply**：
- 报 exit code 前自问「这个 `$?` 是哪条命令的」；有管道就用 `PIPESTATUS`。
- 写 glob/filter 时自问「空参/缺省参会不会匹配到全部」；先打印命中集合。
- 跨库同步后**必须复跑收尾三扫**，把 FAIL 数对回基线（rule 17：
  FAIL 集合相对基线零新增）。基线要**开工前记**，否则无法判定新增。
- 通用句：**任何"仪器读数"都要先验证仪器**——这一课与 [[feedback-rtk-pipeline-count-pollution]]
  同源（噪声行混进 wc 计数造假数）。

相关 [[feedback-rtk-pipeline-count-pollution]] [[feedback-verify-hardcoded-numbers]]。
