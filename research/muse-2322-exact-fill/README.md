# Exact owner fill on #2322: of the 0.025971 pattern gap, 0.017091 is legally realisable — candidate fill passing #2322's owner checks with native endpoint 0.00169714943564754581…

**CHECKPOINT (pipeline running; header updated on completion). Result so
far: a legal fill on #2322's own words/order/windows that strictly improves
its shipped fill. The candidate (357 of 289044 items relocated; cap-16
`[9]` singletons 87 → 1) passes #2322's own `owners_check` verbatim, and its
exact native endpoint bracket
`[0.0016971494356475458117166897688835355107, +10^-40]` (directed
`fine_moment`, #2322's engine/constants) exceeds #2322's shipped bracket
upper endpoint `0.0016970602962588368950279736213908681183` by
`8.91e-08`. The full strict/outer carry-through (`cold_replay.py` on a
candidate data directory against pinned PR2288/PR2312 sources) is RUNNING;
no new conditional kappa is claimed until it returns. For fill rows on
#2322 the changed hypothesis vs Track 3E is decisive: Track 3E's saturated
prefix-57 cut and seven-chain closure were properties of the #2269
instance (150 singletons); on #2322's instance no prefix/suffix cut binds,
time-segment refined duals return exactly the counting bound, and
seven-chains from the (43,0) holes reach donors at depth 3 — so the
pattern units are realisable, and 8 full units + 3 pairs are constructed
below. The remaining pattern gap is 0.008880 (cap-48 patterns in two
windows; see Finding 3). The selected record
(kappa = 836330098538459/500000000000000000, #1094) is unchanged; #2322
(kappa = 0.001697060296258836) is open/unreviewed.**

Out-of-distribution session (Meta Muse, `muse-wonder-full-1.0`; see *Credit
and disclosure*). Local-only package for maintainer review: nothing was
committed, pushed or posted. (Two read-only `git fetch`es added
`refs/tmpfetch/*` and the pinned PR2288/PR2312 objects to this worktree's
`.git`, because `fetch_suppliers.py`'s GitHub-API route returned HTTP 403
in the sandbox; the pinned commits' `MANIFEST.json` sha256s match
`delta_replay.py`'s pins exactly. No history was rewritten.) Workspace
base: #2322 head `002304ef` (`research/t74-joint-owner-hillclimb`),
upstream main `0fdd7d8`, priority revision 4. Methods reused from Track
3D/3E (`research/prior-muse-t74-exact-fill/`, copied into this worktree;
its README records the #2269 counting bound, the `10|k` balance, the
seven-chain closure, and Track 3E's prefix-57 cut on the #2269 words).
Prior rounds `muse-ood-coverage-template`, `muse-ood-template-k5`,
`muse-ood-bit-wall`, `muse-ood-block-copy` are not present in this
worktree; the Track-3D README (which records they were read) was re-read
here. Prior result 3F (dispatch is exactly zero on #2322) is rechecked in
`ANALYSIS.json`: both providers' width lists and paid profiles are
identical, so dispatch cannot price anything here.

## Task card

```text
Task ID / scope: muse-2322-exact-fill (Track 3G, exact owner fill on #2322)
Base: #2322 head 002304ef (Vlado Vojdanovski; coherent four-helper
  handoffs on #2312 by Jeremy Kothe, which charges #2269's private
  cleanup buffers as physical stock after #2315's check by Sagar Thakrar;
  mechanism #2226 by Cinna Davis; words/order/windows pinned in
  research/t74-joint-owner-hillclimb data/).
Concrete object: owner fill for 666 calls x 434 helpers, widths per call
  {4:33, 5:9, 7:38, 8:114, 9:240}, 149184 bins (1332 windows x 112 ports,
  caps {8,16,32,48}, bins {8:49728, 16:33152, 32:33152, 48:33152},
  contiguous time-interval windows under #2322's call order), distinct
  physical families per call, active-data-family exclusion; H = paid+idle.
Changed hypothesis vs Track 3D/3E: words, widths, order and fill all
  changed (#2312 refit + #2322 handoffs/exchanges). Track 3E's prefix-57
  saturation does NOT transfer automatically; retested from scratch.
  Anti-basin: no packing gain on a fixed word is claimed as a supplier
  improvement; the question is how much of #2322's fixed-profile headroom
  (PACKING-CAP b ~ 0.00172006 vs kappa 0.001697060296258836) is legal-fill
  headroom under its own windows/families/order.
Questions: (1) exact pattern/counting bound for #2322's fill — distance
  to the pattern optimum and where the gap sits; (2) a window+family-legal
  fill (or joint moves beyond #2322's hillclimb) beating the shipped
  moment, tested with #2322's own owners_check; (3) if found, carry
  through #2322's full pipeline and report exact conditional kappa.
Method: cheapest falsification first (pattern LP -> exact rational dual;
  prefix/suffix cuts; time-segment refined duals; seven-chain BFS), then
  deterministic unit construction. Moments labelled exact are rational
  intervals (ceiling.child_cost / #2322 vendored fine_moment).
```

## Findings

### 1. Counting bound (exact): shipped fill is 0.0259712878 above the pattern bound; gap = 87 cap-16 `[9]` + 126 cap-48 bins in two windows

Shipped fill uses 15 patterns (`ANALYSIS.json`; owners_check reproduces
CLAIM profile; windows are contiguous intervals; same-family-group
windows are pairwise time-disjoint, so per-call family distinctness
collapses to per-bin distinct calls). Exact rational dual
(`scripts/bounds.py`, prices rounded to 10^-12, gamma re-derived over all
1163 patterns with `ceiling.child_cost` intervals; rechecked in
`verify.py`): idle moment of any fill at b_2322 (shipped native endpoint
lower) is at least `16994.848113380336`, vs shipped idle
`16994.874084668183` — gap `0.0259712878` (`0.0260154757` at
A_2322=K/(1-K)). Reduced-cost decomposition (exact): the 11 tight
patterns are the Track-3D set; all shipped waste is
87×`[9]`16 (rc 2.016e-4, contrib 0.017543; 86 in window (43,0), times
0–51, 1 in (35,17)), 109×`[9,9,9,9,8,4]`48 (rc 5.487e-5, 0.005981;
windows (56,10)/(53,12)), 17×`[9,9,9,9,8]`48 (rc 1.134e-4, 0.001927;
same windows), and the two #2322 exchange bins `[9,9,9]`48/`[9,9,9,9]`48
(0.000520). The LP primal optimum is fractional (cap-48 `[9x5]`x8591.4):
over the 11 tight patterns + `[9]`16 (count k), balances force
`e1+e2+e3=2627+k/2`, `d=2553-k/2`, `5*g5=42957+k/2`, hence integral tight
counts need `k ≡ 6 (mod 10)`; the k=6 pattern vector sits at
LB + 0.0012099 (pattern level only). So the pattern optimum lies in
`[LB, LB+0.00121]` and the shipped fill is 0.0248–0.0260 above it.

### 2. Window cuts do not close the gap here (contrast Track 3E)

Exact prefix/suffix tight-cut scan: the best cap-16 lower bound over all
prefixes is −83 (at T=60), i.e. no prefix forces even one `[9]` bin
(suffixes weaker). Inside S_51 (windows with hi≤51, containing (43,0))
the shipped fill uses only 1684 of 1976 width-7 items. Time-segment
refined duals (float; segments one / p51 / p57 / early, constraint
generation converged) all return exactly the counting bound
`16994.8481134753`, gap 0.025971 unchanged (`REFINED-DUAL.json`). A finer
8-segment run reached the same restricted bound at iteration 0 (hence the
same optimum by the sandwich argument of Track 3D) before its 900 s
timeout in constraint generation; reported as float non-closure only.
Seven-chain BFS (families ignored = superset; `CHAIN-DIAG.json`): the
(35,17) hole reaches a `[7,7,9,9]`32 donor at depth 1, the (43,0) holes
at depth 3 (5018 bins visited). All 1976 width-7 items of calls 0–51 sit
in cap-16 `[7,9]` bins in the shipped fill, so direct donation is
impossible but short chains exist. Nothing at flow level protects the
shipped fill; the obstruction, if any, had to be integrality/distinctness
— tested constructively next.

### 3. Construction: 8 units + 3 pairs are legal under #2322's own checker; remaining gap 0.008880 is the cap-48 patterns

Deterministic unit construction (`scripts/build_candidate.py`): a unit is
`10×[9]16 + 5×[7,7,9,9]32 + 1×[9x5]48 → 10×[7,9]16 + 5×[9,9,9]32 + 1×[]48`,
realised as explicit relocations — BFS width-7 ejection chains (lengths
3–5; per-bin distinct calls and active-data-family exclusion checked at
every move) closed by one width-9 relocation per donor. All 8 units
succeed (k: 87→7), then 3 further donor pairs on one more cap-48 bin
(k→1, that bin ends as `[9,9]`48 rem 30); every pair step strictly lowers
the float idle moment. Final candidate (`CANDIDATE-OWNERS.json.gz`, 357
items moved): idle `{1:21869, 3:8470, 4:17, 5:2693, 7:1, 12:1, 21:1, 30:1,
48:24553}`, H `{1:1576979, 2:340992, 3:292186, 4:79937, 5:28001, 7:1,
8:5328, 12:1, 21:1, 30:1, 48:24553}`, passing
`research/t74-joint-owner-hillclimb/verify.py:owners_check` unmodified
(independent source-event windows, families, capacities, prefixes, mass).
Exact idle gain vs shipped at b_2322: float 0.0170906; exact global
moment intervals and the directed endpoint are in Finding 4
(`verify.py` stages 2–3). The one remaining `[9]` bin is pattern-forced
at this exchange granularity (a lone chain only relocates rem-7). The
residual gap to the counting bound is ≈0.008880: the 126 cap-48
non-tight bins in (56,10)/(53,12) (0.007908 in the shipped
decomposition), the two exchange bins, the leftover `[9,9]`48 and the
last `[9]`16. Eliminating `[9,9,9,9,8,4]`48 needs a recipient for a
width-8 item outside tight patterns (no tight bin has rem≥8), i.e. a
multi-width cycle through non-tight intermediates whose pattern cost we
did not find negative by the small exchanges tried (recorded as Open
question 1). A generic simulated-annealing prototype over legal
relocate/swap moves (300k proposals, /tmp prototype, not retained as a
deliverable) found no improvement and is *not* evidence about the cap-48
residual — it is not used for any claim here.

### 4. Exact endpoint; carry-through status

Directed `fine_moment` (#2322's engine and constants, positive control:
shipped moment−1 at b_lo = −7.569689295709701e-41, matching
`EXACT-MOMENT.json`): candidate moment−1 at the same b_lo is
`−2.577608038418995e-07` (interval strictly below the shipped interval).
Bisected 40-digit candidate native bracket:
`[0.0016971494356475458117166897688835355107,
0.0016971494356475458117166897688835355108]`
(`scripts/endpoint.py`, `CANDIDATE-ENDPOINT.json`), i.e. native endpoint
gain `8.913938870891669e-08` over #2322's shipped upper endpoint.
**Carry-through: RUNNING** — `cold_replay.py --source-root <pinned
PR2288 614c74a6> --candidate-source-root <pinned PR2312 fb76f799>
--data work/candidate-data` (candidate data by
`scripts/build_candidate_data.py`: OWNERS/PROFILE/CONSTRUCTION/PLAN
bindings updated, `owners_check` re-passed in-process). Final conditional
kappa will be inserted here verbatim from `DELTA-ADMISSION.json`, or the
failure stage will be recorded. `PACKING-CAP.json` is unchanged by
construction (paid profile and idle *mass* unchanged; only idle rank
distribution improved, staying below the same cap).

## Tests run

(updated at completion)

## Open proof obligations / conditional status

Any candidate kappa here is conditional exactly as #2322's is: all
inherited all-size/compiler, common-label/mutable-source, whole-call
hosting, precision/tape, exact-recovery, analytic-transfer, PR559 and
bit H1–H5 obligations remain; #2226/#2269/#2312/#2322 are open/unreviewed.
This package changes only owner placement on #2322's fixed
words/order/dispatch; native words, provider programs and the outer are
#2322's. Float LP/refined-dual numbers are discovery only; every
inequality used for a conclusion is re-derived exactly in `verify.py`
(rational intervals / directed integer engine), except BFS reachability
(exact integer computation) and refined-dual non-closure (float, reported
only as non-closure).

## Open next questions

(completed at session end)

## Credit and disclosure

Mechanism: #2226 Cinna Davis / 1337isnot1337 (anticipatory dirty
borrowing). Packages built on: #2322 Vlado Vojdanovski (coherent
four-helper handoffs, retimed owner exchanges, owner checker/pipeline),
#2312 Jeremy Kothe (physical cleanup-buffer charging after #2315 Sagar
Thakrar's check; refit fill), #2269 Jeremy Kothe (T74 + 43 aliases +
PR1673 outer by Vlado Vojdanovski). Methods: Track 3D/3E
`prior-muse-t74-exact-fill` (Meta Muse sessions; pattern LP, exact dual,
unit/balance analysis, chain BFS, refined duals). Exact engines: Douglas
Colkitt (`research/complex-local-word-ceiling/ceiling.py`) and #2322's
vendored `fine_moment.py`. This package's contribution is the #2322
instance extraction, its exact counting certificate and `k ≡ 6 (mod 10)`
balance, the negative window-cut/refined-dual results for this instance,
the legal 8-unit+3-pair construction with exact endpoint, and its
pipeline carry-through. Prepared with substantial assistance from Meta
Muse (`muse-wonder-full-1.0`). Apache-2.0; predecessor notices retained.
No independent human review is claimed.
