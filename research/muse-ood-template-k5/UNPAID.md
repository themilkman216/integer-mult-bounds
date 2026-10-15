# Addendum: cheapest decisive test for the surviving unpaid-coordinate lever

Companion to `README.md` (K=5 legal-window falsification, preserved unchanged). **No construction, no new supplier, no new κ.** Selected record κ = 836330098538459/500000000000000000 unchanged; exact moment acceptance test still governs any future claim. Evidence: `unpaid.py` → `UNPAID.json`, checked by `verify_unpaid.py`. Meta Muse (`muse-wonder-full-1.0`) assisted; see README credit section.

## Why this lever, and why this test first

#2052 Theorem S explicitly does **not** cover ρ through a third bank class (≥2 unpaid coordinates per family), #2076 covers only zero-storage early centre fanout in the scalar projection, and #2048 covers only an 8-row linear transcript for two centre cuts. The unpaid lever is therefore the strongest surviving ceiling from round 1 (unpaid-2 ×3.774 shape-fixed). Its cheapest decisive test is not a construction attempt but exact sign evidence at the declared planning target `a = 1/99`, on the base *legal* template (896 families, 9 stages, m=73, R=51), selected PR1094 word fixed, under the pinned engine's coverage what-if `total = (m − unpaid)w + centre`. Three questions decide where effort belongs: does unpaid-2 reach 1/99 at any centre (T1)? If not, how large must a partner rank-shape improvement be, in exact rank-1 mass/call (T2)? Does unpaid-3 still pass with its round-1 advancement budget intact (T3)?

## Exact evidence (`UNPAID.json` is authoritative; decimals shown to 12 significant figures)

**T1 — certified `relax(1/99)` signs (whole exact interval on one side of 1):**

| Point | relax interval (dec) | Sign | Reading |
|---|---|---|---|
| unpaid=2, centre=64 | [1.01105474131, 1.01105474131] | **+1 (fails)** | 1.105% over budget at zero advancement cost |
| unpaid=2, centre=0 | [1.00221651998, 1.00221651998] | **+1 (fails)** | fails even centre-free, by 0.222% |
| unpaid=3, centre=64 | [0.99730639702, 0.99730639702] | −1 (passes) | passes at full centre |
| unpaid=3, centre=0 | [0.988468175691, 0.988468175691] | −1 (passes) | passes with 1.153% slack |

So on this word shape **no (unpaid ≤ 2, any centre) reaches 1/99** — now certified by displayed exact intervals, not only by round 1's "fails at 0" budget notation. The centre-free unpaid-2 failure is narrow (0.222%), which is exactly why T2 matters: the partner-lever size is finite and now sharp.

**T2 — rank-1 deletion a partner lever must supply for unpaid=2 at 1/99** (0.1-grid adjacent brackets, certified opposite signs at both endpoints; deletion = removing fractional rank-1 children from the 2,412/call, freed mass re-billed as rank-51 idle inside the same coverage total — the most favourable billing for the partner):

| Centre | Still fails | First passes | Fraction of rank-1 stock |
|---|---|---|---|
| 64 (full) | delete 1975.8 | delete **1975.9** | 81.9% of 2412 |
| 0 (free) | delete 396.1 | delete **396.2** | 16.4% of 2412 |

Reading: unpaid-2 + full centre needs a partner that removes four-fifths of the rank-1 mass — implausible as a mere decoder reshaping (round-1 candidate-D excess arithmetic already required ~95% excess discount). Unpaid-2 + centre-free needs a 16.4% rank-1 reduction — still a real second mechanism, and centre-free itself is unbuilt (and narrowed by #2076/#2048 to persistent-bank/phase-reorder routes). Either way, **unpaid-2 alone is decisively insufficient for 1/99; the minimal sufficient coverage change on this shape is unpaid-3, or unpaid-2 plus two stacked partner levers.**

**T3 — unpaid-3 advancement budget re-confirmed** (centre 64, target 1/99, added rank-1 mass/call): +481.4 passes with `relax_hi = 0.999999808296` (sign −1); +481.5 fails with `relax_lo = 1.00000036779` (sign +1). Round 1's sharp bracket [481.4 / 481.5] stands under fresh recomputation. Both extra advancements together may therefore cost at most 481.4 rank-1-shaped mass/call (≈4.84 per live family at w = 896/9); any three-bank contract whose advancement word exceeds this — e.g. a fresh small-rank data climb per port per extra coordinate — is falsified before hosting is even considered.

## What this test does and does not decide

Decided, under the stated favourable hypotheses: unpaid-2 (any centre, fixed selected shape) cannot certify `a = 1/99`; the exact partner-lever sizes above; unpaid-3's zero-cost pass and 481.4 budget. Not decided: whether any three-bank ρ / endpoint contract realises unpaid ≥ 2 at all (progress preservation, dirty restoration, chronological hosting all open — the row-space waste-identity screen in README *Next experiment* remains the gate); whether a different local word shape changes the T2 fractions (rank-shape is the named partner, outside this test); any κ consequence without a bit-side co-improvement (round-1 S5 joint budgets unchanged). Covered obstructions are not reopened: the changed hypothesis throughout is exactly the coverage law `(m−1)W + cst·N` → `(m−unpaid)W + cst·N`, which #2052 §5 names as its uncovered case.

## #2044 relevance (restated for this addendum)

Unchanged from README: #2044's conditional κ = 0.0016797549561255 (+0.424% over selected κ) is unreviewed, conditional on inherited hypotheses plus new union-schedule/structured-boundary/gauge-free constructions its own README flags as requiring independent review (precision section an error argument, not a stability theorem; large-p real-regime check unrun; exponent margin 2e-30010, no practical cutoff). It does not move the baseline for any budget above. If its T74 supplier lineage were admitted, T1–T3 would need re-issuing on the T74 per-call words (the unpaid what-if is word-shape-dependent); the K=5 falsification would not change, since #2052 already prices B₅ negatively on those words.

## Reproduce

```sh
python3 -B research/muse-ood-template-k5/unpaid.py          # regenerates UNPAID.json
python3 -B research/muse-ood-template-k5/verify_unpaid.py   # PASS_MUSE_OOD_TEMPLATE_K5_UNPAID_VERIFY
python3 -I -O -B research/muse-ood-template-k5/verify_unpaid.py
```
