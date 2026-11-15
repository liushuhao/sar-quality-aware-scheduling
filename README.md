# Agile SAR Multi-Objective Scheduling — Companion Code and Data

Companion code, scenario definitions, and processed results for:

> **LIU, S.** Physics-Aware Multi-Objective Scheduling for an Agile SAR Satellite:
> Balancing Profit, NESZ-Based Radiometric Ordering, and Geometric Resolution.
> *Advances in Space Research* (under review).

## What is in this repository

| Path | Contents |
|---|---|
| `src/sar_sim/` | Shared simulation library: solver (`solver/`), instance and scenario generation (`generator/`), metrics — NESZ quality score, resolution, coverage (`metrics/`), conflict handling (`conflict/`), numerical verification (`verification/`) |
| `papers/single-sat-quality/experiments/` | Experiment drivers, scenario definitions (`scenarios/`), and processed results (`results/`, JSON/CSV) |
| `papers/single-sat-quality/scripts/` | Figure and table generation scripts |
| `papers/single-sat-quality/figures/` | Rendered figures (PDF/PNG) |

Not included: the manuscript source, and generated binary scenario files / per-run
pickle objects (regenerable from the supplied scripts and seeds).

## Environment

Tested with Python 3.11.

```
pip install -r requirements.txt
```

## Quick start

Run everything from the repository root with `src` on the import path:

```
# Windows
set PYTHONPATH=src
# Linux / macOS / Git Bash
export PYTHONPATH=src

python papers/single-sat-quality/experiments/<script>.py
```

Key entry points (function names do not always match file names):

| Purpose | Module | Entry point |
|---|---|---|
| NSGA-III 3-objective solve | `sar_sim.solver.moea` | `moea_solver()` (a function, not a class) |
| GA-P-BL (GA seeded by greedy baseline) | `sar_sim.solver.so_f1` | `b2_profit_solver_bl_seeded()` |
| NESZ quality score | `sar_sim.metrics.nesz` | `quality_score()`, `off_nadir_to_incidence()` |

## Reproducibility notes

- Scenario definitions under `experiments/scenarios/` carry the fixed scenario
  seeds and configuration used in the paper.
- Processed results under `experiments/results/` pin the exact realizations that
  were analyzed; within-instance solver process draws are not pinned (the
  manuscript reports the resulting class-level variation).
- Figures in `papers/single-sat-quality/figures/` are produced from the tracked
  result files by the scripts in `papers/single-sat-quality/scripts/`.

## License

CC-BY-4.0. See `LICENSE`.

## Contact

LIU Shuhao — shuhao.liu.86@outlook.com — ORCID 0009-0009-2116-3670
