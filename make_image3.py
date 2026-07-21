"""Image 3: how each reshape pick performs as your keep-it bar rises.

Broad-audience redesign of the notebook's plot_preference_curves: the
technical top panel (raw E[(damage - thr)^+] curves) is dropped, and only
the comparison that carries the story remains -- each pick's payoff as a
percentage of the best possible pick at that bar. Pairs with identical
damage distributions are merged (HP and DEF are interchangeable junk),
cutting six index-labeled curves down to four named ones. The bar is the
% damage improvement the artifact must beat. Renders a light and a dark
variant.

Run:  python make_image3.py
"""
import itertools

import matplotlib.pyplot as plt
import numpy as np

import reshape_common as rc

OUT = 'images/Image3-guarantees-cmp.png'


def render(theme, report=False):
    rc.set_theme(plt, theme)
    subs, vals = rc.outcome_table()
    combs = list(itertools.combinations(range(4), 2))
    pmat = {ci: rc.pair_pmf(subs, ci) for ci in combs}

    kinks = np.unique(vals)
    xr = kinks[-1]
    thrs = np.unique(np.concatenate([kinks, np.linspace(0, xr, 801)]))

    def payoff(ci):
        return np.array([np.sum(np.maximum(vals - t, 0.0) * pmat[ci])
                         for t in thrs])

    payoffs = {ci: payoff(ci) for ci in combs}
    best = np.max(list(payoffs.values()), axis=0)

    # Representative pairs: (HP, x) behaves identically to (DEF, x).
    curves = [
        ((0, 1), 'CRIT Rate + ATK%  (the "obvious" pick)', rc.BLUE, '-'),
        ((0, 3), 'CRIT Rate + a dump stat', rc.GOLD_DEEP, '-'),
        ((1, 3), 'ATK% + a dump stat', rc.GRAY, '--'),
        ((2, 3), 'both dump stats', rc.RED, ':'),
    ]

    fig, ax = plt.subplots(figsize=(10.4, 5.4), dpi=150)
    fig.subplots_adjust(left=0.09, right=0.98, top=0.86, bottom=0.14)
    rc.style_axes(ax)

    for ci, label, color, ls in curves:
        frac = np.full_like(best, np.nan)
        np.divide(payoffs[ci], best, out=frac, where=best > 1e-12)
        ax.plot(thrs, frac, ls, color=color, linewidth=2.2, label=label,
                zorder=3)

    # Crossover: where the obvious pick stops being (tied for) best.
    prefs = rc.calc_preference()
    cross = next(hi for lo, hi, winners in prefs if (0, 1) in winners)
    ax.axvline(cross, color=rc.MUTED, linewidth=1, linestyle=':',
               clip_on=False)
    ax.text(cross - 0.015 * xr, 1.02, 'easygoing: obvious pick wins',
            ha='right', va='bottom', fontsize=12, color=rc.TEXT,
            transform=ax.get_xaxis_transform())
    ax.text(cross + 0.015 * xr, 1.02, 'picky: dump pick wins',
            ha='left', va='bottom', fontsize=12, color=rc.TEXT,
            transform=ax.get_xaxis_transform())

    # The worst moment for the obvious pick.
    frac01 = payoffs[(0, 1)] / np.where(best > 1e-12, best, np.nan)
    i = int(np.nanargmin(frac01))
    ax.annotate(f'worst case: obvious pick gives\n'
                f'{frac01[i]:.0%} of the best choice',
                xy=(thrs[i], frac01[i]),
                xytext=(thrs[i] - 0.26 * xr, frac01[i] + 0.14),
                fontsize=11.4, color=rc.MUTED,
                arrowprops=dict(arrowstyle='-', color=rc.MUTED,
                                linewidth=0.8))

    ax.set_xlim(0, xr)
    ax.set_ylim(0.55, 1.02)
    ax.xaxis.set_major_formatter(lambda x, _: f'{x * 100:g}%')
    ax.yaxis.set_major_formatter(lambda y, _: f'{y:.0%}')
    ax.set_xlabel('the damage gain this artifact must beat '
                  'for you to keep it  (easygoing → picky)', fontsize=13.2)
    ax.set_ylabel('payoff, as % of the best pick', fontsize=13.2)
    ax.set_title('How each pick holds up as your standards rise',
                 fontsize=15.6, pad=34)
    ax.legend(loc='lower left', frameon=True, edgecolor='none',
              facecolor=rc.PAGE_BG, framealpha=0.92, fontsize=12.6)

    rc.save(fig, OUT, theme)
    plt.close(fig)
    if report:
        print(f'  crossover at bar = {cross * 100:.2f}%; worst '
              f'obvious-pick payoff {frac01[i]:.1%} '
              f'at bar = {thrs[i] * 100:.2f}%')


def main():
    render('light', report=True)
    render('dark')


if __name__ == '__main__':
    main()
