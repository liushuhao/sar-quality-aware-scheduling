---
name: feedback-frozen-artifact-byte-identity
description: 脚本修改冻结工件（prereg/spec/注册件）必须字节保持——json.dumps 往返会破坏格式，且断言必须比冻结前缀的字节
metadata:
  node_type: memory
  type: feedback
  originSessionId: d0f5ed3f-b55c-4299-bd18-892a682b9298
  modified: 2026-10-01T00:36:40.111Z
---

**改冻结工件的脚本，禁用 `json.dumps` 往返，改用文本插入 + 断言冻结前缀字节。**

**Why**：2026-10-01 paper2 加 amendment 到 `analysis_prereg.json` 时，
`json.load` → 改 dict → `json.dumps(indent=2)` 回写，把原文件里 Prettier 风格的单行对象
（`{"pop": 40, "gen": 60, ...}`）展开成多行 ⇒ diff 成 `29 insertions / 3 deletions`。
原文件的 append-only 纪律要求**冻结字段字节不变**（不只是语义相等），且该仓有
「byte-compare 拒 resume」规则，真按字节比对会炸。三次尝试才定案。

**How to apply**：
1. 读原文件**字节**（`read_bytes`），检测换行风格（CRLF/LF），保留。
2. 在末尾闭合括号前**插入文本**构造新块，不整体重序列化。
3. 断言分两层：① 冻结前缀的**字节切片**不变（`after[:len] == before[:len]`）；
   ② 逐字段 `json.dumps` 语义相等。只做②漏掉格式漂移。
4. 断言本身也要对——首次断言写成 `before_keys == [k for k in after if not startswith(amendment)]`，
   左边含原有 amendment 键、右边过滤掉全部 ⇒ 恒假。比之前先想清比较对象。
5. 验证判据 = `git diff --numstat` 的 **deletions == 0**（纯追加）。

同一模式的其他实例：本仓 `scripts/run_*.py` 只写运行产物（progress 文件），用
`atomic_write_json`（tmp+fsync+os.replace）是合适的——**冻结件与运行产物的写策略不同**，
勿混用。全仓 grep 确认无第二处改冻结注册件。

相关 [[feedback-premise-laundering]]。
