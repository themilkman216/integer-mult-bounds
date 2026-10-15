# Pricing a block-valued COPY for the selected P111 bit decoder

**Scoped falsification and price; no new supplier or kappa.**
[research/p111-parseval-copy-interface](../p111-parseval-copy-interface/README.md)
left one mechanism unpriced: a physical block-valued copy implementing each
rank-2 Parseval block at its union-support pairing rank (five blocks, 8 each,
total 40 instead of 63). This package defines that primitive's contract,
tests the most favourable block on the actual selected word, and prices it.

**Verdict.** Simultaneous liveness is *not* the obstruction: across the real
scatter window the centres are immutable, so block ERASE would be legal. The
union charge 8 nevertheless fails for block 4 (the pure `(e7, e8)` pair, no
channel-formation cost): one copied stream delivers only a rank-1 F2 update
(all nine candidates fail on the full dirty map, 6,490–12,790 wrong entries),
and two streams cost exactly **14**, not 8. Charge 8 is the price of *one*
stream through the join frame — packing two streams into one child. Priced
per stream, all five blocks total **73** versus the incumbent 63. A cheaper
block price needs a vector-valued child / plane-port supplier (a different
coverage law), not a repricing of this word.

## 1. The block COPY/ERASE contract (definition)

State: persistent registers over F2 formal dirty columns; every register sits
in a frame (a subspace of Q^8, nested along its life; climbs are charged
children). A scalar `COPY(center, slot, center_frame, ZERO, rank)` snapshots
one centre value into a fresh clean slot; `ERASE` is legal only if the slot
still equals its own saved copy and the current centre value, in the same
centre frame (retained ABI of
[bit-two-copy-bank-boundary](../bit-two-copy-bank-boundary/README.md)).

A **rank-2 block copy** is the following proposed extension.

- *What is copied.* Two centres `c1, c2` (distinct persistent registers) and
  the block functional `Λ = (λ1, λ2)`, where `λi` is the F2 value functional
  of stream `i` at the COPY cut. COPY creates two fresh, disjoint,
  non-aliased ZERO-frame slots with `ti = λi(state)`. Each role has a fixed
  complete snapshot operator `Ci` (centre value in its frame → slot).
- *What may change while live.* Targets may read the slots. Slots may be
  sheared (e.g. `t1 += t2` for common targets, as in
  [bit-two-copy-scatter](../bit-two-copy-scatter/README.md)) only if restored
  exactly before ERASE. Centres may not change in value or frame. Helper
  changes `U` are legal only under the block stabiliser
  **`ΛU = Λ`** (row-wise generalisation of `lU = l` in
  [bit-copy-live-stabilizer](../bit-copy-live-stabilizer/README.md)), or, with
  a synchronised slot map `V ∈ GL2(F2)`, under the block intertwining
  **`VΛ = ΛU`**, the two-role form of `diag(Ci) U = V diag(Ci)` in
  [bit-live-copy-operator-intertwiner](../bit-live-copy-operator-intertwiner/README.md).
  If the copy is instead one projection `t = Pc`, a helper shear `A` is legal
  exactly when `PA = 0`, and two distinct projections of one centre force
  `A = 0` ([live-projected-copy-kernel](../live-projected-copy-kernel/README.md)).
- *ERASE legality.* At the ERASE cut, for each role: `slot_i = saved copy_i =
  Ci(current centre_i)`, same centre frames as at COPY. Restoration after
  ERASE does not count.
- *Charge and composition.* The tested invoice is one child of rank
  `ρ∪ = rank_Q G[∪ supp li, ∪ supp ri]` in the local profile and `cst += ρ∪`.
  It composes with the coverage law `total = (m − unpaid)·w + cst` at
  **`unpaid = 1`** (Parseval coefficient planes are not physical per-family
  planes, so no `unpaid = 2` credit), `w = 888/9`, `m = 64`; the deficit
  `D = T[(s−1)v − s·cst]` is then recomputed with the new `cst`. Peak live
  workspace is two slots; this physical admission is an obligation, not a
  consequence of the algebra.

