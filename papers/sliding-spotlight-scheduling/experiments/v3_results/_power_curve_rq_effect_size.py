import math
try:
    from scipy import stats
    HAVE= True
except ImportError:
    HAVE = False
import statistics

df = 9
crit = 1.8331  # t_.95,9 one-sided alpha=.05
tsum = crit + 0.8834  # + t_.80,9  (MDE formula consistency check)

strata = {"R2F": 5.67, "R3H": 16.14}
deltas = [2, 3, 4, 4.87, 6.0, 8.0, 10.0, 11.99, 12.13, 13.87, 16.0, 20.0]

# sanity: reproduce MDE80
for k, sd in strata.items():
    print(f"# check MDE80 {k}: {(crit+0.8834)*sd/math.sqrt(10):.2f}")

def power(delta, sd):
    se = sd / math.sqrt(10)
    ncp = delta / se
    if HAVE:
        return 1 - stats.nct.cdf(crit, df, ncp)
    # normal approx fallback
    return 0.5*(1+math.erf((ncp-crit)/math.sqrt(2)))

def n_for_80(delta, sd):
    # n such that (tsum*sd/sqrt(n)) <= delta
    return math.ceil((tsum*sd/delta)**2)

hdr = "delta(dB) | " + " | ".join(f"{k} power" for k in strata)
print(hdr); print("-"*len(hdr))
for d in deltas:
    row = f"{d:>8.2f}  | " + " | ".join(f"{power(d, sd):>8.3f}" for sd in strata.values())
    print(row)
print()
for d in [6.0, 9.75, 11.99]:
    print(f"n seeds for 80% power @ {d} dB: " + ", ".join(f"{k}={n_for_80(d, sd)}" for k, sd in strata.items()))
print("HAVE_scipy:", HAVE)
