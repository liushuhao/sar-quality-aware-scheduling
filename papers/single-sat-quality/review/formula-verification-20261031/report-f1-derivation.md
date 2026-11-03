# F1 first-principles derivation report — formula-verification-20261031

## Method note

I re-derived each item from standard SAR matched-filter/resolution theory, the radar equation, Doppler geometry, and central projection; I did not inspect the manuscript's derivations or use external material. Arithmetic for #11–#12 was independently recomputed with Python, using a spherical Earth radius of 6371 km for #12. In the geometric derivations, \(x\) is along-track, \(z\) is local vertical, \(\hat{\boldsymbol\ell}\) is a unit LOS vector, \(\psi\) is the angle from the zero-Doppler (\(y\)-\(z\)) plane, and \(\theta_{\rm elev}\) is the angle of the LOS projection in that plane from vertical.

## Per-formula verdicts

### 1. Ground-range resolution: \(\rho_{rg}=c/(2B\sin\theta)\)

**Derivation.** Range compression gives slant-range resolution \(\delta R=c/(2B)\). On locally flat ground, \(R^2=h^2+y^2\), so \(dR/dy=y/R=\sin\theta\). Hence \(\delta y=\delta R/\sin\theta\).

**Verdict: CORRECT-UNDER-APPROXIMATION** (local flat-ground projection, effective processed bandwidth \(B\), and no additional resolution broadening).

**Assumptions/omissions.** Terrain, Earth curvature, spectral weighting, and mode-dependent processed bandwidth change the numerical value. The incidence ordering is preserved when those factors are fixed across compared tasks; near nadir the flat-ground expression diverges and is not a useful scheduling metric.

### 2. Stripmap azimuth resolution: \(\rho_{az}=D/(2\cos\psi)\)

**Derivation.** Let \(\alpha\) be the instantaneous azimuth look angle and take a fixed physical antenna beamwidth \(\Delta\alpha\simeq\lambda/D\) in that angular coordinate. The along-track spatial frequency of the aperture phase is \(k_x=(4\pi/\lambda)\sin\alpha\), whose collected bandwidth near \(\psi\) is
\[
\Delta k_x\simeq{4\pi\over\lambda}\cos\psi\,\Delta\alpha .
\]
Thus \(\rho_x\simeq2\pi/\Delta k_x=D/(2\cos\psi)\). The target illumination time itself grows as \(1/\cos\psi\) under this fixed-antenna-beamwidth assumption.

**Verdict: CORRECT-UNDER-APPROXIMATION** (fixed physical angular antenna beamwidth, full-aperture stripmap focusing, narrow beam, and the usual small-resolution/mainlobe convention). The \(1/\cos\psi\) form is ordering-preserving in squint when the beamwidth and weighting are fixed.

**Assumptions/omissions.** If instead the along-track aperture length/illumination time is held fixed at the value that would give \(D/2\) at the same slant range in broadside geometry, then \(\Delta\alpha\propto\cos\psi\), \(\Delta k_x\propto\cos^2\psi\), and the corresponding result is \(D/(2\cos^2\psi)\). Thus the exponent is a beamwidth/aperture assumption, not interchangeable. Amplitude weighting multiplies the ideal resolution by a window-dependent mainlobe-broadening factor; 10–20% is plausible for mild weighting but is not a universal platform constant. Mode-, beam-, or squint-dependent weighting would alter ordering.

### 3. Stripmap NESZ scaling: \(\mathrm{NESZ}\propto R^3\)

**Derivation.** Before processing, the two-way point-target power scales as \(R^{-4}\). Range-compression gain is fixed when the pulse time-bandwidth product is fixed. For ordinary stripmap, illumination/aperture duration scales as \(T_a\propto R\lambda/(Dv)\), so azimuth-compression gain contributes a factor proportional to \(R\). Consequently the noise-equivalent reflectivity scales as \(R^4/R=R^3\), with all other radar-equation factors held fixed.

**Verdict: CORRECT-UNDER-APPROXIMATION** (standard stripmap azimuth gain and fixed hardware/processing parameters). It preserves range ordering within that fixed regime.

