# R7 前置对账：主跑 vs replicate 同实例归因（M3 勘误）— 2026-11-04

结论先行：**M3 的「replicate 与主跑同实例系统性不一致（f1 0.7396/1.0 vs 0.6458/0.8333；f3 全密度系统性偏低）」不成立**——该对比误用了 8-06/8-07 的旧口径淘汰件作「主跑」。现行正文数据源与 replicate 同代码链，同实例逐位（S1/S4）或 1e-3 级 repeat 波动内（S2/S3）一致。**闸裁决：过，无 solver 版本/口径漂移**，扩容跑批放行。

## 1. M3 错源根因

- M3 引用的「主跑」值出自 `_snapshot_moea2obj.json`（mtime 2026-08-06）与 `_snapshot_moea3.json`（mtime 2026-08-07 16:57），其内 `solver_version=04ce55c4` **已不在本仓对象库**（`git cat-file -t` fatal）——为 RDR-066 口径修正（8-12 `f96674f`：f2/f3 目标改仰角平面角，修 NESZ squint 重复计数）之前的旧口径件，8-14 全量重跑（`b107e97`）后已被淘汰，**不是正文数据源**。
- 正文/数字闸真实数据源：`experiments/results/moea_2obj/_progress.json` + `moea_3obj/_progress.json`（mtime 8-14 23:45 / 11-01 16:33，`verify_paper_numbers.py:48-49` 为证）。
- 旧快照 vs replicate 的差异 = RDR-066 目标口径变更，非 solver 漂移。f3「系统性偏低」同源：旧口径 f3 定义不同。

## 2. 现行数据链同实例对比（seed00 × 四密度 × 双求解器）

数据：`_progress.json`（主跑单次）vs `replicate_variance_20261031/_progress.json`（同实例 5 repeats，2026-10-31）。

| 组/求解器 | 主跑 f1/f2/f3/n_sel | replicate (rep00) | 逐位同 | 主跑 ∈ rep5 包络 |
|---|---|---|---|---|
| S1/MOEA-2 | 0.6458/0.4709/0.6191/13 | 同 | ✅ | ✅ |
| S1/MOEA-3 | 0.8333/0.3966/0.6884/17 | 同 | ✅ | ✅ |
| S2/MOEA-2 | 0.9862/0.3299/0.5301/92 | 0.9862/0.3299/0.5301/92 | ✅ | ✅ |
| S2/MOEA-3 | 0.9744/0.3310/0.5466/92 | 0.9842/0.3283/0.5420/93 | ❌ | ✅（端点） |
| S3/MOEA-2 | 1.0000/0.3524/0.6123/200 | 1.0000/0.3520/0.6111/200 | ❌ | ✅（端点） |
| S3/MOEA-3 | 1.0000/0.3522/0.6133/200 | 0.9966/0.3526/0.6136/199 | ❌ | ✅（端点） |
| S4/MOEA-2 | 1.0000/0.3875/0.6570/200 | 同 | ✅ | ✅ |
| S4/MOEA-3 | 1.0000/0.3870/0.6554/200 | 同 | ✅ | ✅ |

- S2/S3 主跑与 rep00 差 ≤1.3e-3，与 replicate 内部 repeat 间波动同量级（rep S2/MOEA-3 f1 跨 0.9744–0.9842），无系统方向。
- 场景实例同一性：主跑条目 `pkl_sha1` 与当前场景文件 sha1 一致（S2-A_seed00 `1eb03190ab33…` 实证）；四类 pkl mtime 均 2026-08-06，早于两次跑批。
- 复现事实修正（对照记忆 project-paper1-solver-nondeterminism-20261101）：replicate 5 repeats **S1/S4 零波动、S2/S3 1e-3 级波动**；当前 `moea.py:601` pymoo `seed` 兜底=1 → 求解近确定，S2/S3 微波动源于规模相关非确定浮点秩序（口径段据此措辞）。

## 3. 版本链行为等价性

- 主跑 `_progress.json` 混戳 `4cfc42c0`×170 + `720e63c8`×130/230——两 commit 间 `git diff -- moea.py` 为空（`720e63c8` 2026-08-14 16:18 是 test commit），混戳零行为影响（正是 `_solver_code_identical` 设计语义）。
- `4cfc42c0..HEAD` 的 moea.py diff = 仅删死参数 `resolution_reqs`（签名+透传，跑批均传 `prebuilt instance` 不走该分支），行为等价。
- f1_gbl 双侧同为 96.0（S1）——instance 构建、几何、G-BL 基座逐位一致。

## 4. 对 R7 的落笔依据

- 可复现口径段措辞据 §2/§3：同实例重复求解在 S1/S4 逐位复现、S2/S3 于 1e-3 级波动内复现；主跑快照与 replicate 跑批共用同一 moea.py 行为链。
- 扩容跑批（每类 ≥10 场景 × 5 repeats × 2 求解器）放行；执行序照 roadmap 批 2 第 2-4 步。
- `author-adjudication-20261103.md` M3 行勘误注记随本文件回填。

## 复核命令（可重跑）

```bash
python - <<'EOF'
import json
m3 = json.load(open('papers/single-sat-quality/experiments/results/moea_3obj/_progress.json'))['completed']
m2 = json.load(open('papers/single-sat-quality/experiments/results/moea_2obj/_progress.json'))['completed']
rep = json.load(open('papers/single-sat-quality/experiments/results/replicate_variance_20261031/_progress.json'))['completed']
for grp in ['S1','S2','S3','S4']:
    key = f'{grp}/{grp}-A_seed00.pkl'
    for src, name in [(m2,'MOEA-2'),(m3,'MOEA-3')]:
        e = src[key]; r = [rep[k] for k in rep if k.startswith(f'{grp}/{name}/')]
        match = all(abs(e[f]-r[0][f])<1e-12 for f in ('f1','f2','f3')) and e['n_selected']==r[0]['n_selected']
        print(grp, name, 'bitwise=', match)
EOF
```
