#!/usr/bin/env python3
"""Generate the two Results-section figures added in the 2026-11 revision.

fig7_corr_density : f2-f3 objective conflict vs target density (Sec. 6.4)
fig8_controls     : initialization / perturbation / search-budget controls (Sec. 6.6)

Both are drawn at the true column width of the elsarticle preprint layout
(5.7 in measured from the compiled PDF) so that a 9 pt label stays 9 pt.
Every value plotted is printed to stdout first, so the numbers shown can be
checked against small-paper-ijae.tex.
"""
import json
import os
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import scienceplots  # noqa: F401  (registers the 'science' styles)

SCIPLOT = os.path.expanduser('~/.claude/skills/scipilot-figure-skill/scripts')
if os.path.isdir(SCIPLOT):
    sys.path.insert(0, SCIPLOT)
    from export_figure import export_figure
else:
    def export_figure(fig, basename, formats=None, dpi=300, **kw):
        out = []
        for fmt in (formats or ['pdf', 'png']):
            p = f"{basename}.{fmt}"
            fig.savefig(p, dpi=dpi, bbox_inches='tight')
            out.append(p)
        return out

PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS = os.path.join(PROJECT, 'experiments', 'results')
FIG_DIR = os.path.join(PROJECT, 'figures')
os.makedirs(FIG_DIR, exist_ok=True)

plt.style.use(['science', 'nature'])
plt.rcParams.update({
    'font.size': 9,
    'axes.titlesize': 9, 'axes.labelsize': 9,
    'xtick.labelsize': 8, 'ytick.labelsize': 8, 'legend.fontsize': 7.5,
    'figure.dpi': 150,
    'text.usetex': False,
    'pdf.fonttype': 42,
    'ps.fonttype': 42,
    'axes.unicode_minus': False,
})

TEXT_WIDTH = 5.7          # inches, measured from the compiled PDF
CLASSES = ['S1', 'S2', 'S3', 'S4']
N_OF = {'S1': 20, 'S2': 100, 'S3': 300, 'S4': 500}
# Okabe-Ito, colour-blind safe
VARIANT_STYLE = {
    'A_full_physics': dict(label='A: full physics', color='#0072B2', marker='o', ls='-'),
    'B_no_squint':    dict(label='B: no squint',    color='#E69F00', marker='s', ls='--'),
    'C_no_incidence': dict(label='C: no incidence', color='#009E73', marker='^', ls='-.'),
    'D_no_physics':   dict(label='D: no physics',   color='#CC79A7', marker='D', ls=':'),
}


def load(name):
    with open(os.path.join(RESULTS, name), encoding='utf-8') as f:
        return json.load(f)


def fig7():
    abl = load(os.path.join('schedule_correlation_ablation.json'))['variants']
    nullnew = load('null_new_caliber2026.json')
    seq = load('schedule_correlation.json')['variants']

    xs = [N_OF[c] for c in CLASSES]
    env = [nullnew[c]['r_envelope'] for c in CLASSES]
    nl_mu = [nullnew[c]['r_shuffle_null_mean'] for c in CLASSES]
    nl_lo = [nullnew[c]['r_shuffle_null_p025'] for c in CLASSES]
    nl_hi = [nullnew[c]['r_shuffle_null_p975'] for c in CLASSES]

    print('== fig7 values ==')
    print('envelope      ', [round(v, 3) for v in env])
    print('null mean     ', [round(v, 3) for v in nl_mu])
    print('null 95%      ', [round(v, 3) for v in nl_lo], [round(v, 3) for v in nl_hi])
    series = {}
    for key, style in VARIANT_STYLE.items():
        src = seq.get(key) or abl.get(key)
        vals = [src[c]['r'] for c in CLASSES]
        series[key] = vals
        print(f'{style["label"]:18s}', [round(v, 3) for v in vals])

    fig, ax = plt.subplots(figsize=(TEXT_WIDTH, 2.9))
    # N8/R1-04: the band is the observed range of 20 shuffles, not a nominal
    # 95% interval (the body says a nominal 95% interval would need ~10x more
    # draws) — label it as what it is.
    ax.fill_between(xs, nl_lo, nl_hi, color='0.75', alpha=0.55, lw=0,
                    label='observed shuffle range (20 shuffles/class)')
    # the shuffle-null mean sits inside the band above; drawing it as a
    # separate line duplicated the band and added an unlabelled mark.
    ax.plot(xs, env, color='0.15', lw=1.2, ls='--', marker='_', ms=9,
            label='visibility envelope')
    for key, style in VARIANT_STYLE.items():
        ax.plot(xs, series[key], color=style['color'], marker=style['marker'],
                ls=style['ls'], ms=3.6, lw=1.2, label=style['label'])
    ax.axhline(0, color='0.6', lw=0.6)
    ax.set_xscale('log')
    ax.set_xticks(xs)
    ax.set_xticklabels([f'{c}\n$N$={N_OF[c]}' for c in CLASSES])
    ax.set_xlabel('scenario density class')
    ax.set_ylabel(r'per-task $r(f_2,f_3)$ within schedule')
    ax.set_ylim(-0.75, 0.02)
    ax.legend(loc='lower right', frameon=False, ncol=1, handlelength=1.9)
    fig.tight_layout()
    export_figure(fig, os.path.join(FIG_DIR, 'fig7_corr_density'),
                  formats=['pdf', 'png'], dpi=300)
    plt.close(fig)


