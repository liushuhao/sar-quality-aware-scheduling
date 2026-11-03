# Confirmation Round — paper1 panel 2026-11-03

## Canary

1. Read-only: I must not modify, create, or delete any file except my one report file.
2. I never invent a finding, and never mark SUPPORTED without having seen the quote in the manuscript.
3. I quote the manuscript line I matched, with its tex line number.
4. No network access.
5. Stdout is at most 5 lines; the report goes to the file.

Reading-method note (disclosed, not a deviation from scope): the `Read` tool was blocked in
this session by a failing pre-tool-use hook (`context-mode/hooks/pretooluse.mjs`, missing Git
Bash). Files were read with PowerShell `Get-Content` in bounded line ranges with line numbers
preserved, and matched with `Select-String`. No PDF was opened; nothing under `experiments/` or
`results/` was read. Each seat report was read once, top to bottom, and its findings were
verified before moving to the next report.

Scope of the check: 65 findings across the five seats (EIC 12, R1 13, R2 12, R3 12, DA 16).
Every quoted string was located in `small-paper-ijae.tex`, `sections/_ablation_section.tex` or
`highlights.tex`; none was invented, and **no quote was misquoted**. Where a finding asserted a
number, I compared it with what the manuscript prints at that location.

## Verdict table

| Seat | Finding | Severity | Verdict | Evidence (tex line + 1-line quote) |
|---|---|---|---|---|
| EIC | EIC-01 highlights credit third objective with whole solver gain | MAJOR | SUPPORTED | highlights.tex:22 "Third objective adds +40\% (NESZ-ordering index)"; tex:885 "MOEA-3 raises $f_3$ by $+40\%$ ($0.698$ vs.\ $0.497$)"; the third objective's own margin is tex:1190 "$+6.2\%$" / tex:1196 "$+4.9\%$" (MOEA-3 vs MOEA-2) |
| EIC | EIC-02 evidence never labelled simulated in front matter | MAJOR | SUPPORTED | tex:42 "Across 200 scenarios spanning 20 to 500 targets"; tex:712 "abstracted as a generic C-band Stripmap SAR"; "synthetic" occurs once, tex:1474 |
| EIC | EIC-03 hot-start condition attached asymmetrically | MAJOR | SUPPORTED | tex:49-51 abstract clause; tex:1269-1270 "the sparse-regime margins are anchored-front values"; tex:1483-1484 narrower "coverage convergence … conditional" |
| EIC | EIC-04 no prior method reimplemented but delta claimed | MAJOR | SUPPORTED | tex:248-250 "no existing SAR scheduling method treats … as decomposed optimization objectives"; tex:605-606 "A comparison across algorithmic families … is left to future work" |
| EIC | EIC-05 title says NESZ, body sells ordering proxy | MINOR | SUPPORTED | tex:24 title; tex:426-428 "the suppressed $\sin\theta$ factor varies by roughly $2.4\times$ … read as a geometry proxy" |
| EIC | EIC-06 abstract radiometric headline vs Table 1 | MINOR | SUPPORTED | tex:906 "G-SM & … & $0.722 \pm 0.058$" vs tex:909 "MOEA-3 & … & $0.698 \pm 0.039$"; tex:927 "0.786" vs tex:930 "0.680" |
| EIC | EIC-07 "single-pass" redefined | MINOR | SUPPORTED | tex:81-82 "``single-pass'' denotes a single satellite operating over a two-orbit scheduling horizon" |
| EIC | EIC-08 solver/scenario labels used before definition | MINOR | SUPPORTED | tex:128 "never worse than G-BL"; tex:133 "MOEA-3 raises $f_3$ by $+40\%$"; tex:747-748 "S7 at $N=150$ and S8 at $N=200$"; S5/S6 first appear at ablation:38-41 |
| EIC | EIC-09 abstract internal jargon | MINOR | SUPPORTED | tex:45-46 "under a matched radiometric-aware knee rule"; tex:53 "independent-angle null of $-0.60$"; tex:54 "dilutes" |
| EIC | EIC-10 ablation missing from abstract/highlights | MINOR | SUPPORTED | tex:179-180 "four objective-function variants over six scenario classes, 300 scenarios per variant"; absent from tex:35-59 and highlights.tex:16-26 |
| EIC | EIC-11 two garbled sentences | MINOR | SUPPORTED | tex:1338-1340 "the found G-BL-seeded front … while offering multiple quality-coverage configurations, is compressed"; tex:1529 "the found fronts converge" |
| EIC | EIC-12 availability / AI declaration accuracy | MINOR | SUPPORTED | tex:1568-1569 "The companion repository is publicly available at"; tex:1547-1548 "for manuscript preparation and revision assistance only" |
| R1 | R1-01 GA-P-BL control degenerate | MAJOR | SUPPORTED | tex:658-660 "numerically identical to G-BL in 199 of 200 scenarios"; tex:1375-1376 "claims therefore concern the marginal value of adding physical objectives" |
| R1 | R1-02 two incompatible reproducibility models | MAJOR | SUPPORTED | tex:851-852 "operator-level random draws are not pinned"; tex:1566 "fixed seeds and configurations"; tex:854-857 five repeats on one scenario per class |
| R1 | R1-03 variant-C correlation contradicts ψ-only limit | MAJOR | SUPPORTED | tex:1129-1130 "in the $\psi$-only limit both rise … ($r_\psi = +0.997$)"; tex:1172-1173 "the correlation holds at $-0.65$"; ablation:16-17 "$f_2=\cos\psi$, $f_3=\cos^3\psi$" |
| R1 | R1-04 dense boundary confounded with 200-task ceiling | MAJOR | SUPPORTED | tex:559-562 "arbitrary units … the same ceiling of 200"; tex:1279 "coverage stays flat at 200 of the 300"; tex:1298-1299 "shifts quality by at most $+1.64\%$" |
| R1 | R1-05 timing vs target re-selection not separated | MAJOR | SUPPORTED | tex:1522-1523 "re-optimising observation times buys large quality gains"; ablation:130-132 "mean $\sim 1.5^\circ$ … squint angle sweeps $\sim 20$--$35^\circ$" |
| R1 | R1-06 no coverage-matched / exchange-rate comparison | MAJOR | SUPPORTED | tex:1423-1425 "the knee point trades $14\%$ coverage for $+33\%$ $f_2$"; my grep for matched/equal-coverage wording returned zero hits in both tex files |
| R1 | R1-07 effect-size scale vs thresholds | MINOR | SUPPORTED | tex:798-800 "$\delta_{\text{pairs}} = (W - L)/n$"; tex:984 "Cliff's $\delta = +0.99$" |
| R1 | R1-08 95% interval from 20 shuffles | MINOR | SUPPORTED | tex:1114 "(95\% shuffle interval within $\pm 0.02$, 20 shuffles per class)" |
| R1 | R1-09 omnibus test on HV | MINOR | SUPPORTED | tex:1353-1354 "The Friedman test on pooled HV"; tex:785 "HV is not interpreted as a standalone quality judgment" |
| R1 | R1-10 multiple-comparison family shifts, excludes S5/S6 | MINOR | SUPPORTED | tex:1360-1363 "$\alpha=0.05/12$"; ablation:162-166 "$p = 1.6\times10^{-13}$ … $1.8\times10^{-15}$ … $1.2\times10^{-5}$" outside it |
| R1 | R1-11 "quantitative rule" over-generalises solver class | MINOR | SUPPORTED | tex:57-59 sentence; tex:1040 "Scale sensitivity of MOEA-2 vs.\ G-BL" (boundary is MOEA-2 only) |
| R1 | R1-12 highlights misattribute +40% | MINOR | DUPLICATE (EIC-01) | highlights.tex:22, same sentence, same complaint |
| R1 | R1-13 unverifiable statements | MINOR | SUPPORTED | tex:856 "reproduce bit-identically at S1 and S4"; tex:1487-1488 "currently lacks a mechanistic explanation" |
| R2 | R2-01 incidence channel inert vs three-objective claim | MAJOR | SUPPORTED | ablation:128-129 "Variant C (no incidence) produces no measurable change in any reported metric"; ablation:65-70 A $0.376/0.698$ vs C $0.375/0.703$ |
| R2 | R2-02 mean-per-task rewards dropping bad geometry | MAJOR | SUPPORTED | tex:365-367 "independent of the number of scheduled tasks $m$"; ablation:69 C reaches $f_2=0.375$ vs G-BL tex:905 $0.295$ |
| R2 | R2-03 quality baseline pinned to window edge; G-SM beats MOEA | MAJOR | SUPPORTED | tex:612-616 "earliest feasible time … rather than through any quality criterion"; tex:1410 "G-BL $f_2$ rises from $0.295$ to $0.405$ to $0.448$" |
| R2 | R2-04 squint / Doppler / PRF inconsistency | MAJOR | SUPPORTED | tex:521-525 "$f_{\text{dc}}$ … order $10^2$\,kHz … versus a PRF of order $10^0$--$10^1$\,kHz"; tex:385 "$\rho_{\text{az}} = D/(2\cos\psi)$"; bandwidth $56.5$\,MHz at tex:717 |
| R2 | R2-05 suppressed sinθ factor stated in opposite directions | MAJOR | UNSUPPORTED | The three statements are one operation seen from the NESZ side and the quality-index side: tex:418 "suppresses the $\sin\theta$ factor", tex:432 "dividing by $\sin\theta$", tex:434-435 "with the retained factor". Because $f_3$ is an inverse-NESZ index, restoring $\sin\theta$ into NESZ *is* dividing $f_3$; no contradiction |
| R2 | R2-06 "single-pass" collides with SAR usage | MINOR | DUPLICATE (EIC-07) | tex:81-82 |
| R2 | R2-07 quality indices never in physical units | MINOR | SUPPORTED | tex:391 "Higher $f_2$ indicates a smaller per-task ground-pixel-area factor"; tex:406 "$f_3$ … lower per-task NESZ factor"; tex:1386 "roughly a $25\%$ smaller per-task geometric area factor" |
| R2 | R2-08 null choice anchored on most negative baseline | MINOR | SUPPORTED | tex:1113-1117 three nulls, permutation adopted; tex:52-53 abstract quotes $-0.62$ against $-0.60$ |
| R2 | R2-09 placeholders + fixed dwell not carried forward | MINOR | SUPPORTED | tex:560 "(arbitrary units)"; tex:1495-1496 "dwell time is fixed at 30\,s" |
| R2 | R2-10 opposite sign conventions in one table | MINOR | SUPPORTED | ablation:43-50 "the opposite sign of the $\Delta f_1^*\%$ column" |
| R2 | R2-11 "physics-derived vs proxy" contrast overstated | MINOR | SUPPORTED | tex:242-244 "a scalar attribute or coarse proxy rather than a decomposed physical objective"; tex:238-240 ChangZhou proxy |
| R2 | R2-12 SAR operational constraints absent | MINOR | SUPPORTED | §3.3 constraints are C1–C4 only (tex:500-570); grep for PRF/echo-window/duty/ambiguity returns only tex:523 (physical-scope aside) and tex:1494 (a budget caveat). Note: this finding supplies no literal quote |
| R3 | R3-01 baseline ignores the objective it is scored on | MAJOR | SUPPORTED | tex:612-613 "sorted by earliest start time $t_{\text{start}}$"; the whole G-BL definition (tex:608-623) never reads $p_i$ |
| R3 | R3-02 coverage cost never says which targets are lost | MAJOR | SUPPORTED | tex:885 "$15\%$ coverage cost ($f_1^* = 0.85$)"; the only priority evidence is ablation:56 "$f_1/n$ is the mean priority weight of the selected tasks" |
| R3 | R3-03 "operational densities" is a synthetic ceiling | MAJOR | SUPPORTED | tex:1528-1530 "It vanishes at operational densities"; tex:561-564 "same ceiling of 200 … 20 of 50 G-BL schedules at S3 and 27 of 50 at S4" |
| R3 | R3-04 platform hypothetical; own Doppler numbers remove mechanism | MAJOR | SUPPORTED | tex:521-525; tex:529-530 "absolute performance claims for platforms without Doppler compensation at large squint are out of scope"; tex:1414-1415 conditional |
| R3 | R3-05 quality scored at an instant over a moving dwell | MAJOR | SUPPORTED | tex:761-762 "quality indices are then evaluated at each scheduled acquisition time"; tex:765-767 "median change of squint … $11^\circ$, 95th percentile $15^\circ$" |
| R3 | R3-06 mean-per-task decouples from priority | MINOR | SUPPORTED | tex:392-394 "unweighted means … orthogonal to the priority weights used in $f_1$" |
| R3 | R3-07 incidence objective carries no solver behaviour | MINOR | DUPLICATE (R2-01) | ablation:128-129, same sentence and same complaint |
| R3 | R3-08 cheapest competitor never tested | MINOR | SUPPORTED | tex:1395-1396 "this gain comes from the one-line squint-minimization heuristic"; tex:770 "22\,s (S1), 66\,s (S2), 220\,s (S3), and 260\,s (S4)" |
| R3 | R3-09 two contradictory HV statements | MINOR | SUPPORTED | tex:966-967 "HV rewards front cardinality as well as front quality"; tex:1223 "insensitive to cardinality" |
| R3 | R3-10 null spans a factor of two, one end anchored | MINOR | DUPLICATE (R2-08) | tex:1113-1116, same null-choice defect |
| R3 | R3-11 reproducibility tension + two availability channels | MINOR | DUPLICATE (R1-02) | tex:850-853 vs tex:854-856; tex:1567-1569 same evidence |
| R3 | R3-12 highlights overstate third objective | MINOR | DUPLICATE (EIC-01) | highlights.tex:22 |
| DA | DA-01 density boundary sold as physics vs own "initialisation" text | CRITICAL | SUPPORTED | tex:1530-1531 "because coverage pressure removes the freedom to move acquisitions" vs tex:1346-1347 "conditional on the hot start, not a structural property" and tex:1087-1088 "not the feasible surface as a whole" |
| DA | DA-02 highlights misattribute whole gain | CRITICAL | DUPLICATE (EIC-01) | highlights.tex:22 |
| DA | DA-03 non-redundancy mechanism contradicted by own ablation | CRITICAL | SUPPORTED | tex:476-478 "leaves the $\theta_{\text{elev}}$ trade-off, whose exploitation is what saturates"; ablation:128-137 variant C inert. Same root fact as R2-01 but a distinct contradiction at a different locus |
| DA | DA-04 one-line heuristic beats method where headline lives | MAJOR | DUPLICATE (R1-06; also R2-03) | Table 1 tex:906/909 and tex:913/916 |
| DA | DA-05 HV described both ways; demotion self-serving | MAJOR | DUPLICATE (R3-09) | tex:782-783, tex:966-967, tex:1223 |
| DA | DA-06 variant correlations unreadable from printed definitions | MAJOR | DUPLICATE (R1-03) | tex:1129-1132 vs tex:1172-1173 |
| DA | DA-07 boundary is artefact of arbitrary constant | MAJOR | DUPLICATE (R1-04; also R3-03) | tex:559-564; tex:1279-1280 |
| DA | DA-08 coverage cost measured against weak baseline | MAJOR | DUPLICATE (R3-01) | tex:611-613 |
| DA | DA-09 mean-per-task improvement by dropping targets | MAJOR | DUPLICATE (R2-02) | tex:365-367 |
| DA | DA-10 headline gain model-dependent by 2.4× | MAJOR | SUPPORTED | tex:433-436 "enlarges … from $+40\%$ to $+94\%$ … the proxy reading is conservative"; the abstract carries only the $+40\%$ (tex:44) |
| DA | DA-11 one scenario per class bounds stochasticity | MAJOR | DUPLICATE (R1-02) | tex:849-860 |
| DA | DA-12 reported front dominated by own control's points | MAJOR | SUPPORTED | tex:1264-1265 "$0.505$ vs.\ $0.395$ at S1, $+28\%$"; tex:833-834 "the best-$f_2$ point reaches $f_2 = 0.449$"; tex:1185-1186 "All fronts reported here are approximate" |
| DA | DA-13 two printed $f_2$ ranges cannot both hold | MINOR | SUPPORTED | tex:1180 "with pooled range $0.65$ in every class" vs tex:808 "($f_2$: $0.11$--$0.56$)" — a $0.65$ span inside a $0.45$ global span |
| DA | DA-14 correlation calibres do not line up | MINOR | SUPPORTED | tex:54-55 "-0.13 and -0.23 at high density" vs tex:742-743 "-0.80, -0.23, -0.15, -0.31 from S1 to S4, the caliber of" |
| DA | DA-15 dispersion swamps HV summary | MINOR | SUPPORTED | tex:944 "MOEA-3 & $0.0893$ & $0.1053$" (SD 1.2× the mean) |
| DA | DA-16 multiple-comparison families defined two ways | MINOR | DUPLICATE (R1-10) | tex:1360-1363; ablation:56; ablation:110 "applied within each reported metric" |

