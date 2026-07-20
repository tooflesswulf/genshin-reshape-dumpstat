"""Image 2: what artifact you end up with, under each reshape choice.

Broad-audience redesign of the notebook's plot_reshape_comparison: plain
grouped bars (total chance per damage value, no per-outcome stacking or
hatching), named picks instead of index pairs, and a strip on top reading
off the best pick as your keep-it bar rises. Damage is the % improvement
from the finished artifact. Renders a light and a dark variant.

Run:  python make_image2.py
"""
import matplotlib.pyplot as plt
import numpy as np

import reshape_common as rc

OUT = 'images/Image2-guarantee-vs-thr.png'


def render(theme, report=False):
    rc.set_theme(plt, theme)
    subs, vals = rc.outcome_table()
    uvals = np.unique(vals)
    slots = np.arange(len(uvals))

    configs = [
        ('no reshape', (0, 1), 0, rc.GRAY),
        ('pick CRIT Rate + ATK%', (0, 1), rc.MN, rc.BLUE),
        ('pick CRIT Rate + DEF', (0, 3), rc.MN, rc.GOLD),
    ]
    # Total chance of each damage value under each config.
    dists = []
    for _, pair, mn, _ in configs:
        pm = rc.pair_pmf(subs, pair, mn)
        dists.append(np.array([pm[np.isclose(vals, v)].sum()
                               for v in uvals]))

    fig, ax = plt.subplots(figsize=(10.4, 5.6), dpi=150)
    fig.subplots_adjust(left=0.08, right=0.98, top=0.80, bottom=0.13)
    rc.style_axes(ax)

    width = 0.25
    for k, ((name, _, _, color), dist) in enumerate(zip(configs, dists)):
        ax.bar(slots + (k - 1) * width * 1.08, dist, width=width,
               label=name, color=color, linewidth=0, zorder=3)

    ax.set_xticks(slots, [f'{v * 100:.1f}%' for v in uvals], fontsize=9)
    ax.set_xlabel('damage gain from the finished artifact  '
                  '(values in increasing order)', fontsize=11)
    ax.set_ylabel('chance', fontsize=11)
    ax.yaxis.set_major_formatter(lambda y, _: f'{y:.0%}')
    ax.legend(loc='upper right', frameon=False, fontsize=10.5)

    # Callouts for the two outcomes the story hinges on, located by their
    # roll counts so they track the damage formula.
    def callout(counts, k, text, dx, dy, ha):
        slot = int(np.argmin(np.abs(uvals - rc.fn(counts))))
        x = slot + (k - 1) * width * 1.08
        y = dists[k][slot]
        ax.annotate(text, xy=(x, y), xytext=(x + dx, y + dy),
                    fontsize=9.5, color=rc.MUTED, ha=ha,
                    arrowprops=dict(arrowstyle='-', color=rc.MUTED,
                                    linewidth=0.8))
    callout([1, 1, 2, 0], 1, 'so-so artifacts:\nCRIT+ATK% boosts these',
            0.6, -0.055, 'left')
    callout([2, 2, 0, 0], 2, 'the best roll a pick can change\n'
                             '(2 CRIT + 2 ATK%): only CRIT+DEF boosts it',
            -0.5, 0.13, 'right')

    # Strip above the bars: the best pick, by where your bar sits.
    prefs = rc.calc_preference()
    zones = []
    for lo, hi, winners in prefs:
        if (0, 1) in winners and len(winners) > 2:
            label = 'tie'
        elif (0, 1) in winners:
            label = 'pick CRIT Rate + ATK%'
        else:
            label = 'pick CRIT Rate + a dump stat'
        if zones and zones[-1][2] == label:
            zones[-1][1] = hi
        else:
            zones.append([lo, hi, label])
    # Drop degenerate slivers (e.g. an exact-tie boundary point).
    zones = [z for z in zones if z[1] - z[0] > 1e-9]

    def pos(t):
        return float(np.interp(t, uvals, slots))

    strip_colors = {'pick CRIT Rate + ATK%': rc.BLUE,
                    'pick CRIT Rate + a dump stat': rc.GOLD,
                    'tie': rc.GRAY}
    y0, y1 = 1.04, 1.14
    for i, (lo, hi, label) in enumerate(zones):
        x0 = -0.5 if i == 0 else pos(lo)
        x1 = len(uvals) - 0.5 if i == len(zones) - 1 else pos(hi)
        color = strip_colors[label]
        ax.add_patch(plt.Rectangle(
            (x0, y0), x1 - x0, y1 - y0, transform=ax.get_xaxis_transform(),
            facecolor=color, alpha=0.22, edgecolor=color, linewidth=0.8,
            clip_on=False))
        if x1 - x0 > 1.2:
            ax.text((x0 + x1) / 2, (y0 + y1) / 2, label, fontsize=9.5,
                    ha='center', va='center', color=rc.TEXT,
                    transform=ax.get_xaxis_transform())
        if i:
            ax.axvline(x0, color=rc.MUTED, linewidth=0.9, linestyle=':',
                       zorder=2)
            ax.text(x0, y1 + 0.015, f'{lo * 100:.1f}%', fontsize=8.5,
                    ha='center', va='bottom', color=rc.MUTED,
                    transform=ax.get_xaxis_transform())
    ax.text(-0.5, y1 + 0.055, 'best pick, by the damage gain you need '
            'this artifact to beat:', fontsize=11,
            transform=ax.get_xaxis_transform())

    rc.save(fig, OUT, theme)
    plt.close(fig)
    if report:
        for lo, hi, label in zones:
            print(f'  bar in [{lo * 100:.2f}%, {hi * 100:.2f}%) -> {label}')


def main():
    render('light', report=True)
    render('dark')


if __name__ == '__main__':
    main()
