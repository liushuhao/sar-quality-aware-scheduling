"""Analytical null distribution of r = corr(f2, f3) under uniform geometry.

f2 = sin(theta) * cos(psi)           (geometric quality)
f3 = cos^3(theta) * cos^3(psi)       (radiometric quality)

Null model: theta ~ U[th1, th2], psi ~ U[-pm, pm], independent.
Envelope: th in [15, 50] deg, psi in [-45, 45] deg (from manifest + C7).

All moments are closed-form integrals; this script evaluates them exactly
(no Monte Carlo). r_null quantifies the definitional correlation floor.
"""
import math

DEG = math.pi / 180.0
TH1, TH2 = 15.0 * DEG, 50.0 * DEG
PSI_M = 45.0 * DEG


def e_sin_theta(th1, th2):
    """E[sin(theta)], theta ~ U[th1, th2]."""
    return (math.cos(th1) - math.cos(th2)) / (th2 - th1)


def e_cos3_theta(th1, th2):
    """E[cos^3(theta)]. int cos^3 = sin - sin^3/3."""
    def F(t):
        s = math.sin(t)
        return s - s ** 3 / 3.0
    return (F(th2) - F(th1)) / (th2 - th1)


def e_sin_cos3_theta(th1, th2):
    """E[sin(theta)*cos^3(theta)] = E[cos^3 * sin] -> int = -cos^4/4."""
    def F(t):
        c = math.cos(t)
        return -c ** 4 / 4.0
    return (F(th2) - F(th1)) / (th2 - th1)


def e_sin2_theta(th1, th2):
    """E[sin^2(theta)]. int sin^2 = t/2 - sin(2t)/4."""
    def F(t):
        return t / 2.0 - math.sin(2 * t) / 4.0
    return (F(th2) - F(th1)) / (th2 - th1)


def e_cos6_theta(th1, th2):
    """E[cos^6(theta)] via recurrence: int cos^n = (1/n)cos^(n-1) sin + (n-1)/n int cos^(n-2)."""
    def int_cos6(t):
        c, s = math.cos(t), math.sin(t)
        c2, c4 = c * c, c ** 4
        s2 = s * s
        # int cos^2 = t/2 + sin(2t)/4
        i2 = t / 2.0 + math.sin(2 * t) / 4.0
        # int cos^4 = (1/4)cos^3 sin + (3/4) int cos^2
        i4 = c ** 3 * s / 4.0 + 0.75 * i2
        # int cos^6 = (1/6)cos^5 sin + (5/6) int cos^4
        i6 = c ** 5 * s / 6.0 + (5.0 / 6.0) * i4
        return i6
    return (int_cos6(th2) - int_cos6(th1)) / (th2 - th1)


def e_cos_psi(pm):
    """E[cos(psi)], psi ~ U[-pm, pm]. Even: = (1/pm) int_0^pm cos."""
    return math.sin(pm) / pm


def e_cos2_psi(pm):
    """E[cos^2(psi)] = (1/pm) int_0^pm cos^2 = 1/2 + sin(2pm)/(4pm)."""
    return 0.5 + math.sin(2 * pm) / (4 * pm)


def e_cos3_psi(pm):
    """E[cos^3(psi)] = (1/pm) int_0^pm cos^3 = sin(pm)/pm - sin^3(pm)/(3pm)."""
    s = math.sin(pm)
    return s / pm - s ** 3 / (3.0 * pm)


def e_cos4_psi(pm):
    """E[cos^4(psi)] = (1/pm) int_0^pm cos^4 = 3/8 + sin(2pm)/(2pm) + sin(4pm)/(32pm)."""
    return 3.0 / 8.0 + math.sin(2 * pm) / (4 * pm) + math.sin(4 * pm) / (32 * pm)


def e_cos6_psi(pm):
    """E[cos^6(psi)] via recurrence, even function -> (1/pm) int_0^pm cos^6."""
    def int_cos6(t):
        c, s = math.cos(t), math.sin(t)
        i2 = t / 2.0 + math.sin(2 * t) / 4.0
        i4 = c ** 3 * s / 4.0 + 0.75 * i2
        i6 = c ** 5 * s / 6.0 + (5.0 / 6.0) * i4
        return i6
    return int_cos6(pm) / pm


# theta-moments
m_sin = e_sin_theta(TH1, TH2)
m_cos3 = e_cos3_theta(TH1, TH2)
m_sin_cos3 = e_sin_cos3_theta(TH1, TH2)
m_sin2 = e_sin2_theta(TH1, TH2)
m_cos6 = e_cos6_theta(TH1, TH2)

# psi-moments
v1 = e_cos_psi(PSI_M)
v2 = e_cos2_psi(PSI_M)
v3 = e_cos3_psi(PSI_M)
v4 = e_cos4_psi(PSI_M)
v6 = e_cos6_psi(PSI_M)

