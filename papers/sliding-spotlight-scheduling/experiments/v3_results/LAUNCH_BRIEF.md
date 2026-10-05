# 执行简报 — 真窗矩阵 v3 重跑（第 2 次发射）

> **首射记录（已闭环）**：首跑 18/30 单元 exit-1——encode_seed_individual 多窗测度缝（anchor 起点恰在区间左缘，tau*total 丢 1 ulp 后游走翻入前一过境）。已修复（commit `036e297`：nextafter 跨缝 + 全量 220P+1S 回归）。本次为修复后干净重跑：
> matrix 产物与 progress 已清空，manifests 保留（与 encode 无关，驱动器会字节对账）。

你是执行员（Claude Code CLI，fresh context）。职责：**启动并看护 v3 真窗矩阵跑完**。
ZCode 负责前置闸（已过）与最终审查（跑完后你不用做）。你是只读执行面：
**禁止修改任何代码/文档**；只允许写 `--scenarios-dir/--matrix-dir` 指定的输出目录。

## 已就绪状态（ZCode 已验证，勿重做）

- 票 25 已落地（HEAD `dbc4d0b`）：过境枚举 + 每窗 t_ca schema，双面回归绿
  （共享库 145P = N₀；paper2 域 219P+1S），四门禁 rc=0。
- 平台轨道（登记输入，勿改）：`.scratch/sliding-spotlight-scheduling/v2-smoke/platform.json`
  （a=6941000.0, e=0.001, i=45°, epoch 2026-01-01T00:00:00）。
- Rule-11 最小单元已过：R1C_seed100 manifest = 20/20 served、158 窗、字节同一（1.7s）；
  pilot exit 0、front 40、anchor f1*=1.0000、promotion=no_promotion。
  产物已在 v3-run/scenarios + v3-run/matrix——驱动器会对它做字节对账并重跑该单元，属预期。

## 要跑的命令（repo root，一次 nohup 后台）

```
cd /d/hermes/my-workspace/projects/planning-paper
PYTHONHASHSEED=0 nohup "/d/Program Files/Python/python" \
  papers/sliding-spotlight-scheduling/scripts/run_matrix.py \
  --generator realwindow \
  --platform .scratch/sliding-spotlight-scheduling/v2-smoke/platform.json \
  --variants 1,2,3 \
  --scenarios-dir .scratch/sliding-spotlight-scheduling/v3-run/scenarios \
  --matrix-dir .scratch/sliding-spotlight-scheduling/v3-run/matrix \
  > .scratch/sliding-spotlight-scheduling/v3-run/matrix.log 2>&1 &
```

预期时长 60–120 分钟（R1C≈10 单元快、R3H N=100 manifest 每个约 1–2 分钟）。

## 看护纪律

- 每 3 分钟一次：`tail -5 .scratch/.../v3-run/matrix.log` 和
  `python -c "import json;d=json.load(open('.scratch/.../v3-run/matrix/_progress.json'));print(len(d['units']), {u['exit'] for u in d['units'].values()})"`（粗读即可）。
- 驱动器自带告警（exit 4=零产出 / 5=出现 exit-10 世代缺陷 / 6=整变体空前沿 / 7=exit-1 崩溃）。
  **出现 exit 1 或任何 ALARM：停止看护，抓 matrix.log 末 30 行原样报告，禁自行改代码**。
- 看护上限约 25 分钟：跑完 → 交完整报告；未跑完 → 交启动报告（已健康完成的单元数、
  各单元 exit、manifest 生成速率），后续监控由 ZCode 接管，你退出。

## 报告格式（≤300 字）

1. 启动命令回显（1 行）2. 已完成单元清单（family_seed → exit + wall_s）
3. 任何异常/告警原文 4. 驱动器 summary（若已出）5. 结论：跑完 / 移交监控。