## 2. Cheapest falsification: block 4 on the real word

Pinned word `research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz`
(SHA256 in `verify.py`); all arithmetic exact F2 / rational, pairing ranks
cross-checked mod 101 on the uncompressed Gram submatrix.

**Chronology (passes).** The nine retained totals (registers 472–480) receive
their last writes at D+A gate indices 2169, 2171, …, 2185 of 2186: the joint
window opens only at the D+A cut. Scatter writes targets only; section B
touches no retained register (0 gates); section C first writes register 480
at its gate 499. Hence `ΛU = Λ` holds across scatter+B and any block ERASE
before C is legal. Liveness does not obstruct a block copy.

**Frames (no single-centre record).** At the cut the nine centres occupy
frames 510–518: nine *distinct* hyperplanes of Q^8. Every pair joins to Q^8
(meet dimension 6), and the only frame in the word's frame list containing
both members of any pair is FULL. So no existing one-`center_frame` COPY
record names a block, and the two snapshot operators are distinct complete
operators — by the intertwiner classification no synchronised rebasing merges
them (only `U = V = I` across the roles). Climbing both centres to FULL
before COPY is timing-neutral (the final climbs exist anyway) but prices two
scalar copies at 8+8 in word accounting, not 8 total.

**Stream count (decisive).** Block 4's operator `L Rᵀ` has F2 rank 2. One
copied stream is one total and delivers a rank-1 update: all nine within-span
candidates fail against the full 661-column dirty block (6,490 to 12,790
wrong entries; smallest witness vs the `e7`-only candidate: target 0, input
column 0, expected bit 0, actual 1). Two streams, minimised over all 512
subsets / every GL2 basis, cost exactly **14** (`(x,y) = (1,1), (2,2)` at
7+7); even the basis-free floor for any two nonzero terms is 6+6 = 12 > 8.
Therefore charge 8 cannot be one stream (rank) nor two streams (price): it
is exactly two streams packed into one child, which the retained model
excludes — every predecessor COPY contract above charges per copied stream
and keeps the COPY rank sum at 63 under simultaneity. Mixed blocks 0–1 are
strictly worse: none of their channel values
(`r0^r1, r0^r2, r1^r2, r0^r1^r2`) exists in any of the 661 registers at the
cut, so they additionally owe channel formation in a common frame.

## 3. Price of all five blocks, obstruction, and the changed hypothesis

Under per-stream PR446 Theorem-C pricing minimised per block (the contract
of section 1 with the union invoice replaced by the stream invoice):

| Block | Union rank (not an invoice) | Priced block charge |
|---|---:|---:|
| 0 | 8 | 16 |
| 1 | 8 | 15 |
| 2 | 8 | 14 |
| 3 | 8 | 14 |
| 4 | 8 | 14 |
| **Total vs incumbent 63** | **40** | **73** |

(These agree with the predecessor audit's scalar minima; they are recomputed
here under the block contract, 512 subsets and 32 exact factorisations per
block, each replayed on the dirty block.)

**Exact obstruction.** The union-support rank prices a *single* stream whose
source/target supports span the join; the block map needs two independent
streams. Within every retained scalar-stream COPY/ERASE contract one child
carries one stream pair, so pricing the pair by the join rank is packing two
families into one child and breaks the per-family accounting (`w`, one unpaid
coordinate) on which the coverage law and deficit rest.

**Minimal changed hypothesis that would evade it.** A vector-valued child
carrying two streams per operand — equivalently a plane-port supplier in the
sense of Discussion 1587: a physical rational 2-plane per data family, a
width-2 drop lemma pricing the joint transport by the join rank, a revised
coverage law, two-slot workspace admission, and a precision/tape invoice.
Nothing in this package prices or excludes that different supplier.