**Assumptions/omissions.** Capped integration time, changed PRF/duty cycle, beam gain, transmit power, bandwidth, processing losses, or a different imaging mode can change both the prefactor and the effective exponent. Cross-mode or cross-beam NESZ ordering cannot use \(R^3\) alone.

### 4. \(R\approx R_{\rm elev}/\cos\psi\) and \(\mathrm{NESZ}\propto1/(\cos^3\theta_{\rm elev}\cos^3\psi)\)

**Derivation.** The LOS projection into the elevation plane has length \(R_{\rm elev}=R\cos\psi\). On plane Earth, \(h=R_{\rm elev}\cos\theta_{\rm elev}\). Therefore
\[
R={R_{\rm elev}\over\cos\psi}={h\over\cos\theta_{\rm elev}\cos\psi}.
\]
Under #3, \(R^3=h^3/(\cos^3\theta_{\rm elev}\cos^3\psi)\).

**Verdict: CORRECT-UNDER-APPROXIMATION** (plane Earth, fixed altitude, consistent orthogonal angle definitions, and the #3 NESZ regime). With those definitions the slant-range decomposition is **exact**, not merely approximate; the approximation enters through plane-Earth geometry and the \(R^3\) NESZ law. It is per-task ordering-preserving in either angle when altitude and other radar factors are fixed.

**Assumptions/omissions.** Curved Earth, varying altitude, terrain, or an \(R_{\rm elev}\) computed in a different geometry makes the decomposition approximate or inconsistent. Those omissions can change cross-task ordering, not just the prefactor.

### 5. Angle identity: \(\cos\xi=\cos\theta_{\rm elev}\cos\psi\)

**Derivation.** For a unit LOS vector, \(\cos\psi=\sqrt{\hat\ell_y^2+\hat\ell_z^2}\) because \(\sin\psi=|\hat\ell_x|\). The projected elevation angle satisfies \(\cos\theta_{\rm elev}=\hat\ell_z/\sqrt{\hat\ell_y^2+\hat\ell_z^2}\), while \(\cos\xi=\hat\ell_z\). Multiplication gives the identity.

**Verdict: CORRECT** (exact direction-cosine identity for the stated local orthogonal frame).

**Assumptions/omissions.** The angles must refer to the same LOS and frame. Mixing satellite off-nadir, target incidence, or angles evaluated at different local verticals invalidates the identity and can corrupt scheduling comparisons.

### 6. \(f_2=|S|^{-1}\sum_i\sin\theta_{{\rm elev},i}\cos\psi_i\) as a ground-pixel-area ordering

**Derivation.** Adopt the manuscript's separable rectangular-cell approximation. In the elevation plane, \(R_{\rm elev}^2=h^2+y^2\), so the ground-range spacing is \(\delta y=[c/(2B)]/\sin\theta_{\rm elev}\). Taking the along-track spacing from #2 and multiplying the two sides gives, per task,
\[
A_i\simeq{cD\over4B}\,{1\over\sin\theta_{{\rm elev},i}\cos\psi_i}
={C\over g_i},\qquad g_i=\sin\theta_{{\rm elev},i}\cos\psi_i .
\]
The factors are dimensionless and \(cD/B\) has units of area, so the per-task expression is dimensionally and physically consistent under this focused-image geometry. Larger \(g_i\) means smaller \(A_i\) when \(C\) is fixed.

The arithmetic mean \(\bar g\), however, does not determine mean area \(\overline{A}=C\,\overline{1/g}\). Counterexample: \(g=(0.1,1.0)\) gives \(f_2=0.55\) and \(\overline{1/g}=5.5\); \(g=(0.5,0.5)\) gives \(f_2=0.50\) and \(\overline{1/g}=2.0\). The first set has higher \(f_2\) but larger mean pixel area.

**Verdict: WRONG** as a biconditional ordering claim for means over heterogeneous task sets. The per-task area law is **CORRECT-UNDER-APPROXIMATION** (separable rectangular ground-range/azimuth cell, flat ground, fixed \(B,D\), and fixed weighting).

**Assumptions/omissions.** Mean area requires averaging \(1/g_i\), not \(g_i\); heterogeneity is decisive. At nonzero squint, iso-range and iso-Doppler directions need not form the assumed orthogonal rectangle, so a full ground-cell Jacobian can change the squint dependence. Varying bandwidth, antenna length, weighting, terrain, or processing mode also breaks the common prefactor. A high \(f_2\) can therefore lead to the opposite scheduling choice from minimum mean area.

### 7. \(f_3=|S|^{-1}\sum_i\cos^3\xi_i\) as an NESZ/radiometric ordering

**Derivation.** On plane Earth, \(h=R\cos\xi\). Under #3, per task
\[
\mathrm{NESZ}_i\propto R_i^3={h^3\over\cos^3\xi_i}={C'\over q_i},
\qquad q_i=\cos^3\xi_i .
\]
Thus larger \(q_i\) means lower per-task NESZ and better sensitivity if \(C'\) is fixed. But \(\bar q\) does not determine \(\overline{1/q}\). Using the same numerical counterexample as #6, \(q=(0.1,1.0)\) has \(f_3=0.55\) and mean NESZ factor \(5.5\), whereas \(q=(0.5,0.5)\) has \(f_3=0.50\) and mean NESZ factor \(2.0\): higher \(f_3\), worse mean NESZ.

**Verdict: WRONG** as a biconditional task-set ordering claim. Per-task NESZ ordering is **CORRECT-UNDER-APPROXIMATION** (plane Earth and fixed all other NESZ factors).

**Assumptions/omissions.** Mean NESZ requires the reciprocal average; moreover real NESZ also depends on altitude, beam gain, power, bandwidth, integration time, and losses. The index is a heuristic utility, not an equivalent radiometric objective across heterogeneous sets.

### 8. Doppler centroid: \(f_{dc}\approx(2v/\lambda)\sin\psi\)

**Derivation.** For carrier phase \(\phi=-4\pi R/\lambda\), \(f_D=(2\pi)^{-1}\dot\phi=-(2/\lambda)\dot R\). Rectilinear along-track motion gives \(|\dot R|=v|\sin\psi|\) at the steered LOS, yielding the stated magnitude.

**Verdict: CORRECT-UNDER-APPROXIMATION** (uniform rectilinear motion, stationary target, narrowband signal, and a consistent sign convention). The monotonic dependence on signed squint is ordering-preserving in the ideal geometry.

**Assumptions/omissions.** Earth rotation, relative ground velocity, acceleration, attitude/yaw steering, and Doppler-centroid ambiguity/PRF aliasing add shifts or sign changes. Ignoring them can change required PRF and feasible scheduling.

### 9. Squint definition: \(\psi=\arcsin(|l_x|/R)\), with \(l_x\) called a unit-vector component

**Derivation.** If \(\boldsymbol L\) is the unnormalised LOS vector, \(|\boldsymbol L|=R\), then \(\sin\psi=|L_x|/R\). If \(\hat\ell_x\) is instead a component of the **unit** LOS vector, then directly \(\sin\psi=|\hat\ell_x|\).

**Verdict: WRONG** as written. For a unit-vector component, \(|l_x|/R\) has dimensions of inverse length and cannot be an arcsine argument. The correct forms are \(\psi=\arcsin(|L_x|/R)\) for an unnormalised LOS vector or \(\psi=\arcsin(|\hat\ell_x|)\) for a unit vector.

**Assumptions/omissions.** This is a notation/dimensional error, not an approximation. It affects decisions only if the same extra division is implemented computationally; that implementation question was outside this independent-derivation seat.

### 10. Optical analogy: off-nadir footprint \(\propto1/\cos^2\eta\)

**Derivation.** For a fixed small IFOV \(\Delta\eta\) on flat ground, slant range is \(R=h\sec\eta\). The footprint dimension orthogonal to the tilt plane is \(R\Delta\eta=h\Delta\eta\sec\eta\). In the tilt plane, \(x=h\tan\eta\), so its linear GSD is \(\Delta\eta\,dx/d\eta=h\Delta\eta\sec^2\eta\). Their product, the pixel **area**, scales as \(\sec^3\eta\).

**Verdict: WRONG** as an unqualified pixel-footprint/area statement. It is **CORRECT-UNDER-APPROXIMATION** only for the linear GSD in the tilt plane (flat ground, fixed IFOV, small pixel).

**Assumptions/omissions.** Sampling scheme, detector geometry, terrain, and Earth curvature alter numerical footprints. The optical analogy cannot by itself justify a SAR area exponent or scheduling ordering.

### 11. Incidence-variation claims: 1.5° mean within windows and 2.4× over 18°–47°

**Derivation/arithmetic.** Independently,
\[
\sin18^\circ=0.3090169944,\qquad \sin47^\circ=0.7313537016,
\]
so \(\sin47^\circ/\sin18^\circ=2.366710294\), which rounds to **2.4×**. The reciprocal factor has the same span in the opposite direction. No window-level incidence samples or definition of the within-window mean were supplied, so the **1.5° mean cannot be independently recomputed in this seat**.

**Verdict: CORRECT-UNDER-APPROXIMATION** for the rounded 2.4× endpoint arithmetic; the 1.5° mean remains unverified rather than confirmed.

**Assumptions/omissions.** The 2.4× result is an endpoint range, not a typical task-to-task variation. A mean within-window variation does not bound worst-case windows; scheduling approximations need the underlying distribution and maximum as well.

### 12. Plane versus curved Earth at 47° incidence and \(h=693\) km

**Derivation/arithmetic.** Let \(R_s=R_E+h=7064\) km and let \(\theta_s\) be the satellite look angle corresponding to target incidence \(\theta_i=47^\circ\). Spherical-Earth geometry gives
\[
\sin\theta_s={R_E\over R_s}\sin\theta_i,\qquad
R_{\rm curv}=R_s\cos\theta_s-R_E\cos\theta_i .
\]
With \(R_E=6371\) km, \(\theta_s=41.2698057^\circ\) and \(R_{\rm curv}=964.3745\) km. A plane model at the **same satellite look angle** gives \(R_{\rm flat}=h/\cos\theta_s=922.0185\) km. Hence
\[
{R_{\rm curv}-R_{\rm flat}\over R_{\rm curv}}=4.3921\%,\qquad
1-\left({R_{\rm flat}\over R_{\rm curv}}\right)^3=12.6060\%.
\]
These round to the stated 922/964 km, about 4%, and about 13%.

**Verdict: CORRECT-UNDER-APPROXIMATION** (spherical Earth with \(R_E\simeq6371\) km, rounded arithmetic, and comparison at the same satellite look angle).

**Assumptions/omissions.** The comparison convention matters: imposing 47° directly as a flat-Earth incidence/look angle would instead give \(693/\cos47^\circ=1016.13\) km, not 922 km. Altitude, Earth radius, terrain, and angle change the error; the 13% figure is not a universal correction or proof of ordering preservation across all geometries.

## Summary

- **#9 is WRONG as written:** a unit LOS component must not be divided by range.
- **#6 and #7 are WRONG as biconditional scheduling claims for arithmetic means.** Their per-task monotonicity is sound under fixed conditions, but means of \(g\) or \(q\) do not order means of \(1/g\) or \(1/q\); explicit counterexamples reverse the claimed task-set ranking.
- **#10 is WRONG if “footprint” means area:** fixed-IFOV optical pixel area scales as \(\sec^3\eta\); \(\sec^2\eta\) is only the in-plane linear GSD.
- **Decision-relevant qualifications:** #2's \(1/\cos\psi\) result assumes fixed physical antenna angular beamwidth; fixed illumination time gives \(1/\cos^2\psi\). The 10–20% weighting broadening is not universal. #4's geometric decomposition is exact on plane Earth but approximate on curved Earth. #11's 2.4× and #12's approximately 4%/13% arithmetic check out; #11's 1.5° within-window mean was not independently verifiable from the supplied information.
