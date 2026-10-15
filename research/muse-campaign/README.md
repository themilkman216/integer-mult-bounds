# Muse out-of-distribution κ campaign (2026-10-14/15)

Orchestration log for a Claude Code session guiding Meta Muse (`muse-wonder-full-1.0`,
contributor mode) on upstream CrocSwap/integer-mult-bounds main `0fdd7d8` (priority
revision 4, selected κ = 836330098538459/500000000000000000, #1094). **No new κ was
established.** Every package is local-only, unreviewed upstream, and carries its own
README (credits, open next questions) and `verify.py` with value-mutating tamper controls.

`briefs/` holds the exact prompts given to Muse each round. `upstream-pr-titles-2028-2478.txt`
lists the open-PR heads read for overlap.

| Round | Package | Outcome |
|---|---|---|
| 1 | `muse-ood-coverage-template` | Ceiling screen: bit side caps κ ≈ 0.0017304; unpaid/centre levers mapped |
| 2A | `muse-ood-template-k5` | K=5 template falsified at legal window m=89 (−1.87%), agrees with #2052 |
| 2B | `muse-ood-bit-wall`, `muse-ood-block-copy` | Bit levers screened; rank-2 block copy costs 73 vs 63 (one-stream obstruction) |
| 3A | `muse-bit-dirty-borrowing` | One legal bit alias (439→438 helpers, +0.079%) |
| 3B | `muse-plane-port-interface` | Shared plane decoders cost ≥224 vs break-even ≤199 |
| 3C | `muse-t74-borrow-extend` | 80 aliases verify on #2269 words; owner fill absorbs gain (+1.86 lower bound) |
| 3D | `muse-t74-exact-fill` | Dispatch 665+1 on #2269: κ 0.0016963106941348668 (PASS_RELEASE log included); superseded, inherits #2269's unpriced buffers |
| 3F | `muse-dispatch-2322` | Dispatch gives exactly zero on #2322 (providers price identically) |
| 3G | `muse-2322-exact-fill` | Legal fill ≈0.0016971494; scooped by #2374 |
| 3H | `muse-2322-low-borrow` | Low aliases worse on #2322 words |
| 4A | `muse-centre-bank` | Two-call centre bank falsified |
| 4B | `muse-rank16-children` | Rank-16 children reduce to an in-place multi-array drop lemma |
| 4C/4D | `muse-joint-rank-drop` | Width-2 joint-rank lift impossible in retained language; JOINT_CLIMB coverage recount |
| 5A | `muse-joint-climb-2374` | JOINT_CLIMB volume-priced at separate cost; 4D's splice gain falsified (checkpoint README) |

## Open leads at hand-off (2026-10-15 12:15 UTC)

Open leader: #2474 (Jeremy Kothe) κ = 0.001703676388.

- **Entrance raises with a joint frame re-solve** (#2435, priced by #2453): 26 width-8,
  first-climb-2 helpers still enter at dimension 1; partner splits eat ~92% of each raise.
  Average-partner raises ≈ +3e-7; partner-free raises up to +4.35e-6. Needs an exact frame
  re-solve with entrances as variables (Kothe's `frames.optimal_frames`).
- **Further #2436 lifted-target aliases** (#2474 added a fifth, +1.24e-7).

Prepared with substantial Meta Muse and Claude assistance. Apache-2.0; predecessor
attribution is in each package.