**Counterfactual prize (labelled screen, not a claim).** If charge 40 were
legal, the favourable relaxation of
[complex-local-word-ceiling](../complex-local-word-ceiling/ceiling.py)
(as driven in [muse-ood-bit-wall](../muse-ood-bit-wall/screen.py): `m=64`,
888 families, 9 stages, `unpaid=1`, `R=45`; copies replaced by five rank-8
children, `centre=40`, idle mass unchanged 1150, deficit 107/3 → 176/3,
`D` per replica unit 321 → 528) brackets the bit-side ceiling at
`a ≤ 1610043333/500000000000 ≈ 0.003220086666`, versus 0.001955918756 at
`cst=63`. This bounds nothing attainable: the exact moment
`(1/W) Σ n_r (r/m)^(1−a) < 1` of a completed word remains the acceptance
test, no such word is supplied, and the complex side currently binds the
selected κ = 836330098538459/500000000000000000 — so even the counterfactual
is not a κ gain.

## Reproduction

```sh
python3 -I -O -B research/muse-ood-block-copy/verify.py          # replay vs RESULT.json
python3 -I -O -B research/muse-ood-block-copy/verify.py --write  # regenerate RESULT.json
```

Expected: `PASS_MUSE_OOD_BLOCK_COPY block4: union=8 one-stream=FAIL
two-stream=14; total=73 vs 63; tamper=5/5 rejected; no_new_kappa`.
The verifier hash-pins the word, `EXPECTED.json` and `ceiling.py` before use,
replays the full word endpoint, and runs five tamper controls (broken
Parseval column, flipped scatter value, merged frames 517/518, rank-1 block
claim, union-rank-7 claim), all of which must be rejected; corrupting
`RESULT.json` likewise fails the replay comparison. No predecessor
executable is imported; `ceiling.py` is reused unchanged. This package
deliberately contains only `README.md`, `verify.py`, `RESULT.json` per its
scoped task, so the registered-package runner (which expects task metadata)
was not run; no full repository suite, native build, or human review is
claimed.

## Overlap and provenance

`scripts/find_overlap.py --refresh` failed in this session (GitHub CLI 401,
no cached snapshot); `--offline` was used and is recorded in `RESULT.json`.
Open PR titles #2028–#2178 and local heads `refs/upr/<N>` were checked
directly: the nearest work is #2061/#2062 (scalar COPY69/COPY72 floors for
other nine-normal decoders) and #2088 (two scalar snapshots with physical
address maps; rank sum retained). None defines or prices a block-valued
copy; no covered obstruction is repeated — the changed hypothesis under test
(one child, two streams, join-rank invoice) is named in section 1.
Predecessors retained and credited: PR1900 (Parseval factorisation),
[p111-copy-rank-certificate](../p111-copy-rank-certificate/PROOF.md) (63
optimal for scalar totals), the Parseval scalar audit, PR446 Theorem C
pricing, and the five COPY/ERASE contracts cited above. Base
`0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority revision 4.

Prepared with substantial assistance from Meta Muse (muse-wonder-full-1.0)
in research, exact computation, verification and writing. Apache-2.0.

## Open next questions

1. **Can a width-2 drop lemma be proved at join-rank price?** This is the
   single missing implication. First write the child operator carrying two
   independent streams per operand on a small dirty fixture and derive its
   invoice; the blocker is that in the current construction one child is one
   stream pair, so the lemma *is* a new supplier mechanism.
2. **Do any two retained centres of a *different* P111 word share a frame at
   their joint cut?** Equal frames would at least admit an equal-operator
   block record (intertwiner) and isolate the pricing question from the ABI
   question. First replay the candidate word's frame paths at its scatter
   cut; the blocker here was nine pairwise-distinct hyperplanes.
3. **What is the exact two-slot physical workspace invoice?** Any future
   block proposal inherits the PR1704/bank-boundary admission obligation
   (disjoint slots vs private COPY workspace, routing, precision). First bind
   slots to physical buffers on the existing raw6 stream; allocator evidence,
   not scalar algebra, is the blocker.
