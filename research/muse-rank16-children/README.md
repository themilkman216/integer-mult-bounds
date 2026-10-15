# Rank-16 local children (Track 4B): the lever is a multi-array drop lemma — every staged realization priced here fails

**Scoped falsification and precise handoff. No construction, no new supplier, no new κ.**
The selected record (κ = `836330098538459/500000000000000000`, [#1094](https://github.com/CrocSwap/integer-mult-bounds/pull/1094)) is unchanged. The beat-target is the unreviewed open leader [#2374](https://github.com/CrocSwap/integer-mult-bounds/pull/2374) at conditional κ = `0.0016971949509...` (Jeremy Kothe; owner fill on [#2322](https://github.com/CrocSwap/integer-mult-bounds/pull/2322)'s words by Vlado Vojdanovski). Every number below is either a certified exact-interval sign/bracket from the pinned ceiling engine or an exact finite census count; float `D/E` values are labelled diagnostics. The exact moment of a completed construction remains the acceptance test.

Out-of-distribution session (Meta Muse, `muse-wonder-full-1.0`; see *Credit and disclosure*). Local-only package for maintainer review: nothing was committed, pushed or posted.

## Verdict in one paragraph

**Rank-16 local children cannot be bought by staging data into a blocked call; they can only come from a new in-place multi-array supplier lemma that bills 16 arrays jointly at rank 16 — and under that (unproved) lemma the conversion needed to pass the frontier is tiny.** Single-register climbs in the selected word have rank `dim(b)−dim(a) ≤ 9` over a 1,004-frame catalogue, so rank 16 needs at least two arrays. For the diagonal/staged realization ([#1779](https://github.com/CrocSwap/integer-mult-bounds/pull/1779) identity, copies billed at frame dimension), an exact census of the pinned gauge44 programs prices staging for all 134 dependency-legal batches at mass **17,432 per call** — 10.6× the entire idle mass (1,646), hence coverage-infeasible — and even the cheapest 3/7/8/12 batches *raise* the relaxation above 1 at the frontier target. This is not an artefact of the frame-dimension tariff: in excess-price form, one zero-charge batch saves `g = 16p₁ − p₁₆` with `g/p₁ = 11.294 < 16` (certified), so **any staging costing at least one rank-1 copy per register (one-way) makes spend worse for every batch count** (net change `+p₁₆ > 0` per batch). A common-frame-pair batch child is dead separately: at most **6** identical-transition batches exist (optimistic bound), below the **7** batches/call the selected word's *actual* global moment needs. Same-register climb fusion has exactly **0** instances. What survives is precisely the width-16 analogue of the width-2 drop lemma left open by [#2203](https://github.com/CrocSwap/integer-mult-bounds/pull/2203): if a joint-rank multi-array child is ever proved with zero (or `< 0.71` rank-1 units/register) staging, then converting just **44.7 rank-1 mass/call (1.85%)** lifts the selected ceiling past the planning frontier target, **7 batches/call (112 rank-1 children, 4.64%)** passes on the actual selected global profile, and **1 batch/call** raises the frontier assembly's own moment endpoint from `0.001697194951` to `0.001700803047`. The batches exist (134/call); the lemma is the whole cost.

## Task card

```text
Task ID / scope: muse-rank16-children (Track 4B, rank-16 local children lever, 2.31x ideal)
Base: main 0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2 (priority revision 4); selected #1094.
  Frontier (unreviewed, local refs): #2374 5449da65d, #2363 d815dbe37, #2322 002304ef0.
Concrete objects: selected per-call word {1:2412,2:418,3:432,4:142,5:82,8:8} (m=73,
  896 families/9 stages, centre 64, R(73)=51, idle 1646/call) and #2322/#2374 T74
  per-call word {1:2335,2:512,3:426,4:120,5:38,8:8} (mass 5371, idle 1861/call).
Questions: (1) what interface change admits rank-16 local children? (2) fully charged
  optimistic moment bound incl. staging/frame charges, idle mass, R(m)? (3) minimal
  fraction of rank-1/2 mass converted to beat 0.0016971949509? (4) cheapest concrete
  merge tested exactly on the selected word.
Anti-basin: NO packing/hosting/owner/dispatch/borrowing work. The pinned relaxation is
  used only as a screen for CHANGED local profiles; no repacking gain is claimed.
Method: cheapest falsification first - exact-interval ceiling/moment signs and brackets
  (research/complex-local-word-ceiling/ceiling.py, sha256 in RESULT.json), excess-price
  break-evens, then exact climb/frame census of the pinned gauge44 programs reusing
  research/diagonal-batch-commutation/batch.py windows.
Targets (both readings reported): a = kappa_2374 = 0.0016971949509 (frontier assembly's
  moment-root reading; recomputed root bracket of its global profile contains it) and
  aF = kappa/(1-kappa) = 0.001700080319 (retained planning transfer), plus the selected
  bit endpoint a_b = 0.001733427040 as the kappa-relevant complex cap.
Artifact: this directory (screen.py -> RESULT.json, verify.py). Result files: S0-S5.
```

## 1. What interface change lets local children be rank 16?

A climb event is `['climb', phase, register, a, b, rank]` with `cur = a`, `span(a) ⊆ span(b)`,
`rank = dim(b) − dim(a) > 0` (semantics replayed explicitly in `verify.py`). Census facts
(both orientations identical; §4): frame catalogue 1,004 frames over 704 registers, dimensions
`{0:1, 1:120, 2:168, 3:168, 4:73, 5:27, 6:168, 7:152, 8:126, 9:1}`; observed climb ranks are
1–5 (the eight rank-8 children per call are centre copies, not climbs). Hence:

- **No single-register child can have rank 16** (max dimension difference is 9). Rank 16
  requires a multi-array child. The halving guard is *not* the blocker: `R(73) = 51 ≥ 16`,
  so blocked children fit the existing outer recipe with no guard change.
- **(B1) Diagonal/block child with staged layout** — 16 rank-1 children embedded as the
  diagonal of one rank-16 child, paying gather/scatter copies per array. Changed hypothesis
  vs [#2203](https://github.com/CrocSwap/integer-mult-bounds/pull/2203) (Jeremy Diviney):
  none in tariff philosophy — #2203 prices a rank-2 block carrying two arrays as two native
  uses under the one-array interface; B1 likewise keeps per-array staging uses and prices
  them (copy of a value in a `d`-frame billed as a rank-`d` child, the centre-copy precedent:
  eight rank-8 copies of 8-dimensional totals = 64/call). **Falsified in §2/§4.**
- **(B2) In-place multi-array child at joint rank (drop lemma)** — one child lifts 16 arrays
  in place, billed once at `(16/73)^(1−a)`. Changed hypothesis: exactly the hypothetical
  primitive #2203 leaves open ("a hypothetical primitive acting jointly on two full arrays;
  that needs a new physical contract and bill") and `muse-plane-port-interface` isolated at
  width 2. **Open; thresholds for it are §3.**
- **(B3) Same-register fusion** `a→b→c ↦ a→c` — no interface change, but capped at rank 9
  and, exactly, **0 instances** in the selected word (§4). Dead as a rank-16 route.
- **Not pursued:** enlarging the frame lattice or merging across calls. The first is a new
  word/template whose window `m` grows (`m = 1+8s` form); `muse-ood-template-k5` priced the
  selected word at the legal `m=89` window at −1.87%, and #2052 Theorem S covers multi-pair
  schedules including degenerate-label pair fusion (Lemma Q). B1/B2 fuse *climbs within one
  call on distinct registers* — pair count, stages and coverage deficit `D = 320/9` per call
  are unchanged — so no #2052 claim is reopened. #2076/#2048 centre routes (centre 64 held
  fixed), #2118 paired-plane *matching* (Cinna Davis; different object, used only through
  #2203's payload accounting) and the P111 copy floor (bit side; `a_b` held fixed) are
  likewise not reopened.

Float `D/E` diagnostic (`RESULT.json` S0, floats only): selected `E_local = 20382.9` with
rank-1 share 50.8% and rank-1+2 share 65.5% (T74: 50.5% / 69.1%); effective rank over
local + ideal-idle mass 4.02 (selected) / 4.29 (T74), consistent with the brief's ≈3.9.
Batching attacks `E` only; `D` is untouched, which is why its ceiling (all local mass at
rank 16: `a < 0.003909456002`, ×2.313, recomputed S0) is the 2.31× lever and no more.

## 2. Fully charged bound (replacement model)

Under B1/B2 the coverage law, template and `R(m)` are unchanged; only the local profile
changes and staging mass displaces idle mass, so the pinned relaxation remains the correct
optimistic screen. In the excess-price form (`ceiling.py` budget, `R = 51`),
`relax(a) ≤ 1 ⟺ Σ n_r p_r(a) ≤ B(a)` with `p_r` the excess of a rank-`r` child over ideal
idle mass. At `a_F`: `B = 0.426641`, selected spend `0.429540` (overspend `0.002898`),
`p₁ = 9.1930e-05`, `p₁₆ = 4.3264e-04 > 0` (certified; S3). Therefore, per batch:

```
spend change = -16 p1 + p16 + (staging excess)  =  -g + staging,   g = 1.0382e-03.
```

- Any staging with excess `≥ g` per batch never helps, for any batch count. One rank-1 copy
  per register one-way has excess `16 p₁ = g + p₁₆ > g` — it makes the word strictly worse
  than no batching. The asymptotic staging cap is `g/p₁ = 11.294` rank-1 units per batch
  (`0.706`/register); finite-count caps are smaller (must also cover the overspend).
- Sharp overhead break-evens at `a_F` (0.1-mass grid, certified opposite signs; S3):

| batches B | rank-1 shape pass/fail | per batch | rank-8 shape pass/fail | per batch |
|---|---|---|---|---|
| 3 | 2.3 / 2.4 | 0.77 | 5.0 / 5.1 | 1.67 |
| 8 | 58.8 / 58.9 | 7.35 | 125.0 / 125.1 | 15.63 |
| 12 | 103.9 / 104.0 | 8.66 | 221.1 / 221.2 | 18.43 |
| 134 | 1481.8 / 1481.9 | 11.06 | coverage-bound (1646 passes) | — |

  At the +5% gate (`a = 0.0017745568155`), B=134 allows 1258.8/1258.9 (9.39/batch),
  reproducing `diagonal-batch-commutation`'s integer headroom 1258. On the frontier's own
  global profile (actual moment at `a = κ₂₃₇₄`, overhead displacing rank-48 idle, S2) the
  break-even is 11.4 per batch at B=1 and 11.45 at B=2 — the same `< 0.72`/register bar.

## 3. Minimal conversion to beat 0.0016971949509 (under B2, zero staging)

Selected word, relaxation thresholds (integer batches certified by adjacent failure;
fractional masses sharp on a 0.1 grid; S1):

| target `a` | rank-1 batches (×16) | rank-1 mass pass/fail | of rank-1 | rank-1+2 mass pass/fail | of pool 3248 | rank-2 batches (×8) |
|---|---|---|---|---|---|---|
| `κ₂₃₇₄` = 0.0016971949509 | 2 | 31.9 / 31.8 | 1.32% | 34.1 / 34.0 | 1.05% | 3 |
| `a_F` = 0.001700080319 | 3 | 44.7 / 44.6 | 1.85% | 47.8 / 47.7 | 1.47% | 4 |
| `a_b` = 0.001733427040 | 12 | 189.6 / 189.5 | 7.86% | 202.6 / 202.5 | 6.24% | 16 |

Ceilings along the way: B=3 `0.001700833077`, B=8 `0.001719107429` (the #1779 point),
B=12 `0.001734012646` (first above the bit endpoint), B=134 `0.002358018699` (+39.5%).
On the **actual** selected global profile (real idle, 144 calls; S2) the minimum is
**7 batches/call under both frontier readings** (at `a_F`: moment `[1.00000953446741]` at
B=6, `[0.999999105743631]` at B=7). On the **T74 word**: its relaxation ceiling
`0.001729477117` already exceeds `a_F` (B=0; relaxation honesty — its *actual* endpoint is
the frontier value), it needs B=2 to reach `a_b` in relaxation (rank-1 mass 16.9/16.8,
0.72%), and on #2374's actual global profile **B=1/call** (16 of 2335 rank-1 children,
0.69%) moves the recomputed moment endpoint `0.001697194951 → 0.001700803047`
(B=2: `0.001704426545`; brackets in S2). All of §3 is conditional on B2 costing nothing to
stage; §2 caps what staging may cost before every row reverses.

## 4. Cheapest concrete merge, tested exactly (selected word)

**Test:** take the dependency-legal diagonal batches of `diagonal-batch-commutation`
(rank-1 climbs movable within their phase past events not touching their register; windows
and distinct destinations enforced by its own `batch.py`, reused pinned) and charge each
batch's staging under the frame-dimension copy tariff: per register, copy-in at rank
`dim(a)`, copy-out at rank `dim(b) = dim(a)+1`, summed exactly from the programs. Cheapest
batches first (most favourable selection). Both orientations give identical aggregates;
frame semantics are replayed as a positive control.

- Batches available: **134/call** (A 58, B 52, cleanup_tail 4, final 20), covering 2,144 of
  2,412 rank-1 climbs. Chronology is not the constraint (predecessor result, reproduced).
- Staging histogram over all batches: `{0:352, 1:768, 2:716, 3:463, 4:211, 5:128, 6:348,
  7:465, 8:517, 9:320}`, **mass 17,432/call** (mean 130.1/batch) vs idle 1,646: the staged
  profile violates the coverage law outright (`verify` S4; the engine rejects it).
- Cheapest-first staged batches still fail, and get worse as more are added (S4):
  B=3 (staging mass 48, all zero-frame origins) `relax(a_F) = 1.00004215147591`;
  B=7 (112) `1.00005953452951`; B=8 (132) `1.0000669209669`; B=12 (260) `1.0001329548043`.
  Even the free-copy-in zero-frame climbs (352 of them, `dim(a)=0`) cannot pay their
  rank-1 copy-out: 16/batch against a ≤11.06/batch break-even.
- Transition diversity: 1,928 distinct `(a,b)` transitions among 2,412 rank-1 climbs (most
  frequent only 32: `(0,3)`, `(0,2)`); batches mix 13.49 distinct transitions on average
  (max 16). A block child with a *single* frame pair therefore admits at most
  `Σ floor(cnt/16) = 6` batches (per-phase bound, windows ignored — a true upper bound),
  `< 7` needed in §3. A product-frame B2 lemma must instead cover arbitrary 16-fold
  products of catalogue frames.
- Same-register adjacent climb pairs (B3 candidates): **0** in each orientation — every
  climb's register is touched by a scalar/adapter before its next climb.

## 5. Disposition by interface

| Interface | Verdict | Decisive quantity |
|---|---|---|
| B1 staged diagonal (any copy tariff ≥1 rank-1/register one-way) | **Falsified** (all B) | `g/p₁ = 11.294 < 16`; census staging 17,432 ≫ idle 1,646 |
| B1 with common frame pair per batch | **Falsified** on actual H | UB 6 batches < 7 needed |
| B3 same-register fusion | **Empty** (and rank ≤ 9) | 0 adjacent pairs |
| B2 in-place joint-rank child (drop lemma) | **Open** — only survivor | needs staging `< 0.71` rank-1/register; then 7 batches/call suffice (selected, actual) |

## Tests run (exact commands and outcomes)

```sh
python3 -B scripts/research_baseline.py
# selected bindings ok (complex binds; planning multipliers 6.029/5.827)
python3 -B research/complex-local-word-ceiling/verify.py
# PASS_COMPLEX_LOCAL_WORD_CEILING a_ceiling 0.001690054109089
python3 -B research/complex-local-word-ceiling/levers.py
# rank-16 x2.31 (a_cap 0.003909) among the ideal rows
python3 -B research/muse-rank16-children/screen.py
# PASS_MUSE_RANK16_CHILDREN_SCREEN (writes RESULT.json)
python3 -B research/muse-rank16-children/verify.py
python3 -I -O -B research/muse-rank16-children/verify.py
# PASS_MUSE_RANK16_CHILDREN_VERIFY both modes (7 groups, 6 tamper controls rejected)
```

Tamper controls in `verify.py` (real value mutations, each required to be rejected):
climb rank →99 and from-frame shift (explicit frame replay rejects), RESULT batch count
134→135 (comparison rejects), #2374 rank-48 count +1 (coverage identity rejects), dropping
rank-9 staging copies (mass check rejects), one extra rank-1 child (ceiling must drop).
Not run (explicitly): `make frontier1094-verify` cold replay (no supplier to admit);
`diagonal-batch-commutation/verify.py` retained-checker runs (its receipts are read as
predecessor evidence; this package replays frame semantics explicitly and re-derives its
batch counts/ceilings, but does not re-run `hpe_audit_local.py`); T74 native/strict chains
for batched profiles (meaningless without the B2 lemma); any Lean check. Open-PR overlap
beyond the local refs and titles supplied for this session was not refreshed online.

## Open proof obligations (conditional — nothing here is admitted)

For B2 to become a supplier mechanism, in dependency order: (1) the drop lemma itself — a
recursive realization (or lower bound) for lifting `k` arrays in product frames
`(a_i)→(b_i)` at joint rank `Σ(dim b_i − dim a_i)`, for arbitrary dirty arrays, with its
complete copy/restoration/precision bill shown `< 11.294` rank-1 excess units per 16-batch
(`< (2p₁−p₂)/p₁` per 2-batch at width 2); (2) all-size uniformity over arbitrary 16-fold
product frames (census batches mix ≈13.5 distinct transitions); (3) simultaneous hosting of
16 co-live arrays at a common gap inside the nine-stage windows (local windows exist;
global owner feasibility unexamined — deliberately out of this session's anti-basin);
(4) scalar/precision behaviour of product frames (coefficients are block-diagonal here,
but row-growth at the larger child must be invoiced); (5) a bit-side co-improvement for any
κ gain beyond the bit-fixed planning cap `0.001730427` (`a_b/(1+a_b)`) — rank-16 ceilings
above `a_b` (B≥12 selected, B≥2 T74 in relaxation) buy no headline κ until the bit side
moves. Inherited all-size/compiler, common-label, whole-call hosting, precision/tape and
analytic obligations are untouched throughout.

## Next experiment (single, bounded)

**Width-2 drop test (≈1 session).** Take the cheapest concrete instance of B2: two rank-1
climbs from the zero frame (352 candidates/call, transitions `(0,3)`/`(0,2)` occur 32×
each) on distinct registers with overlapping legal windows, and ask whether *any* recursive
realization lifts both for one rank-2 child's price. First step: write the width-2 contract
(two dirty arrays, product frames, restoration), compute its exact budget
(`spend gain 2p₁ − p₂` at `a_F` from the pinned engine), then either exhibit a word
realizing it inside that budget or prove a payload lower bound à la #2203 (two independent
arrays ⇒ two uses) for frame lifts. Success: a priced width-2 word (then scale to 16 via
§3 thresholds). Stop/falsify: a width-2 lower bound ≥ budget — then B2 joins B1 as excluded
for product frames of this shape, and the rank-16 lever is closed on this word family.
Do not attempt width-16 engineering, new words, or owner work before this test exists.

## Open next questions

- **Is there a width-2 joint-rank lift?** (Above.) Why: it is the smallest instance of the
  only surviving interface; its answer scales by the excess arithmetic to width 16.
  Blocker: a physical contract for product-frame children does not exist yet.
- **Can a redesigned word align climb transitions?** Why: common-frame batching is killed
  only by transition diversity (UB 6); a word engineered so that ≥112 rank-1 climbs share
  few `(a,b)` pairs would reopen a weaker, single-frame-pair block child. First step:
  measure transition diversity on the T74 words' local programs (not extracted here) and on
  one frame-refit variant. Blocker: frame choice is load-bearing for the word's paid
  profile; alignment may cost more rank elsewhere than batching saves.
- **Zero-frame climb pricing.** Why: 352 rank-1 climbs originate in the zero frame; if
  materializing a zero array in a new frame is scalar-priced (CLEAR-like) rather than
  child-priced in some future contract, the cheapest batches' copy-out model changes.
  First step: locate the retained pricing precedent for zero-frame materialization in the
  selected supplier (private-buffer CLEAR accounting lineage). Blocker: even with copy-out
  free, copy-in at frame dimension for non-zero origins (mean 57/batch) still exceeds every
  break-even, so this can at most rescue the ≤22 all-zero batches — quantify before use.

## Reproduce

```sh
python3 -B research/muse-rank16-children/screen.py          # regenerates RESULT.json
python3 -B research/muse-rank16-children/verify.py          # PASS_MUSE_RANK16_CHILDREN_VERIFY
python3 -I -O -B research/muse-rank16-children/verify.py    # same, optimized mode
```

Python 3.10+ (run here on 3.13.16), standard library only, no network.
`verify.py` recomputes base ceilings, threshold signs, actual-profile moments/endpoints,
the excess cap, one break-even bracket and the full census with explicitly checked frame
replay, compares them to `RESULT.json`, and rejects six value-mutating tamper controls;
it does not import `screen.py`.

## Credit and disclosure

Predecessor credit is retained and not claimed as new: Douglas Colkitt (with Claude) for
the [#1240](https://github.com/CrocSwap/integer-mult-bounds/pull/1240) ceiling/levers engine
reused pinned here; Sagar Thakrar (PR1012) for the coverage identity; Jose Manuel
(@jmbarrancoml, with Codex) for the diagonal rank-16 identity and contiguous census
([#1779](https://github.com/CrocSwap/integer-mult-bounds/pull/1779),
`complex-diagonal-child-batches-seed95da`); Josie Elliston's `diagonal-batch-commutation`
(prepared with Claude) for the dependency-respecting 134-batch reorder whose `batch.py`
windows are reused pinned, and Arham Tahir ([#1605](https://github.com/CrocSwap/integer-mult-bounds/pull/1605)) / Josie Elliston (discussion 1596) for reblocking budgets; woklerx (with Codex) for the joint rank-cap/centre screen; Jeremy Diviney for paired-plane native payload accounting ([#2203](https://github.com/CrocSwap/integer-mult-bounds/pull/2203); building on Philippe Van Velzen's floor and ctoth's team invoice as credited there); Cinna Davis for paired-plane rematching ([#2118](https://github.com/CrocSwap/integer-mult-bounds/pull/2118)); themilkman216 (with Claude) for Theorem S ([#2052](https://github.com/CrocSwap/integer-mult-bounds/pull/2052)); Vlado Vojdanovski ([#2322](https://github.com/CrocSwap/integer-mult-bounds/pull/2322)), Jeremy Kothe ([#2374](https://github.com/CrocSwap/integer-mult-bounds/pull/2374), [#2312](https://github.com/CrocSwap/integer-mult-bounds/pull/2312)), Mason Hale ([#2363](https://github.com/CrocSwap/integer-mult-bounds/pull/2363), [#2349](https://github.com/CrocSwap/integer-mult-bounds/pull/2349)) and Cinna Davis ([#2226](https://github.com/CrocSwap/integer-mult-bounds/pull/2226)) for the T74 frontier lineage whose profiles are screened (unreviewed); prior Meta Muse packages in `research/muse-*`, in particular `muse-plane-port-interface` for the width-2 drop-lemma framing and `muse-ood-template-k5` for legal-window reprices. Selected-construction credit remains in its review.

This package was prepared with substantial AI assistance from Meta Muse (Muse Code,
`muse-wonder-full-1.0`): interface analysis, screen/verify code, census and draft text.
Exact arithmetic is standard-library `Fraction` via the pinned predecessor engine; cited
frontier values are unreviewed and were screened, not admitted; no independent human
review, proof-assistant verification or literature-priority guarantee is claimed.
Apache-2.0, following the repository license.
