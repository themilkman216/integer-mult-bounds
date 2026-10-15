# Bit-side wall screen for the selected PR589 word

**Exact favourable-relaxation screen; no construction, supplier, or kappa.**
`screen.py` reuses the pinned interval engine
[complex-local-word-ceiling](../complex-local-word-ceiling/ceiling.py) at the
selected bit parameters (`m=64`, 888 families / 9 stages, copy charge 63,
per-call profile `{1:1323, 2:1342, 3:79, 4:44, 5:102, 6:11, 7:19}`) and
prices named changed hypotheses one at a time. Every number is a certified
grid bracket `relax(a_lo) < 1 < relax(a_hi)`; a ceiling bounds every
completion with that local profile under the coverage law. The exact moment
of a completed word remains the acceptance test, κ readings use the planning
transfer `κ = a/(1+a)`, and the complex side currently binds the selected
κ = 836330098538459/500000000000000000.

Headline readings (`RESULT.json`, status `PASS_MUSE_OOD_BIT_WALL_SCREEN`):

- **B0 base.** Ceiling `a_hi = 0.001955918756`; selected bit endpoint sits at
  ratio 0.8862 of it; cross-checked against the independent
  bit-revision3-levers-seed03 bracket.
- **B1 helper skeleton.** Replacing fragmented helper climbs by `k` rank-8
  climbs: the κ×2 target needs `k ≤ 258` (267 registers incl. totals) with
  shipped data ladders — below the shipped 439, above the format-limits
  monotone floors (212 sink-only / 222 with shipped ladders), so the route is
  arithmetically open but owes a frame/window realisation. `k=0` ceilings:
  0.00505 (shipped data) / 0.00679 (ideal data).
- **B2 descents.** Below-floor helper counts can pay certified added-mass
  budgets (e.g. at 212 registers, rank-1-shaped 200.6 / rank-8-shaped 443.7
  mass) before κ×2 fails.
- **B3 copy charge.** Price curve in `cst`: 63 → 0.001956, 42 → 0.003109,
  21 → 0.004264, 0 → 0.005420. Reductions below 63 must escape the
  pairing-rank floor (see muse-ood-block-copy for the block-pricing test);
  the 102-port/54-copy scaled puncture what-if reaches only 0.002188, with
  `D = T[(s−1)v − s·cst]` gaining just +9 per replica unit before `w` shrinks.
- **B4 data algebra.** Deleting *all* data-register work caps at 0.002593 and
  still fails κ×2: no data-side algebra alone suffices.
- **B5 connectors.** Even a generous fictional conversion of 1/37 (resp.
  1/10) of all local mass to idle caps at 0.002014 (resp. 0.002191).
- **B6 schedule fence.** Shipped `D/W = 107/296` attains the #2052 Theorem S
  per-port bound at `s=9` (checked as exact fraction arithmetic; that
  theorem's own escapes are named in `RESULT.json`).

Reproduce: `python3 -I -O -B research/muse-ood-bit-wall/screen.py`
(regenerates `RESULT.json`; pass `--out PATH` to write elsewhere). Controls
include the class-split mass identity (5129 = 1554 + 3512 + 63), an
extra-rank-1 monotonicity check, custom-`R` equality with the pinned engine
at `R=45`, and the independent seed03 bracket meeting ours. Idle ranks
`R=50/53` are labelled halving-depth what-ifs needing a new row bound.

Base `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`. Prepared with substantial
assistance from Meta Muse (muse-wonder-full-1.0). Apache-2.0.

## Open next questions

1. **Can a ≤267-register helper skeleton be realised with legal frames?**
   B1/B2 leave arithmetic room; the blocker is a monotone frame/window
   schedule (or priced descents) on an actual word, not the ceiling.
2. **Does any changed-hypothesis row survive a *joint* screen?** Each lever
   here is one-at-a-time; first compose the two strongest (helper skeleton
   with copy charge) in one profile before drawing planning conclusions.
