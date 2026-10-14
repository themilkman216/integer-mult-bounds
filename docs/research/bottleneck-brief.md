# The current bottleneck, in concrete terms

Start with this one-page map, then read only the definitions needed for your
chosen experiment. The [glossary](research-glossary.md) explains the vocabulary.

From the repo root, run the cheap positive control:

```sh
python3 -B scripts/research_baseline.py
```

It checks the selected source bindings and prints both primitive budgets, the
binding side, the review and the full-replay command. This is source-bound
orientation and arithmetic, **not** a full circuit replay. Follow
[selected-result.json](../../certificates/selected-result.json) if the values
below become historical.

At the revision-4 assessment on 2026-10-14, the reviewed conditional saving is
κ = 0.001672660197076918. The complex primitive supports about 0.00167546 and
the bit primitive about 0.00173343: the complex side binds. Under the retained
limiting conversion `κ = a/(1+a)`, κ > .01 needs both effective primitive budgets
above approximately `1/99`, with strict margins and all transfer obligations.
This describes the current construction, not a lower bound for multiplication.

**Revision 3 update (scoped arithmetic replayed for #1240/#1264).** On the binding complex side, packing within any
screened paid local profile and the stated model is capped within about 0.9% of the record. The 64-per-call centre path uses about
64% of the raw deficit, and the effective child rank is about 3.9. See the lever budgets in
[the packing ceiling](../../research/complex-local-word-ceiling/README.md) and the
[priority log](research-priority-log.md).

## What to work on now

The [review through #2027](community-efficient1000-review.md) leaves the selected
κ unchanged. Prioritize one missing interface with a working local predecessor:

- **P104 completion:** [#1991's native channel](../../research/p104-native-channel/README.md)
  is checked. Design and price the missing `I-G/2` correction at a cut where
  the required frames remain available. The channel alone is not a supplier.
- **Joint-query controller:** [#1969's local words](../../research/joint-query/README.md)
  are checked, but the fixed-first-pair selected-only controller has an explicit
  lost-query witness. Test one changed first pair or paid extra observation
  against that witness before designing a full schedule.
- **Selected proof obligation:** [#1990's stock audit](../../research/selected-bootstrap-stock-audit/README.md)
  leaves the actual selected reserve coefficient unknown. Derive one source-bound
  stage envelope rather than recomputing the already checked headrooms.

The new fixed-word frame bounds (#1995/#2013), Eisenstein additive pairing
bound (#2017), and bounded register census (#1974) narrow particular search
classes. Change a named premise before revisiting them. They do not exclude new
words, different physical pricing or every register model.

The task catalogue keeps other construction and audit routes active. These
three tasks are concrete leads, not evidence that a breakthrough is likely.
A partial identity must still pay for correction, dirty restoration, hosting,
address operations and recursion. Stop when even a favorable complete budget
misses the declared target; preserve the useful obstruction or handoff.

## What a successful change must affect

The construction recursively replaces work of width `m` with children of ranks
`r`. A child histogram records how many calls have each rank. At candidate
saving `a`, its main bill is

`Σ n_r (r/m)^(1-a) / W`,

plus the additional charges required by its contract. The complete bill must be
strictly below one. Fewer scalar additions can leave the entire histogram
unchanged. Such an improvement may help execution or precision without improving κ.

There are three central opportunities:

| Change | Why it might help | First useful evidence |
|---|---|---|
| Decoder or helper inventory | Save more rank or incur fewer/smaller recursive calls | Exact small decoding identity plus a favorable complete helper/frame budget |
| Boundary between calls | Remove a restoration or conversion the next call repeats | Two explicit entry/exit contracts and actual eliminated work |
| Supplier interface lemma | Admit a promising word excluded by today's contract | One exact replacement implication, including dirty inputs and its implementation cost |

For example, [the helper-star package](../../research/r439-bsection-stars-seed01/README.md)
reduces scalar additions but keeps its paid profile and carries an H2/K interface
gap. A useful next question is whether one changed helper operation has a valid
replacement interface. Another addition-count reduction alone does not answer it.

The historical 71-record heterogeneous-owner catalogue excludes the selected k8
provider. The [source-bound applicability receipt](../../research/selected-k8-catalogue-scope/README.md)
follows the selected manifest to its exact inventory/profile and records the
seven-slot change from R480; shared rank mass does not establish catalogue membership.

## Your first session need not solve the whole construction

Take the card's known-working first command, inspect its named quantity, and run
one bounded experiment against the stated premise. A counterexample to a proposed
replacement, a favorable fully charged relaxation, or a precise handoff on the
missing lemma can advance the central question.

If you switch to a self-contained side problem, label the scope change and explain
the connection. Useful side work is welcome; it should not be counted as a
mechanism breakthrough. If nothing new is established, a discussion handoff is a
valid outcome—there is no requirement to manufacture a PR.

The [task catalogue](agent-task-catalog.json) supplies concrete first steps and
scope-change triggers. All-size/compiler, realization, hosting, precision/tape,
analytic and bit-interface conditions remain inherited; this project is not a
complete formal verification of integer multiplication.
