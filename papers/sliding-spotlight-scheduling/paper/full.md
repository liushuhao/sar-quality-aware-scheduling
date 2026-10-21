<!--block:B0001-->
# Abstract (placeholder)

<!--block:B0002-->
Agile Earth-observation satellites that steer a single antenna across stripmap, sliding-spotlight, and spotlight modes are usually scheduled under an exogenous, fixed imaging duration. For a sliding-spotlight platform that assumption fails in a quantifiable way: the dwell is produced by the mode continuum and by the selected start, and it enters the inter-task transfer constraint that decides what a pass can carry. This paper makes the dwell endogenous and carries the order resolution requirement as a per-task hard constraint: the mode parameters follow the order where the mode has them, so that the resolution delivered at the selected start equals the order, while the stripmap tier stays at its antenna floor. Served priority is the only objective; a fulfillment ratio, computed on the library quality caliber and averaged over all tie-set members, is a reported reading and not an optimization target. A frozen nine-point demand grid scales every order from 0.8 to 2.0 without regenerating the scenario population or re-routing modes, and three shape criteria (monotone, saturation, tight arm) are frozen in advance and reported with their failures. The dense 100-task family R3H pays a coverage cost at the order point of 4.15 percentage points against its own saturation. The single-orbit family R1C meets a floor step: at $s=0.8$ it admits no feasible individual in 10 of 10 seeds. R1C at $s=0.9$ reads a median coverage of 0.540. The 50-task family R2F pays a coverage cost at the order point of 2.36 percentage points against its own saturation. Over the nine points 477,308 task instances are served, with no delivery-identity violation recorded by the evaluator. Conclusions are scoped to order sensitivity under a fixed mode assignment.


<!--block:B0003-->
# 1. Introduction

<!--block:B0004-->
## 1.1 Motivation

<!--block:B0005-->
Agile Earth-observation satellites steered by a single antenna can operate their synthetic aperture radar (SAR) in a continuum of imaging modes: stripmap, sliding spotlight, and spotlight are one physical mode family parameterised by where the beam's virtual rotation centre sits. Which point of that continuum a task receives is not a free stylistic choice --- it is fixed by the requested resolution, the scene, and the geometry of the pass --- and it determines how long the satellite must dwell on the scene. Scheduling therefore cannot treat the imaging duration as an exogenous constant, as the classical agile-scheduling literature largely does \cite{long2024deep,qin2024multisatellite,li2024earth}: in sliding-spotlight operation the dwell is produced by the imaging physics, it changes from task to task, and it feeds back into how many tasks a pass can carry and at what image quality. In that literature the resolution requirement, when it appears at all, is an attribute of the request that is settled before the schedule is built: the observation duration is a task attribute fixed in advance \cite{chen2024learning,qin2024multisatellite}, and on the SAR side the required resolution already fixes the synthetic-aperture time and steering span of a designed observation \cite{kim2020optimal}.

<!--block:B0006-->
This paper studies that coupling on a single satellite in a regime of single-pass dense task clusters under true orbit geometry. Scheduling decisions select which tasks to serve and when to start imaging within each task's visibility windows; the mode follows from the product order, and the dwell, the maneuver, and the image quality follow from the mode and the window. The systematic study of scenario density as an experimental axis belongs to the thesis companion rather than this paper.

<!--block:B0007-->
Two discipline risks shape the methodology as much as the physics does. First, a measured effect on coverage can be a property of the *search* rather than of the *scenario*: in this world the greedy anchor already attains the family maximum in 258 of the 260 sweep units, so the coverage response reported here is produced by the mode and parameter adaptation rather than by the optimiser's ability to find it. Second, quality statements are only as good as their measurement calibers: several formally plausible formulations (an ambiguity sum that includes the principal image, a range resolution that varies per task, a squint-dependent routing resolution) are registered as not used, and the paper says so where it matters.

<!--block:B0008-->
## 1.2 Contributions

<!--block:B0009-->
Following the registered narrative frame --- registered here meaning fixed in the project's preregistered specification before drafting began --- the paper's contributions are three: the platform that carries the order into the physics, the measured coverage cost of tightening that order, and the discipline that keeps both claims testable:

<!--block:B0010-->
1. **An enabling physics-to-scheduler platform** (the platform leg). A three-mode continuum formalisation (Section 3) that carries the mode choice, the scene-level dwell closures, the order resolution as a per-task hard constraint, and the maneuver-coupled feasibility predicates into one scheduling loop: the imaging mode is resolved from the product order, the mode parameters follow the order where the mode has them so that the delivered resolution equals the order at the selected start, and the dwell duration is a consequence of the order rather than a constant.

2. **The coverage cost of tightening the order** (main result). Three scenario families swept over a frozen nine-point demand grid at a single search budget and under a frozen mode assignment: a floor step on the stripmap family, a non-monotone response on the 50-task family whose two dips are traced to the greedy anchor construction, order-point costs of 4.15 and 2.36 percentage points against each family's own saturation, and 477,308 served task instances with no delivery-identity violation (Section 6).

3. **A discipline that keeps the result falsifiable** (methodology). Shape criteria frozen before this scenario world's data were read and reported with their failures rather than re-tuned to the data; caliber labels that keep the two quality calibers apart and keep the fulfillment ratio a reading; and an explicit separation of the search face from the construction face --- the anchor is coverage-optimal in 258 of 260 units, so the coverage response is a construction result, not a search finding (Sections 5.3 and 6).

<!--block:B0011-->
Throughout, the trade-off the study claims is the resolution-versus-dwell-time axis of the mode continuum; the antenna-design question of resolution against swath is a sensor-layer consequence that this simulation does not model, and it is treated as a limitation with future work (Section 7.1). The serial-bound reading of how many dwell-coupled tasks a pass carries is stated with a per-pass caliber and without a number, because its serial bound has not been recomputed in this scenario world; it is carried as a scope statement (Section 7.1) rather than as a result.

<!--block:B0012-->
The move this paper makes is to take the resolution off the request and put it into the constraint set: the order is what the scheduler must satisfy task by task, the mode parameters are what carry it into the physics, and the coverage loss is what the paper measures. The claim is scoped to the literature surveyed below: the survey rests on the project's curated literature pool --- a converted and catalogued bibliography of the field plus an incremental paper-search sweep over the months preceding writing, whose nearest neighbours Section 2 engages directly. What the tested coupling in fact produced in this scenario world is reported in Section 6: the coverage--demand curves of the three families, the floor step and the two anchor-carried dips, the order-point costs against each family's own saturation, and the demand-satisfaction count --- the platform's value is that each of these readings is registered and reproducible.

<!--block:B0013-->
## 1.3 Paper organisation

<!--block:B0014-->
Section 2 positions the work along sliding-spotlight imaging, agile-satellite scheduling, and quality-aware scheduling. Section 3 formalises geometry, modes, dwell, the order as a per-task constraint, and the demand-tightening axis. Section 4 describes the solver. Section 5 presents the scenario world and the frozen analysis design; Section 6 reports the coverage--demand curves and the demand-satisfaction readings; Section 7 discusses mechanisms, literature contrasts, and the full limitation set; Section 8 concludes.


<!--block:B0015-->
# 2. Related Work

<!--block:B0016-->
This section positions the paper along three lines: sliding-spotlight SAR imaging (where the dwell physics lives), agile Earth-observation satellite scheduling (where the fixed-dwell assumption lives), and quality-aware scheduling (where image quality enters planning decisions).

<!--block:B0017-->
## 2.1 Sliding-spotlight and spotlight SAR imaging

<!--block:B0018-->
The sliding-spotlight family is standardly formulated as steering about a fixed virtual rotation centre: the TerraSAR-X extended chirp scaling processor is built on that geometry \cite{mittermayer2003sliding}, the baseband azimuth-scaling processor of Prats et al. handles both sliding spotlight and terrain observation by progressive scans (TOPS) with the rotation centre beyond the swath \cite{prats2010processing}, and Kim et al. derive the attitude-maneuver and saturation-avoidance time formulas for squint staring and sliding spotlight on the same geometry \cite{kim2021optimal}. Operational descriptions sometimes state the steering as a constant angular rate --- Zhang et al.'s Gaofen-3 (GF-3) account does so explicitly and describes it as a small-angle simplification of the same geometry \cite{zhang2018sliding} --- and processing work that pushes to high squint is likewise explicit that the linearised steering assumption breaks there \cite{guo2011extended,ren2025high}. This paper adopts the rotation-centre formulation throughout (Section 3.1); its scheduling windows reach squints where only the exact geometry is valid, which is why the two readings must not be mixed.

