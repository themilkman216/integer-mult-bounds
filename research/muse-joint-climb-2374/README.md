# One JOINT_CLIMB pair per call on #2374 (Track 5A): fixture pair found; two-row child exact but volume-priced at separate cost — spliced gain falsified

**Scoped falsification and precise handoff. No construction, no new
supplier, no new κ.** The selected record
(κ = `836330098538459/500000000000000000`, #1094) is unchanged. The
beat-target is the unreviewed open leader #2374 (Jeremy Kothe, exact
owner fill on #2322's words by Vlado Vojdanovski) at conditional
κ = `0.0016971949509...`, checked out here at its head
`5449da65da12bdfd94675dccc38731eaa91e93b6` (package
`research/gmx-t74-borrow43-handoff`).

## Verdict in one paragraph

*(Checkpoint draft — numbers are filled in as the checks below complete.)*
Track 4D (`research/muse-joint-rank-drop` §7) left one route standing:
a new two-row `JOINT_CLIMB` primitive billing two rank-1 climbs on two
distinct family rows as one rank-2 child; under that splice one pair
per call on #2374's profile lifts the moment endpoint to
`0.001697307671`. This package executes the next step on #2374's own
T74 words. (a) A best fixture pair is identified by exact census (§2).
(b) The two-row instance and completed-child operator for that pair are
specified and are block-diagonally exact (§3) — but the crux price test
fails: in the retained recurrence every child operates on exactly
`1/W` of its parent's logical volume (one complete role stream), so a
child spanning two streams carries volume weight `2/W`, not `1/W`.
Its cheapest correct price is therefore exactly the two separate
climbs (shared width), and at sum width it is strictly worse. The
spliced endpoint gain is an artefact of §7.3's slice-share accounting,
which counts advanced (family, axis) slices but omits the stream-volume
weight that the `(1/W)` factor in the moment represents. An ordinary
rank-2 child beats two rank-1 climbs only when both slots lie in one
stream, where one volume serves both axes. (c) is therefore not
reached: no #2374 pipeline rebuild is warranted, and the remaining
obligations are restated as the stronger hypothesis a future supplier
would have to change (§5).

Out-of-distribution session (Meta Muse, `muse-wonder-full-1.0`; see
*Credit and disclosure*). Local-only package for maintainer review:
nothing was committed, pushed or posted.

## Task card

```text
Task ID / scope: muse-joint-climb-2374 (Track 5A: realize ONE JOINT_CLIMB
  pair per call on the #2374 word)
Base: main 0fdd7d8 (priority revision 4); selected #1094
  kappa 836330098538459/500000000000000000.
  Frontier (unreviewed): #2374 5449da65d (this checkout), #2322 002304ef0,
  #2363 d815dbe37. Open-leaderboard titles checked in the session titles
  file (#2374/#2363/#2349/#2322/#2312/#2269 T74 line; no JOINT_CLIMB work).
Predecessors (read in full where stated): research/muse-joint-rank-drop
  (§§3,4,6,7; Track 4C retained-model impossibility + Track 4D recount),
  research/muse-rank16-children (Track 4B), research/muse-plane-port-interface
  (W2). The muse-ood-* packages named in the task are not present in this
  checkout (only the three muse-* directories above); their lever budgets
  are used as recorded in those successors.
Concrete objects: #2374 T74 local words
  new/borrow/words/BORROW-WORD-43base.json.gz and ...43extra.json.gz
  (v=112, h=9, R=480 registers 704, 46 removed helpers, 434 live helpers,
  local profile {1:2335,2:512,3:426,4:120,5:38,8:8} per call, 666 calls,
  W=66304, global PROFILE.json); literal owners OWNERS.json.gz
  (289044 = 666x434 helper rows) with chart key (port,child,offset,width)
  per code/audit_allcold.py / independent_core.py.
Questions: (a) best candidate pair per call (identical transition, both
  zero-staging, distinct family rows, common gap, equal owner charts in
  all calls if possible); (b) two-row child instance (obligation 1),
  single completed-child operator (2), block-diagonal exactness/exit
  separation (3) by exact replay on arbitrary dirty inputs, including
  whether a rank-2 instance of the supplier's own recursive problem can
  host a block-diagonal pair of rank-1 subproblems at the same cost;
  (c) embedding at volume 2/73 (4) and precision (6); rebuild only if
  all fixture steps pass.
Changed hypothesis (named before any covered case is touched): exactly
  the JOINT_CLIMB primitive of muse-joint-rank-drop §6 — one event
  transitioning two registers on two family rows, billed as one child.
  No packing/hosting/owner/dispatch/borrowing work is done. Covered
  obstructions #2052 (schedules), #2076/#2048 (centre), #2203/#2118
  (descents/copies), p111 copy floor (bit side) are not reopened; §4
  states the relation of the volume obstruction found here to each.
Method: cheapest falsification first — exact climb/window/chart census,
  then the recursive-price crux, then embedding only on success.
Artifact: this directory (verify.py -> RESULT.json).
```

## 1. The retained recursive price (what a child costs, and why)

*(To be completed with pinned quotations: notes/batched-bit-rows.tex,
notes/batched-complex-rows.tex, notes/finite-alphabet-transfer.tex,
notes/copied-centers-lemma.tex, notes/general-clifford-frames.tex.)*

## 2. (a) Best candidate pair on #2374's T74 words

*(Census in progress.)*

## 3. (b) Two-row instance, completed-child operator, exactness — and the crux

*(In progress.)*

## 4. Disposition and covered obstructions

*(In progress.)*

## 5. What a future supplier would still owe

*(In progress.)*

## Tests run (exact commands and outcomes)

*(In progress.)*

## Open next questions

*(In progress.)*

## Reproduce

*(In progress.)*

## Credit and disclosure

*(In progress.)*
