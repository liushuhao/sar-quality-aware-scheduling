# seed07 进程级熵探针证据 — 2026-11-05

背景：扩容跑批（replicate_variance_20261104）发现 S1-A_seed07/MOEA-2 主跑 f1=0.9391（18 任务）vs 重跑 5 连稳定 0.8087（16 任务）。探针脚本（临时 /tmp/hashseed_probe.py，参数与主跑 runner 完全一致：pop100/gen200/obj2/n_ref_dirs12/hotstart，f1_gbl 同 115.0）。

## 探针结果（10 次运行；脚本入库 experiments/probe_process_entropy_seed07.py）

| 运行 | PYTHONHASHSEED | f1 | n_sel |
|---|---|---|---|
| 1 | 1 | 0.939130 | 18 |
| 2 | 2 | 0.808696 | 16 |
| 3 | 1 | 0.808696 | 16 |
| 4 | 1 | 0.921739 | 17 |
| 5 | 1 | 0.808696 | 16 |
| 6 | 1 | 0.921739 | 17 |
| 7 | 1 | 0.921739 | 17 |
| 8 | unset | 0.808696 | 16 |
| 9 | unset | 0.939130 | 18 |
| 10 | unset | 0.939130 | 18 |

## 事实结论

1. **三个不同局部解**（0.809/16、0.922/17、0.939/18），非二值分歧。
2. **PYTHONHASHSEED 有影响但非唯一源**：seed=1 内部出现**三种**结果（行 1=0.939、行 3/5=0.809、行 4/6/7=0.922）；存在未识别的进程级熵。候选=全局 numpy 流被某组件条件性消费（moea.py 自身仅 :516 np.random.seed(seed)（未触发）与 :573 RandomState(1)（已钉）；pymoo minimize(seed=1) 钉 pymoo 内部流）。
3. **同进程稳定性只对多数场景成立**：replicate 批大多数格同进程 5 连逐位一致，**但 S1-A_seed08/MOEA-2 的 5 连在同一进程内即分裂为两种值（0.934×2 + 0.811×3）**——临界场景连内也不稳定。主跑多数场景跨进程逐位一致，分歧集中 S1 稀疏类 2/10（seed07/08）——组合临界场景经 200 代演化放大进程级微差。
4. **参数一致性排除**：主跑条目 params={pop100,gen200,obj2} 与 replicate runner 相同；f1_gbl 双侧 115.0（实例与 G-BL 基座一致）；moea.py 行为链等价（4cfc42c0..HEAD 仅删死参数）。

## 对 R7 口径段的落笔依据

- §5.4 报分层事实（终稿以正文为准）：聚合层复制子集类均值移动 S2–S4 ≤0.0041/0.0032、S1 f2/f3 ≤0.0082、f1 最差对 0.033；场景层 91% 包络覆盖（misses S1 5/60、S2 8/60、S3 8/60、S4 1/60——幅度稀疏大、频次中密度高但小一个量级）；S1 临界场景分歧可达多个局部解（seed07 跨进程 3 个，seed08 连内 2 个）。
- 措辞：报"exact source of the residual process-level entropy was not identified"（诚实），钉 PYTHONHASHSEED 与全局流列为复现建议/future work，不断言根因。
- 论文结论层（类均值、密度边界、质量边际）不受影响。

## 复核命令

探针脚本逻辑同 `run_replicate_variance.py::run_one`（S1-A_seed07, MOEA-2），任意 PYTHONHASHSEED 下重复运行应复现 {0.809, 0.922, 0.939} 值集合（个体分布随进程熵浮动）。
