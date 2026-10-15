# Width-2 joint-rank lift (Track 4C): retained-model lower bound — one climb carries one register

**Scoped falsification and precise handoff. No construction, no new
supplier, no new κ.** The selected record
(κ = `836330098538459/500000000000000000`, [#1094](https://github.com/CrocSwap/integer-mult-bounds/pull/1094))
is unchanged. The beat-target is the unreviewed open leader
[#2374](https://github.com/CrocSwap/integer-mult-bounds/pull/2374) at
conditional κ = `0.0016971949509...`. Every number below is either a
certified exact-interval sign/bracket from the pinned ceiling engine, an
exact finite census count, or an exact symbolic replay over ℚ; the exact
moment of a completed construction remains the acceptance test.

## Verdict in one paragraph

**Under the retained recursive interface, the width-2 joint-rank lift at
sum billing does not exist: every realization of the product lift
`(a₁,a₂) → (b₁,b₂)` on two independent dirty arrays costs at least the
sum of the two separate children, in mass, in moment and in excess, with
equality only for the two direct climbs.** The forcing property is
*per-register frame locality*: frame state `cur[r]` is per-register,
scalars and adapters never change it inside a climb phase, centre steps
move only private arrays, and a climb — the paid child — names exactly
one register (§1). Hence each register's climbs telescope to its own
`dim(bᵢ) − dim(aᵢ)` (§5, Lemmas A–B), splitting only raises the moment
(Lemma C), and helpers, private transfers, scalar mixing and staging can
only add non-negative bill. The would-be saving is certified tiny in any
case: `g₂ = 2p₁ − p₂` with `(2p₁−p₂)/p₁ ≤ 0.3536` at every frontier
reading (§3), so a single rank-1 staging copy (`p₁ ≈ 2.83·g₂`) already
exceeds it, and on the cheapest real pair (registers 546/560, identical
`0 → 4` climbs, rows exactly the basis arrays) every shortcut word is
rejected on frames or on values (§4). What remains open is exactly what
[#2203](https://github.com/CrocSwap/integer-mult-bounds/pull/2203) left
open: a *new* primitive acting jointly on two full arrays. §6 names the
minimal changed hypothesis (a two-register `JOINT_CLIMB` event with a
product-frame child contract) and the complete bill it must re-derive;
under that unproved primitive, 90 zero-staging pairs/call would pass the
frontier planning target in relaxation (§3). The lemma is therefore
decided *as a statement about the retained supplier*: Track 4B's route
B2 and the plane-port route W2 cannot be implemented inside it and must
be pursued, if at all, as a new supplier mechanism.

Out-of-distribution session (Meta Muse, `muse-wonder-full-1.0`; see
*Credit and disclosure*). Local-only package for maintainer review: nothing
was committed, pushed or posted.

## Task card

```text
Task ID / scope: muse-joint-rank-drop (Track 4C, width-2 joint-rank drop lemma)
Base: main 0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2 (priority revision 4); selected #1094.
  Frontier (unreviewed, local refs): #2374 5449da65d, #2322 002304ef0.
Converging predecessors: research/muse-rank16-children (B2, §3 thresholds,
  Open proof obligations (1)-(2), Next experiment = this width-2 test) and
  research/muse-plane-port-interface (W2, §7; C=112 conditional ceiling
  a <= 0.004078546959). #2203 refs/upr/2203 c3c85ea8
  (research/paired-plane-native-payload) leaves "a hypothetical primitive
  acting jointly on two full arrays" open. Drop packages read:
  e8-first-rank-drop, p112-joint-rank5-parent, p112-star-first-cost-drop,
  root-pair-first-drop-seed48, p104-first-copy-drop, p104-two-copy-drops
  (all price single-stream / single-term ranks; none prices a two-register
  climb — see §6 for why they do not decide this lemma).
Concrete objects: selected per-call word {1:2412,2:418,3:432,4:142,5:82,8:8}
  (m=73, 896 families/9 stages, centre 64, R(73)=51, idle 1646/call);
  pinned gauge44 programs (1004 frames over F2^9, 704 registers);
  cheapest width-2 instance = two rank-1 climbs from the zero frame
  (352/call; transitions (0,3) and (0,2) occur 32x each).
Questions: (1) state the width-2 joint-rank lift in the retained recursive
  interface with complete bill; (2) decide it: construct a recursive
  realization on the smallest real instance below the width-2 threshold
  (2p1-p2)/p1, or prove the joint child costs >= the sum of separate
  children under the retained model and name the forcing property and the
  minimal escape.
Anti-basin: NO packing/hosting/owner/dispatch/borrowing work. No covered
  obstruction is reopened without a named changed hypothesis (§6).
Method: cheapest falsification first — optimistic fully-charged bound for
  the changed interface, exact threshold, exact dirty-input replay of
  candidate words on the cheapest pair, then the general lower bound.
Targets: a = kappa_2374 = 0.0016971949509 and aF = kappa/(1-kappa) =
  0.001700080319 (both readings, as in Track 4B), plus the selected bit
  endpoint as the kappa-relevant complex cap.
Artifact: this directory (verify.py -> RESULT.json). 
```

## 1. The retained recursive interface (what a climb is)

The semantics below are those replayed literally by the retained local
checker (`research/complex-571-cold14-k492b/code/hpe_audit_local.py`,
PR514/PR433 lineage) on the pinned gauge44 programs. They are restated
here only to fix the lemma's terms; no checker condition is disabled.

- **State.** Each logical register `L r` holds one array (one formal dirty
  column block): symbolically a row `rows[r]` over ℚ in the input basis
  (initially the basis vector `e_r`; arbitrary dirty inputs are arbitrary
  coefficient vectors, so row identity on the basis is exactness on all
  dirty inputs and all address sizes). Each register also has a current
  frame `cur[r]`, an index into the 1,004-frame catalogue; a frame is a
  subspace of 𝔽₂⁹ given by a basis list, `dim = len(basis)` (frame 0 is
  `[]`, frame 1 is FULL, dim 9). Private centre arrays `C k` have their
  own current frames and hold one array each.
- **Scalar events** (`clear/copy/scale/add` with dyadic coefficients) are
  elementary row operations. They require every `L` register touched to
  satisfy `cur[r] == f` for the event's common frame `f` (private arrays
  analogously). They **do not change any `cur`**. Their coefficient growth
  is tracked by the prefix norm (`< 2^192` allowance in the selected word).
- **Climb events** `['climb', phase, r, a, b, rank]` are the paid recursive
  children inside phases `A/B/cleanup_tail/final`. A climb requires no
  private array live, `cur[r] == a`, `span(a) ⊆ span(b)` and
  `rank = dim(b) − dim(a) > 0`; it sets `cur[r] = b`, leaves `rows[r]`
  unchanged, and adds one child of rank `rank` to the paid histogram.
  A climb names **exactly one** `L` register.
- **Centre events** change exactly one private array's frame stepwise
  (nested, `rank = |dim difference| > 0`), each step one paid child.
  They never change an `L` register's `cur`.
- **Adapters** (`adapter`, `residual_adapter`) occur only in the
  `entry_adapters`, `exit_adapters` and `full_frame_cleanup` phases
  (census in §4), once per (wrapped) register, naming its start/final
  frame. In the local replay they record entry/exit wrappers and
  **do not change `cur`** mid-phase.
- **Billing.** A child of rank `r` at width `m = 73` costs
  `(r/m)^{1−a}` in the moment `(1/W) Σ n_r (r/m)^{1−a} < 1`; in excess
  form (`research/complex-local-word-ceiling/ceiling.py`, `R = 51`) it
  costs `p_r(a) = (r/m)^{1−a} − r·(R/m)^{1−a}/R` over ideal idle mass.
  Rank mass `Σ r·n_r` is the `a = 0` bill.

## 2. The width-2 joint-rank lift, stated precisely

**Product lift `J(a₁,a₂ → b₁,b₂)`.** Let `r₁ ≠ r₂` be distinct registers,
`aᵢ, bᵢ` catalogue frames with `span(aᵢ) ⊆ span(bᵢ)` and
`ρᵢ = dim(bᵢ) − dim(aᵢ) > 0`. At a cut inside one phase, `cur[rᵢ] = aᵢ`
and `rows[rᵢ]` are two **independent arbitrary dirty arrays** `X₁, X₂`
(formally: the restriction of the state matrix to `{r₁,r₂}` has rank 2
over the input basis; equivalently the lemma must hold with
`rows[rᵢ] = eᵢ` after relabelling the two input directions, all other
registers carrying independent arbitrary dirt). A realization is a word
fragment that ends with `cur[rᵢ] = bᵢ`, `rows[rᵢ] = Xᵢ` (values preserved
exactly), every other register's row *and frame* restored to its entry
state (drop-in fragment: the remainder of the word is unchanged), no
private array live, and the prefix/precision bill inside the selected
allowance. Helper/private registers may be used only if their dirt is
restored and every climb/centre step they consume is in the bill.
(§5's lower bound favourably waives helper-frame restoration and still
holds; restoration only makes helper climbs additionally impossible.)

**Separate price (retained).** Two climbs, histogram `{ρ₁:1, ρ₂:1}`,
mass `ρ₁+ρ₂`, moment `(ρ₁/m)^{1−a} + (ρ₂/m)^{1−a}`, excess `p_{ρ₁}+p_{ρ₂}`.

**Joint claim (the lemma under test).** One child billed at rank
`ρ₁+ρ₂` — moment `((ρ₁+ρ₂)/m)^{1−a}`, excess `p_{ρ₁+ρ₂}` — plus a complete
staging/restoration/precision/hosting bill `S` (in excess units), with
total **strictly below** the separate price. For the smallest instance
`ρ₁ = ρ₂ = 1` the saving available to pay `S` is exactly

```text
g2(a) = 2p1(a) − p2(a) = 2·(1/73)^{1−a} − (2/73)^{1−a}  > 0   (0 < a < 1),
```

so the joint claim needs `S < g2(a)`, i.e. staging below
`(2p₁−p₂)/p₁` rank-1 excess units per pair. The complete bill must
itemise: gather/scatter copies (centre-tariff precedent: a copy of a
value in a `d`-frame is a rank-`d` child), helper climbs, centre steps,
adapter wrappers, dirty restoration of helpers, prefix growth from any
scalar mixing, co-liveness/hosting of the two arrays at one cut, and
uniformity over the product frames actually used. Anything billed `0`
must be justified, not waived.

*Remark on the plane-port cousin.* The `W2` invoice of
`muse-plane-port-interface` §7 bills two descents `E → 0` (pairing rank 2
each, separate mass 4/plane) at the **shared** pairing rank 2/plane.
That is strictly stronger than sum billing (which would bill 4 as one
rank-4 child). This package decides the sum-billed climb lemma as
tasked; the descent cousin under the scalar-total interface is already
decided by [#2203](https://github.com/CrocSwap/integer-mult-bounds/pull/2203)
and the pair theorem of `muse-plane-port-interface` §4, and is not
reopened (§6).

## 3. Optimistic bound for the changed interface (the prize, fully charged form)

Following `autoresearch.md`'s rule, the changed interface is priced
before any construction is attempted. The replacement model keeps the
coverage law, template, centre and `R(73) = 51` and changes only the
local profile: `n` disjoint pairs of rank-1 climbs are replaced by `n`
rank-2 joint children, staging mass displacing idle mass. This splicing
is conditional in exactly the sense of Track 4B §2 and
`muse-plane-port-interface` §7: the `(r/m)^{1−a}` law presumes one data
family per child, so these numbers are the prize *if* a product-frame
supplier re-derives the same law, not a supplier.

Exact thresholds (pinned `ceiling.py`; certified intervals in
`RESULT.json`; decimals here are display only):

| target `a` | `p₁` | `p₂` | `g₂ = 2p₁−p₂` | `(2p₁−p₂)/p₁` | max staging mass/pair (rank-8 shape) |
|---|---:|---:|---:|---:|---:|
| `κ₂₃₇₄` 0.0016971949509 | 9.1774e-05 | 1.5110e-04 | 3.2447e-05 | 0.35355 | 0.7518 |
| `aF` 0.001700080319 | 9.1930e-05 | 1.5136e-04 | 3.2502e-05 | 0.35355 | 0.7518 |
| bit endpoint 0.001733427040 | 9.3741e-05 | 1.5434e-04 | 3.3144e-05 | 0.35357 | 0.7518 |

Consequences, cheapest first:

- **Any staging with excess `≥ g₂` per pair never helps, for any pair
  count.** One rank-1 copy has excess `p₁ ≈ 2.83·g₂`; even billed at
  rank-8 shape, one mass unit of staging (`p₈/8`) exceeds `g₂`. The
  width-2 bar (`< 0.354` rank-1 units/pair total, `0.177`/register) is
  four times stricter per register than the width-16 asymptotic bar
  (`0.706`/register, Track 4B §2), because the subadditivity gap at
  rank 2 is small.
- **Zero-staging conversion needed to beat the frontier** (relaxation;
  a pass is necessary, not sufficient — Track 4B needed 7 actual
  batches where the relaxation needed 3): on the selected word, **64
  pairs/call** at `κ₂₃₇₄`, **90 pairs/call** at `aF`, **379 pairs/call**
  to reach the bit endpoint; on the T74 word, 0 pairs to reach `aF` in
  relaxation (its ceiling already exceeds it) and **34 pairs/call** to
  reach the bit endpoint. Converting *all* rank-1 mass in pairs gives
  ceilings `a ≤ 0.001836572422` (selected, ×1.087) and
  `a ≤ 0.001877835209` (T74) — the width-2 fragment of the 2.31×
  rank-16 lever, still κ-capped near `0.0017304` by the unchanged bit
  supplier. The target `a = 0.004078546959` of the plane-port `C = 112`
  invoice is *not* reached by sum-billed pairing; it needs the stronger
  shared-rank billing of §2's remark.

So a construction must be essentially staging-free: the joint child
must lift both arrays *in place*. §4 tests that on the cheapest real
pair; §5 proves it impossible in the retained language.

## 4. Cheapest concrete pair, tested exactly (selected word)

**Instance.** Registers `546` and `560`, phase `A`, both orientations:
`['climb','A',546,0,4,1]` and `['climb','A',560,0,4,1]` — identical
transition from the zero frame (`[]`) to frame 4 (`[459]`, the line
`{0,459}`). This is the most favourable instance in every respect:
staging mass `dim(a)+dim(b) = 1` per register (the minimum possible,
since `dim(b) = dim(a)+1` gives `2·dim(a)+1 ≥ 1` with equality iff
`a` is the zero frame; 352 such climbs/call), identical frames (a
common-frame sum is available for free before the climb), and
dependency-legal co-liveness (skeleton windows `(0,1190)` and
`(0,1191)` overlap; either climb may move to any common gap, by the
`diagonal-batch-commutation` window rule reused pinned). The only
catalogue frames between 0 and 4 (spanwise) are 0 and 4 themselves,
so each register's lift has a unique one-step chain. The abstract
dirty-pair model is literal here: in the forward program the symbolic
rows of 546/560 just before these climbs (event indices 9297/9299) are
exactly the basis arrays `e₅₄₆, e₅₆₀` — two untouched independent dirty
inputs — and in the backward program they are independent over ℚ
(2×2 minor `−1/4` on columns 113/140; `RESULT.json` S4). For contrast,
distinct zero-frame lines have no rank-2 catalogue join at all (e.g.
frames 2 and 3, lines `30` and `51`: the smallest catalogue frame
containing both spans has dim 4), so a sum-climb for a mixed pair
overshoots before it starts.

**Candidate words** (symbolic replay on rows over ℚ — exact on all
dirty inputs, since every operation is ℚ-linear and frame checks are
value-independent; `verify.py` §MACHINE):

| candidate | hist claimed | replay verdict |
|---|---|---|
| Separate climbs (positive control) | `{1:2}` | **Passes**: frames `(4,4)`, rows identity |
| One climb only | `{1:1}` | Rejected: second register still at frame 0 |
| Sum then climb (`X₂+=X₁`, climb `X₂`, copy back) | `{1:1}` | Rejected twice: copy-back needs common frame 4 while `cur=0`; ignoring frames, the delivered map is `[[1,1],[1,1]] ≠ I₂` (witness input `(1,0)`) |
| Staged via clean helper (pack sum, climb helper, scatter) | `{1:1}` staged | Scatter rejected on frames; cheapest completion climbs both registers anyway (`{1:3}` total, excess `3p₁ > 2p₁`) and leaves the helper's frame unrestorable by climbs |
| Private-centre transfer | `{1:1}` centre step | Private frame moves; both `L` frames unmoved — endpoint rejected |

No candidate with total excess below `2p₁` passes. §5 shows this is
not a search failure: every retained word fails the same way.

## 5. Lower bound under the retained model

**Theorem.** Let a word fragment in the language of §1, inside climb
phases, realize the product lift `J(a₁,a₂ → b₁,b₂)` of §2 (ranks
`ρ₁, ρ₂ > 0`), using arbitrary scalar mixing, arbitrary helper registers
(clean or dirty, restored), private centre transfers and centre steps,
with scalars and precision billed favourably at zero. Then its paid
histogram `H` satisfies, for every `0 < a < 1`,

```text
mass(H) ≥ ρ₁+ρ₂,   Σ_{r} H_r (r/73)^{1−a} ≥ (ρ₁/73)^{1−a} + (ρ₂/73)^{1−a},
Σ_r H_r p_r(a) ≥ p_{ρ₁}(a) + p_{ρ₂}(a),
```

with equality throughout only if `H` is exactly the two direct climbs
(each `rᵢ` climbed once, no other paid event). In particular one child
at rank `ρ₁+ρ₂` (excess `p_{ρ₁+ρ₂} < p_{ρ₁}+p_{ρ₂}`) plus any further
bill `S ≥ 0` cannot realize `J`; for `ρ₁ = ρ₂ = 1` the shortfall against
the joint claim is at least `g₂(a) > 0` before `S` is even charged.
The same argument at width `k` gives `Σ H_r p_r ≥ Σᵢ p_{ρᵢ}`: Track 4B's
B2 at width 16 is excluded by the identical property.

*Proof.*

**Lemma A (frame locality).** Inside climb phases, scalar events leave
every `cur[r]` unchanged, a centre event changes only its private
array's frame, and a climb changes exactly the one `cur[r]` it names.
Adapters never occur inside climb phases. — This is the event semantics
of the retained checker (§1); `verify.py` replays both pinned programs
with explicit `cur`/private tracking and censuses every event: climbs
only in `A/B/cleanup_tail/final` (992/1856/124/514 per orientation),
adapters only in `entry_adapters/exit_adapters/full_frame_cleanup`,
centre steps only in `centers` (S4). No other event type occurs.

**Lemma B (telescoping).** Fix a register `r`. Along any fragment its
`cur[r]` changes only at its own climbs, each contributing
`rank = dim(new) − dim(old) > 0` with nested spans. Hence the ranks of
climbs on `r` sum to `dim(cur_end[r]) − dim(cur_start[r])`. If the
fragment meets the §2 endpoint then `cur_end[rᵢ] = bᵢ`, so climbs on
`rᵢ` sum to exactly `ρᵢ`; overshooting to a larger frame can never
return (no `L`-descent event exists in climb phases), and a helper
register that climbs at all cannot restore its entry frame. —
Machine instance: on both full programs every one of the 704 registers
satisfies `Σ climb ranks = dim(final) − dim(start)` (S4).

**Lemma C (splitting costs more).** For `0 < a < 1`,
`φ(t) = t^{1−a}` is strictly concave with `φ(0) = 0`, hence strictly
subadditive on positive ranks: `φ(x+y) < φ(x) + φ(y)`, and by induction
any splitting of `ρ` into `≥ 2` positive pieces has
`Σ φ(pieces) > φ(ρ)`. The same holds in excess form, since
`Σ p_{pieces} = Σ φ(pieces)/73^{1−a} − ρ·(51/73)^{1−a}/51`. —
Machine-checked by certified intervals for all 81 pairs
`ρ₁,ρ₂ ∈ 1..9` and all 502 ordered splittings of `ρ ≤ 9` at `aF` (S2);
the analytic statement covers all ranks.

Combining: paid events partition into climbs on `r₁`, climbs on `r₂`,
climbs on helpers, and centre steps. By Lemma B the first two groups
have rank sums `ρ₁, ρ₂`; by Lemma C their moment contributions are at
least `(ρᵢ/73)^{1−a}` and their excesses at least `p_{ρᵢ}`. Every
remaining paid event has rank `≤ 9 < R`, hence positive excess
(per-mass cost `r^{−a}` is decreasing) and positive moment, so it only
increases all three bills. Scalar mixing cannot help: it changes rows
only at a common frame and never moves a `cur` (Lemma A), so neither
register's telescoping sum is affected by any value-level trick —
forming `X₁+X₂`, swapping values, or routing through helpers/private
arrays still leaves both registers owing their own climbs, and §4
exhibits each failure mode concretely. Equality forces no helper/
centre events and unsplit climbs. ∎

**Corollary (staged/blocked layouts do not evade the bound).** A staged
realization that gathers both arrays into a helper/blocked register,
climbs it once, and scatters back must still deliver the two endpoint
frames on `r₁, r₂`; by Lemma B both registers climb anyway, so staging
is pure addition (cheapest completion `{1:3}` in §4). Waiving the
endpoint frames instead (delivering values in a blocked layout) changes
the lemma's endpoint and runs into the independent value obstruction of
[#2203](https://github.com/CrocSwap/integer-mult-bounds/pull/2203):
one retained array carries one row per address coordinate (capacity
`d`), while the identity on two arbitrary arrays has rank `2d`; one
transported sum delivers the rank-1 broadcast `[[1,1],[1,1]]`, not `I₂`
(§4 witness). Register permutation is likewise not an evasion: the §2
endpoint is ordered, renumbering registers rewrites the remainder of
the word (a hosting/owner change, outside this task's anti-basin and
requiring global repricing), and on the cheapest pair — equal source
frames, equal target frames — it changes nothing.

Two scope boundaries deserve explicit naming, since both look like
evasions. *Entrance promotion* (enlarging a helper's start frame so its
first climb vanishes, the borrowing/promotion mechanism of
[#2226](https://github.com/CrocSwap/integer-mult-bounds/pull/2226) and
the saturated T74 family) changes `aᵢ` itself and pays in helper width
and hosting; the theorem fixes `aᵢ` at the lift cut, and promotion is
excluded by this session's anti-basin with its global bill already
accounted in the predecessor packages — it is not a joint-rank child.
*Global frame refits* (keeping both registers at a join frame and
rewriting every later common frame) change the word and its whole paid
profile; they are new words, priced by their own ceilings, not
realizations of the drop-in lift `J`.

**What the forcing property is, in one line.** *One child = one
register's frame transition = one array = one data family.* The product
frame `(a₁,a₂)` is not a catalogue frame, no retained event transitions
it, and the moment law's normalization (child logical volume `V/W`, one
unpaid coordinate per family) is built on that one-to-one
correspondence. The joint-rank claim is therefore not a lemma *within*
the retained supplier; it is a request for a different supplier.

## 6. Disposition, covered obstructions, and the minimal escape

| Interface for two rank-1 climbs | Verdict | Decisive quantity |
|---|---|---|
| Separate climbs (retained) | Baseline, optimal in retained model | hist `{1:2}`, excess `2p₁` |
| In-place joint child at rank 2, retained language | **Falsified** (§5, all words) | any word ≥ `2p₁ > p₂`; gap `g₂ > 0` certified |
| Staged/blocked, any staging ≥ 1 copy/pair | **Falsified** (§3, §4, §5 Cor.) | budget `0.354` rank-1 units/pair; cheapest staging mass 2 |
| Sum/broadcast sharing, private transfer, dirty-helper pack | **Falsified** on cheapest pair (§4) | frame rejection; `[[1,1],[1,1]] ≠ I₂` |
| New `JOINT_CLIMB` primitive (changed hypothesis) | **Open** — new supplier, §3 prize | needs `S < g₂`; then 90 pairs/call pass `aF` in relaxation |

**Covered obstructions — none reopened.** Theorem S
([#2052](https://github.com/CrocSwap/integer-mult-bounds/pull/2052))
bounds multi-pair *schedules* and pair fusion on shared labels; this
package fuses no pairs and changes no schedule — pair count, stages and
`D` are untouched, as in Track 4B. The centre obstructions
([#2076](https://github.com/CrocSwap/integer-mult-bounds/pull/2076)
zero-storage fanout, [#2048](https://github.com/CrocSwap/integer-mult-bounds/pull/2048)
8-row transcript) concern centre cuts; the centre charge 64 is held
fixed and centre steps appear here only as a billed candidate that
fails. Paired-plane matching
([#2118](https://github.com/CrocSwap/integer-mult-bounds/pull/2118))
and the native payload floor
([#2203](https://github.com/CrocSwap/integer-mult-bounds/pull/2203))
price *descents/copies* under the scalar-total interface; §5's theorem
is the climb analogue via a different mechanism (frame telescoping,
not pairing rank), and §2's remark records that the plane-port shared-
rank invoice is strictly stronger than the sum billing decided here —
it remains conditional on the same new primitive, now with its climb
form excluded in the retained model as well. The P111 copy floor is
bit-side (`a_b` held fixed); the block-COPY stream count of
`muse-ood-block-copy` is the same value-rank obstruction in COPY form,
cited in the Corollary, not repeated. The drop packages
(`e8-first-rank-drop`, `p112-joint-rank5-parent`,
`p112-star-first-cost-drop`, `root-pair-first-drop-seed48`,
`p104-*-drop`) all price when a *single* term's pairing/support rank
first falls under deletions or cuts; none defines or prices a
two-register frame transition, so none decides or is contradicted by
this lemma — their common premise (one term, one stream) is exactly
Lemma A's locality in decoder language.

**Minimal changed hypothesis that escapes §5.** Add one event type and
re-derive its contract; nothing smaller suffices, because Lemma A must
fail for at least one event:

```text
JOINT_CLIMB[(r1,a1,b1),(r2,a2,b2)]:  cur[r1]=a1, cur[r2]=a2, no private live
  -> cur[r1]=b1, cur[r2]=b2, rows unchanged, ONE child of rank rho1+rho2.
```

For this to become a supplier mechanism, in dependency order:
(1) a physical child contract carrying two independent arrays (capacity
`2d`) at relative size `(ρ₁+ρ₂)/73` — i.e. two data families co-hosted
on one recursive row, with the `V/W` normalization, coverage law
(unpaid coordinates per *pair*), halving guard for product ranks, and
moment law re-derived rather than spliced (§3's numbers assume the
splice); (2) a product-frame lattice (catalogue frames pair to
≈10⁶ products; census rank-1 transitions number 1,928, so arbitrary
pairs must be admitted or the word redesigned to align transitions —
Track 4B's common-frame bound of 6 width-16 batches shows the cost of
alignment on this word); (3) chronological co-hosting of the two arrays
at one gap (windows exist for the cheapest pair; global owner
feasibility for 90 pairs/call is unexamined and deliberately outside
this session's anti-basin); (4) precision: a truly diagonal joint child
keeps block-diagonal coefficients, so the prefix bill is unchanged —
this must be proved of the physical child, not assumed; (5) dirty
restoration of *both* arrays by the one call at all sizes; (6) a
bit-side analogue before any κ gain beyond the planning cap
`0.001730427` (the all-paired complex ceilings of §3 already exceed the
bit endpoint). Inherited all-size/compiler, common-label, whole-call
hosting, precision/tape and analytic obligations are untouched.

## 7. Track 4D: the JOINT_CLIMB coverage recount on the §4 fixture

*This section executes the single bounded Next experiment below. §§1–6
(Track 4C) are unchanged; their verdict — no width-2 lift inside the
retained language — stands. The question here is narrower: assuming the
named new primitive `JOINT_CLIMB` of §6, does the coverage recount keep
one unpaid coordinate per family (so §3's spliced prize is the correct
fully charged form), or must the pair be counted as one family (so the
lever is closed even for a new supplier)?*

### 7.0 Verdict

**The recount survives: the paired fragment keeps one unpaid coordinate
per family — two per pair — and §3's prize stands as the correct
conditional price of the new primitive.** On the literal global
template, the two fixture registers are owned by two distinct physical
families in every one of the 144 calls (§7.1), the coverage identity
counts families, calls and advanced coordinates — none of which a
`JOINT_CLIMB` event changes (§7.2) — and the child-level template
constants are scale-invariant, so no lineage term exists to halve
(§7.3). The collapse branch is priced anyway and is not close: charging
the pair as one family (one lost unpaid coordinate per pair per call,
billed most favourably) makes every pair strictly worse by a certified
`+1.374e-04` of relaxation moment per pair against a survive-branch
gain of `−3.26e-07` (§7.4) — so the dichotomy is real and the fixture
evidence decides it on the survive side. Under the survive recount, the
exact conversion needed on *actual* global profiles is **221
zero-staging pairs/call** on the selected profile to pass the planning
target `aF` (196 at the moment-root reading `κ₂₃₇₄`), and **26
pairs/call** on the frontier [#2374](https://github.com/CrocSwap/integer-mult-bounds/pull/2374)
profile to pass `aF` (§7.5). What remains is exactly a physical
contract for a two-row child; §7.6 lists its obligations in dependency
order. No construction is supplied and no covered obstruction is
reopened: the changed hypothesis is still the §6 primitive itself.

```text
Track 4D addendum card
Base/selected/frontier: unchanged (Task card above). New pinned objects (same
  archive): ASSEMBLY complex_profile, global/audit/OWNERS-AND-PROFILE.json,
  global/hosted/GLOBAL-TEMPLATE.json.gz (144 calls, literal owners).
  Frontier global profile H74 from refs/upr/2374 PROFILE.json (sha256 in
  RESULT.json S8), checked by its coverage identity.
Question: on the §4 fixture, write the two-family row layout at the common
  gap, the logical volume W and the coverage identity; decide one unpaid
  coordinate per family vs per pair for JOINT_CLIMB.
Anti-basin: unchanged. No owner/window construction is attempted; literal
  owners are read, not redesigned.
Artifact: this section + verify.py S7/S8 (-> RESULT.json). S1-S5 are
  byte-identical to the Track 4C receipt (checked by diff).
```

### 7.1 Explicit two-family row layout at the common gap (fixture)

Registers 546/560 are helpers (word metadata `R = 480, v = 112, h = 9`,
704 registers; neither is in `ports` or `centers`), start frame 0, final
frame 1 (FULL). Their full climb chains (identical `(phase,a,b,rank)` in
both orientations; event indices below, `RESULT.json` S7):

| register | climb chain (phase: a → b, rank) | sum |
|---|---|---:|
| 546 | A: 0 → 4, 1 (idx 9297); B: 4 → 290, 2; B: 290 → 686, 3; final: 686 → 1, 3 | 9 |
| 560 | A: 0 → 4, 1 (idx 9299); B: 4 → 321, 2; B: 321 → 688, 3; final: 688 → 1, 3 | 9 |

The Phase-A skeleton windows (§4) give common gaps `0..1190`; take the
representative gap **1190**, the position of 546's own climb: 560's climb
moves one event earlier, across only `add L546 += −L561` at frame 4,
which does not touch it. At that gap both registers sit at frame 0 and
the forward rows are exactly the basis arrays `e₅₄₆, e₅₆₀` (§4).

Which physical rows host them there is literal in the pinned hosted
global template (144 calls = 16 replicas × 9 stages). Every call assigns
704 **distinct** physical owners, one per register, under the recorded
hosting rule *one-helper-per-physical-family-per-complete-invocation*
(`max_helpers_per_physical_family_per_call = 1`). For call 0 (replica 0,
stage 0, pair 0, forward):

```text
register 546 -> physical row 1134, owner chart [3,0,0]
register 560 -> physical row 1129, owner chart [3,0,0]
```

and the two physical owners differ in **all 144 calls** (owner charts
coincide in 117 of 144; S7). So at the common gap the fixture is, row by
row: *two distinct physical family rows, each holding one independent
dirty array at frame 0, each owing the identical advance `0 → 4`.* A
`JOINT_CLIMB` on this fixture therefore spans **two rows**. It is not
co-hosting on one row — gathering both arrays onto one row is the staged
layout killed in §§3–5, and no owner change is proposed here.

### 7.2 Coverage identity for the paired fragment

Global accounting (exact, S7): live families `W = 14336 = 16·896`,
calls `N = 144 = 16·9`, physical rows 14,826, and

```text
rank mass = 1,041,408 = 72·W + 64·N,        deficit D = W − 64N = 5,120
per replica: 896 families, 9 stages, D = 320;   per call: w = 896/9, D = 320/9.
```

The global profile decomposes as `144 × local + idle` with idle
`{48:4866, 1:2276, 3:377, 7:7}` (mass 237,024 = 1646·144). In PR1012's
per-family form the identity reads
`8·k_f + 1 + hosted_f + idle_f = 73` — 72 paid advances and exactly one
unpaid coordinate per live family (checked family by family on the T37
payload in `research/t37-restoration-deferral`; here its aggregate
`72W + 64N` form and the profile decomposition are rechecked).

Now credit the fixture fragment. Each separate climb advances one
coordinate on its register's owner row, so the credit vector over family
accounts is `(+1 on F₅₄₆, +1 on F₅₆₀)` with `F₅₄₆ ≠ F₅₆₀` (§7.1;
support size 2, machine-checked). `JOINT_CLIMB` by definition (§6)
delivers the same two advances as one child instance: the credit vector
is unchanged. Consequently, for `n` pairs/call,

```text
W(n) = W,   N(n) = N,   mass(n) = 72W + 64N,   D(n) = D,
unpaid = 1 per family, i.e. 2 per pair
```

(machine-checked as exact identities on the global histogram for
`n ∈ {0,1,90,196,221,1206}`; S7). The reason no recount is forced is
that families are template objects — replica/pair/side/port realised on
physical owner rows — defined before any child histogram exists. The
moment law contains three counts: child *instances* in the numerator,
live *families* `W` in the denominator, and advanced *coordinates* as
mass. Pairing changes only the first. The retained supplier's
child↔family bijection (§5, Lemma A) is a property of its event
language, not of these three counts; the new primitive breaks the
bijection at the event level while keeping all three counts coherent.
In particular `W` does **not** count children, child lineages, or
registers: it counts live families, and the fixture's two families stay
two.

### 7.3 Child-level recount: logical volume

One supplier instance processes `W·m` coordinate slices; a rank-`r`
child's logical volume share is `r/(mW)`. The joint child's share is
`(1+1)/(73·14336)` — the ordinary `2/73` family-units, identical to an
ordinary rank-2 child advancing two coordinates of one family. Inside
the child, the template constants (896 families / 9 stages per
replica-unit, centre 64/call, idle cap `R = 51`) are scale-invariant
supplier constants: sub-family density per unit volume is the same for a
rank-2 block whether its two slices descend from one home family or two.
Aggregate unpaid credit in the subtree is therefore proportional to
volume, and the joint child's aggregate equals that of two rank-1
children. There is no lineage term to halve: the entire gain is the
concavity `(2/73)^{1−a} < 2·(1/73)^{1−a}`, exactly the mechanism by
which an ordinary rank-2 child already beats two rank-1 children inside
one family (the `E`-from-small-children diagnosis). Scope honesty: this
settles the *accounting* — no term in the retained moment model
references the home-family identity of a child's slices. It does not
show that a physical child can embed the full template on a two-row
block; that is obligation (4) in §7.6, and if an embedding instead
forced halved sub-family density, its price is bounded by the collapse
branch next.

### 7.4 The collapse branch, priced (why the decision matters)

Suppose, contrary to §§7.1–7.3, a future supplier proof forced either
collapse billing. Both are dead for every `n ≥ 1`, certified per pair in
relaxation form on the selected word (S8; decimals display only):

- **Merged family** (pair keeps one unpaid coordinate total): the lost
  unpaid coordinate must be paid, i.e. `+1` paid mass per pair per call,
  billed most favourably at ideal rank-`R` shape. In excess form each
  pair then shrinks the budget `B(a) = w − total·c_R/R` by `c_R/R ≈
  0.0137` while saving only `g₂` of spend, for a net
  `Δrelax ≥ +1.374e-04` per pair at both `κ₂₃₇₄` and `aF` — against the
  survive-branch `Δrelax = −3.26e-07`. The penalty is >400× the prize,
  linear in `n`, and already strict at `n = 1` and `n = 90`.
- **Volume-doubled child** (joint child counted once per home slice:
  two rank-2 histogram entries, mass `+2` per pair displacing idle):
  `Δrelax ≥ +1.19e-06` per pair. Also strictly worse than separate
  climbs for every `n`.

So the Next experiment's stop condition was genuinely loaded: *if* the
recount had collapsed, sum-billed pairing would gain nothing even as a
new supplier and the width-2/16 lever would close entirely. The fixture
evidence places the accounting on the survive side; §7.6 keeps the
physical embedding that must honour it as an explicit obligation, so a
future failure there re-enters through this priced branch rather than
through silent splicing.

### 7.5 Fully charged JOINT_CLIMB contract and exact pairs per call

Conditional on the §6 primitive, the complete moment contract is:

```text
JOINT_CLIMB[(r1,a1,b1),(r2,a2,b2)] at a common gap, no private live:
  cur[ri]=ai, rows Xi independent dirty -> cur[ri]=bi, rows Xi, all else restored.
Histogram per pair (rhoi = dim(bi)-dim(ai)):  {rho1:-1, rho2:-1, rho1+rho2:+1}
  (fixture tier: {1:-2, 2:+1}).  Mass, W, N, D invariant (§7.2).
Staging/restoration/precision bill S (excess units/pair) charged on top:
  net gain/pair = g2 - S;  viable only if S < g2  (S/p1 < 0.3536, §3).
  One rank-1 copy (S = p1 = 2.83*g2) already reverses every row below.
Acceptance: (1/W) * sum_r n_r (r/73)^(1-a) < 1 on the completed global
  profile, plus the strict outer assembly. Halving guard: rank 2 <= R=51.
```

Exact zero-staging pairs/call needed (adjacent `n−1` failure certified
in S8). Relaxation rows recap §3; **actual** rows use the real global
histograms (selected: ASSEMBLY profile, `W = 14336`, 144 calls;
frontier: [#2374](https://github.com/CrocSwap/integer-mult-bounds/pull/2374)
profile, `W = 66304`, 666 calls, coverage-checked):

| profile (actual unless noted) | at `κ₂₃₇₄` (moment-root) | at `aF` (planning) | at bit endpoint |
|---|---:|---:|---:|
| Selected, relaxation (§3) | 64 | 90 | 379 |
| **Selected, actual global** | **196** | **221** | 511 |
| **Frontier #2374, actual global** | 0 (its own endpoint) | **26** | 315 |

Reading against the beat-target `0.0016971949509`: from the selected
supplier, **196 pairs/call** pass its moment-root reading and **221**
pass the retained planning reading `aF`, on the actual profile. From
the frontier construction itself, 1 pair/call already lifts its exact
endpoint bracket to `a ≤ 0.001697307671` (n = 0 bracket
`[33943899/20000000000, 1697194951/1000000000000]` contains `κ₂₃₇₄`),
and 26 pairs/call pass `aF`. Converting every local rank-1 climb
(`n = 1206`) gives the selected actual endpoint `a ≤ 0.001819350023`
(relaxation `0.001836572422`, §3) — still κ-capped near `0.0017304` by
the unchanged bit supplier. Necessary-count screen (upper bounds only,
windows/charts not yet imposed): identical-transition pairs admit at
most **387/call** (per phase A 132, B 80, cleanup_tail 16, final 159;
both orientations), which covers 221; zero-frame fixture-type pairs
admit at most **176/call < 196**, so the selected-actual targets cannot
be met from zero-frame pairs alone — non-zero identical transitions or
arbitrary product frames (max 1206) are required; the bit-endpoint rows
(511 selected) exceed even the identical-transition bound and need
arbitrary product frames outright. The frontier word's
own transition census was not extracted; its 26 pairs/call are a price,
not a placement.

### 7.6 Physical obligations for a new supplier (dependency order)

Refining §6(1)–(6) with the recount now fixed. Everything below is
owed by the *new* supplier; none of it is discharged here.

1. **Two-row child instance.** One recursive instance whose addressing
   spans two distinct physical owner rows/families at one gap (§7.1),
   including owners for its internal roles and the row/stock bounds for
   a two-row span. The retained one-helper-per-family hosting rule must
   be honoured or explicitly re-derived — families are not merged.
2. **One completed-child operator across two streams.** The two
   streams' cover-conjugated factors must compose into a single
   completed child (fixture: identical frames `0 → 4`, owner charts
   equal in 117/144 calls and unequal in 27 — even the fixture tier
   needs a chart rule). In general: a product-frame/product-chart
   contract, at the identical-transition tier (≤387 pairs/call) or for
   arbitrary products (1,928 census transitions), or a word redesigned
   to align transitions at its own fully charged price.
3. **Block-diagonal exactness and exit separation.** Both arbitrary
   dirty arrays advanced to `(b₁,b₂)` and returned to their own home
   rows with values and frames exact, no mixing, at all address sizes;
   helpers/private state restored. (Mixing re-enters the
   [#2203](https://github.com/CrocSwap/integer-mult-bounds/pull/2203)
   rank-`2d` payload obstruction.)
4. **Full-template embedding at volume `2/73`.** The child instance
   laid out on the two-slice block with the same template constants and
   sub-family density as an ordinary rank-2 child, product-rank halving
   guard, and the moment law re-derived for two-row instances.
   §§7.2–7.3 show the retained accounting contains no extra term; the
   supplier proof that its physical instance matches that accounting is
   still owed, and failure is priced by §7.4.
5. **Chronological co-liveness at scale.** Common gaps and global owner
   feasibility for ≥221 pairs/call (selected) — §7.5 gives only
   transition-count upper bounds. Deliberately outside this session's
   anti-basin; no placement is claimed.
6. **Precision.** Block-diagonal coefficients must be proved of the
   physical child, keeping the prefix bill inside the selected
   allowance; any scalar mixing inside the child is charged.
7. **Bit-side analogue** before any κ gain beyond the planning cap
   `0.001730427` (§3 ceilings already exceed the bit endpoint).

Inherited all-size/compiler, common-label, whole-call hosting,
precision/tape and analytic obligations are untouched. Covered
obstructions remain covered exactly as in §6: the single changed
hypothesis is still the `JOINT_CLIMB` primitive; §§7.1–7.3 change no
schedule, centre charge, matching, copy floor or coverage law — they
read the retained template literally and show its counts already
accommodate the primitive's invoice.

## Tests run (exact commands and outcomes)

```sh
python3 -B scripts/research_baseline.py
# PASS_RESEARCH_BASELINE_BINDINGS_ONLY (complex binds; multipliers 6.029/5.827)
python3 -B research/complex-local-word-ceiling/verify.py
# PASS_COMPLEX_LOCAL_WORD_CEILING a_ceiling 0.001690054109089
python3 -B research/muse-joint-rank-drop/verify.py --write
python3 -B research/muse-joint-rank-drop/verify.py
python3 -I -O -B research/muse-joint-rank-drop/verify.py
# PASS_MUSE_JOINT_RANK_DROP ratio(aF)<=0.353554231377 min_pairs_sel_aF=90
#   cheapest_pair=[546,560] tamper=8/8 rejected; no_new_kappa (all modes)
# Track 4D rerun (same commands, extended verifier):
# PASS_... tamper=14/14 rejected; no_new_kappa 4D: recount=survives
#   actual_pairs_sel_aF=221 frontier_aF=26; no_new_kappa (all modes)
```

Tamper controls in `verify.py` (real value mutations, each required to
be rejected by a live check): climb rank → 99 in the pinned program
(frame replay), dropping the 560 climb (common-frame replay), flipping
frame 4's basis vector 459 → 458 (catalogue check), scalar coefficient
1 → 2 in the mini word (row endpoint), broadcast matrix claimed as
`I₂`, stored `RESULT.json` ratio mutated to `0.99` (replay comparison;
also run externally once: mutated file fails, restored file passes),
min-pairs-minus-one claimed passing (adjacent relaxation sign), and one
extra rank-1 child claimed not to lower the ceiling. Track 4D adds six
controls on the same terms: merging the fixture owners in call 0
(`560 := 546`, owner-distinctness check), live families `14336 → 14335`
(coverage identity), one extra rank-48 child in the frontier profile
(coverage identity), actual min-pairs-minus-one (221 → 220 at `aF`)
claimed passing, the collapse recount claimed better than separate
climbs, and stored S7 chart count mutated `117 → 144` (replay
comparison; externally mutating stored S8 `221 → 220` was also run
once: fails, restored file passes). Preservation check: the regenerated
`RESULT.json` S1–S5, targets and status are identical to the Track 4C
receipt (field-by-field diff), prior pins unchanged, S6's first eight
entries unchanged. Not run (explicitly): `make frontier1094-verify`
cold replay (no supplier to admit); the retained `hpe_audit_local.py`
full scalar replay (its frame semantics are re-implemented explicitly
here and its row semantics are replayed to the pair cut; the full
704-column endpoint identity is predecessor evidence, not relied on for
the new claims); T74 native/strict chains for paired profiles and the
T74 words' own transition/window census (meaningless without the §6
primitive; frontier actual pricing uses its published global profile
only); global owner-feasibility for paired placements (anti-basin;
§7.5 upper bounds only); any Lean check. Open-PR overlap beyond the
local refs and titles supplied for this session was not refreshed
online.

## Next experiment (single, bounded)

*Executed as Track 4D in §7 above: the recount survives (§7.0), the
contract and exact pair counts are in §7.5, and the successor experiment
is the first Open next question below. Original Track 4C text retained:*

**Product-frame child contract on one plane/climb fixture (≈1
session).** §5 closes the retained language, so do not search it
further. Instead, take the §6 `JOINT_CLIMB` as a *named* new primitive
on the §4 fixture (two basis arrays, frames `0 → 4`) and derive the one
quantity the splice assumes: the child's logical volume. Write the
two-family row layout explicitly (which physical row(s) host `r₁, r₂`
at the common gap, what `W` counts), and check whether the coverage
identity for the paired fragment still leaves one unpaid coordinate
per family or only one per pair — the latter halves `D`'s gain and
re-prices §3 before any engineering. Success: a written contract with
volume, coverage and precision invoices whose fully charged moment
still beats `2p₁` by `> 0` after the recount. Stop/falsify: the recount
shows the pair must be counted as one family (or the child volume is
`2V/W` at rank-2 price), in which case sum-billed pairing gains nothing
even as a new supplier and the width-2/16 lever closes entirely.
Do not attempt word redesign for transition alignment before this
recount exists.

## Open next questions

- **Does the paired fragment keep one unpaid coordinate per family?**
  **Answered yes by Track 4D (§7).** The fixture's two families stay
  two (distinct literal owners in all 144 calls), `W`/mass/`D` are
  invariant under pairing, and the collapse billings that would have
  closed the lever are priced in §7.4. The successor question is
  physical, next.
- **Two-row completed child on the fixture rows (≈1 session; the new
  Next experiment).** Why: §7 fixes the invoice; the remaining unknown
  is whether one completed-child operator can act jointly on the two
  owner rows (call 0: physical 1134/1129, charts `[3,0,0]`/`[3,0,0]`;
  unequal in 27/144 calls) as a block-diagonal advance with clean exit
  separation. First step: write the two-stream factor for the fixture's
  `0 → 4` advance in the retained cover/chart language and check the 27
  unequal-chart calls for an obstruction or a chart rule. Success: a
  named two-row operator with its precision/stock invoice at staging
  `< g₂`. Stop/falsify: a chart/cover invariant forcing per-stream
  children — then `JOINT_CLIMB` needs an even stronger changed
  hypothesis and §7.4 prices the fallback. Blocker: no two-row child
  contract exists in the retained supplier.
- **Pairable-pairs census at the needed scale.** Why: §7.5 needs 221
  pairs/call (selected, actual, `aF`) but only transition-count upper
  bounds exist (identical 387, zero-frame 176); windows, owner charts
  and global feasibility will cut these. First step: count disjoint
  same-phase identical-transition pairs with overlapping legal windows
  (reuse the pinned window primitives), per phase, before any owner
  work. Blocker: if the windowed count falls below 196/221, the
  selected-word route needs arbitrary product frames or word redesign,
  repriced from scratch.
- **Shared-rank vs sum-rank for identical transitions.** Why: the
  cheapest pair shares `(0,4)`, and the plane-port invoice bills shared
  frames once (rank 2/plane, not 4). If a future `JOINT_CLIMB` could
  bill two identical `ρ = 1` lifts at rank 1 (shared) rather than 2
  (sum), the saving per pair grows from `g₂ = 2p₁ − p₂` to
  `2p₁ − p₁ = p₁` — still requiring the §6 primitive, but with staging
  room of exactly `1.00` rank-1 excess units per pair instead of
  `0.354`. First step: state the shared-billing contract for identical
  `(a,b)` and recount how many census pairs share a transition with
  overlapping windows (upper bound first, as in Track 4B §4). Blocker:
  shared billing is a second, stronger changed hypothesis on top of
  `JOINT_CLIMB`; unlike sum billing it is not mass-preserving (two
  advances at volume `1/73`), so §7's survive recount does not cover it
  and its coverage identity must be re-derived on its own terms.
- **Bit-side climb analogue.** Why: every complex-only pairing ceiling
  in §3 is κ-capped by the bit endpoint, and `muse-ood-block-copy`
  found the same one-stream obstruction in COPY form on P111. First
  step: restate Lemma A/B for the bit word's frame language (H1–H5
  checker) and check whether its climbs telescope identically.
  Blocker: the bit supplier's COPY/ERASE ABI prices copies per stream
  under a different contract; the climb statement must be re-derived,
  not transcribed.

## Reproduce

```sh
python3 -B research/muse-joint-rank-drop/verify.py --write   # regenerates RESULT.json
python3 -B research/muse-joint-rank-drop/verify.py           # PASS_MUSE_JOINT_RANK_DROP
python3 -I -O -B research/muse-joint-rank-drop/verify.py     # same, optimized mode
```

Python 3.10+ (run here on 3.13), standard library only, no network.
`verify.py` hash-pins the selected replay archive, its gauge44 members,
`ceiling.py`, `batch.py` and `hpe_audit_local.py`, recomputes the
catalogue geometry, certified thresholds, optimistic ceilings/min-pairs,
the full frame census with per-register telescoping and rows at the
pair cut, and the mini dirty replays, compares the whole receipt with
`RESULT.json`, and rejects eight value-mutating tamper controls. It
reuses the pinned `ceiling.py` engine unchanged and `batch.py`'s
window primitives (`touched/split_phases/is_r1`) pinned; all frame and
row replays are re-implemented explicitly with `require` checks that
survive `-O`. Track 4D additionally pin-records the archive's
`ASSEMBLY.json`, `OWNERS-AND-PROFILE.json` and hosted
`GLOBAL-TEMPLATE.json.gz` members (archive SHA-256 binds their bytes),
recomputes the fixture layout/coverage recount (S7) and actual-profile
pair counts with collapse-branch signs (S8), and rejects six further
controls (fourteen total). The frontier global profile is a cited
constant from `refs/upr/2374` (SHA-256 in S8), admitted only through
its coverage identity, as in Track 4B.

## Credit and disclosure

Predecessor credit is retained and not claimed as new: Douglas Colkitt
(with Claude) for the [#1240](https://github.com/CrocSwap/integer-mult-bounds/pull/1240)
ceiling/levers engine reused pinned here; Sagar Thakrar (PR1012) for
the coverage identity; Jose Manuel (@jmbarrancoml, with Codex) for the
diagonal rank-16 identity ([#1779](https://github.com/CrocSwap/integer-mult-bounds/pull/1779));
Josie Elliston's `diagonal-batch-commutation` (prepared with Claude)
for the dependency-respecting windows whose primitives are reused
pinned; Jeremy Diviney for paired-plane native payload accounting
([#2203](https://github.com/CrocSwap/integer-mult-bounds/pull/2203),
head `c3c85ea8`; building on Philippe Van Velzen's floor and ctoth's
team invoice as credited there), whose "hypothetical primitive acting
jointly on two full arrays" this package prices as the minimal escape;
Cinna Davis for paired-plane rematching
([#2118](https://github.com/CrocSwap/integer-mult-bounds/pull/2118));
themilkman216 (with Claude) for Theorem S
([#2052](https://github.com/CrocSwap/integer-mult-bounds/pull/2052));
the retained local checker lineage (icekylinx / PR514 / PR433, via
`complex-571-cold14-k492b/code/hpe_audit_local.py`) whose semantics §1
restates; Vlado Vojdanovski ([#2322](https://github.com/CrocSwap/integer-mult-bounds/pull/2322))
and Jeremy Kothe ([#2374](https://github.com/CrocSwap/integer-mult-bounds/pull/2374))
for the T74 frontier lineage screened (unreviewed); the drop-package
authors listed in the task card (Chi Zhao, Ross Richardson, Cinna
Davis, woklerx et al. via their packages' notices); prior Meta Muse
packages in `research/muse-*`, in particular `muse-rank16-children`
(whose Next experiment this package executes), `muse-plane-port-interface`
(width-2/W2 framing, `γ+ρ` pair theorem), `muse-ood-block-copy`
(block-COPY stream count) and `muse-ood-coverage-template` /
`muse-ood-template-k5` (lever budgets, hypothesis boundaries).
Selected-construction credit remains in its review.

Track 4D additionally uses the per-family coverage form and deficit
`D = W − 64N` as recorded in `research/t37-restoration-deferral`
(PR1012 lineage, credited above), the literal owner map and async
owners/profile audit inside the pinned selected replay archive
(`global/hosted/GLOBAL-TEMPLATE.json.gz`,
`global/audit/OWNERS-AND-PROFILE.json`; selected-construction lineage),
and Jeremy Kothe's [#2374](https://github.com/CrocSwap/integer-mult-bounds/pull/2374)
global `PROFILE.json` for the frontier actual histogram (unreviewed,
coverage-checked here).

This package was prepared with substantial AI assistance from Meta
Muse (Muse Code, `muse-wonder-full-1.0`): lemma statement, proof,
verify code, census and draft text; the Track 4D continuation (§7,
S7/S8) likewise. Exact arithmetic is standard-library
`Fraction` via the pinned predecessor engine; cited frontier values are
unreviewed and were screened, not admitted; no independent human
review, proof-assistant verification or literature-priority guarantee
is claimed. Apache-2.0, following the repository license.
