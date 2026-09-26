"""sss_core — solver package forked for the sliding-spotlight scheduling paper (Paper 2).

Code-fork isolation per ADR GRILL-002: this package lives inside the paper
domain `papers/sliding-spotlight-scheduling/` and is the ONLY place Paper 2
solver code may evolve. The shared library `src/sar_sim/` is read-only
(zero-byte guarantee, M1 baseline tag `paper2-m1-baseline`).

Top-level package name is deliberately distinct from `sar_sim`: both roots
are on sys.path simultaneously in guard tests, and a same-named package
would resolve to whichever root imports first, making identity guards
compare the module against itself (false green). See FORK_MANIFEST.md.
"""
