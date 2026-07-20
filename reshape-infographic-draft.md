## How reshaping works

While leveling up an artifact, each roll has 1/4 chance to land in each substat. The reshape guarantees activate _only_ on the last 2 (resp. 3,4) rolls if you need them to hit the guaranteed 2 rolls.
The effect is the *only* buckets with boosted probability are those with exactly 2 rolls in the selected stats.

Examples table:
| roll outcomes | default | reshape(CR, ATK%) | reshape(CR, DEF) |
| :--- | ---: | ---: | ---: | 
| [4, 0, 0, 0] | 0.39% | 0.39% | 0.39% |
| [0, 4, 0, 0] | 0.39% | 0.39% | **0%** |
| [2, 2, 0, 0] | 2.34% | 2.34% | **4.30%** |
| [2, 0, 1, 1] | 4.69% | **8.59%** | 4.69% |

<Image 1>

## Why it's sometimes correct to pick (CR, DEF)
Take note of the 2CR / 2ATK bucket in the above table. The probability of that event is boosted when you select (CR, DEF) because there are exactly 2 rolls between CR and DEF, which qualifies it for the reshape boost; meanwhile selecting (CR, ATK) does not grant that event a boost.

Depending on the damage threshold you're trying to beat (keep vs revert the reshape), that single event can dominate the comparison between selecting (CR, ATK) vs (CR, DEF), and make it unintuitively optimal to select a dump stat.

<Image 2> shows the best pair to guarantee for a simple formula of (a + 0.7*b). Your threshold (build quality), determines the best choice of guarantee, with higher thresholds favoring selecting a dump stat.
<!-- We can change this to more standard atk * (1 + cr cd) later -->

## How much do you lose from picking (CR, ATK%)

Up to 10% reduction in E[(dmg - thr)^+] in the example. It depends on the specific formula, but generally the optimal is within +/-10% of just picking the highest contribution substats (CR, ATK%).