<!--block:B0019-->
Two quantitative anchors from the imaging line matter to this study, and both are quoted as their own platforms' literature values. First, Kim et al.'s Table 2 defines a $\pm 12^{\circ}$ task envelope for its reference mission; the design envelopes registered in this paper --- $\pm 45^{\circ}$ for stripmap/spotlight and $\pm 26.9^{\circ}$ (a registered conservative value, a design choice) for sliding spotlight --- are separate fields and are never merged with the literature task domain \cite{kim2021optimal}. Second, Song et al. report for their sparse-imaging platform that the azimuth ambiguity-to-signal ratio is anti-correlated with the PRF and degrades as the scan angle grows (by about 8.6 dB beyond 1° of scan for conventional sliding spotlight, and about 15.2 dB for the sparse variant), alongside a range-ambiguity reduction of about 10.7 dB for the sparse mode \cite{song2025spaceborne}; as Section 7.2 shows, the direction of the ambiguity-versus-squint dependence in our model is the opposite of that literature anchor, and the contrast is a result of this paper rather than a contradiction to be smoothed over. The standard ambiguity and resolution relations otherwise follow the textbook treatment \cite{cumming2005digital}.

<!--block:B0020-->
The dwell time itself is treated in the imaging literature as a deterministic function of mode and geometry --- Kim et al.'s saturation-avoidance time chain is exactly that \cite{kim2021optimal} --- but it stops at the imaging problem boundary: the scheduling layer above it is not part of that literature's concern.

<!--block:B0021-->
## 2.2 Agile Earth-observation satellite scheduling

<!--block:B0022-->
The agile-scheduling literature is broad and mature: hybrid genetic-simulated-annealing planners for moving-target observation \cite{qin2024multisatellite}, deep-reinforcement-learning planners for large mission-planning instances \cite{long2024deep,chen2024learning,zhang2025deep}, adaptive large-neighborhood search with learned guidance or with neighbourhood repair \cite{du2025satellite,he2018a}, constraint-programming formulations for super-agile platforms \cite{caleiras2026a}, memetic and multi-chromosome cooperative planners \cite{wang2024memetic,wang2024research}, and profit models in which the observation value depends on the interval between revisits \cite{li2024earth,peng2019agile}. Across these formulations one structural assumption is essentially universal: the imaging duration of a task is an exogenous constant of the task, known before the scheduler runs. The scheduler then packs fixed-length intervals into time lines, and whatever the objective --- profit, coverage, latency --- the duration never feeds back.

<!--block:B0023-->
For an agile SAR platform in sliding-spotlight operation that assumption is false in a specific, quantifiable way: the dwell is produced by the mode physics (the tan-exact closure chain of Section 3.2), it varies per task with the assigned mode and the squint of the selected start, and it enters the inter-task transfer constraint that decides what else the pass can carry. This paper makes the dwell endogenous, carries the order resolution as a per-task constraint on that dwell, and measures what tightening the order costs in coverage.

<!--block:B0024-->
## 2.3 Quality-aware scheduling

<!--block:B0025-->
Image quality reaches the planning literature in three roles, and the difference between them and this paper is worth stating plainly. Image-quality research on the SAR side is largely an assessment discipline --- fidelity metrics, quality checkers, and radiometric corrections applied to formed images \cite{cumming2005digital}. Imaging-mode design starts from a resolution requirement and trades it against swath \cite{song2025spaceborne}, and mission-level SAR planning computes the required synthetic-aperture time and steering span from the required resolution and the incidence angle \cite{kim2020optimal}. Multi-objective Earth-observation and SAR mission studies optimise more than one criterion explicitly alongside coverage or priority \cite{chang2021integrated,kim2019multi,kim2020optimal}; that line of work exists, it is not the line this paper takes, and nothing here claims its absence. What changes here is the *placement* of quality. It leaves the objective set: the per-mode index of Section 3.3 states a platform capability and supplies the numerator of a reported fulfillment ratio, and it carries no selection pressure on the search.

<!--block:B0026-->
## 2.4 Positioning

<!--block:B0027-->
The three lines meet at a seam rather than at a gap, and the seam is narrow. The imaging line supplies the resolution-to-aperture chain and stops at the imaging problem boundary: a required resolution and incidence angle fix the synthetic-aperture time and steering span of a designed observation \cite{kim2020optimal}, and the sliding-spotlight processors deliver such a design at a fixed rotation centre \cite{mittermayer2003sliding,prats2010processing}. The scheduling line supplies the packing machinery for tasks whose duration is an attribute fixed before the schedule is built \cite{chen2024learning,qin2024multisatellite}. The quality-aware line supplies assessment calibers and mission-level weightings \cite{cumming2005digital,kim2019multi}. This paper puts the order resolution into the scheduling constraint set: the mode parameters follow the order where the mode has them, the resolution delivered at the selected start equals the order, and the coverage cost of tightening the order is measured on a frozen grid under a fixed mode assignment (Section 3 and Section 6). Sections 3--6 build that problem on a registered, preregistered footing --- the demand grid, the shape criteria and the caliber labels are fixed before this world's data were read --- and report what the tightening costs.


<!--block:B0028-->
# 3. Problem Formulation and Scheduling Model

<!--block:B0029-->
This section formalises the observation geometry, the three-mode imaging library, the dwell-duration closures, the per-mode image-quality model, and the constraints and objectives of the scheduling problem.

<!--block:B0030-->
## 3.1 Observation geometry and imaging modes

<!--block:B0031-->
We adopt the X-band reference platform of Kim et al. \cite{kim2021optimal}: altitude $h=570$ km, inclination $45^{\circ}$, wavelength $\lambda=0.031$ m, azimuth beam width $\theta_a=0.36^{\circ}$, and a square scene of 5 km side length. The derived geometry is $D=\lambda/\theta_a=4.9338$ m (antenna azimuth length), aperture-centre slant range $R_0=775.4$ km, and inertial scene velocity $v_s=7578.05$ m/s. Each task is a scene; the scheduled quantity is *when* to image it, not *whether* to reconfigure the payload.

<!--block:B0032-->
The three imaging modes --- stripmap (STR), sliding spotlight (SLS), and spotlight (SPT) --- are treated as a single-parameter continuum over the position of a fixed virtual rotation centre \cite{kim2021optimal,zhang2018sliding,song2025spaceborne}: writing $k$ for the sliding factor with $A=1-k$, $k\to 0$ places the rotation centre at infinity (stripmap, parallel antenna axis), $0<k<1$ places it below the surface beyond the scene (sliding spotlight), and $k\to 1$ places it at the target (spotlight). The registered operating point of this study is $k=0.797317$, i.e. a rotation-centre-to-scene-centre distance $r_0=197119$ m $\approx 197$ km. We stress the symbol discipline that the two distances are dimensionally identical but semantically distinct: $r_0\approx 197$ km is the rotation-centre-to-scene-centre distance, whereas $R_0\approx 775.4$ km is the aperture-centre slant range; their ratio is $r_0/R_0=0.254207$, and the two are never interchangeable (Fig. 1).

<!--block:B0033-->
The sliding factor: under the rotation-centre semantics adopted here, $A=r_0/(R_0+r_0)$ \cite{zhang2018sliding}; the form $A=1-R_0 k_\theta/v_g$, with $k_\theta$ the azimuth steering rate and $v_g$ the ground speed (Song Eq.(1)) \cite{song2025spaceborne}, is a restatement within the same rotation-centre model --- for the steering rate that places the rotation centre at $r_0$ --- not an independent literature identity. The per-mode azimuth resolutions at zero squint are $\rho_{a,\mathrm{STR}}=D/2=2.4669$ m, $\rho_{a,\mathrm{SLS}}=A\,D/2=0.5000$ m, and $\rho_{a,\mathrm{SPT}}=\lambda/(2\beta_{\mathrm{span}})=0.3000$ m with $\beta_{\mathrm{span}}=2.9603^{\circ}$ the spotlight sweep span (library design constant).

<!--block:B0034-->
Under the rotation-centre semantics the spectral compression factor is a constant at every squint. Presenting the Doppler rates in the aperture-range form,
$$K_a=\frac{2v_s^{2}\cos^{3}\bar\psi}{\lambda R_0},\qquad
K_c=\frac{2v_s^{2}\cos^{3}\bar\psi}{\lambda\,(R_0+r_0)},\qquad
a_{\mathrm{res}}=1-\frac{K_c}{K_a}\equiv A,$$
the $\cos^3$ factors cancel at beam-centre crossing, so $a_{\mathrm{res}}$ does not degrade with squint; the sliding-spotlight azimuth resolution is the design constant $A\,D_a/2$ at all squints \cite{zhang2018sliding,song2025spaceborne}.

<!--block:B0035-->
The registered squint domains are separate registered fields, listed apart from the literature task envelope of Kim et al. ($\pm 12^{\circ}$, their Table 2 \cite{kim2021optimal}): STR and SPT carry a design domain of $\pm 45^{\circ}$, and SLS carries a registered conservative envelope of ±26.9°. The SLS cap is a *registered conservative value (design choice)* --- antenna steering margin plus frozen-data continuity --- and not a physical boundary: under the rotation-centre semantics $a_{\mathrm{res}}\equiv A>0$ at every squint, so high-squint reachability is limited by the registered cap rather than by mode physics. Two extrapolation disclosures attach to the $45^{\circ}$ design domain: the azimuth-resolution projection correction (resolution-ellipse rotation) is outside the closed form, and the $45^{\circ}$ dwell readings of STR/SPT are extrapolated, because the planar tan-difference closure omits Earth curvature against the full-curvature $R_0$ (Section 7.3).

