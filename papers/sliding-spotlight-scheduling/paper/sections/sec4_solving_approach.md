# 4. Solving Approach

## 4.1 Encoding and evaluation

The solver is a dual-objective evolutionary search over the chromosome of Section 3.4: a selection bit and a start fraction $\tau\in[0,1]$ per task --- no mode gene, since the mode is fixed by the product order --- so the densest real-window family (R3H) encodes 100 drawn tasks (99 served by the generation ledger) over 753 enumerated windows as 200 decision variables. Decoding projects $\tau$ onto the union of feasible window intervals of the admitted windows: a served task is feasible with respect to the generator's discrete 11-point admission rule (Section 5.1), and the evaluator performs no AASR recheck of its own --- feasibility statements in the results are relative to that generation-side caliber, not to an independent physical guarantee (Fig. 2).

![fig-2 The encoding-evaluation loop](figures/fig2_scheduling_loop.tex){#fig:2}

**Caption (fig-2).** The scheduler's encoding-evaluation loop. Generation side (blue): scenario construction and AASR admission (11 evenly spaced in-window samples, worst-of-11 against the threshold). Genome: selection bits and start fractions, no mode gene; the greedy anchor seed is injected into the initial population. Decode is a measure projection of $\tau$ onto the union of feasible window intervals (nonlinear by construction). Evaluation: tasks are sorted by start time (index order is not time order), the C2 chain charges the $(1+0.25)$ pad on the dwell --- never on the maneuver --- plus the maneuver and settle terms, conflicts use the bare dwell, and C3/C4 (dashed) are slack by construction inside the envelope. The evaluator itself performs no AASR recheck: feasibility is relative to the generator's admission caliber.

## 4.2 Anchor-seeded initialization

The initial population contains the greedy anchor: a bounded single-pass re-timing repair of the all-selected schedule. The seed is what makes the $f_1$ normalisation meaningful --- every front carries a solution anchored at the served-priority reference --- and its injection into the population is checked by a dedicated cross-check that once exposed spurious violations from time-inverted index pairs, which is also why the evaluation loop sorts by start time before charging the C2 chain.

## 4.3 Search operators and selection

Variation uses standard binary crossover on the selection bits and simulated binary crossover with polynomial mutation on the start fractions; environmental selection is the standard non-dominated sorting with crowding distance. The search runs under a fixed random seed per unit, single-threaded, with manifest task-list order everywhere (no set or dictionary iteration order may influence a run), so every unit is bit-reproducible.

## 4.4 The measure normalisation of $\tau$ and its implicit bias

One parameterisation choice is disclosed as intentional. A start fraction $\tau$ indexes position within the *feasible measure* of a task's window union, not within wall-clock time: decoding is the measure projection of Fig. 2. Because the projection is measure-normalised, a uniform grid on $\tau$ samples wider windows more finely --- the parameterisation carries an implicit weighting toward wider windows. This bias is registered as deliberate in the amendment record (AD-3), which is where the disclosure lives: the main specification does not cover it, and pointing there would misattribute the registration. No selection mechanism in the loop undoes the weighting; it is part of the search design, and every reading in Section 6 inherits it.