# f2, f3 moments (theta, psi independent -> product factorizes)
E_f2 = m_sin * v1
E_f3 = m_cos3 * v3
E_f2f3 = m_sin_cos3 * v4
E_f2sq = m_sin2 * v2
E_f3sq = m_cos6 * v6

Cov = E_f2f3 - E_f2 * E_f3
Var_f2 = E_f2sq - E_f2 ** 2
Var_f3 = E_f3sq - E_f3 ** 2
r_null = Cov / math.sqrt(Var_f2 * Var_f3)

print("=== theta moments (theta in [15,50] deg) ===")
print(f"  E[sin th]         = {m_sin:.6f}")
print(f"  E[cos^3 th]       = {m_cos3:.6f}")
print(f"  E[sin th cos^3 th]= {m_sin_cos3:.6f}")
print(f"  E[sin^2 th]       = {m_sin2:.6f}")
print(f"  E[cos^6 th]       = {m_cos6:.6f}")
print("=== psi moments (psi in [-45,45] deg) ===")
print(f"  E[v]   = {v1:.6f}")
print(f"  E[v^2] = {v2:.6f}")
print(f"  E[v^3] = {v3:.6f}")
print(f"  E[v^4] = {v4:.6f}")
print(f"  E[v^6] = {v6:.6f}")
print("=== f2, f3 moments ===")
print(f"  E[f2]    = {E_f2:.6f}")
print(f"  E[f3]    = {E_f3:.6f}")
print(f"  E[f2 f3] = {E_f2f3:.6f}")
print(f"  E[f2^2]  = {E_f2sq:.6f}")
print(f"  E[f3^2]  = {E_f3sq:.6f}")
print(f"  Var(f2) = {Var_f2:.6e}")
print(f"  Var(f3) = {Var_f3:.6e}")
print(f"  Cov     = {Cov:.6e}")
print()
print(f"  r_null  = {r_null:.4f}")
print(f"  r_emp   = 0.93 -- 0.98")
print(f"  1 - r_null = {1 - r_null:.4f}  (definitional residual)")
print(f"  1 - r_emp  = 0.02 -- 0.07  (observed residual)")
print()
print("=== axis decomposition (which angle drives the correlation?) ===")
# theta-axis covariance: g=sin th, A=cos^3 th. sin inc in th, cos^3 dec -> NEGATIVE
cov_gA = m_sin_cos3 - m_sin * m_cos3
# psi-axis covariance: h=cos psi, B=cos^3 psi. both inc in cos -> POSITIVE
cov_hB = v4 - v1 * v3
print(f"  Cov_theta(sin th, cos^3 th) = {cov_gA:+.6f}  (theta-axis, NEGATIVE)")
print(f"  Cov_psi(cos psi, cos^3 psi) = {cov_hB:+.6f}  (psi-axis, POSITIVE)")
# Cov(f2,f3) = Cov_gA*Cov_hB + Cov_gA*E[h]E[B] + Cov_hB*E[g]E[A]
cov_check = cov_gA * cov_hB + cov_gA * v1 * v3 + cov_hB * m_sin * m_cos3
print(f"  Cov(f2,f3) decomposed = {cov_check:+.6e}  (matches Cov above)")
# axis-only limits
# theta-only (psi fixed at mean -> cancels): r = corr(sin th, cos^3 th) over uniform th
def corr_moments(eg, eA, egA, eg2, eA2):
    cov = egA - eg * eA
    varg = eg2 - eg ** 2
    varA = eA2 - eA ** 2
    return cov / math.sqrt(varg * varA) if varg * varA > 0 else float('nan')

# need E[cos^6 th] already (m_cos6) for E[A^2]; E[sin^2]=m_sin2 for E[g^2]
r_theta_only = corr_moments(m_sin, m_cos3, m_sin_cos3, m_sin2, m_cos6)
# psi-only: corr(cos psi, cos^3 psi) needs E[cos^2]=v2, E[cos^6]=v6, E[cos^4]=v4
r_psi_only = corr_moments(v1, v3, v4, v2, v6)
print(f"  r_theta_only = {r_theta_only:+.4f}  (theta-axis limit, expect ~-1)")
print(f"  r_psi_only   = {r_psi_only:+.4f}  (psi-axis limit, expect ~+1)")
print()
print("Interpretation:")
print(f"  empirical r = +0.93 to +0.98 means PSI axis dominates (both f2,f3 want low squint).")
print(f"  theta axis is the GENUINE CONFLICT (f2 wants high th, f3 wants low th).")
print(f"  r_null under uniform geometry = {r_null:+.4f}: baseline if scheduler did nothing.")
