# Experiments — Canonical Runners

All runners write incremental `_progress.json` / JSON results and resume by
default. After regenerating scenario pkls, rerun with `--no-resume`; the
pkl_sha1 guard (see below) makes stale cached entries recompute automatically.

## Solver runners

| Solver | Runner | Scope | Output |
|--------|--------|-------|--------|
| G-BL, G-SM | `run_baselines_v4.py` | S1–S4 (200) | `results/baselines_200.json` |
| G-BL, G-SM | `run_baselines_S7S8.py` | S7/S8 (100, §6.3 scale) | `results/baselines_S7S8.json` |
| GA-P-BL | `run_so_f1_bl.py` | S1–S4 (200) | `results/b2_profit_bl/_progress.json` |
| MOEA-2 | `run_moea_2obj.py` | S1–S4,S7,S8 (300) | `results/moea_2obj/_progress.json` |
| MOEA-3 | `run_moea_3obj.py` | S1–S4 (200) | `results/moea_3obj/_progress.json` |
| no-squint (B) | `run_moea_3obj_no_squint.py` | S1–S4 (200) | `results/moea_3obj_no_squint/_progress.json` |
| no-incidence (C) | `run_moea_3obj_no_incidence.py` | S1–S4 (200) | `results/moea_3obj_no_incidence/_progress.json` |
| no-physics (D) | `run_moea_3obj_no_physics.py` | S1–S4 (200) | `results/moea_3obj_no_physics/_progress.json` |

S5/S6 are a separate N=20 layout not used by the paper. All runners take
`--groups S1 S2 ...` and `--no-resume`.

## Provenance guard (`_provenance.py`)

Every runner persists `pkl_sha1` per scenario. Downstream merge scripts call
`check_pkl_sha1_consistency()` and hard-exit if two families/variants ran on
different pkl bytes (e.g. a baseline not rerun after a window fix paired with
a post-fix MOEA). Wired into `statistical_analysis.py`,
`recompute_scale_sensitivity.py`, `analyze_ablation.py`,
`gen_fig6_ablation.py`. Tests: `pytest test_provenance_guard.py`.

## Audit + downstream

```bash
python progress_to_snapshot.py results/<family>/_progress.json _snapshot_<fam>.json
python _audit_full_hard.py --snapshot _snapshot_<fam>.json --jobs 6   # C1-C4/OOW
python statistical_analysis.py          # → statistical_results.json
python gen_table1.py                    # Table 1
python recompute_scale_sensitivity.py   # §6.3 N50
```

## Run from project root

```bash
python papers/single-sat-quality/experiments/run_so_f1_bl.py   # GA-P-BL
```
