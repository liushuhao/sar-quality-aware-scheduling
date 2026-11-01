# 任务书：改稿批次独立复验 + 代提交

仓库根：`D:\hermes\my-workspace\projects\planning-paper`
本机 shell：Git Bash（Windows）。所有命令按写的 cwd 执行，用绝对路径。

## 一、红线（产出第一段必须逐条复述；不复述视同未读，产物作废）

1. 禁止修改任何 `.tex` / `.bib` / `.md` / `.py` / `.pdf` 文件——本次复核是**只读**。唯一允许改动的两样：`git index`（提交）与你在第 5 步写的报告文件。
2. 禁止 `git checkout` / `git reset` / `git stash` / `git clean` / 任何丢弃工作树改动的命令。
3. 禁止修改 `~/.claude`、`~/.agents`、任何配置文件、任何规则文件。
4. 禁止联网、禁止安装依赖、禁止改测试脚本或门禁脚本。
5. 只允许提交本任务书列出的 16 个文件；`git add` 一律用明确路径，禁止 `git add -A` / `git add .`。
6. 任何一个门禁不通过（含退出码非 0 或计数不符），**停止并报告，不许提交**。

## 二、背景（只读，不许据此改文件）

工作树已由主线程改好两篇论文，需要你独立复验后提交。两批改动：

- **paper2**：`paper/main.tex` 的滑聚驻留闭式原先把 Kim Eq.(22) 两种写法混印（用了 `(R_0+r_0)` 杠杆又多加了一个 `W_a`），已改成代码实际执行的形式；另外按评审把若干主张的范围限定写进摘要/贡献/§5.5/§7.1/§3.3/§3.4，并给 `tab:modes` 图注补了取整说明。
- **paper1**：中文版四处与英文矛盾的表述已改（消融场景数 200→300、G-BL 放置规则、发现(4) 的伪造百分比、结论的覆盖率代价归属），另修若干小项与三条参考文献元数据。

## 三、复验步骤（逐条实跑，记录 exit code 与关键计数）

按顺序执行，每条命令的 cwd 已标出。

### 步骤 1 — 工作树核对

cwd = `D:\hermes\my-workspace\projects\planning-paper`

```
git status --porcelain
```

期望：**恰好**下列 17 个 ` M` 行（顺序无关）：

```
 M papers/single-sat-quality/sections/_ablation_section-zh.tex
 M papers/single-sat-quality/small-paper-ijae-zh.pdf
 M papers/single-sat-quality/small-paper-ijae-zh.tex
 M papers/single-sat-quality/small-paper-ijae.bib
 M papers/single-sat-quality/small-paper-ijae.pdf
 M papers/single-sat-quality/small-paper-ijae.tex
 M papers/sliding-spotlight-scheduling/formulas/formula-spec.md
 M papers/sliding-spotlight-scheduling/paper/full.md
 M papers/sliding-spotlight-scheduling/paper/main.pdf
 M papers/sliding-spotlight-scheduling/paper/main.tex
 M papers/sliding-spotlight-scheduling/paper/refs.bib
 M papers/sliding-spotlight-scheduling/paper/sections/sec1_introduction.md
 M papers/sliding-spotlight-scheduling/paper/sections/sec3_problem_formulation.md
 M papers/sliding-spotlight-scheduling/paper/sections/sec4_solving_approach.md
 M papers/sliding-spotlight-scheduling/paper/sections/sec6_results.md
 M papers/sliding-spotlight-scheduling/paper/sections/sec7_discussion.md
 M papers/sliding-spotlight-scheduling/sss_core/duration.py
```

另有未跟踪目录 `?? papers/sliding-spotlight-scheduling/review/panel-full-20261031/`，属审查产物，**不提交**。
出现清单外的改动 → 停止并报告。

### 步骤 2 — paper2 门禁（cwd = `D:\hermes\my-workspace\projects\planning-paper\papers\sliding-spotlight-scheduling`）

