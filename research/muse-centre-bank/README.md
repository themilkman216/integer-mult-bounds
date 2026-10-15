# Persistent centre bank between two calls: cheapest contract, full invoice, break-even, and selected-word test

**Scoped falsification and handoff. No construction admitted, no new supplier, no new κ.**
The selected record (κ = 836330098538459/500000000000000000 ≈ 0.00167266019708,
[#1094](https://github.com/CrocSwap/integer-mult-bounds/pull/1094)) is unchanged. Upstream
`main` is `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2` (priority revision 4). The open
leaderboard values used only as targets (#2374 κ = 0.0016971949509, #2363, #2322
0.001697060296) are unreviewed and are not baselines. Every ceiling below is a favourable
relaxation under stated hypotheses; the exact moment of a completed construction remains
the acceptance test.

Out-of-distribution session (Meta Muse, `muse-wonder-full-1.0`; see *Credit and
disclosure*). Local-only package for maintainer review: nothing was committed, pushed
or posted. Track 4A (centre path). Prior packages read before starting:
`research/muse-ood-coverage-template/`, `research/muse-ood-template-k5/` in full, and the
README headline tables of `muse-ood-bit-wall`, `muse-ood-block-copy`,
`muse-plane-port-interface`, `muse-2322-exact-fill`, `muse-2322-low-borrow`,
`muse-dispatch-2322`, `muse-t74-exact-fill`, `muse-t74-borrow-extend`,
`muse-bit-dirty-borrowing` (T74/borrowing/dispatch/owner family recorded there as
saturated; none of that work is repeated here).

## Task card

```text
Task ID / scope: muse-centre-bank (Track 4A, centre path; recursive-interfaces)
Base: main 0fdd7d8 (priority revision 4); selected kappa #1094 above.
Predecessors read at head: #2076 a49b52e4 (centre-prefix fanout obstruction),
  #2048 a0e55f35 (native rank 8192 for two centre cuts), #2088 95669bdd
  (two copied snapshots, selected physical address maps, bit side),
  #2241 5688d8b1 (temporary two-output sum-anchor), #2052 79cb4818
  (Theorem S), #2203 c3c85ea8 / #2118 5d324bba (paired-plane tariffs);
  on main: complex-local-word-ceiling (ceiling.py sha256 in RESULT.json),
  centre-sharing-overhead-budget, centre-sharing-mixed-overhead,
  centre-fanout-two-panel-seed962302 (PR1708 forward fusion),
  centre-shared-return-guard (PR1748 reverse fusion),
  selected-centre-adjacent-pair-seed01fcb1 (143 adjacent pairs),
  selected-centre-composed-source-rank (scalar rank 16 pair),
  centre-cut-pair-sharing (296 intra-call mixed totals),
  centre-descent-tree-audit (8/value descent floor).
Concrete object: selected complex per-call word {1:2412,2:418,3:432,4:142,
  5:82,8:8} (mass 5586; centre 8x rank-8 = 64/call), m=73, 896 families,
  9 stages, w=896/9, idle cap R=51; selected 144-call schedule
  (gauge44, 704 roles/call, 8 centre source roles [92,57,81,224,11,240,9,256],
  frames 415..422, 176 scatter edges/call, 88 active targets/call).
Question: design the cheapest concrete two-call centre-sharing contract
  (persistent bank or phase reordering, extra reads/storage allowed),
  price storage/reads/frame changes in full, test against break-even
  with the exact ceiling engine; construct on the selected word iff it survives.
Declared targets: a_lead = k_lead/(1-k_lead) for k_lead=0.0016971949509
  (exact Fraction in RESULT.json, ~0.0017000803); selected a_sel
  = 836330098538459/499163669901461541 (~0.0016754627); bit endpoint
  (predecessor pin, for the +3.45% cap context only).
Method: cheapest falsification first -- (1) exact ceiling brackets and
  break-even overhead, (2) all-pairs owner/chart census, (3) exact
  value-equality witnesses for dependent pairs. No network built unless
  (1)-(3) leave a surviving pair.
Anti-basin: no packing/hosting/owner/dispatch/borrowing variation.
Intended artifact: this directory (screen.py, census.py, verify.py, RESULT.json).
```

## Changed hypotheses (named before any covered obstruction is touched)

| Covered result (scope) | Hypothesis this package changes, or respects |
|---|---|
| [#2052](https://github.com/CrocSwap/integer-mult-bounds/pull/2052) Theorem S + §1 star floor: same-stage pairs on *independent* data each pay full centre (`cst=64`); F13 "two pairs, one centre path" impossible there | **Breaks only the full-per-call centre premise (its (2)) for a *sequential related-data* pair**, the opening #2052 §1 itself names (PR1708-line reuse in a later call). Shear words (1), two-bank coverage (3) and window `m=1+8s` (4) are kept. Same-stage fusion is not retried. |
| [#2076](https://github.com/CrocSwap/integer-mult-bounds/pull/2076): zero-storage early fanout before the forward scalar prefix fails (34–56/704 roles differ; witness `1/4` at role 114), common-frame scalar projection only | **Storage > 0 and native timing kept**: values are descended at the native centre phase into a persistent bank; nothing is injected before the prefix. This is exactly #2076's stated open route. |
| [#2048](https://github.com/CrocSwap/integer-mult-bounds/pull/2048): an 8×512-row *sole* linear transcript cannot reconstruct two centre scatters (joint native rank 8192); extra reads, larger rows, reusable storage, sequential reuse explicitly not excluded | **Time-multiplexed 16-row transcript + every extra read invoiced.** For disjoint-data pairs the rank-8192 fact is used as an input, not disputed. The sequential-reuse loophole is closed by pricing (contract CB-B), not by rank. |
| Adjacent census (`selected-centre-adjacent-pair-seed01fcb1`): 0/143 adjacent pairs share any centre source owner; 9 share all chart tuples; zero-transport direct reuse only | **All 10,296 unordered pairs, nonadjacent liveness, partial-slot sharing, and value equality** (owner equality is only evidence; descended-value equality is the requirement). |
| Descent-tree audit: one value to its 22 targets costs ≥ 8 (meet zero), independent nested trees; total 64 optimal | **Independence broken only via banked reuse / mixing, with mixing priced** by the same codimension rule. No claim that a single fresh value beats 8. |
| `centre-cut-pair-sharing`: one intra-call mixed total `H=C_i+λC_j` (296 cases) ties mass 64 at best and loses moment | Cross-call mixing (CB-B/CB-C) changes the domain to disjoint panels in two calls; the same concavity accounting is applied, not assumed away. |
| [#2203](https://github.com/CrocSwap/integer-mult-bounds/pull/2203)/[#2118](https://github.com/CrocSwap/integer-mult-bounds/pull/2118) + p111 copy floor: per-stream pricing; joint-rank (width-2) invoice is a different supplier | CB-A/CB-B **respect per-stream pricing**. CB-C (fused rank-16 descent) is labelled hypothesis (W), a changed child, and is screened separately; it is never folded into CB-A's invoice. |
| Packing ceiling (+0.87%, κ<0.001687203): fixed word, centre 64 | Centre charge itself is the variable, so the screen uses `ceiling()` with changed centre (the `levers.py` precedent). No hosting/owner gain is claimed. |

## The three cheapest concrete contracts (full invoices)

Notation per call. Forward centre phase (selected word, both predecessor counts agree):
16 CLEAR, 8 source COPY, 8 rank-8 descents, 176 scatter ADDs (22 per centre).
Two separate calls: 32 CLEAR, 16 COPY, 16 R8, 352 ADD; centre rank mass 128/pair
(64/call). Reverse phase: two separate 16 R8, 368 ADD (352 gathers + 16 source
writes), 32 CLEAR; fused reverse (PR1748) 8 R8, 360 ADD, 16 CLEAR with a factor-two
gather envelope (one extra magnitude bit `μ+1`). Forward reuse below does **not**
double any envelope (each panel is scattered separately); the `μ+1` guard is charged
only where gathers or values are actually combined (CB-C). Scalar ADD/CLEAR/COPY
counts do not enter the recursive moment directly; they enter the invoice/precision
guards, whose headroom is large (overhead-budget §5: ≤654,144 extra macros/call under
`2^48`). Rank mass is the moment currency. Ideal two-call sharing saves 8 R8 per pair
= 64 mass/pair = **32/call**; every contract is judged net of its own added rank mass.

### CB-A — Persistent 8-slot zero-frame bank, identical-value reuse (primary)

*Storage.* Eight bank slots `B_0..B_7`: private physical families distinct from every
persistent owner and from each call's eight private centres, at frame ZERO, tagged by
family so no cover class `d` aliases them (the addressing argument of
[#2088](https://github.com/CrocSwap/integer-mult-bounds/pull/2088), transposed from two
bit slots to eight complex slots; #2088 itself proves the bit instance only — the
complex allocator admission is an obligation, § *Open proof obligations*). One bank
serves the whole sequential 144-call schedule (pairs are time-disjoint), so physical
stock grows by 8 families total, not per replica. Slots start zero, end zero.

*Schedule for an ordered pair (A before B, same orientation, disjoint 112-row panels).*
1. A runs its native prefix unchanged. At A's centre phase, the 8 COPY+descent pairs
   write into `B_k` instead of A's private centres (same 8 R8, same frames 415+k → ZERO).
2. A's 176 scatter ADDs read `B_k` (source-preserving). A's 8 final private CLEARs are
   **deferred**; A otherwise completes normally (private centres unused by A stay zero).
3. Intervening calls run unchanged; none allocates the bank families (allocator
   reservation). Bank magnitudes are single-panel values; no growth while live.
4. B runs its native prefix unchanged **except** its centre COPY/descents are skipped.
   B's 176 scatter ADDs read `B_k`. Then 8 CLEARs zero the bank (plus B's own unused
   private CLEARs retained verbatim — favourable variants that delete them are noted,
   not needed).
*Correctness condition (exact):* for every `k`, B's descended carrier value equals
`B_k` as a native row for all inputs and dirt — equivalently the normalized scalar
source maps are equal **and** the descent/chart factors agree (cf. #2048 §1–2:
descended value `= (P⊗I)x` with `x` chart-twisted). Partial form: equality for a
subset `J` of slots saves `|J|` R8 per pair; other slots run natively.

*Invoice per pair, conditional on full equality (forward; reverse is the adjoint).*

| Item | Separate | CB-A | Δ rank mass |
|---|---:|---:|---:|
| Rank-8 descents | 16 | 8 | **−64** |
| Source COPY | 16 | 8 | 0 (scalar) |
| Scatter/gather ADDs | 352 | 352 | 0 |
| CLEARs | 32 | 32 (8 deferred) | 0 |
| Extra reads | — | 0 (B scatter reads bank, same count) | 0 |
| Frame changes | 16 descents | 8 descents, no new frames | in R8 row |
| Storage | 16 private slots (time-shared) | +8 persistent bank families | 0 rank; stock obligation |
| Precision | `μ` | `μ` forward (no combined envelope) | 0 |
| Hosting | baseline | bank families reserved, helpers unchanged | 0 rank; allocator obligation |

So *if* an equal pair existed, CB-A nets the full 32/call on paired calls with
near-zero rank overhead — the entire question is existence of the equality, plus the
fraction of calls that can be disjointly paired (dilution, § *Exact results*).
Transport cannot purchase equality: moving A's values does not change what B demands.
(If demands were equal but sat in different owners, the bank scatter already *is* the
transport, at ADD cost.) CB-A is therefore falsified by an equality census, not by
storage pricing; both are reported so the conditional invoice is reusable.

### CB-B — Deferred joint scatter with sequential reuse (control closing #2048's loophole)

Bank A's 8 descended rows as in CB-A; B descends its own 8 rows into its private
centres; scatter both panels in one joint phase, optionally with the
[#2241](https://github.com/CrocSwap/integer-mult-bounds/pull/2241) temporary-sum shear
(`B_k += P_k`, fan out, restore) on corresponding slots. Invoice per pair: 16 R8
(Δ mass **0**), 352 scatter ADDs (panels are disjoint physical rows, so no target is
common and the shear saves no fanout; it adds 16 ADDs), +8 bank families live across
B's prefix, A's panel writes deferred (legal only if no intervening/B-prefix read
consumes A's targets early — census-checked). Net moment gain is identically zero
before storage: sequential reuse *conveys* 16 rows through 8 slots, as #2048 notes,
but conveys no saving. CB-B is included so "reuse" is never again mistaken for the
`levers.py` halving, which deletes mass.

### CB-C — Fused rank-16 joint descent (hypothesis (W), screened separately)

Hold A's 8 carriers **pre-descent** in frame-matched slots (frames 415..422, 8 further
families) across B's prefix; then perform 8 joint descents of pairs `(A_k,B_k)` as
rank-16 children to ZERO and scatter both panels (352 ADDs). Mass per pair stays 128
(8×16); only the rank *shape* improves (`{8:8}`→`{16:4}` per call on average, centre
charge still 64). Requirements beyond CB-A: (i) a width-2 child recipe descending two
rows at once (changed supplier, cf. #2203 (W)); (ii) equal charts per slot, else
alignment transports (each ≥ its pairing rank, charged); (iii) A's scatter deferred
as in CB-B; (iv) combined-value envelope during the joint child (`μ+1`, PR1748 guard).
CB-C is the only contract whose favourable relaxation must be computed before the
census: if even free, universal fusion cannot reach `a_lead`, it is dead without any
word work.

## Fully charged optimistic bound and break-even (derived before building)

Screening model: pinned `ceiling.py` (`relax`/`ceiling`, exact rational intervals,
grid `10^-12`), selected word above, `m=73`, families 896, stages 9. For a candidate
per-call profile `L'` and centre charge `C'`, `relax(L',C',a)<1` is necessary for any
completion under the coverage law `(73−1)w+C'` with ideal idle packing at `R=51`;
`relax>1` falsifies that profile at `a` regardless of hosting. Planning transfer
`κ<a/(1+a)` (complex binds until the bit endpoint; whole-bound cap +3.4536% with bit
fixed, i.e. κ≤0.00173042747 — centre work alone can never pass that, and `a_lead`
lies below the bit endpoint so the bit side does not bind *at the declared target*).

Break-even quantities computed in `screen.py` (exact signs, `RESULT.json` authoritative):
base ceiling; ideal shared (`{8:4}`, C=32); fused (`{16:4}`, C=64); and, for the shared
profile plus added overhead mass `L` in shapes `r∈{1,8,51}` (51 = cheapest per mass,
the mixed-overhead extremal), the largest `L` (0.1-grid bracket + integer-child
bracket) still passing `a_lead` and `a_sel`. Reading: a real two-call contract whose
*average* added rank mass per call exceeds the `a_lead` bracket cannot beat #2374 even
with ideal idle packing on this word; exceeding the `a_sel` bracket cannot beat the
selected record at all. Partial pairing with fraction `f` of calls paired and `j/8`
slots equal scales the ideal saving to `32·f·(j/8)` per call on average; the census
supplies the attainable `(f,j)` upper bounds. T74-word transfer (leaderboard words
carry the same `8:8` centre but a different non-centre profile and outer assembly) is
an explicit obligation: beating #2374 *as published* needs the same centre saving
re-priced through #2322's pipeline, not only this selected-word screen.

