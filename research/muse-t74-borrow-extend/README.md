# Extending anticipatory dirty borrowing on the T74 pivot-566+554 words: 48 aliases verified, priced profile invariant — no new kappa

**Result: a verified 48-alias extension of [#2269](https://github.com/CrocSwap/integer-mult-bounds/pull/2269)'s borrowing that passes every finite admission stage through native lowering and owner fill, but whose priced global profile is *identical* to #2269's — so it yields no kappa above 0.0016962471390584742 under #2269's assembly. No new kappa is claimed.** The selected record (kappa = 836330098538459/500000000000000000, [#1094](https://github.com/CrocSwap/integer-mult-bounds/pull/1094)) is unchanged.

Out-of-distribution session (Meta Muse, `muse-wonder-full-1.0`; see *Credit and disclosure*). Local-only package for maintainer review: nothing was committed, pushed or posted. Workspace base: #2269 head `b479fc55` (package `research/gmx-t74-borrow43`), upstream main `0fdd7d8`, priority revision 4. Prior rounds read first: `muse-ood-coverage-template`, `muse-ood-template-k5`, `muse-ood-bit-wall`, `muse-ood-block-copy` (in sibling worktrees).

## Task card

```text
Task ID / scope: muse-t74-borrow-extend (Track 3C, beat the open leader)
Base: #2269 b479fc55 (T74 pivot-566+554 + 43 aliases + PR1673 outer),
  mechanism #2226 dacaf3d8 (Cinna Davis), touring #2271 95fd4395
Concrete object: the two T74 local words (gauge44/extra canonical, v=112,
  h=9, 480 helpers) and their 12 rank-4/5 blocks (96 helpers, 48 "high")
Changed hypothesis vs #2269: the alias set is not limited to #2269's 43
  high helpers. Levers in order: (a) the 5 unaliased highs (606; block 632:
  635,637,638,639) with X-register retired fields; (b) low helpers with
  #2226-style initial compensation (not attempted, see Open questions);
  (c) #2271 touring (assessed inapplicable here, below).
Anti-basin: no packing/hosting/owner repacking of a fixed word is claimed
  as the mechanism; borrowing changes the paid local profile itself. The
  negative result below is precisely that, after owner filling, this
  profile change does not survive into the priced global profile.
Method: exact-interval screen first (SCREEN.json), then lender census,
  witness extension, #2269's own rebuild/audit/native/rebind/owner chain.
```

## What was built and verified (all with #2269's own checkers)

1. **Price screen** (`scripts/screen.py`, pinned `ceiling.py`, m=73, 896/9, centre 64; favourable relaxation, not an attained price). Audited local ceilings: borrow43 base `a_hi = 0.001727146802`; the realised borrow48 base profile `{1:2351,2:501,3:414,4:129,5:37,8:8}` (mass 5360) gives `a ∈ [1732028999/10^12, 1732029/10^6]`, `a_hi = 0.001732029` — the whole 48 bracket lies above the 43 ceiling, still below the bit endpoint `a_b ≈ 0.00173343` (relax(a_b) > 1). An 80-alias analogue would reach `a_hi ≈ 0.001759–0.001764`, past the bit wall (kappa then capped ≈ 0.0017304 by the planning transfer). Cross-check: #2226's selected 80-alias profile reproduces its published ceiling `0.001754331547`.
2. **Lender census** (`scripts/census.py`, `scripts/nominate.py`). #2269's witness uses 43 of 48 high helpers, all `low=false`, zero initial corrections. The missing five have 16 static candidate lenders each after necessary filters (retired before deadline in replay order including the 48 early-tail gates, dimension 4 ≤ first-gate frame dimension 4, not removed/lent/cold-restored/block-helper/centre/target): the X-registers {1,4,6,12,31,33,49,55,68,74,80,83,85,88,98,101}. Nominated: 606←1, 635←4, 637←6, 638←12, 639←31 (same for both words); `G_columns` by `bw_gauss.change(retirement_basis, handoff_basis, 9)` (verified to reproduce #2269's record for operator 1). Why #2269's own search skipped these helpers is not recorded in its package; the witness search itself was not shipped, only the replay/audit side.
3. **Exact replay + word build + independent audit + controls** (`scripts/build48.py`): adapted free-operator replay `PASS_FIXED_BORROWED_WORD columns=656 removed=48 cold=76` (0.7 s/word); `build_word.py` emits `words/BORROW-WORD-48{base,extra}.json.gz`; #2269's `audit_local.py` returns `PASS_INDEPENDENT_EXACT_BORROWING_WORD`, mass **5360** (was 5385), widths `{4:36, 5:4, 7:36, 8:116, 9:240}` (helpers 437→432), both orientations PASS (~1 s); `borrow_controls.py` ALL CONTROLS OK (~8 s).
4. **Native lowering** (`new/run_native_borrow.py`): all five steps PASS on both words (base 215 s, extra 207 s; receipts `NATIVE48-*-STEPS.json`; native trees left in `/tmp/native48-{base,extra}`, regenerable by the recorded command).
5. **Rebind** (`new/rebind.py`): passes; global paid+idle arithmetic gives rank-5 count 28785→25455 = 666 calls × −5 (`REBIND.json`).
6. **Owner fill** (`scripts/adapt_fill.py` + literal checker `scripts/reconstruct48.py`, a path-patched copy of #2269's `reconstruct.py`): #2269's fill solver (`solve_fill.py`) was not shipped, so the shipped 437-fill was adapted by dropping the five dead helpers' roles, renumbering, and repacking each bin to a gap-free prefix (surviving-helper widths verified identical register-by-register). Checker: `PASS_OWNER_VERIFY`, 287,712 roles.

## The falsification: priced global profile is invariant

The adapted fill's global profile `H = aggregate paid + idle` is **exactly** #2269's `{1:1584738, 2:337002, 3:286065, 4:84246, 5:28785, 7:150, 8:5328, 48:24479}`: paid rank-5 fell by 3330 while idle rank-5 rose 813→4143. Each dropped width-5 role sat in a full cap-32 bin (3×width-9 + width-5); removing it creates a rank-5 remainder. The exact unnormalised global moment `Σ n_r (r/73)^(1-a)` at `a = kappa/(1-kappa)` for #2269's kappa is therefore identical (`verify.py` stage 3), and #2269's endpoint prices this global profile (`independent_core.py`: `profile = aggregate_paid + idle`), so **no endpoint or kappa gain is available from these five aliases through this assembly**, despite the local-relaxation ceiling rising. The screen's gain assumes idle mass repackable at rank 51; the actual bin arithmetic forbids it here:

- Remainder patterns are locked by caps {8,16,32,48} × widths {4,5,7,8,9}: width-4 roles occur only in remainder-1 cap-32 bins, width-5 only in full cap-32 bins, remainder-3 bins are cap-48 with five width-9s.
- Every single-role move into a freed remainder-5 bin merely permutes the remainder multiset ({5,1}→{1,5} etc.); improving width-4 concentration moves {5,3}→{1,7} have no legal donors (no width-4 role sits in a remainder-3/5/7 bin). A greedy consolidator over both move classes found **0 legal improving moves** (`scripts/consolidate.py`, `CONSOLIDATE.json`). This is a scoped statement about the examined move classes on the adapted fill, not a proof over all legal fills (see Open questions).

**#2271 assessment.** The Gray-tour fanout is an F2 row-XOR circuit identity (13 vs 21 ADDs) in the bit-register model with no frames, warps or recursive billing; no occurrence of its three-mask pattern exists in the complex BORROW-WORD's gate structure as shipped, and importing it would change the word, not the borrowing. Not pursued; it remains a bit-side candidate per its own README.

## Tests run (exact commands; runtimes as recorded)

```sh
python3 -B research/muse-t74-borrow-extend/scripts/screen.py        # 16 s; SCREEN.json
python3 -B research/muse-t74-borrow-extend/scripts/census.py        # CENSUS.json
python3 -B research/muse-t74-borrow-extend/scripts/nominate.py      # witness_48_{base,extra}.json
python3 -B research/muse-t74-borrow-extend/scripts/build48.py       # replay 0.7s + build 0.5s + audit 1s + controls 8s, per word
python3 -B research/gmx-t74-borrow43/new/run_native_borrow.py \
  research/muse-t74-borrow-extend/words/BORROW-WORD-48base.json.gz /tmp/native48-base    # 215 s, 5/5 PASS
python3 -B research/gmx-t74-borrow43/new/run_native_borrow.py \
  research/muse-t74-borrow-extend/words/BORROW-WORD-48extra.json.gz /tmp/native48-extra  # 207 s, 5/5 PASS
python3 -B research/gmx-t74-borrow43/new/rebind.py research/gmx-t74-borrow43 \
  /tmp/native48-base/local /tmp/native48-extra/local /tmp/rebind48   # PASS
python3 -B research/muse-t74-borrow-extend/scripts/adapt_fill.py    # FILL48.json.gz
python3 -B research/muse-t74-borrow-extend/scripts/reconstruct48.py --out /tmp/owners48  # PASS_OWNER_VERIFY
python3 -B research/muse-t74-borrow-extend/scripts/consolidate.py   # 0 improving moves
python3 -B research/gmx-t74-borrow43/code/lemmag_stage.py /tmp/LEMMAG48.json \
  /tmp/native48-base /tmp/native48-extra                             # PASS_LEMMAG_LABELS, 6+14 mutants rejected
python3 -B research/muse-t74-borrow-extend/verify.py                # PASS (also under -I -O)
```

`verify.py` re-runs the audits and owner checker fresh, recomputes the exact ceilings and global-moment identity, binds the native/rebind receipts, and runs three tamper controls that must be rejected: T1 a flipped gate coefficient in a word copy (audit rejects), T2 a shifted fill offset (owner checker rejects), T3 an off-by-one claimed mass (comparison rejects). Status `PASS_MUSE_T74_BORROW_EXTEND_VERIFY` in `RESULT.json`.

**Not run:** `lift_parent.py`, the strict mixed assembly (`replay.py`/`audit_mixed.py` inside the retained parent layout), certified endpoints, and the outer witness (`outer/run_outer.py`). They are downstream of the priced profile, which is unchanged, so they cannot produce a kappa above #2269's from these artifacts; running them would only re-derive #2269's number at large cost. The full `research/gmx-t74-borrow43/verify.py` was likewise not run on a modified package copy (it pins #2269's shipped words/manifest by design).

## Open proof obligations / conditional status

Nothing here is admitted as a supplier. The 48-alias words inherit every conditional obligation of #2269 (all-size compiler, common-label/mutable-source realisation, whole-call hosting, precision/tape, exact recovery, analytic transfer, PR559/PR589 assumptions) plus #2226's unreviewed status. New obligations specific to this package: (i) the five X-register lenders are validated only by the same replay/audit/native chain as #2269's 43 — no independent review; (ii) the adapted owner fill is checker-verified but not solver-optimal; (iii) strict assembly, endpoints and outer witness were not rerun for the 432-helper providers (rebound PLAN exists only as a `/tmp` receipt); the Lemma G label stage was rerun on the new natives and passes, including its 14 borrow-specific mutants.

## Open next questions

1. **Can a from-scratch fill solver change H for the 432-helper words?** Matters because it decides whether the local-ceiling gain (+0.28% in a) is realisable at all in this assembly. First step: port an alternating-path/exact-fill search (the shipped fill's stated method) with the global moment of H as objective, seeded from FILL48, allowing multi-role rearrangements across windows — not just single moves. Blocker: `solve_fill.py` was not shipped in #2269; the search must be re-derived from `reconstruct.py`'s literal rules. Success test: any legal fill whose H has strictly smaller exact moment at a2269 than #2269's H.
2. **Low-helper aliases (the other 32 of #2226's 80).** Matters because the screen prices 80 aliases past the bit wall, and low aliases remove width-4 helpers — whose roles sit in remainder-1 bins, so the invariance above need not repeat. First step: solve for initial frame-zero compensation terms per low helper (the Y-error is linear in the unknown dyadic coefficients under the fixed replay; sources must be frame-zero initial helper inputs) and test one low pair end-to-end through replay/audit. Blocker: prefix-echo deletion/rewrite fields (`deleted_echo_indices`, `early_prefix_rewrites`) must be derived per helper; no shipped search does this.
3. **Why did #2269 stop at 43?** First step: ask on the PR / check for a shipped search log elsewhere in its lineage. The five new pairs pass every rerun stage here (replay, audit, controls, natives, Lemma G labels), so any unstated exclusion would have to live in the unrerun strict-assembly/outer stages — or their search simply did not consider X-register lenders for these blocks.

## Round 2 (Track 3C, in progress): low-helper aliases, then exact fill search

Round 2 pursues Open question 2 first, then 1, preserving all round-1 results above. Success test (unchanged): a legal owner fill whose priced global profile `H` has strictly smaller exact moment at #2269's kappa than #2269's `H`; only then run strict assembly/endpoints/outer through #2269's pipeline (bit endpoint `a_bit ~= 0.0017334`, kappa cap ~= 0.0017304, reported honestly).

Structural facts established by census of the T74 canonical words (to be shipped as `scripts/low_census.py` / `LOW-CENSUS.json`):

- There are 48 low helpers (4 per block x 12 blocks) but only **32 candidate low lenders**: the width-4 cold registers with start frame zero and final dimension 4, in 8 groups of 4 sharing a final frame — exactly [#2226](https://github.com/CrocSwap/integer-mult-bounds/pull/2226)'s 32 lenders (273-394). Other cold registers end at dimension 7/8 and cannot hand off at paid rank 0 into a dimension-4/5 common frame. #2269's shipped witness already contains the 48 `early_tail_events` that restore these 32 lenders to their own initial inputs before any block deadline.
- Each low helper has 4 early B "echo" gates `Y += c*h` before its block's `first_correction`. Three helpers in the #2226 low set have interleaved temporary additions into `h` from external sources whose rows are still their own initial inputs at echo time, so direct rewrite gates are derivable: 628 (temps from 566 and, new in T74, 567), 676 (566), and 672 (a -2*566 temp inserted at B6 by the T74 pivot gates, restored at B232, spanning its first two echoes). The remaining #2226-set low helpers need only echo deletion.
- Correction to the round-1 phrasing in Open question 2: low helpers themselves are **width 8** in the providers; it is the *lenders* that are width 4. A low alias therefore deletes one width-8 role and (expected, to be confirmed by native lowering) widens one width-4 cold role to width 9, so round 1's width-preserving fill adaptation cannot be reused unchanged — the fill search must move widened roles.

(Findings below this line are appended as round 2 proceeds; nothing in round 2 is claimed until its replay/audit/controls pass and are recorded here.)

### Round-2 checkpoint 1: 80-alias words verified; fill is 6.13 moment units over budget at starting point

- **One low pair first** (helper 592 <- lender 298, `scripts/low_solve.py`): prefix echoes B56-59 deleted, no rewrites; diagnostic replay Y-error = exactly 2 terms, giving corrections `Y193 += (1/2) K49 z298`, `Y199 += (1/2) K49 z298`, lender exactly restored at handoff. End-to-end `scripts/build_low.py`: vendored replay PASS (`columns=655 cold=75`), `audit_local.py` PASS (mass 5360 -> 5357; widths 4:36->35, 8:116->115, 9:240->241 — i.e. a low alias deletes a width-8 role and widens its width-4 lender to width 9), `borrow_controls.py` ALL CONTROLS OK including the four initial-correction mutants.
- **Scaling to 80** ([#2269](https://github.com/CrocSwap/integer-mult-bounds/pull/2269) 43 + round-1 5 high + 32 low with #2226's lender assignment): both words pass replay/audit/controls. Base profile `{1:2303,2:527,3:386,4:125,5:37,8:8}` mass **5264**, extra `{1:2287,2:535,3:386,4:125,5:37,8:8}` mass 5264; local ceilings (relaxation) `a ~= 0.0017576 / 0.0017586`, above the bit endpoint. **Independent corroboration:** the 64 derived initial corrections for each T74 word coincide exactly as a (target, source, coefficient) set with #2226's 64 published terms for the selected word (compared in-session against `git show dacaf3d8:research/anticipatory-dirty-borrowing/WITNESS.json`, ref `refs/upr/2226`), although they were re-derived here by linear solve under the fixed replay. Special-prefix helpers required derived rewrites only for 628 (566, and the T74-new 567), 672 (B6 -2*566 pivot temp), 676 (566).
- **Natives + rebind:** both 80-words pass all 5 native steps (~240 s each; receipts `NATIVE80-*-STEPS.json`, trees in `/tmp/native80-{base,extra}`); `rebind.py` PASS (`REBIND80.json`). Per-register provider widths change exactly at the 32 lenders (4 -> 9); widths are identical between providers per helper index.
- **Singles screen** (`scripts/screen_low_singles.py`, `LOW-SINGLES.json`): every one of the 48 low helpers (including non-#2226 blocks 632/640/648/656 and specials 636/641) solves individually with a fixed lender, exactly 2 corrections each; paid delta is mass -3 for all (rank3 -1, except blocks 624/648 rank4 -1 & rank1 +1, marginally worse). So the lender scarcity (32), not per-block solvability, limits the count; allocation choice among blocks changes paid moment by only ~0.14 units total.
- **Starting owner fill** (`scripts/fill_search80.py --from48`, `FILL80-START.json.gz`): drop low roles, widen lenders, best-fit repair of the 21,312 over-full lender bins; literal checker `reconstruct80.py` **PASS_OWNER_VERIFY**. Its exact-float priced moment at a2269 is, in unnormalised global units, paid80 48327.485 + idle 17983.198 = 66310.68 vs #2269's 66304.55 — **6.13 units over budget**. The arithmetic is knife-edge: the idle-moment budget to beat #2269 is 17977.07 against an absolute concentration floor of 17967.43 (all idle mass at rank 48), i.e. the fill's distribution penalty over the floor must be < 9.64 (the adapted starting fill has 15.77, concentrated in rem5 lender bins and rem8 cap-8/cap-16 bins). Plain move/swap hill-climbing for 240 s improves only to 17982.79 (margin -5.72).

### Round-2 conclusion: the fill cannot win in this template — exact pattern-level obstruction

The round-2 success test is **not met, and is now shown to be unmeetable for the built 80 providers in this owner template** (scoped precisely below), so by the campaign rule the strict assembly, certified endpoints and outer witness were not run (they price a global profile that cannot pass #2269's). No new kappa is claimed. The bit cap (~0.0017304) is therefore moot in this round, although the local 80-ceiling above `a_bit` is recorded at checkpoint 1.

- **Fill searches performed.** Move/swap hill-climbing on the real fill (240 s seeded): 17983.198 -> 17982.79. Pattern-count hill-climbing in the window/family relaxation (`scripts/pattern_bound.py`, maximal-multiplicity exchanges): 17982.58 from the adapted start, and a hand-built second basin ("variant B": all cap-8 bins filled `(8)`, cap-16 as `(9,7)/(8,8)/(9)`, 5s/4s in cap-32 rem-0/rem-1 patterns) is already a pattern local optimum at 17978.92.
- **Exact LP obstruction** (`scripts/pattern_lp.py`, verified in `verify.py` stage 7). Enumerating all 1163 bin patterns (caps {8,16,32,48} x widths {9,8,7,5,4}) and solving the fractional pattern-count LP gives optimum idle moment **17978.923367** (support = variant B, which is integral). The simplex dual, floored to a 10^-12 rational grid, is *exactly* feasible against the `ceiling.child_cost` lower bounds on all 1163 patterns (minimum slack 3.7e-13) with dual objective 17978.923366. Hence every legal fill of these providers has total exact moment at a2269 at least `paid80_lo + 17978.923366 = 66306.409 > 66304.553` (#2269), a certified margin of **+1.856** in the same unnormalised units. Scope: bin caps and role-width totals of this template (widths are provider-index-identical between gauge44/extra, so role totals are dispatch-independent), paid profile at the shipped dispatch counts (249/417); float estimates put an all-extra dispatch saving at <= 0.07 and an allocation swap avoiding block 624 at <= 0.14, neither closing the gap, but those two variants are estimates, not part of the exact certificate.
- **Why it is so close (per-alias arithmetic).** Each low alias saves exactly a rank-3 child per call in singles/joint paid profiles: `f(3) = 0.041319` at a2269. The cheapest possible idle increase it forces at pattern level (idle mass +3 per alias-call, concentrated optimally) has slope `0.041374` per alias-call at k=0->1 in the LP sweep (`scripts/pattern_lp_k.py`, `PATTERN-LP-K.json`). Each low alias thus *loses* ~5.5e-5 moment units per call even under perfect packing; the modelled net vs #2269 worsens monotonically with k (+0.007 at k=1, within the singles-model error there, up to +1.86 exact at k=32). Round 1's high aliases were converted one-for-one into idle rank 5; the low aliases are converted into a mix whose only slack is this 0.13% sliver — which has the wrong sign.
- **Side answer to round-1 Open question 1.** The same float LP at k=0 (48-helper widths) has optimum idle 17095.9289 vs the shipped/adapted fill's 17095.9592: any exact-fill re-optimisation of the 48 words can gain at most ~0.03 moment units at pattern level (float screen, no exact dual was stored for k=0).
- **Lemma G tooling note.** #2269's unmodified `lemmag_stage.py` fails on the 80 natives with `borrow mutant ACCEPTED warp_dropped`: with initial corrections, the forward program begins with 64 frame-zero warp *pairs* (`from == to == 0`, the compensation reads), and dropping one is invisible to frame-label mutants. Honest programs pass all label/adapter checks. `scripts/lemmag80_stage.py` (documented minimal scope fix: borrow mutants restricted to frame-changing handoff warps) passes both natives, both orientations (`LEMMAG80.json`); compensation mutants are covered at word level by `borrow_controls.py` section 11 and by verify.py T4.

**Tests run in round 2 (exact commands):**

```sh
python3 -B research/muse-t74-borrow-extend/scripts/low_census.py
python3 -B research/muse-t74-borrow-extend/scripts/low_solve.py --tag base --pairs 592:298 \
  --out witness_49_base.json --report LOW-SOLVE-49base.json
python3 -B research/muse-t74-borrow-extend/scripts/build_low.py --tag base \
  --witness witness_49_base.json --stem 49base --word BORROW-WORD-49base.json.gz
PAIRS32=592:298,593:291,594:289,596:314,600:305,601:325,602:330,604:323,608:346,609:339,610:337,612:362,624:378,625:371,626:369,628:394,672:385,673:387,674:389,676:373,680:353,681:355,682:357,684:341,688:321,689:277,690:282,692:307,696:275,697:273,698:309,700:293
python3 -B research/muse-t74-borrow-extend/scripts/low_solve.py --tag $tag --pairs $PAIRS32 \
  --out witness_80_$tag.json --report LOW-SOLVE-80$tag.json        # tag in base,extra
python3 -B research/muse-t74-borrow-extend/scripts/build_low.py --tag $tag \
  --witness witness_80_$tag.json --stem 80$tag --word BORROW-WORD-80$tag.json.gz
python3 -B research/muse-t74-borrow-extend/scripts/screen_low_singles.py
python3 -B research/gmx-t74-borrow43/new/run_native_borrow.py \
  research/muse-t74-borrow-extend/words/BORROW-WORD-80{base,extra}.json.gz /tmp/native80-{base,extra}
python3 -B research/gmx-t74-borrow43/new/rebind.py research/gmx-t74-borrow43 \
  /tmp/native80-base/local /tmp/native80-extra/local /tmp/rebind80
python3 -B research/muse-t74-borrow-extend/scripts/lemmag80_stage.py \
  research/muse-t74-borrow-extend/LEMMAG80.json /tmp/native80-base /tmp/native80-extra
python3 -B research/muse-t74-borrow-extend/scripts/fill_search80.py --from48 --seconds 0 --seed 1
python3 -B research/muse-t74-borrow-extend/scripts/fill_search80.py \
  --resume FILL80-START.json.gz --seconds 240 --seed 2 --out FILL80.json.gz
python3 -B research/muse-t74-borrow-extend/scripts/reconstruct80.py --out /tmp/owners80   # PASS_OWNER_VERIFY
python3 -B research/muse-t74-borrow-extend/scripts/pattern_bound.py FILL80-START.json.gz
python3 -B research/muse-t74-borrow-extend/scripts/pattern_bound.py VARIANTB
python3 -B research/muse-t74-borrow-extend/scripts/pattern_lp.py
python3 -B research/muse-t74-borrow-extend/scripts/pattern_lp_k.py
python3 -B research/muse-t74-borrow-extend/verify.py        # PASS (also under -I -O -B)
```

`verify.py` stage 5-8 re-runs the 80 audits and the owner checker fresh, recomputes the exact global moment of the shipped `FILL80` (66310.276, i.e. +5.72 above #2269) and the exact dual certificate above, binds the BUILD/NATIVE80/REBIND80/LEMMAG80 receipts, and runs the round-1 tamper controls plus T4 (flipped initial-correction sign, audit rejects) and T5 (dual variable inflated by 1/1000, exact feasibility rejects). Round-1's RESULT is preserved as `RESULT-R1.json`.

**Not run in round 2:** `lift_parent.py`, strict mixed assembly, certified endpoints, outer witness — the priced profile cannot pass #2269's by the exact certificate above (for its stated scope), so those stages cannot yield a conditional kappa above 0.0016962471390584742 from the 80 providers. An intermediate-k provider set (1..31 low aliases) was not built as words/natives: the LP-k sweep is a model screen there (paid side from singles), included as guidance, not as an exact obstruction for k < 32.

**Round-2 open next questions.**

1. **Change the priced object, not the packing.** The exact obstruction only covers this bin template + these provider width/count totals. A supplier whose borrowing does not widen a width-4 role to width 9 while deleting a width-8 role — e.g. lenders whose final dimension already matches the carrier lifetime, or a template/bin-cap change — escapes the LP entirely. First step: before building any such word, run the pattern LP on its proposed width multiset (generalised `pattern_lp.py`) and require LP-optimum + paid_lo < 66304.553 with margin.
2. **Exact certificates at intermediate k and alternative allocations.** First step: build the alternate-allocation 80 words (exclude blocks 624/648) through audit to get exact paid profiles, then re-run the dual check with their exact paid_lo (role totals unchanged). This closes the estimated <= 0.14 caveat either way.
3. **Lemma G compensation mutants upstream.** First step: propose to #2269's stage that borrow mutants select frame-changing warps, plus compensation-pair mutants judged by an algebraic (not label) check. Blocker: discussion/PR process; our local scope fix is a receipt only.

## Credit and disclosure

Mechanism: [#2226](https://github.com/CrocSwap/integer-mult-bounds/pull/2226) Cinna Davis / 1337isnot1337 (with OpenAI Codex assistance) — anticipatory dirty borrowing, K_G handoffs, exact replay (vendored in #2269). Package built on: [#2269](https://github.com/CrocSwap/integer-mult-bounds/pull/2269) Jeremy Kothe (T74 pivot-566+554 + 43 aliases + PR1673 capped phase-cell fusion outer by Vlado Vojdanovski), with the full supplier lineage (PR1625/PR1661/PR1319/PR1297 et al.) as credited in `research/gmx-t74-borrow43/README.md`. Exact interval engine: Douglas Colkitt, `research/complex-local-word-ceiling/ceiling.py`. Touring reference assessed: [#2271](https://github.com/CrocSwap/integer-mult-bounds/pull/2271) Cinna Davis. This package's contribution is the lender census/nomination for the five remaining high helpers, their verified 48-alias words and natives, the adapted owner fill, and the priced-profile invariance finding; round 2 adds the low-helper census/solver (initial-compensation derivation), the verified 80-alias words and natives, the owner-fill adaptation/search for the 400-helper providers, the exact pattern-LP dual obstruction for this fill template, and the scoped Lemma G stage adaptation. Prepared with substantial assistance from Meta Muse (`muse-wonder-full-1.0`). Apache-2.0; predecessor notices retained. No independent human review is claimed.
