# Cross-Solver Audit Report — 20260822_205834

**Paper:** `small-paper-ijae.tex`

## Results

- ✅ Pass: 70
- ❌ Fail: 0
- ⚠ Warn: 5
- 👻 Orphan: 0

### ✅ Passes

  ✓ baselines_200.json: 200 scenario entries
  ✓ baselines: all entries have required b1/b3 fields
  ✓ moea_3obj: 300 entries
  ✓ moea_3obj: all entries have required fields
  ✓ moea_2obj: 400 entries
  ✓ moea_2obj: all entries have required fields
  ✓ scenario keys: 200 common across all 3 solvers
  ✓ GA-P-BL _progress.json exists (will check schema separately)
  ✓ Table2 G-BL S1 f1*: paper=1.0±0.0, data=1.0000±0.0000 [OK]
  ✓ Table2 G-BL S1 f2: paper=0.295±0.037, data=0.2948±0.0374 [OK]
  ✓ Table2 G-BL S1 f3: paper=0.497±0.044, data=0.4974±0.0438 [OK]
  ✓ Table2 G-SM S1 f1*: paper=0.51±0.16, data=0.5094±0.1645 [OK]
  ✓ Table2 G-SM S1 f2: paper=0.389±0.086, data=0.3895±0.0860 [OK]
  ✓ Table2 G-SM S1 f3: paper=0.722±0.058, data=0.7218±0.0579 [OK]
  ✓ Table2 MOEA-2 S1 f2: paper=0.394±0.059, data=0.3929±0.0552 [OK]
  ✓ Table2 MOEA-2 S1 f3: paper=0.654±0.038, data=0.6574±0.0400 [OK]
  ✓ Table2 MOEA-3 S1 f1*: paper=0.85±0.12, data=0.8502±0.1229 [OK]
  ✓ Table2 MOEA-3 S1 f2: paper=0.377±0.05, data=0.3762±0.0498 [OK]
  ✓ Table2 MOEA-3 S1 f3: paper=0.699±0.037, data=0.6985±0.0391 [OK]
  ✓ Table2 G-BL S2 f1*: paper=1.0±0.0, data=1.0000±0.0000 [OK]
  ✓ Table2 G-BL S2 f2: paper=0.317±0.026, data=0.3172±0.0263 [OK]
  ✓ Table2 G-BL S2 f3: paper=0.561±0.06, data=0.5611±0.0603 [OK]
  ✓ Table2 G-SM S2 f1*: paper=0.35±0.09, data=0.3534±0.0895 [OK]
  ✓ Table2 G-SM S2 f2: paper=0.357±0.078, data=0.3568±0.0783 [OK]
  ✓ Table2 G-SM S2 f3: paper=0.735±0.055, data=0.7346±0.0554 [OK]
  ✓ Table2 MOEA-2 S2 f1*: paper=0.99±0.03, data=0.9812±0.0289 [OK]
  ✓ Table2 MOEA-2 S2 f2: paper=0.328±0.03, data=0.3287±0.0296 [OK]
  ✓ Table2 MOEA-2 S2 f3: paper=0.589±0.045, data=0.5894±0.0440 [OK]
  ✓ Table2 MOEA-3 S2 f1*: paper=0.98±0.04, data=0.9764±0.0401 [OK]
  ✓ Table2 MOEA-3 S2 f2: paper=0.329±0.03, data=0.3289±0.0296 [OK]
  ✓ Table2 MOEA-3 S2 f3: paper=0.597±0.042, data=0.5965±0.0422 [OK]
  ✓ Table2 G-BL S3 f1*: paper=1.0±0.0, data=1.0000±0.0000 [OK]
  ✓ Table2 G-BL S3 f2: paper=0.342±0.026, data=0.3420±0.0264 [OK]
  ✓ Table2 G-BL S3 f3: paper=0.616±0.042, data=0.6165±0.0421 [OK]
  ✓ Table2 G-SM S3 f1*: paper=0.29±0.04, data=0.2927±0.0438 [OK]
  ✓ Table2 G-SM S3 f2: paper=0.317±0.055, data=0.3173±0.0553 [OK]
  ✓ Table2 G-SM S3 f3: paper=0.756±0.036, data=0.7558±0.0362 [OK]
  ✓ Table2 MOEA-2 S3 f1*: paper=1.0±0.0, data=0.9991±0.0029 [OK]
  ✓ Table2 MOEA-2 S3 f2: paper=0.343±0.026, data=0.3434±0.0262 [OK]
  ✓ Table2 MOEA-2 S3 f3: paper=0.622±0.04, data=0.6216±0.0400 [OK]
  ✓ Table2 MOEA-3 S3 f1*: paper=1.0±0.01, data=0.9979±0.0052 [OK]
  ✓ Table2 MOEA-3 S3 f2: paper=0.344±0.026, data=0.3436±0.0263 [OK]
  ✓ Table2 MOEA-3 S3 f3: paper=0.623±0.04, data=0.6227±0.0399 [OK]
  ✓ Table2 G-BL S4 f1*: paper=1.0±0.0, data=1.0000±0.0000 [OK]
  ✓ Table2 G-BL S4 f2: paper=0.336±0.039, data=0.3364±0.0385 [OK]
  ✓ Table2 G-BL S4 f3: paper=0.675±0.074, data=0.6754±0.0738 [OK]
  ✓ Table2 G-SM S4 f1*: paper=0.37±0.12, data=0.3727±0.1248 [OK]
  ✓ Table2 G-SM S4 f2: paper=0.291±0.067, data=0.2910±0.0674 [OK]
  ✓ Table2 G-SM S4 f3: paper=0.786±0.046, data=0.7863±0.0464 [OK]
  ✓ Table2 MOEA-2 S4 f1*: paper=1.0±0.01, data=0.9972±0.0073 [OK]
  ✓ Table2 MOEA-2 S4 f2: paper=0.338±0.038, data=0.3375±0.0384 [OK]
  ✓ Table2 MOEA-2 S4 f3: paper=0.68±0.073, data=0.6796±0.0731 [OK]
  ✓ Table2 MOEA-3 S4 f1*: paper=1.0±0.01, data=0.9965±0.0081 [OK]
  ✓ Table2 MOEA-3 S4 f2: paper=0.338±0.038, data=0.3379±0.0379 [OK]
  ✓ Table2 MOEA-3 S4 f3: paper=0.68±0.073, data=0.6804±0.0731 [OK]
  ✓ Table5 S1 f1*: paper=0.86±0.14, data=0.859±0.135
  ✓ Table5 S1 f2 improvement: paper=33.7%, data=33.30%
  ✓ Table5 S1 % f1*<0.95: paper=80%, data=80%
  ✓ Table5 S2 f1*: paper=0.985±0.03, data=0.981±0.029
  ✓ Table5 S2 f2 improvement: paper=3.5%, data=3.61%
  ✓ Table5 S2 % f1*<0.95: paper=10%, data=10%
  ✓ Table5 S3 f1*: paper=0.999±0.0, data=0.999±0.003
  ✓ Table5 S3 f2 improvement: paper=0.4%, data=0.41%
  ✓ Table5 S3 % f1*<0.95: paper=0%, data=0%
  ✓ Table5 S4 f1*: paper=0.996±0.01, data=0.997±0.007
  ✓ Table5 S4 f2 improvement: paper=0.4%, data=0.32%
  ✓ Table5 S4 % f1*<0.95: paper=0%, data=0%
  ✓ MOEA-2 S4 f3 exists: 50 entries, mean=0.6796±0.0731
  ✓ MOEA-3 S4 f3 exists: 50 entries, mean=0.6804±0.0731
  ✓ Scenario count: paper=200, data=200 unique baselines entries

### ⚠ Warnings

  ⚠ moea_3obj has 100 scenarios not in baselines (first 5: ['S5/S5-A_seed00.pkl', 'S5/S5-A_seed01.pkl', 'S5/S5-A_seed02.pkl', 'S5/S5-A_seed03.pkl', 'S5/S5-A_seed04.pkl'])
  ⚠ moea_2obj has 200 scenarios not in baselines (first 5: ['S5/S5-A_seed00.pkl', 'S5/S5-A_seed01.pkl', 'S5/S5-A_seed02.pkl', 'S5/S5-A_seed03.pkl', 'S5/S5-A_seed04.pkl'])
  ⚠ Table2 MOEA-2 S1 f1*: paper=0.86±0.14, data=0.8589±0.1348 [MISMATCH]
  ⚠ MOEA-2 S4 f3: paper says 0.169±0.066, actual 0.6796±0.0731
  ⚠ MOEA-3 S4 f3: paper says 0.170±0.066, actual 0.6804±0.0731

