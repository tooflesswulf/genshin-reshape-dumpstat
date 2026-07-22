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
from matplotlib.colors import to_rgba
from matplotlib.patches import BoxStyle
from matplotlib.transforms import Affine2D, offset_copy
from scipy.interpolate import PchipInterpolator

import reshape_common as rc

OUT = 'images/Image2-guarantee-vs-thr.png'

# X-axis pip chain: PIP_ANGLE tilts both the chain of four pips and the
# pips themselves (45deg -> diamonds tiling along the diagonal). PIP_STEP
# is their center-to-center spacing in points; PIP_Y is the axis-fraction
# height of the chain's top (last) pip, which lands at the bin center.
PIP_ANGLE = 40.0
PIP_STEP = 9.3
PIP_Y = -0.05

# Pip glyph: a rounded square (the .pip CSS in the infographic template,
# 11px box / 3px radius). On the axis it is tilted by PIP_ANGLE; the
# legend key uses it upright.
PIP_SQUARE = BoxStyle('round', pad=0, rounding_size=0.3)(
    -0.5, -0.5, 1.0, 1.0, 1.0)
PIP_MARKER = PIP_SQUARE.transformed(Affine2D().rotate_deg(PIP_ANGLE))


def render(theme, report=False):
    rc.set_theme(plt, theme)
    subs, vals = rc.outcome_table()
    uvals = np.unique(vals)
    slots = np.arange(len(uvals))

    configs = [
        ('no reshape', (0, 1), 0, rc.GRAY),
        ('pick CRIT Rate + ATK%', (0, 1), rc.MN, rc.BROWN),
        ('pick CRIT Rate + DEF', (0, 3), rc.MN, rc.PURPLE),
    ]
    # Total chance of each damage value under each config.
    dists = []
    for _, pair, mn, _ in configs:
        pm = rc.pair_pmf(subs, pair, mn)
        dists.append(np.array([pm[np.isclose(vals, v)].sum()
                               for v in uvals]))

    fig, ax = plt.subplots(figsize=(10.4, 5.6), dpi=150)
    fig.subplots_adjust(left=0.08, right=0.98, top=0.80, bottom=0.19)
    rc.style_axes(ax)

    # Three overlaid histograms (one per config, all centered on each bin),
    # each capped by a smooth spline through its bar tops. A distinct hollow
    # marker at every bin tip keeps the splines legible where they overlap.
    width = 0.9
    markers = ['.', '^', 's']
    xg = np.linspace(slots[0], slots[-1], 400)
    for (name, _, _, color), dist, mk in zip(configs, dists, markers):
        # Translucent fill (RGBA so alpha doesn't dim the edge) with a solid
        # outline in the config color.
        ax.bar(slots, dist, width=width, facecolor=to_rgba(color, 0.46),
               edgecolor=color, linewidth=1.2, zorder=2)
        # ax.plot(xg, PchipInterpolator(slots, dist)(xg), color=color,
        #         linewidth=2.3, zorder=4)
        # One ink color for every tip (rc.TEXT tracks the theme, so it reads
        # on the light page and the dark navy alike); shape tells them apart.
        ax.plot(slots, dist, linestyle='none', marker=mk, markersize=7.,
                markerfacecolor='none', markeredgecolor=rc.TEXT,
                markeredgewidth=1., zorder=5)

    # X labels: the four substat rolls behind each damage value, drawn as
    # pips (gold = CRIT Rate, blue = ATK%, gray = junk HP/DEF). Each unique
    # damage value pins down one (CRIT, ATK%) count, the rest being junk.
    ab_of = {}
    for c, v in zip(subs, vals):
        ab_of.setdefault(round(float(v), 9), (int(c[0]), int(c[1])))
    xt = ax.get_xaxis_transform()

    def pip(x, y, color, dx=0.0, dy=0.0, marker=PIP_MARKER):
        # dx/dy are screen-space point offsets from the (x, y) anchor, so a
        # row of pips can climb at a true 45deg regardless of axis scaling.
        tr = offset_copy(xt, fig=fig, x=dx, y=dy, units='points')
        ax.plot([x], [y], marker=marker, markersize=9.4, color=color,
                markeredgecolor=color, markeredgewidth=0.6,
                linestyle='none', transform=tr, clip_on=False, zorder=4)

    rad = np.deg2rad(PIP_ANGLE)
    for s, v in zip(slots, uvals):
        a, b = ab_of[round(float(v), 9)]
        cols = [rc.GOLD] * a + [rc.BLUE] * b + [rc.GRAY] * (rc.N_ROLLS - a - b)
        for i, col in enumerate(cols):
            # Chain climbs to the right; the last pip lands at the bin center.
            off = (i - (rc.N_ROLLS - 1)) * PIP_STEP
            pip(s, PIP_Y, col, dx=off * np.cos(rad), dy=off * np.sin(rad))
    ax.set_xticks(slots, [''] * len(slots))
    ax.tick_params(axis='x', length=0)

    # Pip key, doubling as the x-axis caption.
    key = [(rc.GOLD, 'CRIT Rate'), (rc.BLUE, 'ATK%'),
           (rc.GRAY, 'HP / DEF')]
    kx, ky = 0.0, -0.19
    for col, txt in key:
        pip(kx, ky, col, marker=PIP_SQUARE)
        t = ax.annotate(txt, xy=(kx, ky), xytext=(10, 0),
                        textcoords='offset points', xycoords=xt,
                        va='center', ha='left', fontsize=11.4, color=rc.MUTED)
        fig.canvas.draw()
        bb = t.get_window_extent().transformed(xt.inverted())
        kx = bb.x1 + 0.55
    ax.annotate('— the finished artifact’s four rolls, in increasing '
                'damage order', xy=(kx - 0.35, ky), xycoords=xt,
                va='center', ha='left', fontsize=11.4, color=rc.MUTED)
    ax.set_ylabel('chance', fontsize=13.2)
    ax.yaxis.set_major_formatter(lambda y, _: f'{y:.0%}')
    handles = [plt.Line2D([0], [0], color=color, linewidth=2.3, marker=mk,
                          markersize=7., markerfacecolor='none',
                          markeredgecolor=rc.TEXT, markeredgewidth=1.)
               for (name, _, _, color), mk in zip(configs, markers)]
    ax.legend(handles, [c[0] for c in configs], loc='upper right',
              frameon=False, fontsize=12.6)

    # Callouts for the outcomes the story hinges on, located by their roll
    # counts so they track the damage formula. Each callout can point to
    # several buckets: the text anchors on the first, leaders reach the rest.
    def callout(buckets, k, text, dx, dy, ha):
        def tip(counts):
            slot = int(np.argmin(np.abs(uvals - rc.fn(counts))))
            return slot, dists[k][slot]
        x0, y0 = tip(buckets[0])
        tx, ty = x0 + dx, y0 + dy
        leader = dict(arrowstyle='-', color=rc.MUTED, linewidth=0.8)
        ax.annotate(text, xy=(x0, y0), xytext=(tx, ty),
                    fontsize=11.4, color=rc.MUTED, ha=ha, arrowprops=leader)
        for counts in buckets[1:]:
            xi, yi = tip(counts)
            ax.annotate('', xy=(xi, yi), xytext=(tx, ty),
                        arrowprops=dict(leader, shrinkA=8))
    callout([[1, 1, 2, 0], [0, 2, 2, 0], [2, 0, 2, 0]], 1,
            'so-so artifacts:\nCRIT+ATK% boosts these', 0.6, -0.055, 'left')
    callout([[2, 2, 0, 0], [2, 1, 1, 0]], 2,
            'CRIT+DEF boosts a couple\ntop-end outcomes', -1.5, 0.14, 'center')

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

    strip_colors = {'pick CRIT Rate + ATK%': rc.BROWN,
                    'pick CRIT Rate + a dump stat': rc.PURPLE,
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
            ax.text((x0 + x1) / 2, (y0 + y1) / 2, label, fontsize=11.4,
                    ha='center', va='center', color=rc.TEXT,
                    transform=ax.get_xaxis_transform())
        if i:
            ax.axvline(x0, color=rc.MUTED, linewidth=0.9, linestyle=':',
                       zorder=2)
            ax.text(x0, y1 + 0.015, f'{lo * 100:.1f}%', fontsize=10.2,
                    ha='center', va='bottom', color=rc.MUTED,
                    transform=ax.get_xaxis_transform())
    ax.text(-0.5, y1 + 0.075, 'best pick, by the damage gain you need '
            'this artifact to beat:', fontsize=13.2,
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
