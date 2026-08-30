# Table 1: Solver Performance Matrix (per Scenario Group)

**5 solvers × 4 groups × 3 metrics** (mean ± 1 SD across 50 seeds per group)

| Solver | S1 (N=20) | S2 (N=100) | S3 (N=300) | S4 (N=500) |
|:---|:---|:---|:---|:---|
| G-BL | 1.00 / 0.295±0.037 / 0.497±0.044 | 1.00 / 0.317±0.026 / 0.561±0.060 | 1.00 / 0.342±0.026 / 0.616±0.042 | 1.00 / 0.336±0.039 / 0.675±0.074 |
| G-SM | 0.51±0.16 / 0.389±0.086 / 0.722±0.058 | 0.35±0.09 / 0.357±0.078 / 0.735±0.055 | 0.29±0.04 / 0.317±0.055 / 0.756±0.036 | 0.37±0.12 / 0.291±0.067 / 0.786±0.046 |
| GA-P-BL | 1.00±0.02 / 0.295±0.037 / 0.498±0.044 | 1.00 / 0.317±0.026 / 0.561±0.060 | 1.00 / 0.342±0.026 / 0.616±0.042 | 1.00 / 0.336±0.039 / 0.675±0.074 |
| MOEA-2 | 0.86±0.13 / 0.393±0.055 / 0.657±0.040 | 0.98±0.03 / 0.329±0.030 / 0.589±0.044 | 1.00±0.00 / 0.343±0.026 / 0.622±0.040 | 1.00±0.01 / 0.337±0.038 / 0.680±0.073 |
| MOEA-3 | 0.85±0.12 / 0.376±0.050 / 0.698±0.039 | 0.98±0.04 / 0.329±0.030 / 0.597±0.042 | 1.00±0.01 / 0.344±0.026 / 0.623±0.040 | 1.00±0.01 / 0.338±0.038 / 0.680±0.073 |

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
| G-BL | 0.0068±0.0055 | 0.0179±0.0093 | 0.0302±0.0095 | 0.0385±0.0110 |
| G-SM | 0.2154±0.0601 | 0.2505±0.0391 | 0.2519±0.0497 | 0.2187±0.0845 |
| GA-P-BL | 0.0068±0.0055 | 0.0179±0.0093 | 0.0302±0.0095 | 0.0385±0.0110 |
| MOEA-2 | 0.1651±0.0559 | 0.0290±0.0110 | 0.0319±0.0098 | 0.0414±0.0135 |
| MOEA-3 | 0.2498±0.0972 | 0.0315±0.0131 | 0.0332±0.0109 | 0.0428±0.0135 |

**Note:** Higher HV = better overall multi-objective performance.

## Overall HV (across all 200 scenarios)

| Solver | HV Mean | HV Std |
|:---|---:|---:|
| G-BL | 0.0234 | 0.0150 |
| G-SM | 0.2341 | 0.0627 |
| GA-P-BL | 0.0234 | 0.0151 |
| MOEA-2 | 0.0668 | 0.0642 |
| MOEA-3 | 0.0893 | 0.1053 |
