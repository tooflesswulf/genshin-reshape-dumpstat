"""Shared math + styling for the reshape infographic images.

Model (matches reshape.ipynb and the infographic table): N upgrade rolls,
each landing on one of 4 substats uniformly. Reshaping picks 2 substats
and guarantees at least MN rolls land on the pair; the guarantee only
forces the final rolls when they are the last chance to hit it.

Stat order: 0 = CRIT Rate, 1 = ATK%, 2 = HP, 3 = DEF.
Damage: standard ATK x (1 + CRIT Rate x CRIT DMG) for a 3000-ATK
character at 80% / 180% crit; fn returns the % improvement over the
artifact contributing nothing, so HP and DEF are pure junk.

Each figure is rendered twice -- a light and a dark variant with
transparent backgrounds -- so the page can swap them with its theme and
the dotted ground shows through.
"""
import itertools

import numpy as np
from scipy.special import binom
from scipy.stats import multinomial

N_ROLLS = 4
MN = 2
STAT_NAMES = ['CRIT Rate', 'ATK%', 'HP', 'DEF']


def fn(counts):
    a, b, c, d = counts
    atk = 3000 + 900 * .0583 * b
    cr = .8 + .0389 * a
    cd = 1.8
    baseval = 3000 * (1 + .8 * 1.8)
    return atk * (1 + cr * cd) / baseval - 1


def reshape_prob(counts, reshape_ixs=(0, 1), reshape_min=0):
    counts = np.array(counts)
    N = int(np.sum(counts))
    rv = multinomial(N, [1 / 4] * 4)

    if reshape_min == 0:
        return rv.pmf(counts)

    reshape_total = np.sum(counts[list(reshape_ixs)])
    if reshape_total < reshape_min:
        return 0.0
    if reshape_total == reshape_min:
        # Statistics only modified if reshape guarantees triggered.
        porig = binom(N, reshape_total) / (2 ** N)
        pboosted = np.sum([binom(N, i) / (2 ** N)
                           for i in range(reshape_total + 1)])
        return rv.pmf(counts) * pboosted / porig
    return rv.pmf(counts)


def sums(length, total_sum):
    if length == 1:
        yield (total_sum,)
    else:
        for value in range(total_sum + 1):
            for permutation in sums(length - 1, total_sum - value):
                yield (value,) + permutation


def outcome_table(N=N_ROLLS):
    """All roll outcomes and their damage values."""
    subs = np.array(list(sums(4, N)))
    vals = np.array([fn(c) for c in subs])
    return subs, vals


def pair_pmf(subs, pair, mn=MN):
    """Probability of each outcome when guaranteeing `pair` (mn=0: no reshape)."""
    return np.array([reshape_prob(c, pair, mn) for c in subs])


def calc_preference(fun=fn, N=N_ROLLS, mn=MN, tol=1e-9):
    """For each threshold thr, the payoff of a reshape pair is
    E[(damage - thr)^+]. Returns the intervals of thr on which each pair is
    preferred, as a list of (lo, hi, [best pairs]). See reshape.ipynb for
    the piecewise-linear argument behind the candidate boundaries.
    """
    subs = np.array(list(sums(4, N)))
    vals = np.array([fun(c) for c in subs])
    combs = list(itertools.combinations(range(4), 2))
    pmat = {ci: pair_pmf(subs, ci, mn) for ci in combs}

    def Eup(ci, thr):
        return np.sum(np.maximum(vals - thr, 0.0) * pmat[ci])

    def line(ci, lo):
        mask = vals > lo + tol
        return np.sum(vals[mask] * pmat[ci][mask]), np.sum(pmat[ci][mask])

    segments = sorted({0.0, *np.unique(vals)})
    cands = set(segments)
    for lo, hi in zip(segments[:-1], segments[1:]):
        for c1, c2 in itertools.combinations(combs, 2):
            (a1, b1), (a2, b2) = line(c1, lo), line(c2, lo)
            if abs(b1 - b2) > tol:
                t = (a1 - a2) / (b1 - b2)
                if lo + tol < t < hi - tol:
                    cands.add(t)
    cands = sorted(cands)

    intervals = []
    for lo, hi in zip(cands[:-1], cands[1:]):
        mid = (lo + hi) / 2
        scores = {ci: Eup(ci, mid) for ci in combs}
        best = max(scores.values())
        winners = [ci for ci in combs if scores[ci] >= best - tol]
        if intervals and intervals[-1][2] == winners:
            intervals[-1] = (intervals[-1][0], hi, winners)
        else:
            intervals.append((lo, hi, winners))
    return intervals


# ---- theming, matched to the infographic page ----
# Figures are transparent; PAGE_BG is only used to back small labels that
# must mask the page's dot grid (it matches the page ground per theme).
_THEMES = {
    'light': dict(
        TEXT='#2a3140', MUTED='#5c6577', LINE='#dce0e7',
        PAGE_BG='#f5f6f8', GOLD='#e9b54d', GOLD_DEEP='#c28f2c',
        BLUE='#4a6fb5', GRAY='#9aa3b2', GREEN='#3e8e4b', RED='#b8402f',
        PURPLE='#8258c9', BROWN='#8f5a2e',
        CARD='#ffffff', CARD_EDGE='#dce0e7', CARD_TEXT='#000000', PIP_EMPTY='#7d8798',
    ),
    'dark': dict(
        TEXT='#e7eaf1', MUTED='#9aa3b5', LINE='#333a48',
        PAGE_BG='#1e222b', GOLD='#e9b54d', GOLD_DEEP='#d9a53e',
        BLUE='#7095d6', GRAY='#7f8a9c', GREEN='#5fae6d', RED='#d0604d',
        PURPLE='#a98fe0', BROWN='#bd8a58',
        CARD='#313949', CARD_EDGE='none', CARD_TEXT='#f2f4f8', PIP_EMPTY='#55607a',
    ),
}
THEMES = list(_THEMES)


def set_theme(plt, name):
    """Load a theme's palette into this module's globals and rcParams."""
    globals().update(_THEMES[name])
    globals()['INK'] = _THEMES[name]['TEXT']
    plt.rcParams.update({
        'font.sans-serif': ['Seravek', 'Avenir Next', 'Helvetica Neue',
                            'Arial', 'DejaVu Sans'],
        'font.family': 'sans-serif',
        'text.color': TEXT,
        'axes.labelcolor': TEXT,
        'axes.titlecolor': TEXT,
    })


def style_axes(ax):
    ax.set_facecolor('none')
    for side in ('top', 'right'):
        ax.spines[side].set_visible(False)
    for side in ('left', 'bottom'):
        ax.spines[side].set_color(LINE)
    ax.tick_params(colors=MUTED, labelsize=12)
    ax.yaxis.grid(True, color=LINE, linewidth=0.7)
    ax.set_axisbelow(True)


def save(fig, out, theme):
    """Write the figure as <out>.png (light) or <out>-dark.png."""
    path = out if theme == 'light' else out.replace('.png', '-dark.png')
    fig.savefig(path, transparent=True)
    print(f'wrote {path}')
