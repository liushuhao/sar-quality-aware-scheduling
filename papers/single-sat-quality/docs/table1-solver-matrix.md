# Table 1: Solver Performance Matrix (per Scenario Group)

**5 solvers × 4 groups × 3 metrics** (mean ± 1 SD across 50 seeds per group)

| Solver | S1 (N=20) | S2 (N=100) | S3 (N=300) | S4 (N=500) |
|:---|:---|:---|:---|:---|
| G-BL | 1.00 / 0.541±0.068 / 0.32±0.17 | 1.00 / 0.540±0.059 / 0.31±0.15 | 1.00 / 0.578±0.025 / 0.217±0.071 | 1.00 / 0.580±0.025 / 0.210±0.071 |
| G-SM | 0.85±0.16 / 0.474±0.077 / 0.44±0.16 | 0.74±0.09 / 0.454±0.059 / 0.46±0.12 | 0.64±0.07 / 0.501±0.034 / 0.361±0.073 | 0.61±0.09 / 0.506±0.035 / 0.356±0.075 |
| GA-P-BL | 1.09±0.14 / 0.550±0.069 / 0.29±0.18 | 1.28±0.22 / 0.548±0.056 / 0.28±0.14 | 1.15±0.15 / 0.579±0.024 / 0.203±0.072 | 1.17±0.27 / 0.579±0.025 / 0.203±0.073 |
| MOEA-2 | 0.68±0.29 / 0.585±0.055 / 0.24±0.15 | 0.82±0.25 / 0.564±0.044 / 0.24±0.13 | 0.98±0.04 / 0.587±0.021 / 0.175±0.065 | 0.98±0.03 / 0.589±0.021 / 0.169±0.066 |
| MOEA-3 | 0.66±0.30 / 0.569±0.066 / 0.29±0.15 | 0.83±0.24 / 0.561±0.044 / 0.24±0.13 | 0.97±0.03 / 0.587±0.021 / 0.175±0.066 | 0.97±0.04 / 0.589±0.021 / 0.170±0.067 |

**Footnotes:**
- **f1\*** = coverage fraction relative to G-BL baseline (f1_raw / f1_G-BL)
- **f2** = comprehensive geometric quality (lower is better)
- **f3** = NESZ radiation quality (lower is better)
- Each cell shows: **f1\* ± SD / f2 ± SD / f3 ± SD**
- All statistics computed across 50 random seeds per scenario group

## Hypervolume (HV) by Solver and Group

Normalized 3D HV (reference point: [0, 0, 0], all objectives maximized after normalization).

| Solver | S1 (N=20) | S2 (N=100) | S3 (N=300) | S4 (N=500) |
|:---|:---|:---|:---|:---|
| G-BL | 0.1338±0.0257 | 0.1431±0.0191 | 0.1423±0.0061 | 0.1414±0.0054 |
| G-SM | 0.1661±0.0447 | 0.1941±0.0356 | 0.2219±0.0195 | 0.2242±0.0236 |
| GA-P-BL | 0.1214±0.0314 | 0.1062±0.0353 | 0.1232±0.0239 | 0.1188±0.0394 |
| MOEA-2 | 0.2023±0.0391 | 0.1787±0.0399 | 0.1469±0.0072 | 0.1465±0.0059 |
| MOEA-3 | 0.2175±0.0521 | 0.1789±0.0441 | 0.1480±0.0056 | 0.1468±0.0071 |

**Note:** Higher HV = better overall multi-objective performance.

## Overall HV (across all 200 scenarios)

| Solver | HV Mean | HV Std |
|:---|---:|---:|
| G-BL | 0.1401 | 0.0168 |
| G-SM | 0.2016 | 0.0400 |
| GA-P-BL | 0.1174 | 0.0334 |
| MOEA-2 | 0.1686 | 0.0366 |
| MOEA-3 | 0.1728 | 0.0448 |
