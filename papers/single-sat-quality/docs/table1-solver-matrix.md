# Table 1: Solver Performance Matrix (per Scenario Group)

**5 solvers × 4 groups × 3 metrics** (mean ± 1 SD across 50 seeds per group)

| Solver | S1 (N=20) | S2 (N=100) | S3 (N=300) | S4 (N=500) |
|:---|:---|:---|:---|:---|
| G-BL | 1.00 / 0.574±0.026 / 0.271±0.057 | 1.00 / 0.549±0.033 / 0.366±0.084 | 1.00 / 0.527±0.020 / 0.452±0.064 | 1.00 / 0.490±0.052 / 0.53±0.11 |
| G-SM | 0.51±0.16 / 0.475±0.057 / 0.644±0.058 | 0.35±0.09 / 0.460±0.054 / 0.649±0.052 | 0.29±0.04 / 0.437±0.036 / 0.664±0.035 | 0.37±0.12 / 0.408±0.045 / 0.700±0.058 |
| GA-P-BL | 1.00 / 0.574±0.026 / 0.271±0.057 | 1.00 / 0.549±0.033 / 0.366±0.084 | 1.00 / 0.527±0.020 / 0.452±0.064 | 1.00 / 0.490±0.052 / 0.53±0.11 |
| MOEA-2 | 0.87±0.08 / 0.600±0.021 / 0.233±0.027 | 0.98±0.03 / 0.556±0.031 / 0.347±0.077 | 1.00±0.00 / 0.530±0.019 / 0.444±0.062 | 1.00±0.01 / 0.493±0.053 / 0.53±0.11 |
| MOEA-3 | 0.98±0.03 / 0.540±0.021 / 0.428±0.064 | 1.00±0.00 / 0.548±0.031 / 0.375±0.075 | 1.00 / 0.528±0.020 / 0.453±0.064 | 1.00 / 0.490±0.053 / 0.54±0.11 |

**Footnotes:**
- **f1\*** = coverage fraction relative to G-BL baseline (f1_raw / f1_G-BL)
- **f2** = comprehensive geometric quality (higher is better)
- **f3** = NESZ radiation quality (higher is better)
- Each cell shows: **f1\* ± SD / f2 ± SD / f3 ± SD**
- All statistics computed across 50 random seeds per scenario group

## Hypervolume (HV) by Solver and Group

Normalized 3D HV (reference point: [0, 0, 0], all objectives maximized after normalization).

| Solver | S1 (N=20) | S2 (N=100) | S3 (N=300) | S4 (N=500) |
|:---|:---|:---|:---|:---|
| G-BL | 0.0197±0.0030 | 0.0196±0.0018 | 0.0188±0.0016 | 0.0165±0.0049 |
| G-SM | 0.0806±0.0295 | 0.1090±0.0165 | 0.1239±0.0155 | 0.0955±0.0492 |
| GA-P-BL | 0.0197±0.0030 | 0.0196±0.0018 | 0.0188±0.0016 | 0.0165±0.0049 |
| MOEA-2 | 0.1005±0.0382 | 0.0286±0.0125 | 0.0196±0.0021 | 0.0181±0.0061 |
| MOEA-3 | 0.1654±0.0555 | 0.0326±0.0168 | 0.0205±0.0021 | 0.0187±0.0066 |

**Note:** Higher HV = better overall multi-objective performance.

## Overall HV (across all 200 scenarios)

| Solver | HV Mean | HV Std |
|:---|---:|---:|
| G-BL | 0.0186 | 0.0033 |
| G-SM | 0.1023 | 0.0346 |
| GA-P-BL | 0.0186 | 0.0033 |
| MOEA-2 | 0.0417 | 0.0398 |
| MOEA-3 | 0.0593 | 0.0681 |
