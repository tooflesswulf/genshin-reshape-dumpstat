"""Image 1: how the reshape promise plays out over the last two rolls.

Standalone replacement for the hand-made tree screenshot. Tracks how many
rolls have landed on the picked pair (CRIT Rate + ATK%) through rolls 3
and 4. States where the promise can still be missed get forced (gold)
arrows; branches that would break it die (0%). Probabilities are exact:
the mass freed by the dead branches is what boosts finishing on exactly
2 picked rolls from 37.5% to 68.75%. Renders a light and a dark variant
with transparent backgrounds, so the page's dotted ground shows through.

Run:  python make_image1.py
"""
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch, Wedge

import reshape_common as rc

OUT = 'images/Image1-reshape-probs.png'

CARD_W, CARD_H = 3.3, 1.
PIP_R, PIP_GAP = 0.19, 0.62


def draw_pick_pip(ax, cx, cy, alpha=1.0):
    """A picked-pair roll: half CRIT gold, half ATK% blue (the tree does
    not track which of the two stats a roll landed on)."""
    ax.add_patch(Wedge((cx, cy), PIP_R, 45, 225, facecolor=rc.GOLD,
                       edgecolor='none', alpha=alpha, zorder=5))
    ax.add_patch(Wedge((cx, cy), PIP_R, -135, 45, facecolor=rc.BLUE,
                       edgecolor='none', alpha=alpha, zorder=5))


def draw_card(ax, x, y, picked, junk, prob, dead=False, note=None,
              note_color=None):
    if dead:
        ax.add_patch(FancyBboxPatch(
            (x - CARD_W / 2, y - CARD_H / 2), CARD_W, CARD_H,
            boxstyle='round,pad=0.12,rounding_size=0.22',
            facecolor='none', edgecolor=rc.RED, linewidth=1.2,
            linestyle=(0, (3, 2)), alpha=0.6, zorder=4))
    else:
        ax.add_patch(FancyBboxPatch(
            (x - CARD_W / 2, y - CARD_H / 2), CARD_W, CARD_H,
            boxstyle='round,pad=0.12,rounding_size=0.22',
            facecolor=rc.CARD, edgecolor=rc.CARD_EDGE, zorder=4))
    pip_alpha = 0.45 if dead else 1.0
    x0 = x - PIP_GAP * (4 - 1) / 2
    for i in range(4):
        cx = x0 + i * PIP_GAP
        if i < picked:
            draw_pick_pip(ax, cx, y - 0.25, pip_alpha)
        elif i < picked + junk:
            ax.add_patch(Circle((cx, y - 0.25), PIP_R, facecolor=rc.GRAY,
                                edgecolor='none', alpha=pip_alpha, zorder=5))
        else:
            ax.add_patch(Circle((cx, y - 0.25), PIP_R, facecolor='none',
                                edgecolor=rc.PIP_EMPTY, linewidth=1.1,
                                linestyle=(0, (2, 2)), alpha=pip_alpha,
                                zorder=5))
    if dead:
        label, color = f'{prob:g}% — impossible', rc.RED
    else:
        label = f'{prob:g}%'
        color = rc.GOLD if note_color == rc.GREEN else rc.CARD_TEXT
    ax.text(x, y + 0.25, label, ha='center', va='center', fontsize=11.5,
            fontweight='bold', color=color, zorder=6)
    if note:
        ax.text(x, y - CARD_H / 2 - 0.42, note, ha='center', va='center',
                fontsize=8.8, color=note_color or rc.MUTED, zorder=6)


def draw_edge(ax, x1, y1, x2, y2, label, kind='normal'):
    color = {'normal': rc.MUTED, 'forced': rc.GOLD_DEEP,
             'dead': rc.RED}[kind]
    lw = 2.2 if kind == 'forced' else 1.4
    ls = (0, (3, 2)) if kind == 'dead' else '-'
    start = (x1 + CARD_W / 2 + 0.18, y1)
    end = (x2 - CARD_W / 2 - 0.25, y2)
    ax.annotate('', xy=end, xytext=start, zorder=3,
                arrowprops=dict(arrowstyle='-|>', color=color,
                                linewidth=lw, linestyle=ls,
                                shrinkA=0, shrinkB=0,
                                mutation_scale=14))
    mx, my = (start[0] + end[0]) / 2, (start[1] + end[1]) / 2
    weight = 'bold' if kind == 'forced' else 'normal'
    ax.text(mx, my + 0.16, label, ha='center', va='bottom', fontsize=9,
            color=color, fontweight=weight, zorder=6,
            bbox=dict(facecolor=rc.PAGE_BG, edgecolor='none', pad=1.2))


