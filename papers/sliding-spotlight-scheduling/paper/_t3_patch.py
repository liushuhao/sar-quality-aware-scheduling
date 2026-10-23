import io

p = 'main.tex'
s = io.open(p, encoding='utf-8').read()
BS = chr(92)
NL = chr(10)

def rep(old, new, n=1):
    global s
    c = s.count(old)
    assert c == n, f"anchor x{c} (want {n}): {old[:70]}"
    s = s.replace(old, new)

# ---- E5: nomenclature (after frontmatter, before Introduction) ----
nomen = (
    NL + BS + "section*{Nomenclature}" + NL
    + BS + "noindent" + BS + "begin{tabular}{@{}ll@{" + BS + "extracolsep{" + BS + "fill}}@{}}" + NL
    + "$A$ & sliding factor ($=r_0/(R_0+r_0)=1-k$) " + BS + BS + " $A_{\\mathrm{task}}$ & task-level sliding factor \\\\" + NL
    + "$D$ & antenna azimuth length & $k$ & rotation-centre parameter \\\\" + NL
    + "$R_0$ & aperture-centre slant range & $r_0$ & rotation-centre-to-scene-centre distance \\\\" + NL
    + "$v_s$ & inertial scene velocity & $T$ & dwell duration (SAT) \\\\" + NL
    + "$\\rho_a$ & azimuth resolution & $\\rho_{\\mathrm{rg}}$ & ground-range resolution \\\\" + NL
    + "$\\rho_{\\mathrm{req}}$ & required azimuth resolution & $\\rho_{a,\\mathrm{ach}}$ & squint-achieved azimuth resolution \\\\" + NL
    + "$g_T$ & dwell-gain ratio & $f_q$ & quality index \\\\" + NL
    + "$f_1$ & served priority fraction & $s$ & demand-tightening factor \\\\" + NL
    + "$\\tau$ & start-time fraction gene & $t_{\\mathrm{man}}$ & maneuver time \\\\" + NL
    + "$d_\\psi$ & inter-task squint difference & AASR & azimuth ambiguity-to-signal ratio \\\\" + NL
    + "PRF & pulse repetition frequency & NESZ & noise-equivalent sigma zero \\\\" + NL
    + "STR/SLS/SPT & stripmap / sliding spotlight / spotlight & SAT & synthetic-aperture time \\\\" + NL
    + "C1--C5 & constraint families (Section~" + BS + "ref{sec:constraints}) & S1--S3 & frozen shape criteria (Section~" + BS + "ref{sec:hypotheses}) \\\\" + NL
    + BS + "end{tabular}" + NL
    + BS + "vspace{0.6em}" + NL + NL)
rep(BS + "end{frontmatter}" + NL + NL + BS + "section{Introduction}",
    BS + "end{frontmatter}" + NL + nomen + BS + "section{Introduction}")

# ---- P7: wall-clock line ----
rep("Every point of the grid is read at the single registered budget of 40/60; no budget ladder "
    "is run in this scenario set, and no frontier-richness statement in either direction is made "
    "from these artifacts.",
    "Every point of the grid is read at the single registered budget of 40/60; no budget ladder "
    "is run in this scenario set, and no frontier-richness statement in either direction is made "
    "from these artifacts. The wall-clock cost of one unit at that budget is 5--15~s "
    "(single-threaded; median 4.9~s for the 20-task control, 10.0~s for the 50-task and 15.3~s "
    "for the 100-task family on the registered workstation), so the full 270-unit sweep with the "
    "counterfactual arm is a single-afternoon computation.")

# ---- P8: continuation sentence (conclusion) ----
rep("The sensor-layer question of resolution against swath, the joint mode-and-time formulation, "
    "the recomputation of the serial bound under this scenario set, and an operational-cost "
    "evaluation are future work rather than results.",
    "The sensor-layer question of resolution against swath, the joint mode-and-time formulation, "
    "the recomputation of the serial bound under this scenario set, and an operational-cost "
    "evaluation are future work rather than results. Two continuations follow directly from the "
    "counterfactual: onboard replanning against realised dwells, where the fixed-dwell failure "
    "mode bites hardest, and constellation-level tier management, where the requirement tiers "
    "this paper tightens are priced products.")

io.open(p, 'w', encoding='utf-8', newline=NL).write(s)
print("Tier-3 patch applied (nomenclature + wall-clock + continuations)")
