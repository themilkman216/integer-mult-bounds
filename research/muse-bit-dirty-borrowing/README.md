# Anticipatory dirty borrowing on the selected P111 bit word

**Exact local construction (one alias) + exact obstruction census; conditional
bit endpoint gain +0.079%; no new admitted κ.** Porting anticipatory dirty
borrowing
([#2226](https://github.com/CrocSwap/integer-mult-bounds/pull/2226)) to the
selected P111/PR589 bit word yields exactly **one** alias under exact
monomial (frame-zero) compensation: helpers **439 → 438**, local rank mass
**5129 → 5121**, conditional bit endpoint `a_bit` **0.001733427041 →
0.00173479764** (certified grid lower ends; hypothesis in §3), bit-limited
planning cap κ **0.0017304274698236 → 0.00173179332901985**. The other
4,192 handoff points are killed by two independently near-total walls —
frame-inclusion seam (99.1% of chronological triples) and X-part
compensation matching (1,537 of 1,538 seam-legal triples) — both counted
exactly in §2. The bit side still binds against the #2226 complex ceiling
(gap `1.95e-5` in `a`; 16 aliases of the found shape would be needed); it
does not bind #2269's claim before or after. Borrowed-source Gray touring
([#2271](https://github.com/CrocSwap/integer-mult-bounds/pull/2271)) has no
priced channel in this word (§4). Selected record unchanged
(κ = 836330098538459/500000000000000000, #1094).

Out-of-distribution session (Meta Muse, `muse-wonder-full-1.0`; see *Credit
and disclosure*). Local-only package: nothing was committed, pushed or posted.

## Task card

```text
Task: TRACK 3A (bit rail) — port #2226 anticipatory dirty borrowing and
  #2271 borrowed-source mask touring to the selected P111/PR589 bit word.
  Steps: (1) census helpers admitting an alias with exact monomial (F2)
  compensation from frame-zero inputs; (2) cheapest exact F2 witness with
  restoration + chronological/COPY-ERASE legality; (3) scale, price with the
  exact ceiling engine and exact bit moment; report helpers removed, new
  a_bit, bit-limited kappa cap vs 0.0017304 and vs #2269.
Base: upstream main 0fdd7d82 (priority revision 4). Word resolved via
  certificates/selected-result.json: research/e8-bit-p111-tuned/tune/
  bitE8mut-p111-tuned.json.gz (sha256 e3e301e6..., v=111, R=439).
  Predecessor heads read at refs/upr: #2226 dacaf3d8 (README/PROOF/
  price_engine/replay/operators), #2271 95fd4395; prior rounds
  muse-ood-bit-wall, muse-ood-block-copy, muse-ood-coverage-template,
  muse-ood-template-k5 (read first; not repeated).
Changed hypothesis (anti-basin): logical address reference changes, as in
  #2226 — a retired helper field is re-used as a later helper with its
  terminal dirty value, error cancelled at frame zero before the word
  starts. NOT packing/hosting/owner repacking; COPY63/scatter pricing,
  the block-copy union-charge question, format-limits simultaneous-liveness
  floors and the helper-skeleton fresh-climb assumption are not reopened.
Cheapest falsification first: naive lifetime census -> Class-H/G census ->
  single-alias replay -> greedy scale -> pricing (§2 order is run order).
```

## 1. The exact F2 port

Word semantics (`tune/wlib.py`, replayed independently here): 661 registers
(X 0–110, Y 111–221, helpers 222–660); gates `val[t] ^= val[s]` over F2 formal
input columns, with charged frame climbs (a register incident to a gate
climbs, by line-set inclusion, to the gate frame; increments of Q-rank are
the paid profile). Sections: D (111 frame-0 gates into Y reading helpers),
A (2075 helper-destination gates), scatter over 9 retained totals (copy ranks
9×7 = 63), B (712), C (reverse of A/B non-target gates at FULL), final climbs.
Endpoint: `Y += X`, every other input restored. Base paid profile
`{1:1323, 2:1342, 3:79, 4:44, 5:102, 6:11, 7:19}`, mass 5129 — reproduced
here and cross-checked against `wlib.paid()` in `verify.py`.

All helpers and targets start at the empty frame, so **D synthesises exactly
the F2 forms supported on helper input columns, at zero climb cost** — the
F2 form of #2226's monomial compensation from frame-zero inputs (in F2 the
warp `K_G` on compensation terms collapses to single helper reads; the
frame-changing part of `K_G` has **no** free bit analogue, see seam below).

For lender `i` (last incidence before handoff `t*`), borrower `j` (removed;
gates at/after `t*` rerouted `j→i`; earlier `j`-destined gates dropped;
earlier reads of `j` lose that source; `j` deleted from D; C rebuilt as the
reverse of the aliased non-target gates), compare against the original word
projected by π = "drop input column `j`". Deleting `j` from D is free under
π (it reads form 0). The total error at target `t` is

`E_t = Epre_t + [t ∈ P]·(π(u) + π(v_i))`,

where `u` = borrower value at `t*`, `v_i` = lender terminal value,
`P` = targets whose finals depend on `val[j]` just before `t*` (exact
0/1 propagation, computed by adjoint replay), and `Epre` accumulates the
deleted pre-handoff reads of `j`. The alias is D-compensable iff every `E_t`
is helper-supported; free (zero compensation) iff every `E_t = 0`, in
particular if `π(u) = π(v_i)` and `Epre = 0`. Chronological/frame legality:
`last(i) < t*` and the **seam** — lender terminal frame line-set-included in
the borrower's handoff gate frame (merged frame path then nested; final
frames are FULL for all helpers). Non-target restoration is automatic for
the rebuilt reverse C on the autonomous non-target subsystem (H1: no target
feeds a non-target destination — re-verified structurally), and is in any
case decided by full endpoint replay on every column. This is Step 1's
criterion and Step 2's legality contract; `build.py` implements the census
as a shortlist only — an early adjoint bug briefly produced ten phantom
"zero-response" pairs, all rejected by replay; the corrected census and
the replay now agree, and only replay-feasible aliases are ever applied.

## 2. Census: one survivor, two walls (Steps 1–2)

Naive port (handoff at first incident gate) is dead on arrival: every helper
is read in D, every helper's first A-incidence is a write, lifetimes overlap
almost completely, terminal values all carry X columns, no clean lenders.
The general handoff census (any incident event of the borrower; 4,193
handoff points, all 439 helpers as borrowers; retained totals allowed as
lenders, and as borrowers before scatter) funnels as follows
(`RESULT.json` `base_funnel_classG`, recomputed by `build.py`):

| Stage | Triples / points | Borrowers |
|---|---:|---:|
| Handoff points | 4,193 | 439 |
| — fail: prefix error X-dirty outside `P` / inconsistent on `P` | 2,890 / 26 points | — |
| Chronological (lender retired before `t*`) | 174,020 | 438 |
| Seam-legal | 1,538 | 256 |
| — seam fails at equal frame dimension (warp-gated) | 109,120 | — |
| Seam-legal ∧ D-compensable (X-clean) | **1** | **1** |
| Warp-gated ∧ X-clean | **0** | 0 |

Wall 1 (seam): lender terminal frames are typically incomparable with the
borrower's next frame; the complex word's free monomial warp between
equal-dimension frames is precisely what the bit frame lattice lacks — but
Wall 2 makes the warp moot here: all 430 non-total lender terminal X-parts
are **distinct** (supports of size 8–19 over 111 X columns), so the required
exact X-part match for D-compensation essentially never occurs; even
granting a free warp, zero further aliases appear. Best paid-compensation
proxies among seam-legal X-blocked triples (for §5): 13 borrowers need only a
2-X-column error form, but on 54–55 targets each.

**The witness** (Step 2; cheapest, and in fact only): lender register 470
(helper 248; two incidences; retires as source of A-gate 1993 at frame 79,
dimension 1, line {77}) → borrower register 444 (helper 222), handoff just
before A-gate 1994. Borrower's single prefix gate is the tune *hoist* gate
`444 += 470` at frame 79, so its prefix value is exactly `e_444 + v_470`:
`π(u) + π(v_i) = 0` — a **perfect dirty borrow needing no compensation at
all**, although its error would have reached 55 targets. D-deletion removes
borrower 444 from 55 of 111 D source lists; its three later gates are
rerouted to register 470; seam 79 ⊆ 509 holds with the merged register
already sitting at the borrower's own frame 79; retained-total snapshot and
COPY ranks are untouched (neither register is retained; scatter reads the
same projected forms, endpoint replay decides). Exact replay of the aliased
word: endpoint correct on all 660 remaining columns, all non-target inputs
restored by rebuilt C, profile `{1:1322, 2:1342, 3:79, 4:44, 5:102, 6:11,
7:18}` (one rank-1 and one rank-7 child removed). Greedy iteration with full
re-census (chained handoffs allowed) finds no second candidate: **scaling
stops at one alias on this word**.

## 3. Price (Step 3)

Exact ceiling (pinned `complex-local-word-ceiling/ceiling.py`, sha256 in
`RESULT.json`; bit parameters `m=64`, 888 families, 9 stages, centre 63,
grid `10^-12`): before `a_hi = 488979689/250000000000 = 0.001955918756`
(matches muse-ood-bit-wall B0), after `a_hi = 978862497/500000000000 =
0.001957724994` (+0.092%). Ceilings bound completions of the local profile;
they are not endpoints.

Exact bit moment, conditional form (the local profile is exact; the global
histogram is `288×local + REM` with `REM` pinned from `tune/fastc.py` and
freed mass re-hosted as rank-42 children plus one remainder child, deficit
fixed at 10272 — a stated re-hosting hypothesis, **not** a hosted audit):
certified root brackets (grid `10^-12`, moment `<1` at `a_lo`, `>1` at
`a_hi`) before `[1733427041/10^12, 866713521/5·10^11]` — the pinned endpoint
`0.001733427039589844...` sits just below this bracket and is independently
re-certified here (moment `<1`) — after
`a_lo = 43369941/25000000000 = 0.00173479764`. Hence, under the retained
planning transfer `κ = a/(1+a)` (not an admission):

- **New bit endpoint (conditional): `a_bit = 0.00173479764`**, bit-limited
  κ cap **0.00173179332901985**, vs 0.0017304274698236 before (+0.079%).
- **vs #2269** (κ = 0.0016962471390584742, unreviewed): the bit cap exceeds
  it by a factor 1.021 — the bit side does not bind #2269, before or after;
  this alias only widens that headroom marginally.
- **vs #2226 complex ceiling** `a ≈ 0.001754331546940`: gap remains
  `1.953390694e-05` in `a`. Exact sensitivity (histogram what-if, labelled):
  16 aliases of the observed `(−1 rank-1, −1 rank-7)` shape would be needed;
  this word offers one.

## 4. #2271 Gray mask touring: screened, no priced channel

#2271 saves row ADDs (21→13) by touring parity masks on a borrowed row. In
this word the paid profile counts frame climbs only — row ADDs are not
priced (21,149 ADDs in D+A+B vs mass 5129; `RESULT.json` gate census: priced
sections are overwhelmingly single-source gates, the only wide gates are the
111 already-free frame-0 D gates, and scatter fanout is priced by snapshot
copy ranks, not per-mask delivery). Touring therefore changes no climb and
no profile on this word; no alias above uses it. Its restoration discipline
(closed tour, exact dirty return) is the same discipline the rebuilt reverse
C already enforces here.

## 5. Remaining conditional obligations (nothing is admitted)

(1) Emit the aliased word as a reindexed `bitE8` artifact (R=438) and re-run
the predecessor checkers (`xcheck` H1–H5, legality, Gram witnesses) — here
the word is replayed via register mapping only. (2) Whole-call hosting/owner
map for 438 helpers in the nine-stage template: the frozen hosting selection
and `REM` remainder belong to the 439-helper audit; §3's rank-42 re-hosting
must be replaced by a hosted audit before any endpoint is claimed. (3) Full
strict outer assembly in the style of the package built on (#2226 leaves the
same items open on the complex side): both orientations, precision/tape,
stock/cutoff, finite work constants. (4) Inherited selected-record
assumptions (all-size/compiler, common-label/mutable-source, analytic side)
untouched. Any κ statement beyond the planning caps in §3 would require
(1)–(3) plus maintainer review; none is made.

## Open next questions

1. **Paid pre-handoff correction for the seam-legal X-blocked pool.** 256
   borrowers pass chronology+seam and fail only X-matching; 13 need a
   2-column X error form (borrowers 464/468/471/469…, |P|≈55). First step:
   build one (suggest borrower 464) with compensation delivered by B-gate
   source toggles and/or pre-handoff lender correction gates, all charged by
   exact replay; success = net profile moment still improves. Blocker: climb
   fragmentation of toggled X registers across 55 targets may eat the ≤8
   mass saving — that comparison is the test.
2. **Alias-aware word tuning.** Terminal X-parts are all distinct in this
   word, but that is a property of the frozen tune, not a theorem: the one
   found alias was *created* by the tune's hoist gate. First step: add
   "terminal X-part collision + seam inclusion" to the tune objective and
   re-run its elementary-move search; success = ≥16 replay-feasible aliases
   (the §3 threshold). Blocker: tune moves must remain endpoint-exact and
   moment-improving before aliasing is counted.
3. **Bit-side monomial warp.** 109,120 triples fail the seam at equal frame
   dimension. A zero-rank E8-frame relabel (bit analogue of `K_G`) is the
   named missing primitive — but warp-gated ∧ X-clean = 0, so it only pays
   combined with Q1 or Q2. First step: decide on one equal-dimension pair
   whether a charged relabel gate exists in the retained bit gate alphabet
   at all; if its price exceeds one climb increment, record and stop.
4. **Hosted 438-helper audit.** Replace §3's re-hosting hypothesis: emit the
   R=438 word and run the nine-stage hosting pipeline. Blocker: pipeline
   compute/environment (C++/Boost chain), not mathematics.

## Tests run (exact commands and outcomes)

```sh
python3 -I -B research/muse-bit-dirty-borrowing/build.py
# base replay PASS; census funnel as §2; alias 470->444 applied;
# PASS_MUSE_BIT_DIRTY_BORROWING_BUILD (writes RESULT.json)
python3 -I -B research/muse-bit-dirty-borrowing/verify.py
python3 -I -O -B research/muse-bit-dirty-borrowing/verify.py
# PASS_MUSE_BIT_DIRTY_BORROWING_VERIFY aliases=1 helpers 439->438
# mass 5129->5121 a_bit_cond 0.00173479764 tamper=6/6 rejected  (both modes)
```

Tamper controls (each mutates a value and must fail): wrong lender (471),
wrong handoff (event 2064), one flipped D source, omitted-alias profile
claim, seam-illegal lender, mutated `RESULT.json` value; plus a file-level
test (corrupting `local_mass_after` in `RESULT.json` makes `verify.py` exit
nonzero; restored file passes). Not run: predecessor `verify.sh` pipeline
(native toolchain chain; no emitted word to feed it — obligation 1),
`make frontier1094-verify` (no selected-record change), any Lean check,
#2226/#2271 package replays (read at pinned heads; their local claims are
not relied on beyond the mechanism definitions). No concurrent
artifact-regenerating suites were run.

## Reproduce

```sh
python3 -I -B research/muse-bit-dirty-borrowing/build.py    # regenerates RESULT.json (~2 min; do not use -O, build guards are asserts)
python3 -I -B research/muse-bit-dirty-borrowing/verify.py   # PASS_..._VERIFY (mode-safe checks)
```

Python 3.10+ (run on 3.13), standard library only; word, engine and record
hash-pinned in `RESULT.json`. Contents: `build.py` (census, alias builder,
pricing), `verify.py` (independent rebuild/replay + tamper controls),
`RESULT.json`, this README.

## Credit and disclosure

Mechanisms and predecessors retain full credit: Cinna Davis (with OpenAI
Codex) for anticipatory dirty borrowing
([#2226](https://github.com/CrocSwap/integer-mult-bounds/pull/2226)) and
borrowed-source Gray mask fanout
([#2271](https://github.com/CrocSwap/integer-mult-bounds/pull/2271)); the
selected bit supplier lineage PR589/PR555 (eumemic: punctured R439 word,
checkers, pipelines), on #543 (R420), #545 (punctured unit,
DreamingOfClouds), #510 (nine-stage chain), with tune moves by Dugongue
(#541/#548) and rohanarun (#542) — the found alias is literally the tune
hoist pair; Douglas Colkitt (with Claude) for the exact interval ceiling
engine; Jeremy Kothe (#2269) and the #2226-on-T74 claims used only as
comparison values (unreviewed); COPY/ERASE contract lineage cited in
muse-ood-block-copy. Selected-construction credit remains in its review.

This package was prepared with substantial AI assistance from Meta Muse
(Muse Code, `muse-wonder-full-1.0`): port derivation, census/builder/verifier
code and draft text. All arithmetic is exact (F2 bitmasks, `Fraction`
intervals via the pinned engine); no independent human review,
proof-assistant verification, hosted supplier admission or new κ is claimed.
Apache-2.0, following the repository license.
