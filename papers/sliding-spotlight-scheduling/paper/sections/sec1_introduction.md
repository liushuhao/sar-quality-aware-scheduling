# 1. Introduction

## 1.1 Motivation

Agile Earth-observation satellites steered by a single antenna can operate their synthetic aperture radar (SAR) in a continuum of imaging modes: stripmap, sliding spotlight, and spotlight are one physical mode family parameterised by where the beam's virtual rotation centre sits. Which point of that continuum a task receives is not a free stylistic choice --- it is fixed by the requested resolution, the scene, and the geometry of the pass --- and it determines how long the satellite must dwell on the scene. Scheduling therefore cannot treat the imaging duration as an exogenous constant, as the classical agile-scheduling literature largely does \cite{wang2024deep,qin2024multisatellite,li2024earth}: in sliding-spotlight operation the dwell is produced by the imaging physics, it changes from task to task, and it feeds back into how many tasks a pass can carry and at what image quality.

This paper studies that coupling on a single satellite in a regime of single-pass dense task clusters under true orbit geometry. Scheduling decisions select which tasks to serve and when to start imaging within each task's visibility windows; the mode follows from the product order, and the dwell, the maneuver, and the image quality follow from the mode and the window. The systematic study of scenario density as an experimental axis belongs to the thesis companion rather than this paper.

Two risks motivate the methodology as much as the physics does. First, a claim that a frontier property (its richness, its collapse) is a property of the *scenario* can silently be a property of the *search budget*; our own calibration caught exactly such a reading, and the paper reports it as a falsified artifact (Section 6.3). Second, image-quality statements are only as good as their measurement calibers: several formally plausible formulations (an ambiguity sum that includes the principal image, a range resolution that varies per task, a squint-dependent routing resolution) are registered as not used, and the paper says so where it matters.

## 1.2 Contributions

Following the registered narrative frame, the paper's contributions are:

1. **An enabling physics-to-scheduler platform** (the platform leg). A three-mode continuum formalisation (Section 3) that carries the mode choice, the scene-level dwell closures, the per-mode image-quality index, and the maneuver-coupled feasibility predicates into one scheduling loop: the imaging mode is resolved from the product order, the dwell duration is a decision consequence rather than a constant, and the quality headroom is a second objective rather than a post-hoc image check.

2. **A capacity law with a registered per-pass caliber** (co-headline). A serial-bound reading of how many dwell-coupled tasks a pass carries --- window width over transfer-plus-dwell --- together with the closure's containment semantics and its deviation pattern along the overload axis. Under the present real-window scenario world the serial bound is registered as not yet recomputed, so the paper states the law and its discipline and reports no capacity number (Section 7.1).

3. **A convergence-verification methodology for evolutionary scheduling** (co-headline). A preregistered budget-ladder calibration that separates search-budget artifacts from scenario properties, carries the NOT-PLATEAUED honesty clause for any frontier reading, and whose verdict criterion is budget-bounded: falsifiable in principle by extending the ladder, capped by the registered budget decision in practice. The verdict rests on 90 units spanning three budget tiers with ten seeds per family (Sections 5.3 and 6.3, disclosed in Section 7.4).

Throughout, the trade-off the study claims is the resolution-versus-dwell-time axis of the mode continuum; the antenna-design question of resolution against swath is a sensor-layer consequence that this simulation does not model, and it is treated as a limitation with future work (Section 7.1).

To our knowledge, treating the steering-coupling loop as a first-class constraint and carrying a per-mode SAR metric as an independent objective simultaneously has no prior work; the platform leg is what makes the joint claim testable.

## 1.3 Paper organisation

Section 2 positions the work along sliding-spotlight imaging, agile-satellite scheduling, and quality-aware scheduling. Section 3 formalises geometry, modes, dwell, and quality. Section 4 describes the solver. Section 5 presents the scenario families, calibers, and preregistered test design; Section 6 reports results on the primary pooled stratum with the two-axis promotion verdict and convergence calibration; Section 7 discusses mechanisms, literature contrasts, and the full limitation set; Section 8 concludes.