| # | 命令 | 期望 |
|---|---|---|
| 1 | `python scripts/verify_paper_numbers_l8.py --paper paper/main.tex --paper paper/full.md` | exit 0；末三行含 `0 mismatch(es) over 299 checked` |
| 2 | `python scripts/check_red_lines.py` | exit 0；`0 violation(s) over 1487 file(s)` |
| 3 | `python scripts/check_figure_receipts.py` | exit 0；`70/70` |
| 4 | `python scripts/verify_prereg_v2.py` | exit 0；`0 failure(s) over 28 checks` |
| 5 | `python scripts/sync_mirrors_check.py` | exit 0；`60/60` |
| 6 | `python scripts/verify_claim_traces.py` | exit 0；`11/11` |
| 7 | `python scripts/check_layout_gotchas.py --tex paper/main.tex --log review/panel-full-20261031/build-20261101/main.log` | exit 0；`0 layout FAIL(s)` |

### 步骤 3 — paper1 门禁（cwd = `D:\hermes\my-workspace\projects\planning-paper`）

| # | 命令 | 期望 |
|---|---|---|
| 1 | `python src/tools/verify_paper_numbers.py` | exit 0；`LEDGER: 204 assertions, 0 failed` 且 `CALIBER OK` |
| 2 | 编译英文：`cd papers/single-sat-quality && pdflatex -interaction=nonstopmode -output-directory=review/final-redteam-20261031/build-en small-paper-ijae.tex` 连跑两遍 | 两遍 exit 0；日志 `build-en/small-paper-ijae.log` 里 `! ` 计 0、`Rerun to get` 计 0、页数 48 |
| 3 | 编译中文：同 cwd，`xelatex -interaction=nonstopmode -output-directory=review/final-redteam-20261031/build-zh small-paper-ijae-zh.tex` 连跑两遍 | 两遍 exit 0；日志 `build-zh/small-paper-ijae-zh.log` 里 `! ` 计 0、`Rerun to get` 计 0、页数 38 |
| 4 | `python src/tools/check_refs.py`（若报找不到脚本，改在 `papers/single-sat-quality` 下跑 `python ../../src/tools/check_refs.py`） | exit 0；输出 `none — all references resolve` |

**注意**：步骤 2/3 的编译只写 `review/.../build-en`、`build-zh` 目录（已 gitignore 或属未跟踪审查目录），不得改动库里任何被跟踪文件。编译后必须再跑一次步骤 1 的 `git status --porcelain`，确认仍是那 16 个 `M` 行——多一个就停止。

### 步骤 4 — 定点断言（cwd = 仓库根）

```
python -I papers/single-sat-quality/review/final-redteam-20261031/verify_fixes
```

期望 exit 0，`FAILS: 0`，且 19 行全 `PASS`。

```
python -I -c "import pathlib;t=pathlib.Path('papers/sliding-spotlight-scheduling/paper/main.tex').read_text(encoding='utf-8');print('new_form',t.count(r'R_0\big['),'old_form',t.count(r'(R_0+r_0)(\tan\theta_{s0}'))"
```

期望输出 `new_form 1 old_form 0`。

### 步骤 5 — 写报告

写到 `D:\hermes\my-workspace\projects\planning-paper\papers\sliding-spotlight-scheduling\review\panel-full-20261031\verify-and-commit-report.md`，内容结构：

1. 红线复述（六条逐条）
2. 门禁结果表：每条命令 / exit code / 关键计数原文
3. 步骤 4 的两项结果
4. 若提交：两个 commit hash + 每条的 `git show --stat` 输出
5. 回传三段：变更文件清单（应含两个 commit 覆盖的 16 个文件）/ 实跑验证命令+exit code 或计数 / 未验范围
6. 末行：`VERDICT: PASS — committed` 或 `VERDICT: FAIL — <一句话原因，未提交>`

### 步骤 6 — 提交（仅当步骤 2、3、4 全部符合期望时执行；cwd = 仓库根）

先用明确路径 `git add`，再分两次提交，提交信息必须**逐字**如下（不要加署名、不要加 Co-Authored-By、不要改写）：

第一次（paper2）：

