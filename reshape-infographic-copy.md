# Simplified infographic copy

Working title: **"Pick a junk stat on purpose — the weird math of artifact reshaping"**

Design note: each section is one infographic panel. Text is cut to caption length,
plain words, no notation. Index translation for the graphs: 0 = CRIT Rate, 1 = ATK%,
2 = ATK, 3 = DEF.

---

## Panel 1 — The promise

Each upgrade roll lands on one of the artifact's 4 substats at random — 1-in-4 each.

Reshaping lets you pick 2 substats. The game promises: **at least 2 rolls will land
on your picks.** It only steps in when it has to — if you're about to run out of
rolls, the last ones get forced onto your picks. Otherwise nothing changes.

*(Image 1: roll tree — the forced arrows are the promise kicking in.)*

## Panel 2 — The promise doesn't add luck. It moves it.

- Outcomes with **0 or 1** rolls on your picks → now impossible.
- Outcomes with **exactly 2** rolls on your picks → get all the freed-up chance.
- Outcomes with **3 or 4** rolls on your picks → completely unchanged.

That last line is the whole trick: **outcomes stacked in your picks get no boost at all.**

## Panel 3 — The trick

Good stats: CRIT Rate and ATK%. Junk: DEF. The very best roll (4× CRIT) is
equally likely under every pick — the roll that tells picks apart is
2 CRIT + 2 ATK%.

| Outcome | No reshape | Pick CRIT + ATK% | Pick CRIT + DEF |
| :--- | ---: | ---: | ---: |
| 4× CRIT | 0.39% | 0.39% | 0.39% |
| 4× ATK% | 0.39% | 0.39% | **0%** ☠ |
| 2 CRIT + 2 ATK% ★ | 2.34% | 2.34% | **4.30%** ← nearly doubled |
| 2 CRIT + 2 junk | 4.69% | **8.59%** | 4.69% |

★ = the best roll a pick can change. Top rolls like 4× CRIT are identical under
every pick — no choice touches them.

Pick both good stats and the ★ roll already has 4 hits on your picks — so it gets
**nothing**. The boost lands on so-so "2 good + 2 junk" rolls instead.

Pick CRIT + DEF and the ★ roll has exactly 2 hits (2 CRIT, 0 DEF) — so it
**nearly doubles**. The price: rolls like 4× ATK% become impossible.

## Panel 4 — So which do you pick?

Depends on the bar this artifact must clear before you'd actually keep it.

- **Modest bar** — any solid piece is an upgrade → **pick both good stats.**
  Best average. Raises the floor.
- **Sky-high bar** — only a near-perfect piece changes anything → **pick one good
  stat + one junk stat.** The guarantee spends itself making jackpots more likely
  instead of propping up mediocre rolls you'd throw away anyway.

*(Images 2 & 3: the strip above the bars shows the best pick flipping as the bar
rises; crossover ≈ 4.4% damage gain in this model. Each image has a light and a
dark variant with transparent backgrounds, swapped by the page's theme. Generated
by make_image1.py / make_image2.py / make_image3.py — run with the `jupyter`
conda env, then build_infographic.py.)*

## Panel 5 — Fine print

Model: four rolls, keep-or-revert at your bar. Damage uses the standard
ATK × (1 + CRIT Rate × CRIT DMG) formula for a typical build (3,000 ATK,
80% / 180% crit, 900-ATK weapon); the artifact's worth is its % damage gain,
and HP / DEF add nothing. At low bars the wrong pick costs little; at the
pickiest settings the "obvious" pick delivers as little as 79% of the best
choice (worst case, bar ≈ 8.6% gain). Exact cutoffs depend on your build.