## Findings that need author attention first

1. **EIC-01 / DA-02 / R1-12 / R3-12 — highlights misattribute the +40%.** Four of five seats, the
   one sentence a reader may read without the body, and a roughly eight-fold overstatement of the
   third objective's measured contribution (+4.9% controlled, +6.2% on the solvers' own knees).
2. **DA-01 / EIC-03 — the Conclusion states a causal explanation the Discussion retracts.** tex:1530
   says the boundary exists "because coverage pressure removes the freedom to move acquisitions";
   tex:1346 says the same convergence is "conditional on the hot start, not a structural property".
   A referee who reads §6.6 will find the abstract and conclusion overstating in the opposite
   direction from every other finding in the paper.
3. **R1-03 / DA-06 — variant C's correlation is impossible under the printed definitions.** With
   `f_2 = cos ψ` and `f_3 = cos³ ψ`, a negative per-task correlation cannot arise; the $-0.65$ shows
   the numbers are computed on a different metric pair that the text never names. This sits under
   the section that decides whether the physics is real.
4. **R2-04 / R3-04 — the PRF sentence will stop a SAR referee.** "A PRF of order $10^0$–$10^1$ kHz"
   for a 56.5 MHz-bandwidth instrument is not physical; the same paragraph then invokes yaw
   steering to absorb a geometric squint. One sentence, high cost.