<!--block:B0036-->
![fig-1 SLS rotation-centre geometry and the three-mode continuum](figures/fig1_modes_geometry.tex){#fig:1}

<!--block:B0037-->
**Caption (fig-1).** Three modes as a single-parameter continuum over the virtual rotation centre (azimuth squint plane, schematic). (a) Stripmap: rotation centre at infinity, uniform antenna axis. (b) Sliding spotlight: rotation centre beyond the scene ($k=0.7973$); $r_0\approx 197$ km = rotation-centre-to-scene-centre distance, $R_0\approx 775.4$ km = aperture-centre slant range, $r_0/R_0=0.254207$; the SLS cap 26.9° is a registered conservative value (design choice), not a physical boundary. (c) Spotlight: rotation centre at the scene centre. Design squint domains listed as separate registered fields: STR/SPT $\pm 45^{\circ}$ (design domain; $45^{\circ}$ dwell readings are extrapolated), SLS ±26.9° (registered conservative value, design choice), and the $\pm 12^{\circ}$ literature task domain of Kim et al. \cite{kim2021optimal}.

<!--block:B0038-->
## 3.2 Dwell duration and visibility windows

<!--block:B0039-->
The dwell of a task is the saturation-avoidance time (SAT) at scene level: the time the beam needs to sweep the full square scene at the task's squint, where $W_a$ denotes the scene (square) size --- 5 km on the reference platform --- entering as a scene-length traversal term. The production closures are the tan-exact Kim Eq.(22)/(24) chain \cite{kim2021optimal}: for STR the scene dwell is the exact tan difference of the beam-edge crossing angles plus the scene traversal $W_a/v_s$; for SLS it is the symmetric construction of Eq.(22)/(24) with the sliding factor in the denominator; for SPT it is the exact Eq.(10)-(11) tan-difference with the library sweep span. A planar closed form with the $\sec^2\bar\psi$ squint correction, $T_{\mathrm{SLS}}=(R_0\theta_a+W_a)/(A\,v_s)\cdot\sec^2\bar\psi$ (scene size inside the correction), survives as the test-time oracle: at the Kim reference squint of $12^{\circ}$ it deviates from the production chain by $+0.4185\%$, and the deviation grows to $+2.1\%$ at the SLS cap and $+5.3\%$ at $45^{\circ}$ --- which is what triggered the kill-test switch from the planar form to the tan-exact chain in the first place. The residual model error is covered by a frozen window-tail pad of 1% of the dwell, a purely conservative margin on the production path. Two provenance notes complete the closure. First, the Kim Eq.(22)/(24) chain is a zero-Doppler-clamped (broadside) attitude construction; applying it at nonzero squint is a registered approximation, and the growth of the planar oracle's deviation with squint, quantified above, is evidence of that modeling gap rather than of numerical noise. Second, the resulting dwell feeds the C2 inter-task transfer requirement that determines pass capacity, which is why the deviation pattern and the frozen window-tail pad are carried with the constraint semantics (Section 7.3) rather than with the numerics.

<!--block:B0040-->
The zero-squint anchors close an identity: $\theta_a/A=\lambda/(2\rho_{a})$ holds at the library design point ($0.006283185307/0.202683397006=0.031000000000$ rad $=\lambda/(2\times 0.5\,\mathrm{m})$) with a full-precision residual of $3.5\times10^{-18}$. The surviving guard of this identity is the pytest fixture `test_duration_models.py::test_identity_theta_a_over_A_equals_lambda_over_2rho`.

<!--block:B0041-->
Each task carries one or more visibility windows produced by ground-track pass enumeration over the scenario span; a window fixes the closest-approach epoch $t_{\mathrm{ca}}$, the per-window slant range, and the earliest/latest feasible imaging start. The decision variable $\tau\in[0,1]$ of a selected task is mapped onto the feasible start interval of its window (Section 4). The squint at the selected start, $\bar\psi$, is measured at the window's geometry.

<!--block:B0042-->
One scheduling-level geometric quantity needs a definition here because it enters the inter-task constraint: the maneuver angle between consecutive tasks $i,j$, $d_\psi=|\psi_i-\psi_j|$, is the difference of their start squints. This is a planar-caliber *lower bound* on the true attitude excursion: it omits the sweep *during imaging* (the antenna keeps steering at $0.4233$–$0.6686\ ^{\circ}/\mathrm{s}$, i.e. $1.7$–$2.7^{\circ}$ over a $4$ s dwell) and the start-squint difference understates the off-vertical attitude compression by 15-25%. The full disclosure of the two-sided understatement and the margin-pad argument is given in Section 7.3.

<!--block:B0043-->
## 3.3 Image quality model

<!--block:B0044-->
The per-task quality index is an inverse-pixel-area form with a range-normalised (non-normalised, $m^{-2}$ caliber) readout, $$f_{Q,i}=\frac{1}{\rho_{\mathrm{rg}}\,\rho_{a}(m_i)}\;g_T(m_i)\,\Big(\frac{R_0}{R}\Big)^{3},$$ where $\rho_{\mathrm{rg}}$ is the ground-range resolution, $\rho_a(m_i)$ the zero-squint azimuth resolution of the assigned mode, and $g_T$ the transmit-path antenna gain term. The $(R_0/R)^3$ normalisation makes the gain term dimensionally explicit at reference range; at $R=R_0$ the identity chain collapses to $f_Q=(g_T/\rho_a)\cdot(1/\rho_{\mathrm{rg}})$ \cite{song2025spaceborne}. A scope note on the name: the index is dominated by its azimuth-resolution term, and no radiometric quantity --- noise-equivalent sigma zero, signal-to-noise ratio, or radiometric resolution --- enters the index; the ambiguity ratio enters separately as an admission constraint, not as a traded objective. "Image quality" in this paper therefore denotes spatial-resolution quality under a gain-shaped multiplier.

<!--block:B0045a-->
The index has two roles in this paper, and neither of them is an optimization target. It states a platform capability, and it supplies the numerator of a reported reading. As a capability statement, at the zero-squint library caliber the per-mode constants are $0.8107$ (STR), $19.7352$ (SLS) and $54.8322$ (SPT) m$^{-2}$: magnitude ratios of $24.3\times$ (SLS over STR), $67.6\times$ (SPT over STR) and $2.8\times$ (SPT over SLS). Because the squint factor cancels inside the gain term (exactly for STR and SLS, and to within $0.07\%$ for SPT across the full envelope), these constants --- not squint-dependent readings --- are what separates the modes on this axis, and they are properties of the mode library rather than results of a schedule.

The reported reading is a fulfillment ratio. For a served task it is the $f_{q}$ at the realised window and the selected start's squint, divided by the best $f_{q}$ the task could reach over all of its windows at zero squint, so the ratio is at most one. It is computed on the library caliber, averaged over all tie-set members rather than read off the anchor solution, and reported as a reading with no optimization role. Its label travels with every number it states: *[library caliber $f_q$ | per-task $f_q$ at the realised window and squint over the zero-squint optimum over all windows | mean over all tie-set members | reported reading, not an optimization target]*.

A descriptive delivered variant is registered beside it (formula-spec §8.17-10):
$$f_{Q,\mathrm{deliv}}=\frac{D}{2\,\rho_{\mathrm{req}}^{2}\cos^{2}\psi_{\mathrm{sel}}\,\rho_{\mathrm{rg}}}.$$
It is a descriptive variant, it is not comparable with the library caliber, and it is never placed in the same table as that caliber. It also has no stripmap domain: stripmap delivers the library floor and a task-level mode-parameter request on that mode raises.

No directional claim is registered between coverage and the fulfillment ratio. Only the coefficient and its sample size are reported, with the caliber named on the same line; the sign is an observation of this world's data, not a property of the mode continuum.

<!--block:B0045-->
Three caliber statements are frozen with this definition. First, $\rho_{\mathrm{rg}}$ is held at the design-anchor constant of $0.5$ m (registered at $45^{\circ}$ incidence, scene-centre semantics); it is not recomputed per task, and the magnitude narrative carries a limitation (Section 7.3). Second, $g_T$ is *self-derived* and *internally verified*: no external literature source carries the noise-equivalent sigma zero (NESZ) equation set for this mode family, so the verification route is the internal identity chain above (and its pytest guard), and the absence of external cross-validation is disclosed. Third, the squint-dependent achieved resolution $\rho_{a,\mathrm{ach}}(m,\bar\psi)=\rho_a(m,0)/\cos\bar\psi$ is registered for reporting; the router consumes the zero-squint constant, and the only bandwidth consumer of $\rho_{a,\mathrm{ach}}$ is the Doppler bandwidth $B_D=v_s\cos\bar\psi/\rho_a(m,0)$ --- there is no consumer of the achieved resolution in mode routing. The projection relation behind the anchor is $\rho_{\mathrm{rg}}=c/(2\,B_{\mathrm{rg}}\sin\eta_i)$ with the range bandwidth $B_{\mathrm{rg}}$ frozen at the design incidence; the planar evaluation layer holds the incidence at that design value, which is why $\rho_{\mathrm{rg}}$ enters the objective as a constant, with the incidence-band variation disclosed separately in Section 7.3.

<!--block:B0046-->
The azimuth ambiguity-to-signal ratio (AASR) is defined with the ambiguity sum *excluding* the *zeroth* (principal-image) term,
$$\mathrm{AASR}=\frac{\sum_{m\neq 0}\int_{-B_D/2+f_{ac}}^{B_D/2+f_{ac}}\big|G\big(f_a+m\cdot\mathrm{PRF}\big)\big|^{2}\,df_a}{\int_{-B_D/2+f_{ac}}^{B_D/2+f_{ac}}\big|G(f_a)\big|^{2}\,df_a},$$
following the standard convention \cite{cumming2005digital}: keeping $m=0$ would place the principal image in its own numerator and force $\mathrm{AASR}\ge 1$ identically. The frequency-axis rescaling by $(1-K_c/K_a)\approx(1-k_\theta R_0/v_g)$ --- a flat-ground bridge between the $K_c$ and $v_g$ forms, per the frozen formula registration --- under rotation-centre steering is what couples the steering geometry into the ambiguity integral \cite{song2025spaceborne}. The displayed integral is Song's general form, with the absolute-centre shift $f_{ac}$ carried in the integration limits; the implementation integrates the same sums about the DC-relative coordinate, where that shift cancels and the absolute centre drops out (Section 7.3). A footnote on the spotlight special case: Song et al.'s spotlight AASR \cite{song2025spaceborne} is the degenerate integral of the same form in which neither numerator nor denominator contains $f_a$ after the rescaling, which is why the SPT ambiguity in our model is squint-invariant. Integration caliber: the ambiguity sum runs over the azimuth-frequency axis alone --- the two-way pattern enters as a function of azimuth frequency, with no cross-range (elevation-plane) pattern factor --- so far-ambiguous-pulse attenuation from the elevation plane is not modeled; the principal effect of that simplification falls on the absolute ambiguity level, and it is registered with the model caveats (Section 7.3).

<!--block:B0047-->
Admission uses a *discrete* worst-case readout, *not continuous* evaluation: the AASR of a task is evaluated at $11$ equally spaced *in-window* samples and the maximum must not exceed the registered $-13$ dB admission threshold at generation time. Feasibility statements in this paper inherit that caliber --- a selection is feasible with respect to the generator's 11-point admission rule, and the evaluator performs no AASR recheck of its own.

<!--block:B0048-->
## 3.4 Constraints and objectives

<!--block:B0049-->
The decision vector of a scenario with $N$ tasks is $x=(s,\tau)\in\{0,1\}^{N}\times[0,1]^{N}$: a selection bit per task and a start-time fraction per selected task. The imaging mode $m_i$ is *not* a decision gene: the pair (required resolution, scene size) is mapped to a mode by the library table, a *system design input with product order semantics* --- the platform is told what product a customer ordered --- and the mode assignment is frozen for the data of this paper (Section 3.5). What the scheduler does inherit from the order is the mode's parameterisation: for sliding spotlight and spotlight the design parameters are functions of $\rho_{\mathrm{req}}$ (constraint C5), so the order reaches the dwell through the mode rather than through a decision variable. Joint mode-and-time allocation is future work.

<!--block:B0050-->
Five constraint families apply.

<!--block:B0051-->
- **C1 (geometry, generation side).** A selected start must fall inside a visibility window of the task whose node satisfies the serviceability evidence: *every* node in the dense domain carries *at least one* in-band transit over the span ($25/25$ nodes over 72 h, per-node reading, recorded in the generation ledger).
- **C2 (inter-task transfer).** For consecutive tasks in start-time order, the gap must cover $(1+0.25)\,T_{\mathrm{dwell},i}+t_{\mathrm{man}}(d_\psi,\omega_{\mathrm{start}},\omega_{\mathrm{end}})+t_{\mathrm{settle}}$: the $25\%$ pad multiplies the *dwell* (Kim's own margin semantics, stated in four places in \cite{kim2021optimal}), never the maneuver, and the settle term is an unpadded measured constant. The conflict predicate uses the bare dwell: pads are scheduling margin, not physical occupancy.
- **C3 (energy/duty).** Per-task duty is normalised against the mode-library envelope reference $T_{\mathrm{env,max}}=10.5830$ s (the largest feasible scene dwell at the envelope-edge squint, attained by SPT) with mode weights STR/SLS/SPT $=1.0/1.15/1.3$.
- **C4 (solid-state memory).** Per-echo bytes follow $\mathrm{PRF}\cdot T\cdot N_r\cdot b_q\cdot 2/8$ with $N_r=10{,}000$ range samples and $b_q=3$ bits per component (TerraSAR-X-style block-adaptive quantisation), normalised against the same per-window reference as C3 (each measured window's own slant range, the registered v3 caliber) under the single production pulse repetition frequency (PRF) of $3630$ Hz.
- **C5 (order resolution, evaluation side).** Every selected task must be imaged at its ordered azimuth resolution $\rho_{\mathrm{req}}$. For sliding spotlight and spotlight the mode parameters are derived from the order at the selected start's squint $\psi_{\mathrm{sel}}$ --- $A_{\mathrm{task}}=2\rho_{\mathrm{req}}\cos\psi_{\mathrm{sel}}/D$ and $\beta_{\mathrm{task}}=\lambda\sec\psi_{\mathrm{sel}}/(2\rho_{\mathrm{req}})$ --- so the delivered resolution equals the order by construction; the identity is re-verified at every dwell evaluation against a $10^{-12}$ tolerance, and a violation raises instead of being scored. The claim is pointwise at that start: inside the imaging interval the delivered resolution follows $\rho_{\mathrm{req}}\cos\psi_{\mathrm{sel}}/\cos\psi(t)$, so this paper does not claim a constant delivered resolution across a whole imaging pass. The stripmap mode (STR) delivers the library floor of 2.4669 m: it has no task-level parameter, so an order finer than the floor has no admissible mode for that task, and a tighter order there is a step at the floor rather than a continuous degradation.

<!--block:B0052-->
Two structural facts about C3/C4 are disclosed as design semantics rather than discovered: both budgets are *structurally* *never binding* inside the squint envelope (their normalised values cannot exceed 1.0 there, so the binding channels are C2 and interval conflicts), and the task priorities that drive the objective are drawn uniformly at random as $\mathrm{randint}(1,10)$, i.e. they carry *no physical* provenance --- they are demand-side bookkeeping, not measured value.

<!--block:B0053-->
The problem maximises the served priority fraction $f_1=\sum_{i\in S}p_i/\sum_{i}p_i$ over the selections $S$ that satisfy C1--C5. Coverage is the only objective. The quality index of Section 3.3 carries no selection pressure: the search optimises one criterion rather than two, a front is a tie-set on coverage, and the index appears only as the fulfillment reading. The search method is described next.

A reader who meets this model through earlier versions of this line will expect a quality aggregate to be traded against served priority, so the change is stated explicitly. This is not a re-parameterisation of the same problem: the search returns a tie-set instead of a front, and the quality index moves from a decision criterion to a measured property of whatever the scheduler serves. The change is registered as an amendment to the project's preregistration, which vacates the quality-headroom estimand and registers the coverage--demand curve of Section 3.5 as the main result form.

<!--block:B0053a-->
## 3.5 The demand-tightening axis

The experimental axis of this paper is external to the scheduler. A scalar $s$ multiplies every task's ordered resolution, $\rho_{\mathrm{req},i}(s)=s\,\rho_{i}^{\mathrm{order}}$, with $s=1$ reproducing the order as placed and $s<1$ a tighter order; nine values are frozen, $s\in\{0.8,0.9,1.0,1.1,1.2,1.3,1.4,1.5,2.0\}$. Scaling touches the order only: the scenario population --- geometry, task set, and visibility windows --- is not regenerated, so every point of the grid is one scenario world seen through a different order.

The axis is swept under a frozen mode assignment. Which mode a task receives is not re-derived as the order tightens: the assignment is the one the scenario world was generated with, inherited unchanged (the grandfather decision registered in formula-spec §8.17-9). The reason is comparability --- re-cutting the mode mix at every grid point would confound the coverage response with a routing change --- and it fixes the scope of every conclusion that follows. The results are order sensitivity under a fixed mode assignment, not a general statement about how coverage trades against resolution when a router is free to move tasks between modes; the experiment that would answer the general question is a different one and is not run here.

The mode assignment matters most on the stripmap family, because that is where the floor sits. A family whose tasks are all stripmap cannot respond to a tighter order continuously: the delivered resolution is the antenna floor, so the family either serves at the floor or finds no admissible mode. The single-orbit family R1C meets that floor inside the frozen grid --- at $s=0.8$ the family has no feasible individual in 10 of 10 seeds --- and that outcome is an infeasibility record, not a measured coverage of zero. The two statements are kept apart everywhere in this paper: an infeasible grid point is not a point on the curve, and it is never plotted, averaged, or quoted as one.

Three different mode rules are in play in this project, and a reader should not mistake one for another. (i) The admission path routes an order to the coarsest library tier whose zero-squint resolution meets it; that rule consults the requirement and the library alone, one tier per task, with no scene-size test. (ii) The registered selection policy adds the feasibility test ($A_{\mathrm{task}}\in(0,1)$, the mode envelopes, the spotlight footprint bound, the ambiguity gate) and a two-key rule on scene size --- spotlight inside the footprint, sliding spotlight beyond it, stripmap at the coarse end --- and is the policy registered for narrative and for future families (formula-spec §8.17-9). (iii) The data of this paper follow neither of those at run time: they carry the grandfathered assignment described above. Where this paper says that the mode follows the order, it means that the parameters of the *assigned* mode follow the order, not that the assignment itself changes.

Coverage is measured on this axis as a reading: for each family and each grid point, the median over ten seeds of the served priority fraction of the best-covered member, at a single search budget. Three shape criteria are frozen against the curve --- monotone non-decreasing medians across the grid, a saturation arm ($s=2.0$ at least $s=1.5$), and a tight arm ($s=0.8$ below $s=1.0$) --- and they are inherited unchanged from their earlier registration rather than tuned to this world's data. Section 6 reports them as measured, failures included. Coverage admits no pass/fail verdict here: every unit's front is a tie-set carrying one coverage value, so there is nothing for a verdict to decide, and the curve is reported as a reading.


<!--block:B0054-->
# 4. Solving Approach

<!--block:B0055-->
## 4.1 Encoding and evaluation

<!--block:B0056-->
The solver is a dual-objective evolutionary search over the chromosome of Section 3.4: a selection bit and a start fraction $\tau\in[0,1]$ per task --- no mode gene, since the mode is fixed by the product order --- so the densest real-window family (R3H) encodes 100 drawn tasks (99 served by the generation ledger) over 753 enumerated windows as 200 decision variables. Decoding projects $\tau$ onto the union of feasible window intervals of the admitted windows: a served task is feasible with respect to the generator's discrete 11-point admission rule (Section 5.1), and the evaluator performs no AASR recheck of its own --- feasibility statements in the results are relative to that generation-side caliber, not to an independent physical guarantee (Fig. 2).

<!--block:B0057-->
![fig-2 The encoding-evaluation loop](figures/fig2_scheduling_loop.tex){#fig:2}

<!--block:B0058-->
**Caption (fig-2).** The scheduler's encoding-evaluation loop. Generation side (blue): scenario construction and AASR admission (11 evenly spaced in-window samples, worst-of-11 against the threshold). Genome: selection bits and start fractions, no mode gene; the greedy anchor seed is injected into the initial population. Decode is a measure projection of $\tau$ onto the union of feasible window intervals (nonlinear by construction). Evaluation: tasks are sorted by start time (index order is not time order), the C2 chain charges the $(1+0.25)$ pad on the dwell --- never on the maneuver --- plus the maneuver and settle terms, conflicts use the bare dwell, and C3/C4 (dashed) are slack by construction inside the envelope. The evaluator itself performs no AASR recheck: feasibility is relative to the generator's admission caliber.

<!--block:B0059-->
## 4.2 Anchor-seeded initialization

<!--block:B0060-->
The initial population contains the greedy anchor: a bounded single-pass re-timing repair of the all-selected schedule. The seed is what makes the $f_1$ normalisation meaningful --- every front carries a solution anchored at the served-priority reference --- and its injection into the population is checked by a dedicated cross-check that once exposed spurious violations from time-inverted index pairs, which is also why the evaluation loop sorts by start time before charging the C2 chain.

<!--block:B0061-->
## 4.3 Search operators and selection

<!--block:B0062-->
Variation uses standard binary crossover on the selection bits and simulated binary crossover with polynomial mutation on the start fractions; environmental selection is the standard non-dominated sorting with crowding distance \cite{deb2002a}. The search runs under a fixed random seed per unit, single-threaded, with manifest task-list order everywhere (no set or dictionary iteration order may influence a run), so every unit is bit-reproducible.

<!--block:B0063-->
## 4.4 The measure normalisation of $\tau$ and its implicit bias

<!--block:B0064-->
One parameterisation choice is disclosed as intentional. A start fraction $\tau$ indexes position within the *feasible measure* of a task's window union, not within wall-clock time: decoding is the measure projection of Fig. 2. Because the projection is measure-normalised, a uniform grid on $\tau$ samples wider windows more finely --- the parameterisation carries an implicit weighting toward wider windows. This bias is registered as a deliberate design decision: the main specification does not cover it, and the registration lives in the project's amendment record rather than in the main specification. No selection mechanism in the loop undoes the weighting; it is part of the search design, and every reading in Section 6 inherits it.


<!--block:B0065-->
# 5. Experimental Design and Setup

<!--block:B0066-->
This section describes the scenario world, the family and caliber system, and the preregistered test design.

<!--block:B0067-->
## 5.1 Scenario construction

<!--block:B0068-->
The scenario world is built from *real ground-track transit enumeration*, not from an arbitrary orbit phase point: visibility windows come from enumerating true ground-track passes over the scenario span, with a 15 s scan step, gap merging at 300 s (a registered band parameter, invariant across the registered 150/600/1200 s sensitivity band, not a physical lower bound), and 33-point edge refinement. The registry's own ledger records why: under the earlier phase-point pass rule only 0 of 8 clusters were serviceable after the incidence fix, against 6 of 8 under true enumeration. The demand mix itself --- resolution requirements and scene sizes --- is a registered synthetic template parameter, not a measured campaign profile; the priorities that drive the first objective are uniform random integers with no physical provenance (Section 3.4), so the mode composition of the served set reflects the template's requirement distribution.

<!--block:B0069-->
Orbit propagation is two-body only --- no $J_2$ or atmospheric terms --- so the registered repeat figure is the *simulated* ground-track repeat of 14.97 orbits $\approx$ 23.93 h (one sidereal day over the two-body period); the figure that includes $J_2$ nodal drift describes the physical orbit and is deliberately not the one this simulator produces. The surface normal used in incidence computations is an *approximate* normal: its maximum deviation from the true ellipsoidal normal is 0.125° (at $\approx$30° latitude; 0.109° at the dense-domain centre), with no effect on band-boundary judgements at the registered margins. The dense domain is a 1000 km square centred at 20°N/0°E, a 5×5 node grid at 250 km spacing with per-cell target jitter, a 3-day span in coordinated universal time (UTC). The serviceability criterion is per-node: every node carries at least one in-band transit within the span, measured 25/25; the literal best-incidence reading of the dense-domain constraint fails at the centre node (near-nadir passes exist there but yield no in-band window), which is why the operative criterion is the per-node one. The evidence lives in the generation-time guards and the manifest ledger.

<!--block:B0070-->
The AASR admission criterion is evaluated per family, and the two families differ by design --- a discrepancy we disclose rather than harmonise post hoc. Synthetic M-family windows are admitted by a window-edge single-point readout (the AASR at the window edge squint only), whereas the real-window R families sample the AASR at 11 evenly spaced in-window instants ($\mathrm{lo}+(\mathrm{hi}-\mathrm{lo})\,j/10$, $j=0,\dots,10$) and admit the window only if the worst of the 11 samples meets the threshold; a sample outside the physical sliding domain contributes an exclusion, so it can never mask an unserviceable window. The window-edge single-point rule *underestimates* the in-window worst case by about 4 dB, so the two admission rules are stated per family wherever admission is discussed; the R-family rule is the discrete in-window worst-case caliber that all feasibility statements in this paper inherit (Section 3.3). This sampling is *discrete*, *not continuous* evaluation: a window admitted under it is feasible with respect to the 11-point rule, and the evaluator performs no AASR recheck of its own.

<!--block:B0071-->
## 5.2 Families and calibers

<!--block:B0072-->
Three real-window families form the experiment matrix: R1C (20 tasks drawn, 20 served, 158 windows) is the single-orbit control; R2F (50 drawn, 46 served, 342 windows) and R3H (100 drawn, 99 served, 753 windows) are the dense-cluster treatments. Task counts follow the registered density ladder $N=20/50/100$; R4H ($N$=500) was retired at registration because the single-transit STR pass-count scaling exceeds the registered span at $N\ge 150$ (the retirement rationale is registered; no capacity number is asserted anywhere in this paper, since the serial bound has not been recomputed under the v3 scenario world).

<!--block:B0073-->
The primary stratum for the quality-headroom test is the R2F+R3H pooled stratum; R1C is a single-orbit control read descriptively only. Two facts motivate the split, and both are registered: first, the R1C quality axis operates on a different scale than the pooled families (the per-family domains below are separated by up to two orders of magnitude); second, the power design was computed for R2F/R3H only. The R1C served-fraction saturation at 1.0 is anchor-construction-carried (Section 6.5) and is read descriptively, never as a performance result. The per-family observed f_q domains over all 90 promotion units (3 budget tiers × 3 families × 10 seeds, constraint-violation-filtered (CV $\le 10^{-9}$), pooled --- a pool that includes the under-converged 40/60 baseline tier, so the lower extremes can come from that tier, while the results of Section 6 read the top tier only) are:

<!--block:B0074-->
| family (caliber: real-window v3, non-normalised $f_q$, $m^{-2}$) | observed f_q domain |
|---|---|
| R1C (real-window, v3 caliber, non-normalised) | 1.35 -- 2.04 |
| R2F (real-window, v3 caliber, non-normalised) | 55.05 -- 135.22 |
| R3H (real-window, v3 caliber, non-normalised) | 29.75 -- 123.70 |

<!--block:B0128-->
Note: the pooled extremes include the under-converged 40/60 baseline tier (see the caliber note in the lead-in above); the results of Section 6 read the top tier only, whose lower bounds sit higher for R1C and R2F.

<!--block:B0075-->
The R-family f_q is *not normalised*: the per-window slant-range geometry expands the units scene-dependently, so the three domains are incomparable across families and must never be pooled into a single span. The synthetic M families remain available as a controlled reference; their one still-valid artifact carries the annotation "v2 caliber, output commit unregistered (M-family controlled reference)" wherever cited, and no M-family number is mixed with R-family numbers in this paper.

<!--block:B0076-->
## 5.3 Hypotheses, power, and preregistration

<!--block:B0077-->
The quality-headroom test is a one-sample, one-sided $t$-test at $\alpha=0.05$ on the pooled primary stratum (registered as `ttest_1samp` against a null mean of zero, pooled $n=20$; 10 seeds per family), on the registered estimand (the quality headroom of the front over its anchor at the top budget). The effect size is $\delta=6.0$ in R-family $f_q$ units ($m^{-2}$): the numeral inherits the magnitude of the frozen 6.0 dB promotion threshold as a *numerical inheritance* and is dimensionally *not* equivalent to it (dB vs $m^{-2}$); it was registered *after calibration*, and the registration records exactly that --- the honest description is "registered after calibration, value inherited from the frozen threshold", never "pre-registered". The estimand itself is a within-unit difference: $dq_{all}=\max\{f_q(p): p \mathrm{\ on\ the\ front}\}-f_q(\mathrm{the\ anchor\ point\ on\ the\ same\ front})$; per-family $f_q$ levels are never pooled into one span (Section 5.2), while the registered primary test pools these within-unit differences, whose scale is comparable across the two pooled families.

<!--block:B0078-->
The power design is registered with its asymmetry disclosed; the figures below are post-hoc observed powers, recomputed from the same ten units per family that the test reads, so the 0.92/0.29 asymmetry is a property of the measured dispersion, not an a-priori design guarantee. Recomputed from the promoted artifacts at the top budget, the standard deviation of the estimand is 5.67 (R2F) and 16.14 (R3H), giving minimum detectable effects at 80% power of 4.87 and 13.87 respectively. At the registered $\delta$, the R2F power is 0.92, and the R3H power is 0.29; reaching 80% power at $\delta$ would require R2F to run 7 seeds (already met) and R3H to run 54 seeds --- a *cost anchor*, not a plan: the budget decision registered before the run declines to escalate, and the consequence for reporting is mandatory and asymmetric. R2F may claim 0.92 power at the registered δ; R3H must disclose the 0.29 figure and report its result as not reaching significance at this $n$. Two registered elements of the analysis plan travel with the test and are reported in Section 6.1: a sign-flip permutation robustness gate ($10^{5}$ flips; if the $t$ and permutation $p$ disagree across $\alpha$, the result is reported INCONCLUSIVE), and per-family Holm-adjusted secondary tests for locating only. Fig. 7 shows the registered power curve with the operating point marked.

<!--block:B0079-->
![fig-7 Power curves at the registered design](figures/fig7_power_curve.pdf){#fig:7}

<!--block:B0080-->
**Caption (fig-7).** Power at $n=10$ seeds per family versus effect size δ (non-normalised R-family $f_q$ units, $m^{-2}$, real-window v3 caliber). Solid: R2F (sd 5.67); dashed: R3H (sd 16.14). Dotted horizontal line: the 80% convention. The marked square is the registered operating point δ=6.0: R2F power 0.92, R3H power 0.29 --- the asymmetry is a registered disclosure, not a post-hoc finding. Recomputed from the promoted artifacts at the top budget tier (160/240 population/generations); the curve reproduces the calibration-time registration route.

<!--block:B0081-->
Convergence calibration is preregistered before the budget ladder was run: the judgment rule (single-point fronts falling away under budget, distinct-front medians rising, monotone non-saturation at the top budget) was frozen before the two additional budget tiers were executed, and its verdicts are reported with the results (Section 6).


<!--block:B0082-->
# 6. Results and Analysis

<!--block:B0083-->
All readings in this section are taken from the highest tier of the promoted artifacts (160/240 population/generations) and carry the NOT-PLATEAUED qualifier where frontier richness is stated; the 40/60 base tier is retained only as an under-converged baseline and is never read as a result.

<!--block:B0084-->
## 6.1 Primary stratum results

<!--block:B0085-->
The primary stratum for the quality-headroom test is the R2F+R3H pooled stratum, a registered adjudication recorded before the quality-headroom analysis was run; R1C is demoted to a single-orbit control and is read descriptively only, its served-fraction saturation being anchor-construction-carried (Section 6.5). Two registered facts motivate the demotion: the R1C quality axis operates on a different scale from the pooled families (the per-family domains of Section 5.2 are separated by up to two orders of magnitude), and the power design covers R2F/R3H only. The pooled test itself rejects: recomputed from the 20 promoted top-tier units (10 R2F and 10 R3H), the pooled quality-headroom estimand $dq_{all}$ of Section 5.3 reads a mean of 66.872 $m^{-2}$ (sd 12.071), the one-sided $t$-test against a null mean of zero gives $t=24.78$ with $p\approx 3\times 10^{-16}$, and the registered sign-flip permutation gate agrees ($10^{5}$ flips, no exceedance, add-one $p\approx 1\times 10^{-5}$) --- the result is therefore not INCONCLUSIVE. The registered pooled design's own 80%-power detection limit is MDE$_{80}=6.991$ $m^{-2}$ (registered with the stratum adjudication), slightly above the registered $\delta=6.0$: the pooled test's power at $\delta$ therefore sits below the 80% convention, and the decisive rejection reported above reflects an observed effect about an order of magnitude larger than $\delta$, not a design with power to spare. The registered quality-headroom prediction (prediction P2 of the preregistration) lands on its positive branch: the search confers measurable quality headroom over the greedy anchor at matched front, rejecting at $\alpha=0.05$. Two qualifiers travel with this result, as registered. First, the reading is taken at the top budget of a ladder whose fronts are still rising (NOT-PLATEAUED, Section 6.3): the magnitude of the headroom is budget-dependent, and this paper claims the headroom's existence and its registration discipline, not a converged magnitude. Second, the coverage-parity statement travels with this result in every branch (Section 6.5). The per-family readouts remain descriptive and are governed by the registered asymmetric reporting rule below.

<!--block:B0086-->
The asymmetry is reported as registered. At the top budget the R2F power is 0.92 at the registered δ, so R2F may claim the test; the R3H power is 0.29, and R3H's outcome is therefore reported as not reaching significance at $n=10$ --- the honest reading of a design whose seed anchor (R3H would need 54 seeds for 80% power) was registered as a cost anchor, not a plan. What the test does *not* constrain is the structural axis: ALIVE and DEAD verdicts on the model-level bound below are structural statements, and a family can be structurally ALIVE while failing to reject at this $n$. The pooled primary result reported above and this per-family rule operate at different scopes: the registered primary test is the pooled one, and the asymmetric rule governs per-family claims.

<!--block:B0087-->
## 6.2 Promotion, two axes

<!--block:B0088-->
The promotion verdict is stated on two separated axes, and the separation is the result.

<!--block:B0089-->
**Structural axis (model-level).** The real-window structural spread $R_{fam}$ --- the model-level AASR range attainable across each family's windows, recomputed under the rotation-centre (ticket-40) caliber --- is 3.9998 dB for R1C and 8.74/10.91 dB for R2F/R3H (Fig. 5a). R1C is therefore STRUCTURAL DEAD: its base-seed reading and its reading at every one of the ten seeds sit at or below 3.9998 dB (the weakest seed reads 3.9968 dB), all under the 6.0 dB threshold, so the verdict does not depend on which seed is read; its greedy anchor saturates the served fraction at 1.0 in every unit, its front is a pure quality trade-off surface, and that is exactly why it serves as the control. R2F and R3H are descriptively ALIVE at the model-level structural bound. Three disclosures attach. First, "ALIVE" is a model-level statement about what the scenario admits; it does not mean promotion fires, does not mean any readout has converged, and licenses no physical claim. Second, the knife-edge margin often quoted near promotion verdicts --- 0.499 dB, i.e. a 5.501 dB reading one half-dB under the line --- belongs to the synthetic P8WH family of the earlier calibration; R1C's own margin is 2.000 dB, and the two numbers are never interchangeable. Third, stability across calibers: the R2F and R3H structural readings moved by about one dB when the ambiguity semantics switched to the rotation-center caliber (the registered pre-ticket-40 readings were 9.75 and 11.99 dB), while R1C --- which carries no SLS task --- did not move at all; the verdicts are insensitive to that switch because even the lowest registered per-seed aggregate for R2F (7.20 dB) stays above the threshold, so the ALIVE/DEAD labels reported here do not hinge on which admissible steering semantics is chosen.

<!--block:B0090-->
**Reading axis.** Over all 90 units (3 families × 3 budget tiers × 10 seeds) the promotion decision is no_promotion everywhere, with a maximum spread of 3.9722 dB against the frozen 6.0 dB threshold (Fig. 5b). The no-promotion verdict is robust across the 16× budget ladder (16× in population and generations, i.e. 160× in evaluations) and may be cited as a structural reading with its budget evidence attached. The axes must not be merged: structural ALIVE is not a prediction that promotion triggers, and the 90/90 reading-axis outcome does not contradict the structural verdict.

<!--block:B0091-->
## 6.3 Convergence verdicts and budget tiers

<!--block:B0092-->
Convergence was calibrated under a preregistered rule frozen before the two additional budget tiers were run. Both treatment families carry the SEARCH-ARTIFACT verdict, and both disclosures are of falsified readings, not assertions.

<!--block:B0093-->
For R3H the base-budget picture --- 6 of 10 seeds ending at a single-point front (median 1) --- inverts completely under the ladder. At the 160/240 top budget the R3H median front size is 140, and the median distinct-fq count is 99. The apparent collapse was judged a search artifact by the preregistered rule, and the verdict names the mechanism: running a 40×60 budget against 200 decision variables. Any physical-collapse narrative built on the base budget is withdrawn, in both directions; for R2F the same rule fires more mildly: the ladder takes the median front size from 19.5 to 84.5 and the median distinct-fq count from 14.5 to 64.5 (a 4.4× rise), so the base-budget reading there was likewise an artifact of budget, not a property of the scenario (Fig. 4).

<!--block:B0094-->
Neither family has satisfied the plateau rule: between the middle and the highest tier the R3H median distinct-fq count still rises from 26 to 99, so both families are reported as still rising monotonically at the top budget (NOT-PLATEAUED). The converged true front remains unknown, and any frontier-richness bound is forbidden in both directions at this budget. The H/W observation item --- whether higher-density fronts widen trivially --- is settled by the same close-out verdicts: whatever widening appears is a property of the search budget, as the ladder demonstrates, not of the scenario density.

<!--block:B0095-->
![fig-4 Budget-ladder convergence](figures/fig4_budget_ladder.pdf){#fig:4}

<!--block:B0096-->
**Caption (fig-4).** Median front size (left) and median distinct-fq count (right) across the three registered budget tiers, real-window v3 caliber, CV-filtered fronts, 10 seeds per point. Solid: R2F; dashed: R3H. Both families are still rising at the highest tier (NOT-PLATEAUED): no frontier-richness bound is implied in either direction, and the lowest-tier readings are under-converged baselines only.

<!--block:B0097-->
## 6.4 Per-mode quality decomposition

<!--block:B0098-->
The second objective is fully explained by the mode library. At the zero-squint library caliber the per-mode f_q constants are 0.8107 (STR), 19.7352 (SLS), and 54.8322 (SPT) $m^{-2}$: magnitude ratios of 24.3× (SLS over STR), 67.6× (SPT over STR), and 2.8× (SPT over SLS). Because the squint factor cancels inside the gain term (exactly for STR/SLS, to within 0.07% for SPT across the full envelope; Fig. 3), these constants --- not squint-dependent readings --- are what the second objective trades against, and the per-mode decomposition is its whole explainability carrier (Fig. 6).

<!--block:B0099-->
![fig-3 Per-mode f_q versus squint](figures/fig3_quality_vs_squint.pdf){#fig:3}

<!--block:B0100-->
**Caption (fig-3).** Per-task f_q versus beam-centre squint for the three library modes, evaluated through the frozen platform fixture at the zero-squint library caliber (non-normalised, $m^{-2}$). The levels are flat by design (D05-4): solid STR 0.8107, dashed SLS 19.7352, dash-dot SPT 54.8322 $m^{-2}$; the SPT drift across the full envelope is +0.067%. The separation of the levels, not their slopes, is what the second objective responds to.

<!--block:B0101-->
Mode composition differs sharply by family: every R1C task routes to STR (20/20), R2F splits 16 SLS / 30 SPT (no STR), and R3H mixes all three (54 STR / 15 SLS / 30 SPT). The decomposition --- mode share × mode constant --- is drawn in Fig. 6. Because the per-mode constants span two orders of magnitude while the mode is fixed by the product order, the achievable quality range of a plan is dominated by the demand's mode composition: the scheduler moves the plan within that range, but the range itself is set at demand-construction time, not at scheduling time.

<!--block:B0102-->
![fig-6 Per-mode f_Q decomposition](figures/fig6_per_mode_decomposition.pdf){#fig:6}

<!--block:B0103-->
**Caption (fig-6).** Per-family decomposition of the second objective into mode contributions (share of tasks routed to each mode, from the promoted scenario manifests, × the zero-squint library constant; real-window v3 caliber, non-normalised $m^{-2}$). R1C is single-mode (STR) by construction of the control; R2F and R3H mix modes with different weights. The decomposition is a model-level explanatory vehicle (D05-4/D05-8), not a per-solution statistic.

<!--block:B0104-->
A required disclosure on double weighting (D05-5). The quality aggregate is weighted twice by construction, and both weightings must be stated together. First, the mode mapping embeds an implicit priority weighting of the requirement: finer requirements route to finer modes, which pay longer dwells, so the $f_1$--$f_Q$ trade-off is real rather than an artifact of the quality formula. Second, the antenna gain term adds an effective $\rho_a^2$ azimuth weighting on top of that. Stating only the first is the documented failure mode; the two together are what the second objective responds to.

<!--block:B0105-->
## 6.5 Coverage parity

<!--block:B0106-->
The coverage axis is a constructive parity outcome, not a hypothesis test. The dense-domain construction guarantees the per-node serviceability criterion by design (Section 5.1), and the warm start makes the parity verifiable on the promoted artifacts themselves: recomputed over all 90 promoted units (three budget tiers, three families, ten seeds each), the coverage-maximal front member ties the anchor's served fraction exactly in 90/90 units, with R1C saturating at $f_1^*=1.0$ in 30/30 --- the real-window reading of the construction's degeneracy; the 49/50 figure sometimes quoted for this construction is the earlier synthetic-family measurement and is not citable here. A significance test on coverage therefore has no power by construction. We report coverage as what it is --- a construction product inherited by every run --- and make no claim of the form that coverage passed or failed in any branch.

<!--block:B0107-->
![fig-5 Promotion two-axis verdict](figures/fig5_promotion_two_axis.pdf){#fig:5}

<!--block:B0108-->
**Caption (fig-5).** The promotion verdict on its two separated axes. (a) Structural axis, model-level only: recomputed $R_{fam}$ per family under the registered rotation-centre caliber from the promoted scenario manifests (3.9998 / 8.74 / 10.91 dB, base seeds; live recomputation reproduces the registration within its registered tolerance), against the frozen 6.0 dB threshold. R1C is STRUCTURAL DEAD; R2F/R3H are descriptively ALIVE at the model-level bound. (b) Reading axis: raw per-unit promotion outcomes for all 90 units (3 families × 3 tiers × 10 seeds, real-window v3 caliber); every unit is no_promotion; the largest reads 3.9722 dB. The axes are not merged: (a) never predicts (b).


<!--block:B0109-->
# 7. Discussion and Limitations

<!--block:B0110-->
## 7.1 Scope and negative claims

<!--block:B0111-->
Four scope statements are registered before anything is claimed. First, the capacity law carries a per-pass caliber: the registered serial bound is defined per pass, not per orbit, and the closure (the served fraction of the bound) is a containment reading --- it says the schedule fits inside the bound, not that the bound validates the scheduler --- and the minimum-over-pairs transfer time that enters it is a legal lower bound on the true transfer, never an average or a worst case. Under the present real-window scenario world the serial bound has not been recomputed, so this paper reports no capacity number in any form; the law, its caliber, and its discipline are the contribution, and the recomputation is future work. Second, the trade-off this study claims is the resolution-versus-dwell-time axis of the mode continuum. The antenna-design question of resolution against swath is a sensor-layer consequence that requires a width-versus-factor model this simulation does not have; it is reported as a limitation and future work, not as a demonstrated result. Third, the verification methodology's own reach is budget-bounded (Section 7.4). Fourth, the operational layer: the model covers single-pass scheduling decisions only --- no dynamic task arrival, no downlink or ground-station modeling, no cloud-cover attrition, and no replanning loop --- and no wall-clock runtime figure is registered for the promoted runs, so the platform is offered as a falsifiable scheduling substrate, not as an operationally timed planner; operational-cost evaluation is future work (Section 8).

<!--block:B0112-->
## 7.2 Azimuth ambiguity versus the literature: a direction contrast

<!--block:B0113-->
The registered correction behind this section is blunt: in this model the ambiguity-versus-squint direction is the *opposite* of the literature anchor it would most naturally be cited against. Under the production PRF and the registered calibration grid, the sliding-spotlight ambiguity ratio improves monotonically with squint --- from −21.35 dB at zero squint to −23.32 dB at the 26° calibration-grid edge (the registered SLS cap is 26.9°) --- the stripmap ratio likewise improves (−21.35 to −25.40 dB over the same registered 0–26° calibration span), and the spotlight ratio is squint-invariant at −7.05 dB, exactly as the degenerate-integral structure of Section 3.3 predicts. Song et al.'s platform, by contrast, degrades with scan angle (the anchors quoted in Section 2.1) \cite{song2025spaceborne}; those values are cited as that platform's literature readings only. The contrast also carries its model-dependence: it is a consequence of adopting the rotation-centre semantics (under which the compression factor is squint-independent) together with the registered omission of the absolute Doppler centre, and no experiment in this paper discriminates the two steering semantics; the literature-side mechanism --- a degrading compression factor competing with bandwidth narrowing --- is not modeled here, so the comparison establishes a difference of registered model behavior, not a measurement that refutes the anchor.

<!--block:B0114-->
The mechanism is the Doppler bandwidth. In this model the spectral compression factor is the design constant $a_{\mathrm{res}}\equiv A$ at every squint (Section 3.1), so the *only* squint-dependent channel into the ambiguity integral is the Doppler bandwidth $B_D=v_s\cos\bar\psi/\rho_a(m,0)$: squint narrows $B_D$, a narrower band aliases less of the ambiguity power, and the ratio improves. The registered direction contrast therefore differs by mechanism, not merely by sign: it is what remains once the pseudo-boundary of the linearised steering law --- under which the compression factor itself would collapse with squint --- is retired as the extrapolation artifact it is (Section 3.1). We flag the contrast rather than reconcile it: the two statements are made under different steering semantics, and the comparison is only legitimate with that stated. A caliber note on the spotlight reading: $-7.05$ dB is the library-edge constant evaluated at the platform-level scene extent (5 km, worst edge), whereas admission evaluates each task at its own scene extent through the 11-point in-window rule of Section 3.3 --- the spotlight aliasing term scales with scene size over range --- so the two figures are different calibers of the same model, not a contradiction; the admission readings are the ones every feasibility statement inherits.

<!--block:B0115-->
## 7.3 Model caveats

<!--block:B0116-->
**f_ac absolute position is omitted.** The ambiguity folding is integrated about the direct-current (DC)-relative coordinate, so the absolute Doppler centre $f_{ac}$ never enters the model; only the bandwidth and the compression factor depend on squint. The measured magnitude of the omission at the design-domain edge (worst side, 45°, an extrapolated-domain reading) is 345.7 kHz --- 95.2 times the production PRF of 3630 Hz, and 300.6 times the 1150 Hz registration key --- so the folded ambiguity structure sits far outside the band and the omission is defensible; it is disclosed regardless, and pushing the platform to its full 45° design domain must carry this number with it. A second simplification of the same family: the antenna pattern carries azimuth-frequency dependence only --- there is no cross-range (elevation-plane) pattern factor --- so the absolute ambiguity level is an azimuth-integration reading; no verdict in this paper rests on the unmodeled elevation-plane attenuation, and the direction contrast of Section 7.2 is carried by the bandwidth channel alone.

<!--block:B0117-->
**The C2 maneuver angle is a two-sided lower bound.** The inter-task requirement of Section 3.2 forms the maneuver angle from the difference of the tasks' start squints. This is a lower bound on the true attitude excursion from two independent sides: it omits the beam sweep during each dwell (the per-task sweep rate is 0.6686°/s at 30° incidence, 0.5599°/s at 45°, and 0.4233°/s at 60°, i.e. a 1.7--2.7° excursion across a 4 s dwell that the start-point difference never sees), and it understates the off-vertical attitude compression by 15-25%. The 25% inter-task pad is therefore a *margin argument*, not a correctness argument: it buys slack against a bound that is systematically low, and the paper never describes the bound as an exact measure of the attitude change. One cross-reference closes this caveat: the per-task sweep rates quoted here are the antenna steering rates of Section 3.2's definition, and the antenna's own sweep during a dwell is the quantity the 1.7--2.7° excursion describes --- the dwell that feeds C2 comes from the broadside-derived closure whose registered approximation status Section 3.2 records.

<!--block:B0118-->
**g_T has no external cross-validation.** The transmit-path gain term is self-derived and internally verified; the registered search for an external source found no noise-equivalent equation set in the Song platform paper (zero hits across its full text) and the textbook is not in the library with resolvable pages \cite{song2025spaceborne,cumming2005digital}. The verification route is therefore the internal identity chain of Section 3.3 and its pytest guard, and the absence of external cross-validation stands as a limitation in its own right. Consistent with the objective-level scope note of Section 3.3, no radiometric quantity enters the traded objective; the gain term shapes the resolution index but does not import a noise model.

<!--block:B0119-->
**The range-resolution anchor is a design constant.** $\rho_{\mathrm{rg}}$ is held at the design-anchor constant of 0.5 m, registered at 45° incidence with scene-centre semantics. Under the real-window incidence band (30--60°) a physical range resolution would vary by roughly −18%/+41% across the band (the $\sin\eta_i$ projection of the frozen design-incidence bandwidth: −18% at 60°, +41% at 30°, each relative to the 45° anchor); the constant is a modeling choice that keeps the second objective comparable across windows, and the magnitude narrative of any quality reading inherits this caveat.

<!--block:B0120-->
**Per-mode calibers are not economically comparable.** The spotlight admission in the mode library is defined per point target while the sliding-spotlight scenes are scene-level, and the scheduler consumes the scene-level dwell; the two calibers are registered as asymmetric. Any statement that trades dwell economy across modes --- a spotlight dwell against a sliding-spotlight dwell as if they purchased the same thing --- is outside what the model supports, and none is made.

<!--block:B0121-->
## 7.4 Design semantics and pre-answers

<!--block:B0122-->
**Why not jointly optimize mode and time?** Because the mode is a product-order property, not a scheduler preference. The mode follows from the ordered (resolution requirement, scene size) pair by the coarsest-sufficient library table; making it a decision gene would let the optimizer silently upgrade or downgrade the product the customer ordered. The sliding factor is likewise a system parameter. The registered evidence is narrower than that argument needs, and stating it precisely matters: the reading-axis verdict is no_promotion across all 90 units under the current demand mix, so a mode decision gene has no registered activation scenario in this scenario world; whether a mode gene would change the served set under a different demand mix is untested, and the model-level ALIVE verdicts for R2F/R3H leave that open. Within the registered world, the joint version would add decision variables without a registered mechanism to matter; joint mode-and-time allocation remains future work for regimes where that activation exists.

<!--block:B0123-->
**The verification criterion is budget-bounded.** The convergence calibration of Section 6.3 is falsifiable in principle: its judgment rule was frozen before the ladder ran, and any future budget extension can overturn the NOT-PLATEAUED state by satisfying the plateau rule. In practice the ladder is capped by a registered budget decision --- chasing budget was judged to buy frontier richness, not verdicts, since the reading-axis verdict is already robust across the 16× ladder (no_promotion over all 90 units) --- so the falsification route exists on paper and is priced out by policy. That asymmetry is disclosed rather than hidden, and it bounds every frontier statement in this paper.


<!--block:B0124-->
# 8. Conclusion

<!--block:B0125-->
This paper made the imaging physics of a three-mode agile SAR platform --- mode, dwell, and image quality --- into the decision substance of satellite scheduling, and it made the resulting claims auditable. On the platform leg, the sliding-spotlight dwell is an endogenous consequence of the mode continuum and the selected start, the quality index of the served set is a first-class objective, and the maneuver-coupled feasibility chain prices every schedule in physically meaningful time. On the co-headline legs, the per-pass capacity law supplies the registered containment discipline for what a pass can carry, and the convergence-verification methodology separates what the scenario owns from what the search budget owns --- including the falsified base-budget reading that the preregistered ladder caught and retired.

<!--block:B0126-->
The registered verdicts are deliberately modest. The structural axis says the real-window treatment families admit a spread above the threshold at the model level, and the control family does not; the reading axis says none of the 90 units promotes, robustly across the budget ladder; the quality-headroom test on the pooled stratum is powered for one family and honestly under-powered for the other. Every frontier reading carries its honesty qualifier, because the plateau rule was never satisfied.

<!--block:B0127-->
Future work follows the registered deferrals: recomputing the serial bound under the real-window scenario world so that the capacity law can carry numbers again; the sensor-layer design question of resolution against swath, which needs a width-versus-factor model this simulation does not have; joint mode-and-time allocation for regimes where a mode decision gene would actually activate; and the density-axis companion study, which scales the same platform to the regime where the binding constraints trade places. To the registered deferrals this revision adds one: an operational-cost evaluation of the platform --- wall-clock cost at the registered scales and comparison against operationally recognisable baselines --- which requires measurements outside the promoted artifacts and is therefore deferred rather than asserted here.