def render(theme):
    rc.set_theme(plt, theme)
    fig, ax = plt.subplots(figsize=(10.4, 6.52), dpi=150)
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
    ax.set_xlim(0, 16.9)
    ax.set_ylim(0, 10.6)
    ax.set_aspect('equal')
    ax.axis('off')

    c0, c1, c2 = 2.4, 8.45, 14.5
    for x, head in [(c0, 'halfway (2 rolls in)'), (c1, 'after roll 3'),
                    (c2, 'after all 4 rolls')]:
        ax.text(x, 10.0, head, ha='center', fontsize=11.5,
                fontweight='bold', color=rc.TEXT)

    # (picked, junk) -> (x, y, %): exact probabilities with the promise
    # "at least 2 rolls on the picked pair" active.
    N0 = {(2, 0): (c0, 7.6, 25), (1, 1): (c0, 5.3, 50),
          (0, 2): (c0, 3.0, 25)}
    N1 = {(3, 0): (c1, 8.5, 12.5), (2, 1): (c1, 6.2, 37.5),
          (1, 2): (c1, 3.9, 50), (0, 3): (c1, 1.6, 0)}
    N2 = {(4, 0): (c2, 8.9, 6.25), (3, 1): (c2, 6.6, 25),
          (2, 2): (c2, 4.3, 68.75), (1, 3): (c2, 2.0, 0)}

    notes = {(2, 2): ('would be 37.5% without the promise', rc.GREEN),
             (4, 0): ('unchanged', rc.MUTED),
             (3, 1): ('unchanged', rc.MUTED)}
    for col in (N0, N1, N2):
        for (p, j), (x, y, prob) in col.items():
            note, ncolor = notes.get((p, j), (None, None))
            draw_card(ax, x, y, p, j, prob, dead=(prob == 0),
                      note=note, note_color=ncolor)

    def edge(a, src, b, dst, label, kind='normal'):
        x1, y1, _ = a[src]
        x2, y2, _ = b[dst]
        draw_edge(ax, x1, y1, x2, y2, label, kind)

    edge(N0, (2, 0), N1, (3, 0), '50%')
    edge(N0, (2, 0), N1, (2, 1), '50%')
    edge(N0, (1, 1), N1, (2, 1), '50%')
    edge(N0, (1, 1), N1, (1, 2), '50%')
    edge(N0, (0, 2), N1, (1, 2), '100% — forced', 'forced')
    edge(N0, (0, 2), N1, (0, 3), '0%', 'dead')
    edge(N1, (3, 0), N2, (4, 0), '50%')
    edge(N1, (3, 0), N2, (3, 1), '50%')
    edge(N1, (2, 1), N2, (3, 1), '50%')
    edge(N1, (2, 1), N2, (2, 2), '50%')
    edge(N1, (1, 2), N2, (2, 2), '100% — forced', 'forced')
    edge(N1, (1, 2), N2, (1, 3), '0%', 'dead')

    # Legend, one line along the bottom.
    ly = 0.5
    items = [(None, 'split', 'roll on your picks (CRIT Rate / ATK%)'),
             (rc.GRAY, 'solid', 'roll elsewhere (HP / DEF)'),
             (None, 'dashed', 'not rolled yet')]
    lx = 0.9
    for color, style, text in items:
        if style == 'split':
            draw_pick_pip(ax, lx, ly)
        elif style == 'solid':
            ax.add_patch(Circle((lx, ly), PIP_R, facecolor=color,
                                edgecolor='none', zorder=5))
        else:
            ax.add_patch(Circle((lx, ly), PIP_R, facecolor='none',
                                edgecolor=rc.PIP_EMPTY, linewidth=1.1,
                                linestyle=(0, (2, 2)), zorder=5))
        t = ax.text(lx + 0.35, ly, text, ha='left', va='center',
                    fontsize=9.3, color=rc.MUTED, zorder=5)
        fig.canvas.draw()
        bb = t.get_window_extent().transformed(ax.transData.inverted())
        lx = bb.x1 + 0.75

    rc.save(fig, OUT, theme)
    plt.close(fig)


def main():
    for theme in rc.THEMES:
        render(theme)


if __name__ == '__main__':
    main()