5. **R2-01 / R3-07 / DA-03 — the ablation says the incidence channel is inert while the
   contribution list sells a three-objective decomposition.** Three seats, same table cells.
6. **R3-01 / DA-08 — the coverage anchor never reads the priority weight it is scored on.** Every
   coverage-cost number in the paper is a ratio to it, so the price of quality is measured against
   a deliberately weak comparator.
7. **DA-13 — two printed numbers cannot both be true** (pooled $f_2$ range 0.65 versus a global
   span of 0.11–0.56). This is an arithmetic contradiction, not a judgement call.
8. **R1-04 / R3-03 / DA-07 — both resource caps resolve to the same 200-task ceiling**, and the
   perturbation control pins every tested S3 run at it, so part of the density boundary is
   arithmetic.
9. **R1-02 / R3-11 / DA-11 — "operator draws are not pinned" versus "fixed seeds" and
   "bit-identically"**, on a four-scenario basis. Cheap to fix with one paragraph plus a larger
   replication subset.
10. **EIC-02 — the front matter never says the scenarios are simulated.** One clause fixes it and
    removes the only reading an ASR editor could call not fully candid.

## Corroborated clusters (>=2 seats, same defect)

- **Highlights +40% misattribution** — seats: EIC-01, R1-12, R3-12, DA-02.
- **Density boundary: physics vs hot-start artefact / asymmetric scoping** — seats: EIC-03, DA-01.
- **Variant B/C correlation unreadable or impossible** — seats: R1-03, DA-06.
- **Incidence channel inert vs three-objective framing** — seats: R2-01, R3-07, DA-03.
- **200-task resource ceiling confounds the dense boundary** — seats: R1-04, R3-03, DA-07 (and
  R2-09 on the same constants).
