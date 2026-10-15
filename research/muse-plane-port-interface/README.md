# Plane-port interface: shared arrays, borrowing and a multi-array child vs the exact break-even

**Scoped falsification and price screen; no new supplier or kappa.** The
selected record (κ = 836330098538459/500000000000000000, #1094, priority
revision 4, base `0fdd7d8`) is unchanged. All κ numbers below are planning
caps `a/(1+a)` from favourable relaxations, not admitted bounds.

**Verdict.** The two-unpaid plane-port screen has exact zero-saving
break-even native copy mass `C < 1792/9` (integer `C ≤ 199`); passing useful
targets needs `C ≈ 152–162` depending on rank shape. Against that bar:
sharing one scalar-total decoder across **two matched planes can never beat
decoding them separately** (pair lower bound 8 = the direct cost, for every
pair of orthonormal planes, any matching), orthogonal-plane groups of any
size cost exactly the direct `4g`, and the natural triple
global-plus-canceller pattern never beats `12` on any of the 27,720 triples
of the pinned matching. Group-partitioned decoders built from singletons,
pairs and orthogonal groups therefore still cost `C ≥ 224`, which fails at
zero saving (`293/292 > 1`). Borrowing/hosting in the style of #2226 cannot
repair this: the zero-saving ratio depends only on `C`. The only candidate
that passes is a genuinely multi-array (width-2) child **priced at the joint
rank 2 per plane** (`C = 112`, ceiling `a ≤ 0.004078546959`), and that invoice
is precisely the unproved width-2 drop lemma already isolated in round 2B —
a changed supplier, not an implementation of the retained one. A global,
non-partitioned fractional decoder mixing three or more non-orthogonal
planes is **not** excluded; §5 states the pair-restriction inequalities it
must satisfy.

## Task card

```text
Scope: track 3B (plane port), continuation of research/muse-ood-block-copy.
Object: selected 112 complex ports, 56 matched planes E_P=<q_i,q_j> (q_i.q_j=0,
  q_i.q_i=1) from paired-plane-port-matching-seed6c563a CERTIFICATE.json,
  labels from the pinned selected replay DATA-PHASES.json.
Changed hypotheses tested (one at a time, named against covered cases):
  (S) scalar totals shared across matched planes (vs #2203 independent blocks);
  (B) second array hosted by borrowing / changed references (#2226, #2271);
  (W) one native child carrying two arrays at join rank (vs one-array tariff).
Not reopened: plain packing/hosting/owner repacking (packing ceiling +0.87%);
  the F2 identity DT^T=B0 as a scalar endpoint (scalar-mask obstruction);
  one-stream block pricing (round 2B) — its changed hypothesis is (W) itself.
Cheapest falsification first: zero-saving break-even, then two-plane geometry.
Artifact: this directory (verify.py, RESULT.json, README.md). Local only;
  nothing committed, pushed or posted.
```

## 1. Exact break-even native copy mass

Plane-port coverage (retained favourable model): `m = 73`, `W = 896`
families per replica, `N = 9` stages, `w = 896/9` per call, unpaid `= 2`,
centre/copy charge `C` per call replacing the selected eight rank-8 centre
children; all other local children unchanged (the "unchanged" bracket of
[plane-port-copy-budgets](../plane-port-copy-budgets/README.md), no data
shrink credited). Relaxation moments are the pinned exact-interval engine
[complex-local-word-ceiling/ceiling.py](../complex-local-word-ceiling/ceiling.py)
(SHA256 in `RESULT.json`), reused unchanged.

At `a = 0` every child costs `r/m`, so the moment is shape-independent:
`relax(0) = (71·896 + 9C)/(73·896)`. Hence

