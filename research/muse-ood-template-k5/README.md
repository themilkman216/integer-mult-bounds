# K=5 template lever vs Theorem S (#2052) and the centre obstructions (#2076, #2048): verdict, exact re-price, and pivot

**Scoped falsification and handoff. No construction, no new supplier, no new κ.**
The selected record (κ = 836330098538459/500000000000000000 ≈ 0.00167266019708, [#1094](https://github.com/CrocSwap/integer-mult-bounds/pull/1094)) is unchanged. Upstream `main` is `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2` (priority revision 4), unchanged as of 2026-10-14T22:17Z. Every number below is either an exact pinned-engine evaluation under stated hypotheses or a cited unreviewed open-PR claim; the exact moment of a completed construction remains the acceptance test.

Out-of-distribution session (Meta Muse, `muse-wonder-full-1.0`; see *Credit and disclosure*). Local-only package for maintainer review: nothing was committed, pushed or posted. Round-1 predecessor: `research/muse-ood-coverage-template/` (its K=5 break-even budget, 182.0 rank-1-shaped mass/call to the bit endpoint, is the object under test here).

## FIRST DELIVERABLE — verdict (written before any experiment in this package)

### Verdict in one paragraph

**The K=5 template lever, as screened in round 1, does not survive. Theorem S ([#2052](https://github.com/CrocSwap/integer-mult-bounds/pull/2052), head `79cb4818`, `research/multipair-schedule-bound/`) does not exclude the B₅ *schedule* — B₅ attains its bound — but it excludes the round-1 *gain*: once the template is charged at its legal window dimension `m = 1 + 8s` with the full per-pair-call profile, B₅ is dominated by B₄, exactly as #2052 prices on the T74 words (−1.40%). The round-1 +6.0% came from holding `m = 73` and `R = 51` fixed while raising the stage count to 11, which no legal template does: concurrent calls share the stage's 8-dimensional window, so `s = 11` forces `m = 89`. The unpaid-coordinate lever is *not* excluded by any of the three new PRs — #2052 lists it explicitly as uncovered (ρ through a third bank class) — and remains the strongest surviving lever. The centre lever is narrowed, not closed: [#2076](https://github.com/CrocSwap/integer-mult-bounds/pull/2076) kills only zero-storage early fanout in the common-frame scalar projection, and [#2048](https://github.com/CrocSwap/integer-mult-bounds/pull/2048) kills only an 8-row linear transcript for two specific centre cuts. [#2044](https://github.com/CrocSwap/integer-mult-bounds/pull/2044)'s conditional κ = 0.0016797549561255 (+0.424% over the selected κ) is *not* the baseline: it is unreviewed and conditional on inherited hypotheses plus three new outer constructions its own README flags as requiring independent review. The selected record remains the baseline for all budget arithmetic.**

### Why round 1 saw +6.0% and #2052 prices −1.40% (the hypothesis difference, stated exactly)

Both computations hold a per-call word fixed and vary only the template. They differ in three hypotheses, each favourable to round 1:

| Hypothesis | Round 1 (`screen.py`, `M = 73` at line 31; `cap(WORD, fam, st, 64, 1)`) | #2052 (`price_families.py` / `FAMILIES.json`) |
|---|---|---|
| Window dimension `m` | Frozen at 73 for every K; idle cap `R = 51` frozen with it | `m = 1 + 8s` (73 at s=9, **89 at s=11**); `R` follows the halving guard |
| Per-call charge | Selected **PR1094** word `{1:2412, 2:418, 3:432, 4:142, 5:82, 8:8}`, centre 64/call, bridge/terminal overhead uncharged (priced separately in S3) | **T74** (PR #1800) words; each pair-call pays centre path + ≈3,736 hosted-helper width + 1,792 active climbs; coverage `D = W − cst·N` |
| What grows with K | Only `w = families/stages` (99.556 → 101.818), diluting the fixed 64/call centre | `N`, `m`, helper demand and window all grow; chain-seed waste `2K/(s−1)` charged |

Under round 1's hypotheses the K=5 bracket `[0.001792288627, 0.001792288628]` (×1.060) and the 182.0/182.1 break-even bracket are correct arithmetic — for a template that does not exist. Theorem S plus the `m = 1 + 8s` window accounting is what removes it. This is a changed-hypothesis finding, not an arithmetic correction to round 1, whose README already labelled the survival "conditional on per-call invariance" with the hosting lemma unproved.

### Exact hypothesis boundary

**Excluded (no κ gain available) inside ALL of:**
1. shear-type local words (stage `[[I, H], [E, I]]` up to arbitrary block-diagonal bridges; any pairs per stage, mixed orientation, non-pair-aligned calls, any pair-level signed ρ) — Theorem S: `N ≥ 2K + ⌈2K/(s−1)⌉`, hence per port `D/W ≤ 1 − (cst/v)·s/(s−1)`, dominated port-for-port by the B-template at the same `s`;
2. full per-pair-call profile (each pair-call pays its own eight rank-8 centre copies, `cst = 64`, by the star floor on 16 independent decoder totals, #2052 §1; fusing two pairs on shared labels is a degenerate-label unit dominated by its quotient, format-limits Lemma Q);
3. the two-bank coverage law `(m − 1)W + cst·N` (exactly one unpaid coordinate per family);
4. shared stage window, `m = 1 + 8s`.

Inside (1)–(4): B₅/s=11, B₆/s=13, B₇/s=15 lose 1.40% / 3.71% / 6.46% of the T74 endpoint `b`; s=7 hits the hosting wall (helpers 26,156 > idle 25,088); parallel/mixed variants at s=9 reproduce `b` exactly (F05) or lose (F06, −4.15%). The only in-scope residual is **even s=8 attainment**, capped at +0.26% (idle ≤ 40) / +0.70% (packing-ceiling relaxation, R=45) on the T74 words *if* Theorem S were attained there — and attainment already fails at the smallest even case (K=3, s=4), verified exhaustively over all 2,051 stage shapes. One extra pair-call per 35 pairs costs ≈3.4%, so s=8 needs exact attainment to pay anything.

**Not excluded — a K/template or centre construction must break at least one of (1)–(4) and name which:**
- **(3′) ρ through a third bank class / ≥2 unpaid coordinates per family.** #2052 §5 lists this as uncovered and points to the `levers.py` ×3.77 budget. This is the round-1 unpaid lever unchanged.
- **(2′) a centre path cheaper than the full per-call profile** — i.e. genuine cross-call centre sharing on *related* data (the #1708/#1748/#1791/#1829/#1838 line). #2052 §1 blocks only same-stage pairs on *independent* data. Within this opening, two sub-routes are now dead and must not be repeated: zero-storage early fanout before the forward scalar prefix (#2076: endpoints differ in 34–56 of 704 roles per centre output, exact rational replay, witness `normal − early = 1/4` at role 114, channel 0 — scalar-projection scope only), and an 8×512-row linear transcript reconstructing both time-0/time-1 centre scatters with no other source-dependent input (#2048: joint native rank 8,192 = 16×512, `det P = 32`, `det BP = −1/512` — linear-interface scope only; extra reads, larger rows, reusable storage, altered obligations explicitly not excluded). Surviving sub-route: a specified call pair with persistent centre bank / phase reordering, fully invoiced below the 32/call ideal saving (#2076's open question) — no such pair has passed endpoint + budget screens.
- **(1′) a non-shear local word.** Outside Theorem S by statement; no candidate word exists in either round.
- **(4′) even-s=8 exact attainment.** First open instance K=4, s=4 (bound 11, chains 12). Bounded upside (+0.70% on T74 words) makes this a bounded side-question, not a lever.

### #2044 relevance to the baseline

#2044 (`research/capped-fusion-t74-k554/`) claims a **conditional** final κ = 0.001679754956125544… by running PR1673's capped phase-cell fusion outer on the T74 pivot-566+554 supplier, whose certified complex endpoint is the same number `b`. Three reasons it does not move the baseline used here: (i) it is unreviewed — upstream `main` and the selected record are unchanged, and repository rules admit κ only through the exact moment acceptance test on a completed, reviewed construction; (ii) its own README states the package is "[c]onditional on all inherited hypotheses", that the radix-distributed union schedule, structured boundary solves and gauge-free interiors "require independent review", that the structured-boundary precision section "is an error argument … not a verified stability theorem", and that "the real-regime check at large p has not been run"; (iii) its margins are asymptotic with exponent margin 2e-30010 and "no practical cutoff is claimed". It is relevant only as the current top *open* claim (+0.424% over selected κ) and as #2052's pricing substrate: if #2044 (or its T74 supplier lineage) were admitted, the complex endpoint would move from the selected value to `b`, round-1's joint (S5) budgets would need re-issuing against `b`, and the K=5 question would already be answered negatively on those words by #2052's F02. Until admission, all budgets in both rounds correctly use the selected record.

### Disposition of the round-1 levers after #2028–#2178

| Lever (round 1) | Status after new PRs | Changed hypothesis required to reopen |
|---|---|---|
| K=5 template (182.0 budget) | **Falsified as a gain route** inside (1)–(4) above; budget question moot — there is no positive margin for bridge/terminal mass to fit into | Break (1), (2), (3) or attain s=8 exactly |
| Unpaid ≥2 (×3.77; unpaid-3 budget 481.4) | **Survives, untouched** — explicitly uncovered by #2052; #2076/#2048 silent on coverage | Already the changed hypothesis (third bank class); needs progress-preserving endpoint contract |
| Centre sharing (×1.90 ideal, κ-capped +3.45%) | **Narrowed**: early-fanout (#2076) and 8-row transcript (#2048) sub-routes closed with named scopes | Persistent bank / phase reorder with full invoice < 32/call |
| Halving depth HD>2 | Unchanged: falsified standalone in round 1 (S4); #2052's s≥10 window growth points the same way | New outer row bound (unchanged) |

**Cheapest decisive test run in this package (after this verdict was drafted):** re-price the *selected PR1094 word* — not the T74 words — at K=5 with the legal window `m = 89` (`R = 62`) under the pinned ceiling engine, and compare against the bit endpoint and against the same word at K=4/`m = 73`. This isolates the single changed hypothesis (`m`) on round 1's own word: if the K=5 bracket falls to/below the K=4 ceiling, the 182.0 budget is confirmed moot on the selected word itself, without relying on #2052's different word. See `reprice.py` / `RESULT.json`. The pivot target is the unpaid-coordinate contract; its cheapest decisive test is specified in *Next experiment* rather than run here, because it requires a three-bank endpoint contract that does not yet exist in any read package — inventing one inside this session would price a guessed object.

## Task card

```text
Task ID / proposed scope key: coverage-law-change (K=5 template falsification
  + unpaid pivot handoff); continuation of research/muse-ood-coverage-template.
Base commit: 0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2 (canonical main,
  priority revision 4, unchanged 2026-10-14T22:17Z).
New evidence read at head: #2052 79cb4818 (Theorem S + T74 pricing),
  #2076 centre-prefix-fanout-obstruction-seed2803b7, #2048
  selected-centre-native-lift, #2044 capped-fusion-t74-k554 (README,
  CLAIM.json, PRICE.json). Open PRs now run to #2178 (titles file).
Concrete object: selected complex per-call word {1:2412,2:418,3:432,4:142,
  5:82,8:8} at (K=4, s=9, m=73) vs (K=5, s=11, m=89), centre 64, unpaid 1.
Changed hypothesis under test: m frozen at 73 (round 1) -> m = 1+8s (#2052).
Method: pinned exact intervals (ceiling.py, sha256 in RESULT.json), grid 10^-12.
Declared targets: bit endpoint a_b = 0.00173342703959; K=4 base ceiling.
Falsification test (cheapest first): single exact bracket at (1120 fam,
  11 stages, m=89) vs bit endpoint and vs base bracket.
Intended artifact: this directory (reprice.py, verify.py, RESULT.json).
Anti-basin: no packing/hosting/owner repacking; no covered obstruction
  reopened without its changed hypothesis named (boundary list above).
```

## Exact result (`RESULT.json` is authoritative)

Pinned-engine brackets (grid 10⁻¹²) for the selected PR1094 word, centre 64, unpaid 1. Only `m` (and its guard `R`) changes between the two K=5 rows:

| Point | m | R | a bracket | a_hi | ×base | vs bit endpoint |
|---|---|---|---|---|---|---|
| K=4, s=9 (base) | 73 | 51 | [1690054109/10¹², 169005411/10¹¹] | 0.001690054110 | 1.000 | below |
| K=5, s=11, **frozen window** (round 1) | 73 | 51 | [1792288627/10¹², 448072157/25·10¹⁰] | 0.001792288628 | 1.060 | above |
| K=5, s=11, **legal window** m=1+8s | 89 | 62 | [1658434103/10¹², 207304263/125·10⁹] | 0.001658434104 | **0.981 (−1.87%)** | below |
| K=6, s=13, legal window | 105 | 74 | [6478121/4·10⁹, 1619530251/10¹²] | 0.001619530251 | 0.958 (−4.17%) | below |

The legal-window K=5 ceiling falls *below* the K=4 base ceiling, so the round-1 question "does bridge/terminal mass fit in 182.0/call?" has no positive margin to fit into — the budget is moot, on round 1's own word, without relying on #2052's T74 words. The sign and rough magnitude agree with #2052's independent T74 pricing (B₅ −1.40%, B₆ −3.71%), which additionally charges hosted-helper width and active climbs per pair-call; the present relaxation charges neither, so it remains favourable to the lever and still falsifies it. Note idle mass *grows* at m=89 (3438 vs 1646/call) yet the ceiling falls: the loss is the window/child-cost term `(r/m)^(1−a)`, not mass shortage — consistent with #2052's "window growth at s ≥ 10" diagnosis.

## Overlap check

- Round-1 limitation ("open PRs #2028–#2101 unread") is now partially discharged: heads #2044, #2048, #2052, #2076 read in full from local refs `refs/upr/<N>`; titles for #2028–#2178 scanned from the provided titles file. PRs other than the four named were title-scanned only; unmerged overlap beyond them remains possible and must be rechecked before any submission.
- Nearest neighbours, cited not repeated: Theorem S and families F00–F13 (#2052); early-fanout obstruction (#2076, base `e112d71c…`); native centre-cut rank 8,192 (#2048, building on PR1918's scalar minor and `Stream.conj_matrix`); conditional T74 κ (#2044, on PR1673/PR1661/PR1625 lineage). This package's only new computation is the selected-word `m = 89` re-price isolating the changed hypothesis; no local or read package was found that prices the *selected* word at the legal K=5 window.
- Covered cases not reopened: fixed-word frames (#1995/#2013), additive `C=40` model (#2017), GL3 census (#1974), eight-term bound, frozen catalogue, fixed connector alphabet, three-register bound — plus, newly: same-stage centre fusion on independent data (#2052 §1), early fanout (#2076), 8-row transcript (#2048), each cited only with its hypothesis named.

## Tests run (exact commands and outcomes)

```sh
git show refs/upr/2052:research/multipair-schedule-bound/README.md   # Theorem S, F-table
git show refs/upr/2076:research/centre-prefix-fanout-obstruction-seed2803b7/README.md
git show refs/upr/2048:research/selected-centre-native-lift/README.md
git show refs/upr/2044:research/capped-fusion-t74-k554/README.md     # + CLAIM.json, PRICE.json
python3 -B research/muse-ood-template-k5/reprice.py   # writes RESULT.json
python3 -B research/muse-ood-template-k5/verify.py
python3 -I -O -B research/muse-ood-template-k5/verify.py
```

Not run (explicitly): #2052's `verify.py` (≈30 s) and its exhaustive searches (6 min – 1 h) — F-table values are cited as unreviewed-PR evidence, and this package's verdict does not depend on their replay because the selected-word re-price below decides the same question independently; #2044's full admission replay (no baseline change to admit); `make frontier1094-verify` (no supplier change); any Lean/formal check.

## Open proof obligations

Nothing here is admitted. For the surviving unpaid lever: (1) a three-bank-class ρ (cycle X→Y→Z or equivalent) with a progress-preserving endpoint contract — a coordinate counted unpaid while unadvanced is out of scope; (2) the advancement word's actual rank histogram against round-1 S3 budgets (unpaid-3 at 1/99: ≤481.4 rank-1-shaped / ≤1032.7 rank-8-shaped mass/call for both extra advancements together); (3) dirty restoration and chronological hosting at the new coverage law; (4) a bit-side co-improvement (round-1 S5: κ×1.10 needs bit ×1.063) — every complex-only gain remains κ-capped at ×1.0345 with the bit endpoint fixed. For the narrowed centre lever: one specified call pair, saved components, owner windows, and complete copy/restoration/frame/precision/hosting invoice below 32/call, avoiding both dead sub-routes above. For s=8: attainment at K=4, s=4 or a proof even s never beats s−1 (upside ≤ +0.70% on T74 words). Inherited all-size/compiler, common-label, whole-call hosting, precision/tape and analytic obligations are untouched throughout.

## Next experiment (single, bounded)

**Three-bank unpaid-2 endpoint contract — existence screen (≈1 session).** Take the smallest shear-type fragment (one pair, v ports) and ask whether a signed exchange routed through a third bank class Z can terminate with two coordinates per family advanced-but-unpaid while preserving the endpoint identity `M_out(ρ(w)) − M_in(w) = I_m` and dirty-helper restoration. First step: write the pair-level goal for X→Y→Z in the #2052 row-space model (P, Q, plus a third subspace R with its own σ-accounting) and derive the analogue of `N = 2K + W`: either the waste identity forces the second "unpaid" coordinate to be paid elsewhere (falsification — record the exact step where σ leaks), or it exhibits the slack term a real contract must realise, priced against the unpaid-2 budget (round-1 S3: reaching a=0.005 at centre 64 allows ≤1481.1 rank-1-shaped mass/call). Success: a named slack term + budget comparison. Stop/falsify: the identity closes with no slack — then unpaid≥2 joins the excluded list under shear-type words and only (1′) non-shear words remain. Do not attempt K≥5 schedules, s=8 search, or centre-bank engineering until this screen exists; it is the cheapest test that can kill the largest surviving ceiling (×3.77).

## Reproduce

```sh
python3 -B research/muse-ood-template-k5/reprice.py   # regenerates RESULT.json
python3 -B research/muse-ood-template-k5/verify.py    # PASS_MUSE_OOD_TEMPLATE_K5_VERIFY
```

Python 3.10+ (run here on 3.13.16), standard library only, no network/Git needed at replay (engine and selected record hash-pinned in `RESULT.json`).

## Credit and disclosure

Predecessor credit is retained and not claimed as new: themilkman216 (with Claude) for Theorem S, its attainment/searches and T74 pricing ([#2052](https://github.com/CrocSwap/integer-mult-bounds/pull/2052)), generalising `cross-shear-stage-bound` and using `format-limits-corrected` (Sch)/(Dfc)/Lemma Q; Cinna Davis (with Codex) for the centre-prefix fanout obstruction ([#2076](https://github.com/CrocSwap/integer-mult-bounds/pull/2076)); the selected-centre native-lift authors ([#2048](https://github.com/CrocSwap/integer-mult-bounds/pull/2048)), building on Adam Gall's PR1918 scalar minor, Sagar Thakrar's exact Clifford kernel and `Stream.conj_matrix`; jeremykothe2 and the full credited lineage inside [#2044](https://github.com/CrocSwap/integer-mult-bounds/pull/2044) (PR1673 Vlado Vojdanovski capped phase-cell fusion; T74 supplier PR1625/PR1661/PR1319/PR1297 and others; PR1786 Chafik Boukhalfa fine prime padding after Tim Trudgian); Douglas Colkitt (with Claude) for the [#1240](https://github.com/CrocSwap/integer-mult-bounds/pull/1240) ceiling/levers engine reused here; PR1012 coverage identity (Sagar Thakrar lineage). Selected-construction credit remains in its review.

This package was prepared with substantial AI assistance from Meta Muse (Muse Code, `muse-wonder-full-1.0`): hypothesis-boundary analysis, re-price/verify code and draft text. Exact arithmetic is standard-library `Fraction` via the pinned predecessor engine; cited #2052/#2044 values were read, not independently replayed (stated above); no independent human review, proof-assistant verification or literature-priority guarantee is claimed. Apache-2.0, following the repository license.

## Addendum (excluded-branch completion): unpaid-coordinate decisive test

With K=5 excluded above, the strongest surviving lever — unpaid ≥2, explicitly uncovered by #2052 — was given its cheapest decisive test (`unpaid.py` → `UNPAID.json`, full discussion in `UNPAID.md`). Headlines at target `a = 1/99`, base legal template, selected word fixed: unpaid=2 fails at every centre by certified exact intervals (centre 64: `relax_lo = 1.01105474131`; centre-free: `1.00221651998`); a partner rank-shape lever would have to delete 1975.9 rank-1 children/call at full centre (81.9% of stock) or 396.2 centre-free (16.4%) — sharp 0.1-grid brackets [1975.8/1975.9], [396.1/396.2]; unpaid=3 passes (centre 64: `relax_hi = 0.99730639702`) and its round-1 advancement budget is re-confirmed (+481.4 rank-1 mass/call passes, `relax_hi = 0.999999808296`; +481.5 fails, `relax_lo = 1.00000036779`). Conclusion: the minimal sufficient coverage change on this shape is unpaid-3, or unpaid-2 plus two stacked partner levers; whether any three-bank endpoint contract realises unpaid ≥2 remains the open gate (README *Next experiment*). #2044 relevance is unchanged (see *#2044 relevance to the baseline* and `UNPAID.md`): conditional, unreviewed, not the baseline.
