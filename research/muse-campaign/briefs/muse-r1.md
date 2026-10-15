You are the out-of-distribution research contributor on this repository (integer-mult-bounds: conditional T(n)=O(n (log n)^{1-kappa}); current selected kappa = 0.001661960547713947 from upstream PR #942, see README.md, docs/research/current-status.md, certificates/selected-result.json, research/community-frontier942-audit/).

BUSINESS ASK: find a credible edge that increases kappa beyond the #942 selected value.

ROUND 1 TASKS
1. Read the upstream PRs on github.com/CrocSwap/integer-mult-bounds (open and recently closed, especially #890, #942 and anything after #942), plus docs/research/pr-ledger.md and docs/research/community-batch952-review.md. Summarize which mechanism each PR used and which lever moved kappa.
2. Read research/experiment-log/README.md and its negative-search records BEFORE proposing anything. Our process: never repeat a logged experiment without naming the changed assumption/input/neighborhood; a timeout is not infeasibility; a losing finite search is not a global impossibility.
3. ANTI-BASIN RULE: the community has spent many rounds on U8 owner packing / replica hosting / retiming / kernel donor search. Treat that region as a known basin. Produce at least 8 candidate edges spread over at least 4 genuinely different mechanism families (e.g. the analytic/recurrence layer, parameter-recipe hypotheses, complex-side primitive, bit-side primitive, slack assembly inequalities, outer recipe, a different algebraic structure). At most 2 candidates may sit inside the known basin. For each: mechanism, why it is not already in the experiment log, the specific inequality/parameter it moves, an estimated kappa delta with reasoning, and the cheapest falsification test.
4. Run the cheapest falsification test for the top 2-3 candidates (read-only use of existing scripts/certificates; use the exact rational assembly in research/community-frontier942-audit/ASSEMBLY.json to find which constraints are tight/slack and kappa's sensitivity to each). Report honestly, including failures.

CONSTRAINTS
- Write ONLY inside research/muse-wonder-kappa-edge/ (REPORT.md plus one JSON entry per experiment following research/experiment-log/ENTRY-TEMPLATE.json). Do not edit upstream/, certificates/, or any other existing file. Do not git commit or push.
- Do not claim a kappa improvement unless an exact rational check supports it; state which proof obligations remain open.
- Finish with a ranked list in REPORT.md: top edges, evidence so far, and the next experiment for each.