- **Reproducibility contract self-contradictory; 4-scenario replication check** — seats: R1-02,
  R3-11, DA-11.
- **Weak coverage anchor (earliest-start greedy, never reads p_i)** — seats: R3-01, DA-08.
- **One-line G-SM heuristic beats the MOEA on quality; no coverage-matched comparison** — seats:
  R1-06, R2-03, DA-04.
- **Mean-per-task quality can be raised by dropping poorly-geometried targets** — seats: R2-02,
  DA-09.
- **Hypervolume described as cardinality-sensitive and -insensitive** — seats: R3-09, DA-05.
- **Null model choice anchored on the most negative baseline** — seats: R2-08, R3-10.
- **"Single-pass" collides with SAR usage** — seats: EIC-07, R2-06.
- **Multiple-comparison family changes between sections / excludes S5-S6** — seats: R1-10, DA-16.
- **Squint / Doppler-centroid / achievable-envelope physics** — seats: R2-04, R3-04.

## Errors in the reports themselves

- **No misquote anywhere.** Every string quoted by the five seats was located verbatim in the
  manuscript, the ablation section or `highlights.tex`. Reported line numbers matched on every
  finding I checked, and every numeric claim about a printed value matched the printed value.
- **R2-05 is the one substantive argument error** (hence UNSUPPORTED above): the seat reads
  "suppresses", "dividing by" and "retained factor" as three conflicting operations, but because
  $f_3$ is an inverse-NESZ index they are one operation described from two sides. Its residual
  valid points — no printed algebraic step from +40% to +94%, and no discussion of
  ambiguity-limited NESZ — are a fair editorial ask.
