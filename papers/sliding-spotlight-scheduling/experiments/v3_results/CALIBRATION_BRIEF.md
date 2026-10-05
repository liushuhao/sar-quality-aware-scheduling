# 执行简报 — v3 收敛标定（两档预算 × 3 族 × 10 种子 = 60 单元）

你是执行员（Claude Code CLI，fresh context）。职责：**启动并看护两档收敛标定矩阵跑完**。
ZCode 负责设计/判读（`.scratch/sliding-spotlight-scheduling/v3-run/CALIBRATION_PREREG.md`，
你不用判读）。只读执行面：**禁改任何代码/文档**；只允许写两个新 matrix 目录。

## 命令（repo root；解释器路径含空格，bash 里用单引号——首射教训）

档 1（约 3–6 分钟）：
```
PYTHONHASHSEED=0 '/d/Program Files/Python/python' papers/sliding-spotlight-scheduling/scripts/run_matrix.py --generator realwindow --platform .scratch/sliding-spotlight-scheduling/v2-smoke/platform.json --variants 1,2,3 --pop 80 --gen 120 --scenarios-dir .scratch/sliding-spotlight-scheduling/v3-run/scenarios --matrix-dir .scratch/sliding-spotlight-scheduling/v3-run/matrix_p80g120
```

档 2（约 40–120 分钟）：
```
PYTHONHASHSEED=0 '/d/Program Files/Python/python' papers/sliding-spotlight-scheduling/scripts/run_matrix.py --generator realwindow --platform .scratch/sliding-spotlight-scheduling/v2-smoke/platform.json --variants 1,2,3 --pop 160 --gen 240 --scenarios-dir .scratch/sliding-spotlight-scheduling/v3-run/scenarios --matrix-dir .scratch/sliding-spotlight-scheduling/v3-run/matrix_p160g240
```

两个目录都不存在（首跑）。**串行执行**：档 1 跑完 exit 0 再启动档 2。
建议 nohup 后台 + 每 3 分钟 tail 一次驱动器 stdout（两档各存 `matrix_p80g120.log` /
`matrix_p160g240.log`，`> log 2>&1`）。

## 看护纪律

- 驱动器自带告警（exit 4/5/6/7）。**任何 exit-1 或 ALARM：停，抓该档 log 末 30 行原样
  报告，禁自行改代码/重试超过一次**。
- 档 2 时长超 150 分钟仍未完：停看护，报告已完成单元数（读 `_progress.json`），移交 ZCode。
- manifests 已存在：驱动器会做字节对账（无 `manifest generated:` 行 = 对账通过）。

## 报告格式（≤250 字）

1. 两档启动命令回显（各 1 行）2. 每档单元 census（exit 计数）
3. 异常原文（如有）4. 驱动器 summary（exit-code totals）5. 结论：跑完 / 移交。
