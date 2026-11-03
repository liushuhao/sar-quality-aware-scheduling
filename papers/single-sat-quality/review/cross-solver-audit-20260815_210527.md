# Cross-Solver Audit Report — 20260815_210527

**Paper:** `small-paper-ijae.tex`

## Results

- ✅ Pass: 14
- ❌ Fail: 19
- ⚠ Warn: 6
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
  ✓ Table2 G-BL S4 f1*: paper=1.0±None, data=1.0000±0.0000 [OK]
  ✓ Table5 S1 % f1*<0.95: paper=82%, data=80%
  ✓ Table5 S2 f2 improvement: paper=4.4%, data=3.61%
  ✓ MOEA-2 S4 f3 exists: 50 entries, mean=0.6796±0.0731
  ✓ MOEA-3 S4 f3 exists: 50 entries, mean=0.6804±0.0731
  ✓ Scenario count: paper=200, data=200 unique baselines entries

### ❌ Fails

  ✗ Table2 G-BL S4 f2: paper=0.58±0.025, data=0.3364±0.0385 [MISMATCH]
  ✗ Table2 G-BL S4 f3: paper=0.21±0.071, data=0.6754±0.0738 [MISMATCH]
  ✗ Table2 G-SM S4 f1*: paper=0.61±0.09, data=0.3727±0.1248 [MISMATCH]
  ✗ Table2 G-SM S4 f2: paper=0.506±0.035, data=0.2910±0.0674 [MISMATCH]
  ✗ Table2 G-SM S4 f3: paper=0.356±0.075, data=0.7863±0.0464 [MISMATCH]
  ✗ Table2 MOEA-2 S4 f2: paper=0.589±0.021, data=0.3375±0.0384 [MISMATCH]
  ✗ Table2 MOEA-2 S4 f3: paper=0.169±0.066, data=0.6796±0.0731 [MISMATCH]
  ✗ Table2 MOEA-3 S4 f2: paper=0.589±0.021, data=0.3379±0.0379 [MISMATCH]
  ✗ Table2 MOEA-3 S4 f3: paper=0.17±0.066, data=0.6804±0.0731 [MISMATCH]
  ✗ Table5 S1 f1*: paper=0.69±0.3, data=0.859±0.135
  ✗ Table5 S1 f2 improvement: paper=8.0%, data=33.30%
  ✗ Table5 S2 f1*: paper=0.83±0.23, data=0.981±0.029
  ✗ Table5 S2 % f1*<0.95: paper=64%, data=10%
  ✗ Table5 S3 f1*: paper=0.97±0.04, data=0.999±0.003
  ✗ Table5 S3 f2 improvement: paper=1.6%, data=0.41%
  ✗ Table5 S3 % f1*<0.95: paper=14%, data=0%
  ✗ Table5 S4 f1*: paper=0.98±0.05, data=0.997±0.007
  ✗ Table5 S4 f2 improvement: paper=1.5%, data=0.32%
  ✗ Table5 S4 % f1*<0.95: paper=20%, data=0%

### ⚠ Warnings

  ⚠ moea_3obj has 100 scenarios not in baselines (first 5: ['S5/S5-A_seed00.pkl', 'S5/S5-A_seed01.pkl', 'S5/S5-A_seed02.pkl', 'S5/S5-A_seed03.pkl', 'S5/S5-A_seed04.pkl'])
  ⚠ moea_2obj has 200 scenarios not in baselines (first 5: ['S5/S5-A_seed00.pkl', 'S5/S5-A_seed01.pkl', 'S5/S5-A_seed02.pkl', 'S5/S5-A_seed03.pkl', 'S5/S5-A_seed04.pkl'])
  ⚠ Table2 MOEA-2 S4 f1*: paper=0.98±0.05, data=0.9972±0.0073 [MISMATCH]
  ⚠ Table2 MOEA-3 S4 f1*: paper=0.98±0.06, data=0.9965±0.0081 [MISMATCH]
  ⚠ MOEA-2 S4 f3: paper says 0.169±0.066, actual 0.6796±0.0731
  ⚠ MOEA-3 S4 f3: paper says 0.170±0.066, actual 0.6804±0.0731

