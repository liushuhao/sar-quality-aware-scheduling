# Agile SAR Multi-Objective Scheduling — Companion Code

Companion code and data for:

> **LIU, S. (2026).** Physics-Aware Multi-Objective Scheduling for Agile SAR
> Satellites: Balancing Profit, NESZ, and Geometric Resolution.
> *Advances in Space Research* (preparing for submission).
> 
> Companion repository: [liushuhao/sar-quality-aware-scheduling](https://github.com/liushuhao/sar-quality-aware-scheduling)

## Summary

Physics-aware NSGA-III framework for scheduling agile SAR satellite observations. Two SAR physical quality dimensions — NESZ (radiometric) and geometric resolution — integrated with profit maximization.

Five solvers compared on 200 systematic scenarios across four target densities (S1: N=20, S2: N=100, S3: N=300, S4: N=500):

| Solver | Type | Objectives |
|:--|:--|:--|
| G-BL  | Greedy, baseline          | f1 (profit) |
| G-SM  | Greedy, squint-minimizing | f2 (geometric quality proxy) |
| GA-P-BL | Single-objective GA, G-BL-seeded | f1 (profit) |
| MOEA-2 | NSGA-III, 2-objective | f1 + f2 |
| MOEA-3 | NSGA-III, 3-objective | f1 + f2 + f3 (NESZ proxy) |

## Reproducibility

### Requirements

- Python 3.11+
- Dependencies: `numpy`, `scipy`, `pymoo`, `matplotlib`, `SciencePlots`, `pandas` (see `requirements.txt`)

### Run experiments

From repository root:

```bash
# Five solvers × 200 fixed scenarios = 1000 solver runs
python papers/single-sat-quality/experiments/run_baselines_v4.py    # G-BL, G-SM
python papers/single-sat-quality/experiments/run_so_f1_bl.py         # GA-P-BL
python papers/single-sat-quality/experiments/run_moea_2obj.py        # MOEA-2
python papers/single-sat-quality/experiments/run_moea_3obj.py        # MOEA-3

# Statistical analysis
python papers/single-sat-quality/experiments/statistical_analysis.py
```

Each `run_*.py` writes JSON results to `papers/single-sat-quality/experiments/results/<solver>/`.
Scenario pkl files carry fixed seeds; MOEA runs use `seed=None` internally
(pymoo seed=1, unseeded numpy) so reruns may show small stochastic
differences in schedule-level means — reported signs/conclusions are
robust, but exact means are not bit-reproducible.

### Reproduce the coupling analysis (paper §6.4)

The paper's per-task f2–f3 correlation claims are computed by:

```bash
# Variant D (no physics) per-task correlation, all 4 density classes
PYTHONPATH=src python papers/single-sat-quality/scripts/reproduce_variant_d_r.py
# Full-physics MOEA-3 (variant A) per-task correlation
PYTHONPATH=src python papers/single-sat-quality/scripts/reproduce_A_r.py
```

Results: `experiments/results/variant_d_per_task_r.json` (raw per-task
points included), `cross_solver_pool_probe.json`. Note `f2_f3_coupling.json`
is deprecated (its +0.93–0.98 values are not reproducible; see
`review/rdr-002-coupling-plus098-unreproducible.md`).

### Generate figures

```bash
python papers/single-sat-quality/experiments/gen_all_figures.py     # 5 main figures (Fig1,2,4,5,6)
python papers/single-sat-quality/experiments/gen_table1.py          # Table 1 (solver matrix)
```

Figures written to `papers/single-sat-quality/figures/`. Uses SciencePlots + scipilot-figure-skill (global skill) for style presets and export.

### Build the paper PDF

```bash
cd papers/single-sat-quality
pdflatex small-paper-ijae.tex
bibtex small-paper-ijae
pdflatex small-paper-ijae.tex
pdflatex small-paper-ijae.tex
```

Requires TeX distribution with `amsmath`, `booktabs`, `caption`, `hyperref`, `geometry`.

## Data Availability

Tracked assets include solver code, scenario generators, fixed seeds/configuration, processed JSON/CSV results, analysis scripts, and figures. Generated binary scenario files and per-run pickle objects are excluded from Git; regenerate them with the supplied scripts. Configure and publish the repository remote before manuscript submission.

## Code Layout

> **完整目录映射 + 文件放置规则 → 见 [`AGENTS.md`](AGENTS.md)**（协作者必读）

```
.
├── src/sar_sim/              # self-contained solver package
│   ├── solver/               # NSGA-III, GA-P-BL, baselines, GA, CSP, ILP
│   ├── metrics/              # NESZ, coverage, timeliness, utilization
│   ├── generator/            # scenarios (orbit, target, visibility)
│   ├── types.py              # GroundTarget, ObservationWindow
│   ├── verification/         # constraint validators
│   └── conflict/             # conflict detection
├── src/tools/                # utilities (paper-translator, check_numerical, check_refs)
├── src/tests/                # pytest unit tests
├── papers/
│   ├── single-sat-quality/   # ASR paper (Ch3)
│   │   ├── *.tex, *.bib      # paper source
│   │   ├── sections/         # section fragments
│   │   ├── figures/          # paper figures (generated PDFs/PNGs)
│   │   │   └── experiments/   # experiment data (subdirectories per batch)
│   │   ├── experiments/      # experiment scripts + scenario data
│   │   └── scripts/          # driver scripts
│   └── constellation-scheduling/  # Ch5 paper (in progress)
│       └── experiments/      # Ch5 scenarios + pilot results
├── literature/               # references
│   ├── fulltext/             # extracted full-text JSON
│   ├── structured/           # parsed metadata JSON
│   ├── analysis/             # literature analysis reports
│   └── scripts/              # parsing/import scripts
├── reference/                # domain knowledge + ADR
│   └── adr/                  # Architecture Decision Records
├── thesis/                   # PhD thesis outline + chapter assembly
└── archive/                  # process artifacts (reviews, annotations, handoffs)
```

## License

CC-BY-4.0. See `LICENSE`. Underlying paper © 2026 LIU SHUHAO.

## Contact

LIU SHUHAO — liushuhao@hrbeu.edu.cn
Harbin Engineering University, College of Intelligent Systems Science and Engineering