- `C = 199`: `65407/65408 < 1` — the largest passing integer mass;
- `C = 200`: `8177/8176 > 1`; `C = 224`: `293/292 > 1`, deficit `−224/9` per
  call (#2203's screen, recomputed).

Useful targets are much stricter. Largest certified charge `C = r·k`
(`k` copies of rank `r`; `k+1` certified failing), exact in `RESULT.json`:

| copy rank r | selected `a` | bit endpoint `a` | #2226 ceiling `a` | κ +10% `a` |
|---:|---:|---:|---:|---:|
| 1 | 162 | 161 | 161 | 159 |
| 2 | 162 | 160 | 160 | 158 |
| 7 | 161 | 161 | 161 | 154 |
| 8 | 160 | 160 | 160 | 152 |
| 9 | 162 | 162 | 153 | 153 |

Targets: selected `a = κ/(1−κ) ≈ 0.001675462677`; bit endpoint
`≈ 0.001733427040` (round-1 pin); #2226 complex ceiling upper end
`0.001754331546941`; κ+10% `≈ 0.001843317786`. Selected and +10% rows
independently reproduce plane-port-copy-budgets' charges (162/162/161/160
and 159/158/154/152); the bit-endpoint and #2226 columns and rank-9 shape
are new. A **pass is a necessary relaxation condition, not a supplier**.