def fig8():
    hs = load(os.path.join('p1-1_random_init', 'hotstart_control_s1s4.json'))['scales']
    sweep = load(os.path.join('sigma_sweep', 'sweep_summary.json'))['aggregator']
    rnd = load(os.path.join('p1-2_random_search', 'p1-2_s1_random_search.json'))['results']
    vd = load(os.path.join('variant_d_random_init', 'full.json'))

    fig, axes = plt.subplots(2, 2, figsize=(TEXT_WIDTH, 4.5))
    (axa, axb), (axc, axd) = axes

    # (a) hot-start coverage deficit, per class, with every scenario shown
    print('== fig8a: coverage deficit (random - hot) ==')
    labels, means, sds, points = [], [], [], []
    for c in CLASSES:
        d = np.array([r['random']['f1'] - r['hot']['f1'] for r in hs[c]])
        labels.append(f'{c}\n$N$={N_OF[c]}')
        means.append(d.mean()); sds.append(d.std(ddof=1)); points.append(d)
        print(f'  {c}: mean={d.mean():+.3f} sd={d.std(ddof=1):.3f} n={len(d)}')
    pos = np.arange(len(CLASSES))
    rng = np.random.default_rng(0)
    for i, pts in enumerate(points):
        axa.scatter(i + rng.uniform(-0.16, 0.16, len(pts)), pts, s=3.2,
                    color='0.45', alpha=0.65, lw=0, zorder=2)
        axa.errorbar(i, means[i], yerr=sds[i], fmt='o', ms=5, color='#0072B2',
                     capsize=2.5, lw=1.0, zorder=3)
    axa.axhline(0, color='0.4', lw=0.6)
    axa.set_ylim(-0.95, 0.12)
    axa.set_xlim(-0.5, len(CLASSES) - 0.5)
    axa.set_xticks(pos); axa.set_xticklabels(labels)
    axa.set_ylabel(r'coverage deficit $\Delta f_1^*$')
    axa.set_title('(a) random vs hot start', loc='left')

    # (b) perturbation sweep: deviation of f2/f3 from their level means
    print('== fig8b: sigma sweep ==')
    sig = sorted({a['sigma'] for a in sweep})
    for solver, col, mk in (('moea_3obj', '#0072B2', 'o'), ('moea_2obj', '#CC79A7', 's')):
        rows = [a for a in sweep if a['group'] == 'S3' and a['solver'] == solver]
        rows.sort(key=lambda r: r['sigma'])
        f2 = np.array([r['f2_mean'] for r in rows])
        f3 = np.array([r['f3_mean'] for r in rows])
        print(f'  {solver}: f2 {np.round(f2,4).tolist()} f3 {np.round(f3,4).tolist()}')
        axb.plot(sig, f2 - f2.mean(), color=col, marker=mk, ms=3.6, lw=1.2,
                 ls='-', label=f'{solver.replace("moea_","MOEA-").replace("obj","")} $f_2$')
        axb.plot(sig, f3 - f3.mean(), color=col, marker=mk, ms=3.6, lw=1.2,
                 ls='--', mfc='none', label=f'{solver.replace("moea_","MOEA-").replace("obj","")} $f_3$')
    axb.axhline(0, color='0.4', lw=0.6)
    axb.set_xticks(sig)
    axb.set_xlabel(r'geometry perturbation $\sigma$ (deg)')
    axb.set_ylabel('deviation from level mean')
    axb.set_ylim(-0.004, 0.004)
    axb.legend(loc='lower right', frameon=False, ncol=2, handlelength=1.6,
               columnspacing=0.8)
    axb.set_title('(b) perturbation sweep (S3)', loc='left')

    # (c) random search: per-scenario mean / p90 / best coverage
    print('== fig8c: random search ==')
    keys = sorted(rnd)
    mu = np.array([rnd[k]['f1_star_mean'] for k in keys])
    p90 = np.array([rnd[k]['f1_star_p90'] for k in keys])
    best = np.array([rnd[k]['f1_star_best'] for k in keys])
    print('  mean', np.round(mu, 3).tolist(), 'p90', np.round(p90, 3).tolist(),
          'best', np.round(best, 3).tolist())
    ypos = np.arange(len(keys))[::-1]
    for y, m, p, b in zip(ypos, mu, p90, best):
        axc.plot([m, p], [y, y], color='0.6', lw=0.8, zorder=1)
    axc.scatter(mu, ypos, s=16, color='#E69F00', marker='o', label='mean', zorder=3)
    axc.scatter(p90, ypos, s=16, color='#009E73', marker='^', label='90th pct', zorder=3)
    axc.scatter(best, ypos, s=16, color='#0072B2', marker='D', label='best of 5,000', zorder=3)
    axc.axvline(1.0, color='0.35', lw=0.9, ls='--')
    axc.set_yticks(ypos)
    axc.set_yticklabels([k.replace('.pkl', '').replace('S1-A_seed', 'seed ') for k in keys])
    axc.set_xlabel(r'random-search coverage $f_1^*$')
    axc.set_xlim(0, 1.08)
    axc.legend(loc='lower left', frameon=False, handletextpad=0.3, borderpad=0.2)
    axc.set_title('(c) random search (S1)', loc='left')

    # (d) coverage loss under random initialization of the no-physics variant
    print('== fig8d: variant-D random init ==')
    vals = {}
    nsel = {}
    for c in ('S3', 'S4'):
        recs = vd['results'][c]
        f1r = np.array([r['f1'] for r in recs])
        nsel[c] = float(np.mean([r['n_selected'] for r in recs]))
        print(f'  {c}: random-init f1*={f1r.mean():.3f}+-{f1r.std(ddof=1):.3f} '
              f'n_sel={nsel[c]:.1f} ({len(recs)} runs)')
        vals[c] = f1r
    hot_lookup = {}
    prog = load(os.path.join('moea_3obj_no_physics', '_progress.json'))['completed']
    for c in ('S3', 'S4'):
        nsel_hot = [v['n_selected'] for k, v in prog.items() if k.startswith(c + '/')]
        hot_lookup[c] = float(np.mean(nsel_hot))
        print(f'  {c}: hot-started D n_selected={hot_lookup[c]:.1f} (n={len(nsel_hot)})')
    x = np.arange(2)
    w = 0.36
    hotm = [hot_lookup[c] for c in ('S3', 'S4')]
    rndm = [nsel[c] for c in ('S3', 'S4')]
    rndsd = [float(np.std([r['n_selected'] for r in vd['results'][c]], ddof=1))
             for c in ('S3', 'S4')]
    axd.bar(x - w / 2, hotm, w, color='#56B4E9', label='hot start (G-BL seed)')
    axd.bar(x + w / 2, rndm, w, color='#CC79A7', yerr=rndsd, capsize=2.5,
            error_kw=dict(lw=0.8, ecolor='0.25'), label='random init')
    axd.set_xticks(x)
    axd.set_xticklabels([f'{c}\n$N$={N_OF[c]}' for c in ('S3', 'S4')])
    axd.set_ylabel('tasks scheduled (variant D)')
    axd.set_ylim(0, 215)
    axd.legend(loc='upper center', bbox_to_anchor=(0.5, 1.0), frameon=True,
               framealpha=0.9, edgecolor='none', ncol=2, handlelength=1.4,
               columnspacing=0.8, fontsize=7)
    axd.set_title('(d) no-physics variant, random init', loc='left')

    fig.tight_layout()
    export_figure(fig, os.path.join(FIG_DIR, 'fig8_controls'),
                  formats=['pdf', 'png'], dpi=300)
    plt.close(fig)


if __name__ == '__main__':
    fig7()
    fig8()
    print('done')
