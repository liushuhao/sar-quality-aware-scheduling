# Experiments — Canonical Runners

| Solver | Runner | Output |
|--------|--------|--------|
| **G-BL, G-SM** | `run_baselines_v4.py` | `results/baselines_200.json` |
| **GA-P-BL** | `run_so_f1_bl.py` | `results/b2_profit_bl/_progress.json` |
| **MOEA-2** | `run_moea_2obj.py` | `results/moea_2obj/_progress.json` |
| **MOEA-3** | `run_moea_3obj.py` | `results/moea_3obj/_progress.json` |

## Run

From project root:

```bash
python papers/single-sat-quality/experiments/run_so_f1_bl.py   # GA-P-BL
```

## Archived

Debug/diagnostic scripts moved to `experiments/_archive/`.