- **EIC-04 count imprecision**: it says Related Work "names five prior SAR MOEA schedulers"
  (tex:225-244), but six works are named there (Chang2022Gaofen, Wei2025MONP, Kramer2025SARVis,
  Yao2024Bilevel, ChangZhou2025Memetic, Wu2019NSGA3Formation). Does not affect the finding.
- **EIC-11 recurrence claim is loose**: its Conclusion quote ("the found fronts converge",
  tex:1529) is the same attributive oddity as the §7.1 sentence but not the same
  displaced-participle construction, so "it recurs ... reads as a drafting habit" overstates.
  The §7.1 sentence itself is correctly quoted and the grammar point stands.
- **R1-07 overreach**: its clause "the same numeric threshold is being applied to a statistic with
  roughly twice the scale" is contradicted by tex:805, which applies Romano's thresholds to the
  conventional unpaired form "wherever both are quoted". The naming observation still stands.
- **DA-15 arithmetic slip**: its quote of tex:944 is exact ($0.0893 \pm 0.1053$), but the derived
  claim "a mean whose SD is 2.4× its value" is wrong — $0.1053/0.0893 = 1.18$. The qualitative
  point (dispersion exceeds the mean) survives, so the finding is still SUPPORTED.
- **R2-12 supplies no literal quote**, which departs from the panel's own canary #2. I verified the
  absence myself (grep for PRF / echo-window / duty / ambiguity / downlink over both tex files),
  so the finding survives; the format does not.
