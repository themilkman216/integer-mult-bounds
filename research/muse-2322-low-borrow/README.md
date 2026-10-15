# Porting low/high dirty borrowing to the #2322 words: exact screen says no strict gain — no new kappa

**Result: the remaining borrowing levers on
[#2322](https://github.com/CrocSwap/integer-mult-bounds/pull/2322)'s words
(Vlado Vojdanovski's coherent four-helper handoffs on
[#2312](https://github.com/CrocSwap/integer-mult-bounds/pull/2312), conditional
kappa 0.001697060296258836) do not pass the cheap exact screen. Single low
aliases and the re-aliasing of helper 653 lose by about +5.5e-5 priced-moment
units per alias-call at pattern level; width-5 high aliases are exactly
pattern-neutral. No new kappa is claimed; the selected record is unchanged.**

Out-of-distribution session (Meta Muse, `muse-wonder-full-1.0`). Workspace:
#2322 head `002304ef` (package `research/t74-joint-owner-hillclimb`), upstream
main `0fdd7d8`, priority revision 4. Builds on the Track-3C package copied at
`research/prior-muse-t74-borrow-extend/` (48 high + 32 low aliases verified on
the #2269 words; owner fill over budget by an exact +1.86 pattern-LP margin).

## Task card

```text
Task ID / scope: muse-2322-low-borrow (Track 3H)
Base: #2322 (434 helpers, 46 handoffs, profile {1:2335,2:512,3:426,4:120,5:38,8:8}
  per call in both providers, widths {4:33,5:9,7:38,8:114,9:240})
Concrete object: #2322's two BORROW-WORDs; unaliased block helpers are the
  nine width-5 highs (606; 632-block 635,637,638,639; 664-block
  667,669,670,671), helper 653 (width 4, dropped by PR2312's width
  exchange), and all 56 width-8 low helpers; the 32 width-4 low lenders of
  #2226 are all present and unused as warp lenders (CENSUS-WIDTHS.json).
Changed hypothesis vs the 3C obstruction (named before reopening it):
  #2322's words are not #2269's: pivot-518/506 kernels, exact frame refit,
  the 651/653 width exchange and the coherent block-616 handoffs change the
  per-register widths, the paid deltas and the owner fill (joint acyclic
  order + width exchange), so the 3C pattern-LP numbers do not transfer
  verbatim. The screen below recomputes everything on #2322's own totals;
  the obstruction re-emerges with new numbers, plus one new structural
  fact (653 prices like a low alias, measured below).
Anti-basin: no packing/hosting claim is made; the LP is used only as a
  lower bound over all fills of a *changed* word.
Method: cheapest falsification first — pattern-LP idle bound at kappa_2322
  (float sweep), per-register width census with #2322's own paid_profile,
  exact stage-P single-alias builds on the true PR2312 witness
  (replay+build+audit+controls), then exact rational dual certificates.
Stop rule (per assignment): no strict gain in the screen -> no native
  emission, no owner solver run, no full pipeline.
```

## Findings so far (each with its evidence file)

1. **Width census** (`scripts/census_widths.py`, `CENSUS-WIDTHS.json`; width
   definition imported from #2322's `generate_words.paid_profile`, positive
   control reproduces both words' profile/width inventory exactly). Both
   providers identical in all candidate dims. Remaining highs 606/635/637/
   638/639 and the never-aliased 664-block 667/669/670/671 are width 5;
   helper 653 is width 4 (entrance dim 5); all 32 prior low lenders are
   width 4, start 0, end 4, none already a warp lender; all candidate low
   helpers are width 8. So the prior round's width-delta model applies
   verbatim to lows and width-5 highs; 653 is the only nonstandard case.
2. **Float pattern-LP sweep** (`scripts/screen_lp.py`, `SCREEN-LP.json`;
   same caps {8:49728,16:33152,32:33152,48:33152} — cap-mass identity
   rechecked against #2322's widths+idle; positive control reproduces the
   prior round's LP optimum 17978.923367). #2322's actual fill sits only
   +0.026 moment units above its fractional pattern bound. Low aliases:
   total lower bound already exceeds #2322's actual total at k=1 (+0.0106)
   and worsens monotonically (+2.24 at k=32). Width-5 highs: total lower
   bound is *identical* for j=0..6 (dual price of a width-5 role equals
   f(5) exactly while patterns 32:[9,9,9,5] and 32:[9,9,9] are both tight),
   i.e. zero alias-attributable gain; the only headroom is the pre-existing
   0.026 LP gap of the shipped fill itself.
3. **Exact stage-P singles** (`scripts/stagep_builds.py`, `STAGEP-SINGLES.json`,
   receipts in `stagep/`). Canonical words are byte-identical between
   PR2269 and PR2312 (sha256 `65c6d17f...`/`d7e48dcb...`), so the vendored
   #2226 replay/builder/auditor apply to PR2312's shipped 42-pair witness.
   Control V0 reproduces PR2312's pinned audit exactly. Measured deltas vs
   V0 (all replay/build/audit/controls PASS):
   - V653 (653<-73): paid {3:-1}, widths {4:-1, 7:-1, 8:+1}, mass -3 —
     helper 653 prices exactly like a low alias, not a width-5 high.
   - V606 (606<-1): paid {5:-1}, widths {5:-1}, mass -5.
   - Vlow592 (592<-298): paid {3:-1}, widths {4:-1,8:-1,9:+1}, mass -3.
   - Vlow624 (624<-378): paid {1:+1,4:-1}, widths as Vlow592, mass -3.
   With #2322-base LP duals, V653's width delta costs exactly the same idle
   slope as a low alias (+0.041374/call vs paid save f(3)=0.041319/call).

4. **Exact rational certificates** (`scripts/exact_screen.py`,
   `EXACT-SCREEN.json`; duals floored to a 1e-12 rational grid and checked
   feasible against `ceiling.child_cost` lower bounds on all 1163 patterns
   at the exact a2322 = kappa/(1-kappa) from #2322's `CLAIM.json`). Lower
   bounds on the total priced moment at kappa_2322 (actual shipped total
   <= 66304.553152):
   - one low alias (592 class): **+0.010592 above actual — falsified**;
   - 653 re-alias: **+0.010592 — falsified** (identical, as finding 3 predicts);
   - one low alias of the 624 class: +0.045679 — falsified;
   - 32 low aliases: +2.236559 (singles paid model) and +1.814141 (prior
     round's measured joint 48->80 paid delta) — falsified either way;
   - width-5 highs x1 and x9 (all of them): candidate bound exceeds the
     *base word's own* fractional bound by only +3.1e-10 / +2.8e-9 (dual
     flooring scale) — exactly neutral; versus the shipped total they show
     the same -0.026016 as the base word itself, i.e. their entire apparent
     headroom is the shipped fill's pre-existing fractional-LP gap (whose
     LP support is fractional in the cap-48 split), not an alias effect.
   Scope of all certificates: the shipped bin template and role totals
   (widths are invariant from stage P through the kernel stage — refit and
   kernel patches touch frames/sections only, verified in PR2312's
   `kernel_check` — and block-616 removal is already in #2322's totals),
   with paid deltas as measured in finding 3 transferred unchanged through
   the refit/kernel/block-616 stages (**assumption A**). On the base word
   those stages' total paid-moment effects are mass-0 reshuffles of
   -4.9e-5 (refit) and -2.4e-5 (kernels) per call, computed from PR2312's
   stage receipts; no mechanism is known by which they would enlarge a
   rank-3/rank-5 deletion, but this transfer is an assumption, not a
   theorem (see Open questions).
5. **Stock accounting (for completeness).** The measured singles each add
   one warp and *reduce* restored-cold zero buffers 78 -> 77 (lender becomes
   a carrier; 653 likewise displaces one restoration, hence its 7->8 width
   increase), and reduce helpers 434 -> 433, so the #2312/#2315 physical-
   stock charge does not grow; no stock obstruction arises. It is moot:
   the screen already stops every candidate.
6. **Composition note.** V606's prior lender (register 1) is one of
   #2322's four block-616 lenders (1,4,6,12), so that specific pair cannot
   compose with the shipped word; a different retired lender would be
   needed. This does not affect the verdict (width-5 highs are neutral for
   any lender at pattern level, and the stage-P delta was lender-shaped
   only through the measured record).

**Stop rule applied.** No scenario shows a strict gain at kappa_2322 in the
cheap screen, so per the assignment no native emission, owner repricing
solver run, strict assembly or outer witness was attempted for any
candidate, and no conditional kappa above 0.001697060296258836 is claimed
or implied. `verify.py` recomputes findings 1-4 from shipped artifacts and
runs four tamper controls (flipped gate coefficient, inflated LP dual,
off-by-one role total, altered claimed audit profile), all rejected;
status `PASS_MUSE_2322_LOW_BORROW_VERIFY` in `RESULT.json`.

## Tests run (exact commands)

```sh
python3 -B research/muse-2322-low-borrow/scripts/census_widths.py   # CENSUS-WIDTHS.json
python3 -B research/muse-2322-low-borrow/scripts/screen_lp.py       # SCREEN-LP.json (float sweep + control)
python3 -B research/muse-2322-low-borrow/scripts/stagep_builds.py   # STAGEP-SINGLES.json, stagep/ receipts+words
python3 -B research/muse-2322-low-borrow/scripts/exact_screen.py    # EXACT-SCREEN.json
python3 -B research/muse-2322-low-borrow/verify.py                  # PASS + RESULT.json (also passes with -O)
```

Supplier trees for stage 3 were extracted read-only from local refs
(`git archive refs/upr/2269`, `refs/upr/2312`) into `/tmp`; nothing outside
`research/muse-2322-low-borrow/` was written, and no commit, push or PR
was made.

## Open proof obligations / conditional status

Nothing here is a supplier or a kappa. The falsification is conditional on
assumption A above (stage-P deltas transfer through refit/kernels/block-616)
and is scoped to this bin template and these role totals; it inherits every
conditional obligation of #2322/#2312/#2269 (all-size compiler, common-label
realisation, whole-call hosting, precision/tapes, exact recovery, analytic
transfer, PR559/bit H1-H5) without adding discharge of any. The five
stage-P words are receipts, not admitted providers: no native lowering,
Lemma G stage, owner fill or assembly was run on them.

## Open next questions

1. **Close assumption A or break it.** Re-derive the frame refit
   (`frames.optimal_frames` was not shipped in PR2312) and kernel patches
   for one extended word (Vlow592 is built and awaiting exactly this), then
   compare its final paid delta to stage P. Matters because every margin
   here is ~5.5e-5/call, the same order as the refit's whole-word effect.
   First step: reconstruct an exact frame re-solver from PR2312's
   `refit_43*.json` patches (they list 42/30 frame replacements) and check
   whether the shipped patches still audit on Vlow592 (B indices shift by
   the four deleted echoes — an index-remapped patch is testable in an
   hour). Blocker: kernel patches replace whole sections, so the
   pivot-518/506 stage needs its search re-derived, not remapped.
2. **Helpers whose borrowing does not widen a width-4 lender to width 9.**
   The exact slope identity (idle +0.041374 vs save f(3)=0.041319 per call)
   is a property of this width multiset + caps, not of borrowing itself.
   A lender whose final dimension already matches the carrier lifetime, or
   a template change, escapes the LP. First step: before building any such
   word, run this package's LP on its proposed width multiset and require
   a margin, not a tie.
3. **Why is block 664 never aliased?** Its four width-5 highs are live in
   every lineage word checked. The answer does not change pricing here
   (width-5 highs are neutral), but if block 664 has different frame
   structure its *lows* might not be width-8-priced like the others in a
   future template. First step: static deadline/frame census of block 664
   on the canonical word (prior round's `census.py` pattern).
4. **The 0.026 fractional gap.** #2322's shipped fill is 0.026 moment units
   (~1.3e-7 in a) above its fractional pattern bound, whose support is
   fractional only in the cap-48 []/[9,9,9,9,9] split. Is the integer
   pattern optimum already attained by the shipped fill? First step: exact
   integer pattern solve (9 constraints; branch on the fractional split),
   then window/family feasibility — a pure-repacking question, recorded
   here only because it bounds what any future alias could ever add.

## Credit and disclosure

Mechanism: [#2226](https://github.com/CrocSwap/integer-mult-bounds/pull/2226)
Cinna Davis (1337isnot1337) — anticipatory dirty borrowing. Suppliers built
on: [#2269](https://github.com/CrocSwap/integer-mult-bounds/pull/2269) and
[#2312](https://github.com/CrocSwap/integer-mult-bounds/pull/2312) Jeremy
Kothe (T74 words, width exchange, frame refit, pivot-518/506 kernels, exact
fill; physical-stock charge after
[#2315](https://github.com/CrocSwap/integer-mult-bounds/pull/2315) Sagar
Thakrar's audit), and
[#2322](https://github.com/CrocSwap/integer-mult-bounds/pull/2322) Vlado
Vojdanovski (coherent four-helper handoffs, joint acyclic owner order,
`paid_profile` recount imported here). Exact interval engine: Douglas
Colkitt, `research/complex-local-word-ceiling/ceiling.py`. Prior round:
Track 3C `muse-t74-borrow-extend` (Meta Muse) for the 48/80 witnesses, the
low-pair records and initial corrections reused at stage P, and the pattern-
LP method. This package contributes the #2322 width census, the
recomputed LP screen on #2322 totals, the stage-P singles on the true
PR2312 witness (including the 653 measurement), and the exact dual
certificates. Prepared with substantial assistance from Meta Muse
(`muse-wonder-full-1.0`). Apache-2.0; predecessor notices retained. No
independent human review is claimed. Local-only: nothing committed, pushed
or posted.