```
paper2: 修正滑聚驻留闭式并收紧主张范围限定

main.tex:143 原先把 Kim Eq.(22) 的两种写法混印——用 (R_0+r_0)
杠杆又额外加了 W_a——比 sss_core 实际执行的闭式高 10.305%。
改为可执行形式 R_0[tan(θ_s0+θ_a/2)−tan(θ_s1−θ_a/2)]+W_a 并写明
broadened sweep α 与 r_0 的定义；sections/sec3_problem_formulation.md、
full.md、duration.py 文档字符串同步；formula-spec.md 增记两式不可混用。

按评审收紧范围限定：地板占比限定为至多 20.0/44.8 点且含对比政策成分；
摘要补"所有量级为本场景集内部、无外部调度器基线"；贡献二改述为
族形状对比；摘要补锚构造限定（258/260、无平凡上界）；失效断言限定到
最不保守驻留约定；§4 明说服务优先级近似等于服务任务比例；§5.5 的
"单次构造基本解决"限定到所测搜索族与探针覆盖；cosine 机制断言撤回为
带宽侧读数；tab:modes 图注补取整说明；refs.bib 头计数改为实际 36 条。

验证: L8 299 条 0 不符; 红线 1487 文件 0 违规; 图收据 70/70;
预注册 28 项 0 失败; 镜像 60/60; 版式 0 FAIL; 宣称追溯 11/11;
隔离编译 46 页 0 错 0 未定义 0 rerun。
```

第二次（paper1）：

```
paper1: 修正中文镜像与英文的矛盾及三条文献元数据

中文版四处与英文相互矛盾：消融场景数 200 改为 300（英文与中文自己的
贡献列表、消融章节均为 6 类×50=300）；删除自造的 G-BL"固定天底"放置
规则，恢复英文的"最早时刻放置由窗口入射–斜视剖面隐含决定几何"；删除
发现(4) 中凭空添加的 1%/0.5%(f2,f3,n_sel)——该界被表 6 自身推翻
(S3 的 f3 差 0.80%/1.12%)；结论中 14–15% 覆盖率代价改为同时归属
MOEA-2 与 MOEA-3。另修覆盖"优势"→"代价"的方向词错误。

小项: +0.99 交叉引用 §7.1→§6.2; 中文 §4.4 补回被漏译的 GA-P-BL 守卫段
(199/200、13.5%、<0.001); "总是触发"改"仅作用于单一利润目标"; 膝点
选择器段落由 §4 移至 §5.2 与英文同位置; 补回两处范围限定句与目标一的
归一化理由; ξ/sinθ_elev 命名对齐; 两个消融图注补回限定词; 头注同步日期。
英文侧删除一句与上一句重复、且读来防御的"开放问题"收尾。

文献: Chen2024LearnConstruct 页码 5991–6002→5949–5963;
Chen2019MILPMulti 页码 419–434→694–707; Romano2006 的 DOI 实测 404、
期刊卷期页不成立，改为会议论文形式并移除未核实字段; 头注条目数 25→31。

验证: verify_paper_numbers 204 条 0 失败 CALIBER OK; 英文编译 48 页、
中文 38 页, 均 0 错 0 未定义引用 0 rerun; 交叉引用全部解析;
19/19 定点断言通过。
```

`git add` 路径：

第一次：`papers/sliding-spotlight-scheduling/paper/main.tex papers/sliding-spotlight-scheduling/paper/main.pdf papers/sliding-spotlight-scheduling/paper/full.md papers/sliding-spotlight-scheduling/paper/refs.bib papers/sliding-spotlight-scheduling/paper/sections/sec1_introduction.md papers/sliding-spotlight-scheduling/paper/sections/sec3_problem_formulation.md papers/sliding-spotlight-scheduling/paper/sections/sec4_solving_approach.md papers/sliding-spotlight-scheduling/paper/sections/sec6_results.md papers/sliding-spotlight-scheduling/paper/sections/sec7_discussion.md papers/sliding-spotlight-scheduling/formulas/formula-spec.md papers/sliding-spotlight-scheduling/sss_core/duration.py`

第二次：`papers/single-sat-quality/small-paper-ijae.tex papers/single-sat-quality/small-paper-ijae.pdf papers/single-sat-quality/small-paper-ijae-zh.tex papers/single-sat-quality/small-paper-ijae-zh.pdf papers/single-sat-quality/small-paper-ijae.bib papers/single-sat-quality/sections/_ablation_section-zh.tex`

提交后跑 `git status --porcelain`，期望只剩未跟踪的 `?? papers/sliding-spotlight-scheduling/review/panel-full-20261031/`。

## 四、回传格式（缺任一段视同未验证）

1. 变更文件清单（16 个，按 commit 分组）
2. 实跑验证：每条命令 + exit code + 关键计数原文（不许只写"全绿"）
3. 未验范围（至少写明：没有人工通读改后正文、没有重跑论文的数值实验、没有做视觉图件检查）
4. 末行 VERDICT
