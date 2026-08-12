# Table 1: Solver Performance Matrix (per Scenario Group)

**5 solvers × 4 groups × 3 metrics** (mean ± 1 SD across 50 seeds per group)

| Solver | S1 (N=20) | S2 (N=100) | S3 (N=300) | S4 (N=500) |
|:---|:---|:---|:---|:---|
| G-BL | 1.00 / 0.295±0.037 / 0.497±0.044 | 1.00 / 0.317±0.026 / 0.561±0.060 | 1.00 / 0.342±0.026 / 0.616±0.042 | 1.00 / 0.336±0.039 / 0.675±0.074 |
| G-SM | 0.51±0.16 / 0.389±0.086 / 0.722±0.058 | 0.35±0.09 / 0.357±0.078 / 0.735±0.055 | 0.29±0.04 / 0.317±0.055 / 0.756±0.036 | 0.37±0.12 / 0.291±0.067 / 0.786±0.046 |
| GA-P-BL | 1.00±0.02 / 0.295±0.037 / 0.498±0.044 | 1.00 / 0.317±0.026 / 0.561±0.060 | 1.00 / 0.342±0.026 / 0.616±0.042 | 1.00 / 0.336±0.039 / 0.675±0.074 |
| MOEA-2 | 0.86±0.14 / 0.394±0.059 / 0.654±0.038 | 0.99±0.03 / 0.328±0.030 / 0.589±0.045 | 1.00±0.00 / 0.343±0.026 / 0.622±0.040 | 1.00±0.01 / 0.338±0.038 / 0.680±0.073 |
| MOEA-3 | 0.85±0.11 / 0.377±0.050 / 0.699±0.037 | 0.98±0.04 / 0.329±0.030 / 0.597±0.042 | 1.00±0.01 / 0.344±0.026 / 0.623±0.040 | 1.00±0.01 / 0.338±0.038 / 0.680±0.073 |

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
| G-BL | 0.0536±0.0075 | 0.0415±0.0087 | 0.0316±0.0070 | 0.0236±0.0098 |
| G-SM | 0.0509±0.0165 | 0.0673±0.0117 | 0.0761±0.0131 | 0.0585±0.0309 |
| GA-P-BL | 0.0117±0.0081 | 0.0143±0.0046 | 0.0162±0.0020 | 0.0167±0.0026 |
| MOEA-2 | 0.0816±0.0245 | 0.0449±0.0141 | 0.0313±0.0066 | 0.0243±0.0092 |
| MOEA-3 | 0.0957±0.0299 | 0.0461±0.0146 | 0.0318±0.0069 | 0.0252±0.0099 |

**Note:** Higher HV = better overall multi-objective performance.

## Overall HV (across all 200 scenarios)

| Solver | HV Mean | HV Std |
|:---|---:|---:|
| G-BL | 0.0376 | 0.0139 |
| G-SM | 0.0632 | 0.0216 |
| GA-P-BL | 0.0147 | 0.0053 |
| MOEA-2 | 0.0455 | 0.0268 |
| MOEA-3 | 0.0497 | 0.0328 |