Candidate ceilings under the same splicing (grid 10⁻¹² brackets in
`RESULT.json`; first two rows reproduce PR2126's `4078546959/10¹²` and
#2118's `2432366627/500000000000` exactly):

| profile spliced for centre | C | ceiling `a_hi` | status |
|---|---:|---:|---|
| `{2:112}` direct native (#2203) | 224 | fails at `a=0` | retained tariff |
| `{2:56}` identity-fit invoice (#2126) | 112 | 0.004078546959 | conditional on (W) |
| `{2:56}` on #2226 local profile | 112 | 0.004231172584 | conditional on (W)+#2226 |
| `{7:5,8:2,9:5}` (#2118 F2 rematching) | 96 | 0.004864733254 | not a scalar decoder |

## 2. The decoder model being priced (scope)

Retained #2203's scalar-total (one-array) interface: a decoder is a scalar
fitting matrix `K = Σ_t u_t v_tᵀ` over ℚ (coefficients unrestricted;
integrality is **not** assumed), with `K_ii = 1` and `K_xy = 0` whenever
`x ≠ y` lie in planes that are not orthogonal, including two ports of the
same plane (mask-obstruction endpoint conditions; #2126's `K = I₁₁₂` is the
special case with all free entries zero). For total `t` let its reader/source
*plane masks* be the planes where the 2-vector blocks `u_{tP}`, `v_{tP}` are
nonzero, with spans `S_t = Σ_{reader} E_P`, `T_t = Σ_{source} E_P ⊆ 𝔽₂⁹`.
The charge is the complete-plane-span pairing rank
`c_t = rank(S_t × T_t)` under the 𝔽₂ dot form, and `C = Σ_t c_t`.
This is #2203's tariff ("even a single source's plane pairing already has
rank two"), **not** the B14 singleton-support tariff behind the 112/96
invoices. A *group-partitioned* decoder partitions the 56 planes into groups
and every total's masks lie inside one group.

## 3. The plane-pair invariant `γ + ρ ≥ 4`

For two distinct orthonormal planes `E, F` let
`γ = rank((E+F) × (E+F))` and `ρ = rank(E × F)`.

**Lemma.** `γ + ρ ≥ 4`. If `ρ = 0` then `E ∩ F = 0` and `γ = 4`.

*Proof.* `γ ≥ 2` (the sub-Gram on `E×E` is `I₂`), so `ρ = 2` is done. If
`ρ = 0`, any `0 ≠ z ∈ E ∩ F` would satisfy `z·E = 0`, contradicting `E`
nondegenerate; hence `E+F = E ⊕ F` with Gram `diag(I₂, I₂)`, `γ = 4`.
Let `ρ = 1` and `s = dim(E+F) ∈ {3, 4}`.

- `s = 4`: in orthonormal label bases the Gram of `E+F` is
  `[[I, M], [Mᵀ, I]]` with `rank M = ρ = 1`. Adding `Mᵀ`×(top block rows)
  to the bottom over 𝔽₂ gives `γ = 2 + rank(I + MᵀM)`. Now
  `rank(MᵀM) ≤ 1 < 2`, so `I + MᵀM ≠ 0`, its rank is ≥ 1, and `γ ≥ 3`.
- `s = 3`: intersection is a line `⟨z⟩`. If `z·z = 0`, picking
  `a ∈ E∖⟨z⟩, b ∈ F∖⟨z⟩` (norm 1, pairing 1 with `z`) gives `E×F` matrix
  `[[0,1],[1,a·b]]` of determinant 1, i.e. `ρ = 2` — excluded. If
  `z·z = 1`, then `z` is one member of an orthonormal basis of each plane;
  write the other members `a, b` and `t = a·b`. The `E×F` matrix is
  `diag(1, t)`, so `ρ = 1 + t`; the Gram on `(z, a, b)` is
  `diag(1, [[1,t],[t,1]])`, so `γ = 3` if `t = 0` and `γ = 2` if `t = 1`.
  Either way `γ + ρ = 4`; in particular `ρ = 1 ⟹ γ = 3`. ∎

`verify.py` machine-checks both Gram computations (all 16 𝔽₂ matrices `M`;
both `s = 3` cases) and the full census of the pinned matching:

| (γ, ρ) | dim(E∩F) | pairs of 1540 |
|---|---:|---:|
| (4, 0) orthogonal | 0 | 109 |
| (2, 2) | 0 / 1 | 124 / 20 |
| (3, 1) | 0 | 304 |
| (4, 1) | 0 | 575 |
| (4, 2) | 0 | 408 |

There is **no** orthogonal-yet-intersecting pair and no `(γ, ρ)` with
`γ + ρ < 4` — and by the lemma there cannot be one under any rematching
(#2118's included), since only orthonormality of the two planes is used.

## 4. Sharing across two matched planes never pays

**Theorem (pair group).** In a group-partitioned decoder of §2, a group of
two planes costs at least 8 — the direct cost of #2203 per plane (2 totals
× charge 2) — for every pair of orthonormal planes. A singleton group
costs at least 4.

*Proof.* Discard void totals (`u` or `v` zero). For plane `P` in the group,
`Σ_{t: u_{tP},v_{tP}≠0} u_{tP}v_{tP}ᵀ = K_PP = I₂`, so at least 2 totals are
*P-active*; write `a, b ≥ 2` for the two active counts, `m` for totals
active on both, `x` for contributing totals active on neither. Charges:

- P-active only: `E_P ⊆ S_t ∩ T_t`, and the Gram on the label basis is an
  `I₂` submatrix, so `c_t ≥ 2`;
- both-active: both masks are exactly `{P, Q}`, so `S_t = T_t = E_P + E_Q`
  and `c_t = γ`;
- neither: the masks must be `({P},{Q})` or `({Q},{P})` (any mask `{P,Q}` on
  one side forces activity on the other plane), so `c_t = ρ`.

Hence group cost `≥ 2(a−m) + 2(b−m) + γm + ρx`. If the planes are not
orthogonal, every cross entry of `K` on the four ports must vanish, the
principal block is `I₄`, and rank forces `a + b − m + x ≥ 4`. At fixed `m`
the bound is minimised at `a = b = max(2, m)` and minimal feasible `x`,
giving `m = 0: 8`; `m = 1: 4 + γ + ρ ≥ 8`; `m = 2: 2γ + 2ρ ≥ 8`;
`m = 3: 3γ + ρ = 2γ + (γ+ρ) ≥ 8`; `m ≥ 4: γm ≥ 8` — all by the lemma
(`γ ≥ 2`, `γ + ρ ≥ 4`, `ρ ≥ 1`). If orthogonal, cross entries are free but
`γ = 4`, and the same reduction gives `8` (attained by two shared totals of
charge 4). ∎

Consequently any group-partitioned decoder with all groups of size ≤ 2 has
`C ≥ 28·8 = 224`. This strictly extends #2203's independent-block floor to
pair-shared scalar totals with arbitrary rational coefficients and arbitrary
cross-cancellation inside the pair; it does not use Van Velzen's cited
2-integral hypothesis, and its scope (partitioned pairs) is correspondingly
narrower than his claimed one-total floor, which is not reproved here.

## 5. Orthogonal groups, and what survives for non-partitioned decoders

**Orthogonal groups.** If planes are pairwise orthogonal, their sum is
direct (a relation `Σx_P = 0` paired against `E_Q` kills each `x_Q` by
nondegeneracy) and nondegenerate, so `γ(D) = 2|D|` for every subset `D`.
A total active on `D` within such a group has `c_t ≥ γ(D) = 2|D|`
(monotonicity: `Σ_D E_P ⊆ S_t, T_t`), hence group cost
`≥ Σ_t 2|D_t| = 2·(active incidences) ≥ 2·2g = 4g`. Two group-wide totals
of charge `2g` attain `4g` (cross entries are free): sharing is exactly
break-even, in larger-rank shape. On the pinned matching there are 109
orthogonal pairs, 24 orthogonal triples and **no orthogonal quadruples**
(`verify.py`), so this case is small but completely settled. Partitions
into singletons/pairs/orthogonal groups all give `C ≥ 224`.

**Restriction inequalities (any decoder of §2, partitioned or not).**
Restricting a global factorisation to the ports of one pair `{P, Q}` gives
a factorisation of the principal block to which §4's counting applies to the
*restricted charges*
`c_t^{pair} = rank(Σ_{reader∩pair} × Σ_{source∩pair}) ≤ c_t`. Therefore
every decoder satisfies `Σ_t c_t^{pair} ≥ 8` for all 1,540 pairs, and
`Σ_t c_t^{G} ≥ 4|G|` for every orthogonal clique `G`. These do **not** sum
to a global `C ≥ 224`: one widespread total has `c_t ≤ 9` (subspaces of
𝔽₂⁹) yet contributes restricted charge to many pairs, so pair floors
double-count it. Closing that gap is exactly where a global argument
(integrality, or new inequalities) is still missing.

**Triple pattern test (construction, not a lower bound).** The natural
shared construction for three planes — two group-wide totals
(`u = v = Σ_P e_{P,s}`) delivering every diagonal block, plus, per source
plane, two cancellers killing its two non-orthogonal cross blocks at once —
is exact over ℚ (`verify.py` builds it for an orthogonal and a
non-orthogonal triple and checks every 2×2 block). Its fully charged cost
is `2γ_G + Σ_P 2·rank(E_P × Σ_{nonorth. others})`. Over all 27,720 triples
of the pinned matching its cost histogram is
`{12:24, 14:128, 16:542, 18:2767, 20:5847, 22:10945, 24:7467}`: the minimum
is 12, attained exactly by the 24 orthogonal triples. So this pattern
never beats 4 per plane; other triple factorisations are not excluded.

## 6. Borrowing the second array (#2226 / #2271 style) cannot move `C`

`relax(0) = (71w + C)/(73w)` contains no local-profile shape at all (§1):
any mechanism that changes only hosting, storage ownership, or non-copy
local mass leaves the zero-saving screen untouched. `verify.py` certifies
the spliced #2226 local profile
`{1:2382,2:445,3:406,4:128,5:42}` + `{2:112}` at `C = 224` still **fails**
at `a = 0`, exactly as the selected profile does. Mechanistically, #2203's
block word already reuses one private array at peak; replacing the owned
zero array by a borrowed dirty register does not change the transport that
carries the copy: each of the two arbitrary source arrays must still descend
`E → 0`, a rank-2 pairing, individually. Descending their sum once delivers
the rank-1 broadcast matrix `[[1,1],[1,1]]`, not `I₂` (explicit control in
`verify.py`, as in #2203), and touring one borrowed array through both
sources (#2271's mechanism, which tours *same-frame* parity masks by ADDs)
is two sequential descents here, because plane drops are frame transports
charged by rank, not same-frame additions. An anticipatory reference change
in #2226's sense would have to change a source's *entrance frame*; the
two-unpaid credit is tied to entering at the plane `E`, so any such change
must be re-priced inside the coverage law itself (see obligations), and is
not a hosting repair of the present contract.

## 7. The multi-array candidate: exact conditional price

Define **W2**: a native child that descends *two* arrays jointly through
`E → 0` and is invoiced at the joint pairing rank 2 per plane (56 children,
`{2:56}`, `C = 112`). Under that assumed invoice, §1 gives ceiling
`a ∈ [2039273479/500000000000, 4078546959/1000000000000]`, planning cap
`κ ≤ 0.004061979983` on the complex side alone. This is a *relabelled
assumption, not a construction*: per-array pricing of the same physical
descents returns `C = 224`, and the gap between the two invoices is exactly
the width-2 drop lemma (round 2B, open question 1: a child operator carrying
two independent streams per operand, priced by join rank, with its recursive
width/role invoice derived — note the `(r/m)^{1−a}` moment model itself
presumes one data family per child, so even the ceiling above is conditional
on that splicing convention). Even granted W2, the planning κ remains capped
near `0.0017304` by the unchanged bit supplier until a bit-side plane/W2
analogue exists; round 2B found the identical missing lemma on the bit side
(per-stream block total 73 vs 63, union price 40 illegal).

## Candidate scoreboard

| candidate | fully charged `C` | two-unpaid screen | verdict |
|---|---:|---|---|
| Direct native, independent blocks (#2203) | 224 | fails at `a=0` | retained baseline |
| Shared totals, pair groups (§4) | ≥ 224 | fails | falsified for saving |
| Shared totals, orthogonal groups (§5) | = 224 | fails | exact break-even |
| Triple global+canceller pattern (§5) | ≥ 12 per triple | — | never beats direct |
| Borrowed/hosted second array (§6) | 224 | fails at `a=0` | cannot move `C` |
| Global fractional, ≥3 mixed planes | unknown | — | open; pair inequalities apply |
| W2 multi-array at join price (§7) | 112 (assumed) | passes to 0.004079 | conditional on drop lemma |

## Remaining conditional obligations (nothing here is admitted)

For *any* future positive plane-port claim, in dependency order: (1) a
decoder of §2 with proved `C ≤ 199` (to pass zero) and in practice
`C ≤ 152–162` by shape (to pass the targets of §1) — outside the falsified
classes this means a genuinely global fractional factorisation or (W2);
(2) for (W2), the width-2 drop lemma with child operator, two-slot physical
workspace, recursive width/precision invoice, and a re-derived moment law;
(3) native lowering of every total (frame transports, chronological owners,
dirty restoration, application multiplicity across hosted families);
(4) a bit-side plane-port (or W2) decoder on the P111 labels with its own
fully charged invoice — complex-only gains stay planning-capped by the bit
endpoint; (5) the exact moment `(1/W) Σ n_r (r/m)^{1−a} < 1` of the
completed word and the strict outer assembly, with all inherited
all-size/compiler, hosting, precision/tape and analytic obligations of the
selected record untouched by this package.

## Reproduction

```sh
python3 -I -O -B research/muse-plane-port-interface/verify.py          # replay vs RESULT.json
python3 -I -O -B research/muse-plane-port-interface/verify.py --write  # regenerate RESULT.json
```

Expected: `PASS_MUSE_PLANE_PORT_INTERFACE breakeven_C<=199
C224_ratio=293/292 pairLB=8 orthLB=4g triple_pattern_min=12 tamper=6/6
rejected (...); no_new_kappa` (run here on CPython 3.13.16, standard
library only; both normal and `-I -O` modes pass). The verifier hash-pins
the selected replay archive, its `DATA-PHASES.json` payload and
`ceiling.py` before use (hashes in `RESULT.json`), recomputes the
1,540-pair census and pair lower bound by brute force *and* by the §4
minimising-witness formula (they must agree), prices the triple pattern
over all 27,720 triples, recomputes every budget with certified
`k` passes / `k+1` fails, and compares the whole receipt with
`RESULT.json`. Six tamper controls mutate a consumed value and must be
rejected: a flipped label bit (plane validation), a real pair's `ρ` mutated
2→1 (census/pair-LB equality), the stored pair bound mutated 8→4 (replay
comparison), budget+1 copies (moment verdict), a broadcast block claimed as
identity, and a mutated `RESULT.json` zero ratio. Externally mutating
`RESULT.json` (`pair_lb_min` 8→7) was also run once and fails with
`RESULT.json replay comparison failed`; restoring it passes again. No
predecessor executable is imported except the pinned ceiling engine,
reused unchanged; predecessor receipts are cross-checked as constants, not
trusted as oracles for the new claims (the pair theorem, census and triple
pattern are recomputed from the pinned labels). This scoped package has no
registered task metadata, so the registered-package runner was not run; no
full repository suite, cold replay (`make frontier1094-verify`), native
build or Lean check is claimed.

## Overlap and provenance

Predecessors read at exact heads: #2118 `5d324bba`
(`paired-plane-local-swap-seed9c65a5`, F2 invoice 126→96; its ceiling bracket
is reproduced in §1 and labelled non-scalar), #2126 `06be7229`
(`paired-plane-identity-fit-seed21ef98`, identity-fit invoice 112),
#2203 `c3c85ea8` (`paired-plane-native-payload`, native mass 224),
#2226 `dacaf3d8` (`anticipatory-dirty-borrowing`, profile used in §6),
#2271 `95fd4395` (borrowed-source Gray tour); on main:
`paired-plane-port-matching-seed6c563a` (matching/labels),
`paired-plane-scalar-mask-obstruction` (endpoint mask), and
`plane-port-copy-budgets` (break-even cross-checks). Prior Muse rounds
read first: `muse-ood-coverage-template`, `muse-ood-template-k5`,
`muse-ood-bit-wall`, `muse-ood-block-copy` (round 2B, whose width-2 drop
lemma is §7's missing implication). `scripts/find_overlap.py --offline`
(open-PR/discussion coverage unavailable offline; no snapshot) returns only
the expected local plane packages above; open heads #2028–#2273 were checked
directly via local refs/titles. No read package was found that prices
pair-shared scalar totals or proves a `γ+ρ` invariant; absence in offline
search is not a novelty certificate, and live overlap must be rechecked
before any submission.

Credit retained: Cinna Davis (PR1825 matching lineage, #2126 identity fit,
#2226 dirty borrowing, #2271 Gray tour); #2118's authors for the two-edge
rematching; Jeremy Diviney with Codex (#2203 native invoice), ctoth's team
(plane-port contract, Discussion 1587) and Philippe Van Velzen (one-total /
2-integral floor, cited not reproved); the mask-obstruction authors for
adamgall; Douglas Colkitt (ceiling engine, with Claude); the
plane-port-copy-budgets authors (Claude Code for Josie Elliston); the
selected PR1094 lineage for labels and word. Apache-2.0.

Prepared with substantial AI assistance from Meta Muse (Muse Code,
`muse-wonder-full-1.0`): lemma/theorem derivation, exact computation,
verification code and draft text. No independent human review or
proof-assistant verification is claimed.

## Open next questions

1. **Global fractional decoder vs the pair-restriction inequalities.**
   Does any factorisation mixing ≥3 non-orthogonal planes achieve
   `C < 224` (ideally `≤ 160`)? First step: formulate the mask-count ILP/LP
   for one triple group with the 49 mask types, exact charges
   `rank(Σ_S × Σ_T)`, active-count, pair-rank and §5 pair-charge
   constraints, starting from a triple whose §5 pattern cost is 14; a
   fractional optimum below 12 would point at a candidate, a dual
   certificate at 12 would close triples. Blocker: rank/count
   constraints alone are weak — cross-block cancellation structure must be
   encoded, and no exact rational fitting factorisation is known.
2. **The width-2 drop lemma (W2).** Write the two-array child operator on
   one plane block with arbitrary dirty arrays and derive its recursive
   width, workspace and precision invoice from the supplier's own rules.
   First step: a four-array symbolic fixture in the style of #2203's
   block program where the joint descent is a *named* new primitive with
   its cost rule stated, then check which coverage identity it induces.
   Blocker: in the retained model one child carries one array, so the
   lemma is a new supplier mechanism, not a lemma about the old one.
3. **Entrance-frame borrowing priced in the coverage law.** If an
   anticipatory reference change (#2226) let the second array of a plane
   enter at a cheaper frame with frame-zero compensation, what is the
   induced hybrid coverage law (mixed unpaid credits) and its break-even?
   First step: derive the per-family unpaid credit as a function of
   entrance frame for one matched pair and re-run §1 with that law.
   Blocker: plane sources are arbitrary data, not frame-zero helpers, so
   compensability must be proved, not assumed.
4. **Rematching for group structure, not F2 invoice.** §3–§4 are
   matching-independent, so rematching cannot help pairs; can a matching
   maximise orthogonal triples or produce a triple whose pattern cost
   drops below 12 under a smarter-than-§5 pattern? First step: recompute
   the orthogonal-clique and pattern censuses under #2118's matching
   (`5d324bba`) with `verify.py`'s geometry code. Blocker: orthogonal
   quadruples do not exist in the pinned matching and the pair invariant
   caps all pair-level gains regardless.
