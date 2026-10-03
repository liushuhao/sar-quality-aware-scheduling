---
name: feedback-measure-both-switch-paths
description: 有开关/分支的代码，禁用一个分支的读数推断另一分支——先测两侧再下结论
metadata:
  node_type: memory
  type: feedback
  originSessionId: d0f5ed3f-b55c-4299-bd18-892a682b9298
  modified: 2026-10-01T00:36:42.596Z
---

**代码有 flag/分支时，下"某量如何缩放"的结论前必须**分别**测两侧。**

**Why**：2026-10-01 paper2 会话，我主张「g_T 是冗余项、f_Q 的 1/ρ_a² 律全部来自
ρ_a,ach、D05-5『双重加权』声明不成立」，并写进处置件、准备改预注册。gate-review
实测推翻：

```
f_Q(SLS)/f_Q(SPT) @12°：g_T ON = 0.359909   g_T OFF = 0.600000
ρ_STR/ρ_SLS = 4.933803   (…)² = 24.342414
```

`g_T OFF` 时比值 = ρ_SPT/ρ_SLS ⇒ 净**一次方**；`g_T ON` 时 ≠ 一次方
⇒ **1/ρ_a² 律恰恰由 g_T 提供**。我把 OFF 路径的幂次当成了 ON 路径的，
结论方向完全反了。原拟的 prereg amendment 撤销。

**How to apply**：
- 见到 `g_t_enabled` / `enabled` / `use_x` 这类开关，**先各跑一次**，把两侧读数并列，
  再谈缩放/幂次/是否冗余。
- 自查句式：「我这个结论是从哪一次运行的读数来的？那个读数对应的开关状态是什么？」
  两者不一致就是错的。
- 冗余性/恒等式类主张（"X 携带零额外信息"）是高危结论——它们只在一个分支上成立时
  极易误判；必须给出两侧数字才算证据。
- 独立二审能抓住这类错（本次由 gate-review 的实测抓到），所以**主线程的理论判断也必须
  进独立审**，不能以"我自己推过"免审。

相关 [[feedback-premise-laundering]] [[feedback-independent-review-three-lines]]。
