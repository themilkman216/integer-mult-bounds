# Coverage/template frontier: exact budgets for unpaid coordinates, wider templates and halving depth

**Scoped screening and handoff. No construction, no new supplier, no new κ.**
The selected record (κ = 836330098538459/500000000000000000, [#1094](https://github.com/CrocSwap/integer-mult-bounds/pull/1094)) is unchanged. Every number below is a favorable relaxation under explicitly stated hypotheses; the exact moment of a completed construction remains the acceptance test.

Out-of-distribution session (Meta Muse, `muse-wonder-full-1.0`; see *Credit and disclosure*). Local-only package for maintainer review: nothing was committed, pushed or posted.

## Task card

```text
Task ID / proposed scope key: coverage-law-change (primary) + centre-path-sharing
  interaction; chooser track complex-mechanisms, nonce 6bd5a71a274b565575f12386dcefca6f
  (scope_keys: complex-rank-shape-decoder 02b31ebd160542c86299,
   complex-new-helper-inventory f3b0895a4f9f1cc62e75, p104-side-correction
   c5367b1a1b7bed20db53). Scope status: refined across cards by donor assignment
  (compare structural levers, then falsify one); reason recorded in Candidates.
Base commit: 0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2 (= canonical main at
  2026-10-14T19:29:21Z, priority revision 4). Predecessors: #1240 ceiling engine
  (1e136b8c4a552050820334ad113628775182f08c), #1264 census
  (1be64e9ef79fe11f24f05b62b0fd7d70be0b7b4c); reviewed heads in OVERLAP.json.
Concrete object: selected complex per-call word {1:2412,2:418,3:432,4:142,5:82,8:8},
  m=73, under parameterized (families, stages, centre, unpaid, idle cap R).
Changed hypotheses (one family at a time, each labelled): nine-stage 4-pair
  template -> (2K+1)-stage K-pair templates; coverage unpaid 1 -> 2,3;
  halving depth HD=2 (R=51) -> HD>2. Packing of the fixed word is NOT revisited.
Method: pinned exact intervals (ceiling.py, sha256 in RESULT.json), grid 10^-12;
  break-even added-mass brackets on a 0.1-mass grid with certified opposite signs.
Declared targets: bit endpoint a_b, +5% complex ceiling, a=0.003, a=0.005, a=1/99.
Success evidence: certified brackets/signs deciding each sub-lever at its target.
Falsification test (run first, before any construction): S4 sign at +5% for R
  lever; S1/S2 ceilings vs bit endpoint; S3 zero-added-mass signs at 1/99.
Intended artifact: this directory (screen.py, verify.py, RESULT.json, OVERLAP.json).
```

## Headline findings

1. **Every complex-only lever saturates at κ ×1.0345.** With the bit endpoint fixed (`a_b = 0.00173342703959`), the planning transfer caps κ at `0.00173042746982` (+3.4536%), however large the complex ceiling. Lever multipliers in `levers.py` are complex-`a` multipliers, not κ multipliers. Joint targets need both sides: κ×1.10 needs complex ×1.100 and bit ×1.063; κ=0.01 needs ×6.029 and ×5.827 (`RESULT.json` S5, planning transfer; seven-step slacks neglected).
2. **Halving-depth (idle-cap) relaxation is falsified as a standalone +5% route.** At +5% over the base ceiling, the relaxation is certified above 1 even at `R=72` (interval lower end `1.00010677158`), beyond every halving depth. Roots: `R=57` (HD3) `a<0.001704851517` (×1.009, still below the bit endpoint), `R=72` `a<0.001736778937` (×1.028). A new outer row bound alone cannot deliver the rank-shape card's 5% gate (S4).
3. **Template widening survives the relaxation screen but is κ-capped and hosting-unproved.** Holding the per-call word and centre fixed, `K=5` (11 stages, `w=1120/11`) is the first swept template whose whole bracket exceeds the bit endpoint: `a ∈ [1792288627/1000000000000, 448072157/250000000000]`, i.e. `a_hi = 0.001792288628` (×1.060). `K=64` reaches ×1.306 complex, still κ×1.0345 bit-fixed. The survival is conditional on per-call invariance; the next section prices what template overhead may cost (S1, S3).
4. **Unpaid coordinates are the largest lever and still need help for 1/99.** Shape-fixed ceilings: unpaid 2 ×3.774 (`0.006377984109`), unpaid 2 + centre-free ×5.568 (`0.009409963999 < 1/99`, zero-added-mass failure certified), unpaid 3 ×6.510 (`0.011001994531 > 1/99`). Reaching `a=1/99` on this shape therefore needs unpaid ≥3, or unpaid 2 plus a rank-shape improvement (cf. the in-window alternative in `research/bit-revision3-levers-seed03`), or centre-free plus beyond-window rank-16 children (joint screen). No pair (unpaid≤2, any centre, fixed shape) suffices (S2, S3).

## Candidates considered (≥5 scopes, 4 tracks) and disposition

Ideal ceilings use `ceiling.ceiling()`/`levers.py` where their hypotheses apply; κ readings always apply the bit-fixed cap of finding 1. “Cheapest test” is the first test that can kill the scope.

| # | Scope (track / card) | Hypothesis changed | Ideal ceiling | Cheapest falsification | Disposition |
|---|---|---|---|---|---|
| A | P104 `I-G/2` completion at an interleaved cut (complex / `p104-side-correction`) | Selected direct word → native `G/2` channel ([#1991](https://github.com/CrocSwap/integer-mult-bounds/pull/1991), channel from [#1972](https://github.com/CrocSwap/integer-mult-bounds/pull/1972) `fd82d172…`) + side word sharing frames | No completed ceiling from local pins (global embedding + correction registers not on main). Proxies only: predecessor R-free format ceilings P104 `0.004412` vs P112 `0.003995` (fixture §5, different model); selected-shape (V104, cst56) proxy `0.001864970767` ×1.103 (S1, **not** the P104 word) | Optimistic completed moment (correction boundary free) vs declared target; then frame-availability at cut | **Deferred, not rejected.** Highest construction specificity, but the correction's global spec lives in open [#1972](https://github.com/CrocSwap/integer-mult-bounds/pull/1972), unreadable here beyond the vendored channel witness (280 registers, 4058 events, profile `{1:1074,2:58,3:86,4:104,5:48,6:24,7:8,8:8}`, mass 2368 = 2312 + COPY56). Guessing its registers would solve the wrong problem. Next step in *Open next questions*. |
| B | QQ16 + one priced ordinary→selected observation (recursive / `joint-query-controller`) | Fixed F0/B1 observation set + homogeneous selected-only control (blocked by witness) → retain one 8-coordinate ordinary query (witness identifies `B2h`, coeff. 2112) | Centre-free proxy ×2.80 (`0.00473765347`) before observation/cover costs; local overheads small (+24/+8 rank-1; mass 5546/5530 vs core 5522) | Kernel after augmentation: second lost vector in `ker B1 ∩ ker B2`; price 528/288 cover maps physically | **Deferred.** One observation defeats the displayed witness `h` by construction (`X_T` is a linear image of `B2h`); general invertibility needs the cover-algebra kernel, whose checker is archived outside the repo and whose cover-map tariff is unpriced. Needs predecessor artifacts, not another seed. |
| C | **Coverage/template scaling (recursive / `coverage-law-change` + `centre-path-sharing`) — CHOSEN** | Template (K=4, 9 stages), unpaid=1, HD=2 → parameterized family above | Unpaid2 ×3.77; template `K→∞` ~×1.31; unpaid2+centre-free ×5.57 (all κ-capped alone) | Exact signs/brackets at declared targets (this package S1–S4) | **Chosen and executed.** Largest ceiling with a same-session decisive exact test and no missing spec. Results below. |
| D | Masked decoder with subadditive shared climbs (complex / `complex-rank-shape-decoder`) | Eight-term all-pairs + additive per-term charge → masked exactness + shared physical climbs (outside [#2017](https://github.com/CrocSwap/integer-mult-bounds/pull/2017) additive scope; nonlinear/shared pricing explicitly excluded there) | Rank-16 proxy ×2.31 (`0.003909`); in-window rank-9 strictly less | Excess accounting at 1/99: spend 2.59681 vs budget 0.12753 (20.4×); deleting all rank-1 still 9.8× over — sharing must discount ~95% of excess, not just copy terms; plus masked local rigidity near `2G` | **Rejected as primary.** No concrete support alphabet survives the excess arithmetic without also changing coverage/centre; it is a necessary partner lever (finding 4), not a standalone first construction. Reopen with one explicit support family + meet-dimension check. |
| E | Bit helper/register unlock (bit / `bit-helper-contract`, `bit-new-register-model`) | H2/K interface; three-register abelian model → replacement lemma, 4-register or nonabelian alphabet (cf. [#2027](https://github.com/CrocSwap/integer-mult-bounds/pull/2027) UT4 tariff, formal only) | Immediate κ ×1.00 (complex binds); joint value: κ×1.10 needs bit ×1.063 (S5). Bit packing ceiling `0.0019559`, centre-free ×2.77 (bit levers package) | Format-limits cap `X(9)=0.004607` under (Sch)+slot domination: name the axiom broken and price native conversion; helper-star alone keeps paid profile (moment gain 0) | **Rejected as standalone κ raiser; required as partner.** Any complex win beyond +3.45% κ is wasted until this moves. Pair future complex work with a bit budget from S5. |
| F | Halving-depth / outer-recipe `R` relaxation (new mechanism outside incumbent calculator) | Outer guard `2R²<m²` → `2R^HD<m^HD`, HD>2, via improved row bound | `R=72` root ×1.028 (own replacement relaxation, S4) | Single certified sign at +5% (run) | **Falsified standalone** for +5% (finding 2). Retain only as feasibility slack for helper-count thresholds at 1/99 (bit HD4 effect), not as a κ lever. |

Set aside without full scoring: `selected-stock-envelope` ([#1956](https://github.com/CrocSwap/integer-mult-bounds/pull/1956)/[#1965](https://github.com/CrocSwap/integer-mult-bounds/pull/1965)/[#1990](https://github.com/CrocSwap/integer-mult-bounds/pull/1990)) raises confidence, ceiling κ×1.00 by definition — but note template widening (C) *worsens* its stock obligation (larger replica), recorded below. `connector-alphabet-change`: the 5-source optimum gap is 74 vs 72 queries (2.7% on that sub-batch before pricing the new operation, then diluted globally) — ceiling too small for the donor's “largest surviving ceiling” rule. Covered cases were not reopened: [#1995](https://github.com/CrocSwap/integer-mult-bounds/pull/1995)/[#2013](https://github.com/CrocSwap/integer-mult-bounds/pull/2013) fixed-word frames, [#2017](https://github.com/CrocSwap/integer-mult-bounds/pull/2017) `C=40` additive model, [#1974](https://github.com/CrocSwap/integer-mult-bounds/pull/1974) GL3 census, eight-term bound, frozen catalogue, fixed connector alphabet, three-register bound — each is cited above only with its hypothesis named.

## Exact results (chosen scope; `RESULT.json` is authoritative)

Base reproduction (grid 10⁻¹²): `a ∈ [1690054109/1000000000000, 169005411/100000000000]`, `a_hi = 0.00169005411`, matching [#1240](https://github.com/CrocSwap/integer-mult-bounds/pull/1240) to grid; selected endpoint below bracket; one extra rank-1 child lowers `a_hi` to `0.001689738048`.

Template sweep, centre fixed (S1; `w` = live families per call):

| K (stages) | w | a_hi | ×base | vs bit endpoint |
|---|---|---|---|---|
| 2 (5) | 89.6 | 0.001232938806 | 0.730 | below |
| 4 (9, selected) | 99.556 | 0.00169005411 | 1.000 | below |
| 5 (11) | 101.818 | 0.001792288628 | 1.060 | **bracket above** |
| 6 (13) | 103.385 | 0.00186271402 | 1.102 | above |
| 8 (17) | 105.412 | 0.001953428245 | 1.156 | above |
| 16 (33) | 108.606 | 0.002095408888 | 1.240 | above |
| 64 (129) | 111.132 | 0.002206847268 | 1.306 | above |

Port sweep at K=4: with centre *scaled* proportionally the ceiling is exactly invariant (×1.000 at V=96…120 — widening alone is not a lever); with centre fixed, V=120 ×1.120, V=104 ×0.861. The selected-shape (V104, cst56 as 8×rank-7) proxy gives `a_hi = 1864970767/1000000000000 = 0.001864970767` (×1.103): in shape-proxy arithmetic the cst saving outweighs the smaller `w`. This does **not** screen the P104 word.

Break-even overhead budgets (S3; added rank mass per call, 0.1-grid sharp brackets; full table in JSON). Reading: overhead billed in the stated shape must stay at/below `L_pass`; `L_fail` is certified over.

| Context → target | rank-1 shape | rank-8 shape | rank-51 shape |
|---|---|---|---|
| K=5 template → bit endpoint | **182.0 / 182.1** | **387.1 / 387.2** | coverage-bound (1808.9) |
| K=5 template → +5% ceiling | **53.5 / 53.6** | **113.9 / 114.0** | coverage-bound |
| K=6 template → bit endpoint | 400.7 / 400.8 | 852.1 / 852.2 | coverage-bound (1921.6) |
| Centre 32 (base template) → a=0.003 | 379.0 / 379.1 | 807.1 / 807.2 | coverage-bound (1646) |
| Unpaid 2, centre 64 → a=0.005 | 1481.1 / 1481.2 | coverage-bound (1546.4) | coverage-bound |
| Unpaid 3, centre 64 → a=1/99 | **481.4 / 481.5** | **1032.7 / 1032.8** | coverage-bound (1446.8) |
| Unpaid ≤2 (any centre incl. 0) → a=1/99 | fails at 0 | fails at 0 | fails at 0 |

Scale for the K=5 rows: local mass is 5586/call, so retaining the bit-endpoint reach allows template overhead up to ~3.3% of local mass if billed at rank 1, ~6.9% at rank 8. Whether bridges/terminals fit is the decisive unrun measurement (next experiment). For unpaid 3 at 1/99, both extra advancements together may cost ≤481.4 rank-1-shaped mass/call (≈4.8 per live family); a fresh rank-7/8 data climb per port per coordinate would exceed this if billed at small-rank shape, so a viable advancement must reuse climbs or bill at large rank — stated as a conditional budget, not an impossibility proof.

## Overlap check (summary; full receipt in OVERLAP.json)

- Task picker: `python3 scripts/choose_research_task.py` → nonce `6bd5a71a274b565575f12386dcefca6f`, track `complex-mechanisms` (cards/scope_keys in task card). Donor assignment then required cross-track comparison; the nonce does not reserve work.
- Refresh attempted 2026-10-14T19:28:14Z: `gh` Bad credentials (HTTP 401), no remote snapshot; `web_fetch` 403; REST API 403 rate-limit. **Limitation: open PRs #2028–#2101 and live discussions are unread.** Canonical main fetch succeeded and equals the checkout (19:29:21Z), so merged guidance/selected record are current; unmerged overlap remains possible and must be rechecked before submission.
- Offline fallback (1536 local records each; PR/discussion coverage `null`): `p104-side-correction` 65 matches, `joint-query-controller` 1080, `coverage-law-change` 124, `centre-path-sharing` 277, `complex-rank-shape-decoder` 222, `bit-new-register-model` 140, `connector-alphabet-change` 57, `selected-stock-envelope` 74 (timestamps in OVERLAP.json). Nearest retained neighbours read in full: [#1240](https://github.com/CrocSwap/integer-mult-bounds/pull/1240)/[#1264](https://github.com/CrocSwap/integer-mult-bounds/pull/1264) via priority log + packages, centre overhead budgets (actual-histogram sharp budgets; ours are relaxation/template budgets — complementary, cited not repeated), joint rank×centre screen at 1/99 (fixed `w`/unpaid/R; ours varies those + bit-cap translation), bit levers (bit word/helper counts; ours complex template/coverage), [#1969](https://github.com/CrocSwap/integer-mult-bounds/pull/1969) `a6e6ad39…`, [#1991](https://github.com/CrocSwap/integer-mult-bounds/pull/1991) `6e222517…`, [#1956](https://github.com/CrocSwap/integer-mult-bounds/pull/1956) `f8003953…`, [#1965](https://github.com/CrocSwap/integer-mult-bounds/pull/1965) `c9819a94…`, [#1990](https://github.com/CrocSwap/integer-mult-bounds/pull/1990) `c3bd90d9…`. No local package was found that varies K/stages or prices unpaid-advancement break-evens; absence in offline search is not novelty.

## Tests run (exact commands and outcomes)

```sh
python3 scripts/choose_research_task.py
# seed 6bd5a71a274b565575f12386dcefca6f, track complex-mechanisms, priority_revision 4
python3 -B scripts/research_baseline.py
# PASS_RESEARCH_BASELINE_BINDINGS_ONLY (complex binds; target multipliers 6.029/5.827)
python3 -B research/complex-local-word-ceiling/verify.py
# PASS_COMPLEX_LOCAL_WORD_CEILING a_ceiling 0.00169005410908900006
python3 -B research/complex-local-word-ceiling/levers.py
# centre-free x2.80, shared x1.90, rank16 x2.31, unpaid2 x3.77, combined x6.51
python3 scripts/find_overlap.py --task p104-side-correction --refresh --json
# refresh FAILED (gh 401, no snapshot) -> offline searches, see OVERLAP.json
git fetch --no-tags https://github.com/CrocSwap/integer-mult-bounds.git main
# FETCH_HEAD == HEAD == 0fdd7d82..., priority_revision 4, selected kappa unchanged
python3 -B research/muse-ood-coverage-template/screen.py
# PASS_MUSE_OOD_COVERAGE_TEMPLATE_SCREEN (writes RESULT.json)
python3 -B research/muse-ood-coverage-template/verify.py
python3 -I -O -B research/muse-ood-coverage-template/verify.py
# PASS_..._VERIFY both modes (7 check groups incl. tamper comparison)
```

Not run (explicitly): `make frontier1094-verify` cold replay (no supplier change to admit); P104 native replay and QQ16 portable replay (predecessor evidence read, not re-executed; neither is relied on for a new claim); any Lean/formal check; live PR/discussion recheck (unavailable, above). Float prototypes used during exploration were discarded; all reported values come from the exact scripts.

## Open proof obligations (conditional — nothing here is admitted)

For the template direction to become a supplier, all of the following remain, in dependency order: (1) an 11-stage/5-pair (or general-K) schedule with window/hosting lemma — the retained hosting proof is for the inherited nine-stage templates; per-call word invariance across K is assumed, not proved; (2) bridge, terminal-exchange and cover-correction rank accounting as a function of K, compared against the K=5 budgets (182.0 rank-1-shaped mass/call to the bit endpoint); (3) stock/cutoff growth with replica size — larger live stock per level interacts with the still-unknown selected reserve coefficient (`selected-stock-envelope`); do not import historical constants; (4) scalar invoice / row-coefficient growth and precision prefixes at the larger template; (5) a bit-side co-improvement (κ×1.10 needs bit ×1.063) with its own interface proof. For unpaid≥2: a progress-preserving endpoint contract (a coordinate counted unpaid while unadvanced is explicitly out of scope), the advancement word's actual rank shape vs the S3 budgets, dirty restoration and chronological hosting. For HD>2: a new outer row bound admitting the depth at the actual invoice size. Inherited all-size/compiler, common-label, whole-call hosting, precision/tape and analytic obligations are untouched throughout.

## Next experiment (single, bounded)

Instantiate the K=5 template combinatorics and measure its true per-call overhead against the sharp budget. First step (≈1 session): locate the nine-stage template generator behind the selected owner audit, generalize only the pair/stage schedule to 5 pairs/11 stages (same local word, same V=112), emit windows + bridge/terminal events, and count their rank mass per call by shape. Success: overhead ≤182.0 (rank-1-shaped) / ≤387.1 (rank-8-shaped) mass/call with a window-feasible owner assignment sketch — then price the full histogram by exact moment. Stop/falsify: overhead exceeds the bracket, or windows force unhosted helpers whose bank cost exceeds it, or no 5-pair schedule exists under the cover constraints — record which. Do not proceed to K=6+ or to unpaid-2 synthesis until this measurement exists; larger K only helps if overhead grows sublinearly in K, which this step also estimates (two points: K=4 known, K=5 new).

## Open next questions

- **K=5 overhead measurement** (above). Why: it decides the only surviving template sub-lever at its minimal size. Blocker: template generator generalization + bridge accounting.
- **P104 correction spec recovery.** Why: candidate A may dominate template widening if its correction is cheap, but its global registers are not pinned on main. First step: obtain [#1972](https://github.com/CrocSwap/integer-mult-bounds/pull/1972) `fd82d172…` global word/template (or author confirmation of correction inputs/outputs), then replay frame trajectories from the vendored witness to lower-bound extra transports at distributed cuts (fixture precedent: staggered 47 vs single-cut 144 delivery copies, historical pricing). Blocker: open-PR access / author spec.
- **QQ16 augmented kernel.** Why: one observation killing only the displayed witness is insufficient. First step: rebuild stage operators `B_s` from the portable replay and test `ker B1 ∩ ker B2` for a second lost vector with nonzero later query. Blocker: archived witness checker + physical cover-map tariff.
- **Bit partner budget.** Why: S5 turns every complex proposal into a joint requirement. First step: pick the κ×1.10 row (bit ×1.063, ≈649 mass units on the cited bit histogram per centre-overhead package) and name one bit mechanism + escaped format-limits axiom that could supply it. Blocker: native conversion pricing for nonabelian/register candidates.

## Reproduce

```sh
python3 -B research/muse-ood-coverage-template/screen.py   # regenerates RESULT.json
python3 -B research/muse-ood-coverage-template/verify.py   # PASS_MUSE_OOD_COVERAGE_TEMPLATE_VERIFY
```

Python 3.10+ (run here on 3.13.16), standard library only, no network/Git needed at replay (engine and selected record are hash-pinned in `RESULT.json`). `verify.py` recomputes a subset (base/K5/proxy brackets, S4 signs, two S3 brackets, S5 identities) rather than trusting stored decimals.

## Credit and disclosure

Predecessor credit is retained and not claimed as new: Douglas Colkitt (with Claude) for the [#1240](https://github.com/CrocSwap/integer-mult-bounds/pull/1240) ceiling/levers and task catalogue; PR1012 coverage identity (Sagar Thakrar lineage, via retained citations); [#1264](https://github.com/CrocSwap/integer-mult-bounds/pull/1264) census; centre-sharing overhead authors (PR1708/PR1748/PR1791 lineage and mixed-rank closure); joint-lever screen (woklerx); bit levers (seed03 package) and format-limits; Rohan Arun ([#1972](https://github.com/CrocSwap/integer-mult-bounds/pull/1972)), Adam Gall, Chafik Boukhalfa ([#1991](https://github.com/CrocSwap/integer-mult-bounds/pull/1991)) for P104; Ali Romman ([#1969](https://github.com/CrocSwap/integer-mult-bounds/pull/1969)) for QQ16; Josie Elliston and ToikY for stock audits; decoder-bound authors via the scope map. Selected construction credit remains in its review.

This package was prepared with substantial AI assistance from Meta Muse (Muse Code, `muse-wonder-full-1.0`): candidate comparison, screen/verify code and draft text. Exact arithmetic is standard-library `Fraction` via the pinned predecessor engine; no independent human review, proof-assistant verification or literature-priority guarantee is claimed. Apache-2.0, following the repository license.
