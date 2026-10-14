# Which retained complex E8 decoder bound applies?

Use this map before reopening a decoder search. The bounds below cover different
algebraic classes. Changing a coefficient field or adding a term does not by itself
leave every retained obstruction. Conversely, a masked identity is outside these
all-pairs theorems. Check [live overlap](../../autoresearch.md#1-orient-briefly-then-choose-a-distinct-task)
before calling a class outside these hypotheses an open problem.

## Shared model and the three boundaries

The roots have squared norm two. If `R` contains the live E8 root-line
representatives, the decoder identity is `D T^transpose = 2 R R^transpose`.
Transpose is ordinary transpose, including over the complex numbers. Each term
costs the **binary rank** of the label pairing between its two nonzero supports,
with pairing `(<r_i,r_j> + 1) mod 2`. The copied-information charge is the sum
of these separate term costs; it is not the number of terms or their scalar rank.

| Retained result | Required hypotheses | Conclusion and boundary |
| --- | --- | --- |
| [PR968 proof](../../research/complex-frame-pair-decoders/PROOF.md), themilkman216 | Exactly eight terms; arbitrary **real** factors; equality on **every** live pair; any puncture of `p <= 24` out of 120 root lines | Cost at least `max(72-p,56)`. The best cost/port ratio in this class is `7/13`, attained at `p=16`. This does not exclude masked identities or nine-term decoders. |
| [PR1077 proof](../../research/complex-decoder-field-extension-seed44/PROOF.md), woklerx | The same eight-term, all-pairs, `p <= 24` model, now with arbitrary **complex** factors and ordinary transpose | The same floor. Complex isotropic normals invalidate a verbatim reuse of the real cross-term nonparallel argument; the extension proves the restricted nonisotropy needed for the count. Complex coefficients alone do not escape this floor. |
| [PR845 proof](../../research/p112-single-lift/PROOF.md#model-and-result), Mihir Srivastava | The specific frame-punctured P112; **real** coefficients; all-pairs identity; the original eight coordinate reader columns retained up to nonzero rescaling, plus one arbitrary source total (or the transposed family) | Cost at least **64**, even when the new source is outside the coordinate column space. This excludes this fixed-reader ninth-term mechanism, not arbitrary nine-term decoders, complex coefficients, changed readers, several additional totals or masked completions. |

For PR968/1077, attainment is **over the choice of puncture and decoder** at
each size. It does not promise an attaining decoder for every puncture of that
size. Their geometric argument retains the stated real E8 hyperplane-flat
classification premise (F6); the finite checks do not newly prove that theorem.

PR845's exact normal form is useful for recognizing overlap. With coordinate
matrix `X`, reader columns `x_j`, `a in R^8` and arbitrary `z in R^112`, it is

```text
X X^transpose = sum_j x_j (x_j - a_j z)^transpose + (Xa) z^transpose.
```

Every exact nine-term factorization retaining those eight reader columns fits
this family. A ninth term or an asymmetric source alone therefore does not
escape PR845. Allowing reader changes leaves PR845's scope, but does not evade
PR1077 if the resulting decoder still has exactly eight all-pairs terms.

## What the independent Gram evidence proves

[Adam Gall's PR1098](../../research/p112-gram-support-seed80/README.md)
corroborates **PR845's finite support lemma** using a label-free Gram-spectrum
certificate: 511 nonzero pairing characters, 503 full-rank supports and eight
coordinate-axis kernels. It also establishes a sharp restricted-energy constant
four on the full-rank supports.

That check does **not** replay PR845's 3,272 sign systems or its 128 incompatible
kernel cases, and the energy constant is not a physical COPY bill. Follow
[PR845's proof](../../research/p112-single-lift/PROOF.md#annihilators-convert-cost-into-a-dimension-bound)
and its main/independent checkers for those remaining finite premises. PR1098 is
corroboration, not a broader ninth-term or masked-decoder exclusion.

## Reproduce the cited evidence

From the repository root, Python 3.10+ and the standard library. PR968's plain
`verify.py` command rejects the current selected record at `G.selected-record`:
its pricing section requires the historical #942 certificate. Use its existing
`--repo` option with an isolated copy of the pinned pricing inputs and frozen
checkpoint. This runs the **complete unchanged verifier**, including its
selection guard, full frame census, historical pricing and failure controls:

```sh
python3 -I -B - <<'PY'
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

package = Path("research/complex-frame-pair-decoders")
pins = json.loads((package / "SOURCES.json").read_text())
with tempfile.TemporaryDirectory(prefix="pr968-") as work:
    historical = Path(work)
    for relative, expected in pins["pricing_inputs"].items():
        data = Path(relative).read_bytes()
        if hashlib.sha256(data).hexdigest() != expected:
            raise ValueError("Pinned input changed: " + relative)
        target = historical / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    selected = historical / "certificates/selected-result.json"
    selected.parent.mkdir(parents=True, exist_ok=True)
    selected.write_bytes(Path("certificates/checkpoints/frontier942.json").read_bytes())
    subprocess.run([sys.executable, "-I", "-B", str(package / "verify.py"),
                    "--repo", str(historical)], check=True)
PY
```

Expected final line starts `PASS_COMPLEX_FRAME_PAIR_DECODERS`. Temporary files
are removed on exit. The checkout's selected record and predecessor files are
not written. The other packages' direct commands work on the current checkout:

```sh
python3 -I -B research/complex-decoder-field-extension-seed44/verify.py
python3 -B research/p112-single-lift/verify.py
python3 -B research/p112-single-lift/independent_check.py
python3 -I -B research/p112-gram-support-seed80/verify.py
```

These check the packages' declared exact finite evidence, including their
failure controls. The quantified lower bounds also use written arguments.
PR968's quoted headroom belongs to #942; it is not a repricing of today's
selected construction. Resolve current sources and the full replay through
[the selected record](../../certificates/selected-result.json).

A copied-rank floor or a decoder identity does not establish a complete paid
moment, legal centre/frame/restoration program, physical hosting or an all-size
multiplication theorem. Compare any proposed realization's **whole invoice**
with the [current bottleneck](bottleneck-brief.md); a change in the rank
distribution can matter even at the same rank sum. This map adds no new bound
or supplier.

## Open next questions

For a candidate with changed readers, masked exactness or more terms, first
record its precise identity, coefficient field, puncture, support-pairing bill
and which of the above hypotheses changes. This makes the next overlap check
specific and avoids repeating PR845 under a new optimizer seed. A mathematical
identity and a favorable fully charged budget are the first steps toward a
supplier; a legal centre/frame/restoration implementation remains a separate
blocker. Work outside this map may already have a pending result: consult the
[discussion board](https://github.com/CrocSwap/integer-mult-bounds/discussions)
and refreshed PR bodies rather than inferring availability from this index.

## Scope, source heads and credit

Task `scope-navigation`, priority revision 3; scope key `b18e0e173a4430a9564b`,
nonce `2f5e17a27f7174806a1785a7c24a478f`. Scope **refined** to this four-result
family index and its historical replay route: the onboarding eight-term link
did not explain the adjacent fixed-reader ninth-term exclusion, narrower Gram
corroboration or PR968's historical selection guard. Base:
`ee055dc44815497927ef618fc985b93c2dcbda2a`. These are the reviewed source heads
in the retained [#952](../../research/community-batch952-audit/DISPOSITIONS.json),
[#970](../../research/community-batch970-audit/DISPOSITIONS.json) and
[#1099](../../research/community-batch1099-audit/DISPOSITIONS.json) dispositions:

| PR | Reviewed head |
| --- | --- |
| 845 | `125ce25bdae421627b56077adc14940c2d0aa52f` |
| 968 | `6a99e7240b961ac5e115ae6aa0301ec7c4a45d77` |
| 1077 | `1459f58a829e616ddf32a3da2782e166700e3218` |
| 1098 | `75834dfc800511cebc0e4c696788e9081272d761` |

Construction/model credit includes DreamingOfClouds (PR717/446/595), Joel
Pulikkan / GamingPuzzled (PR620) and the lineage credited in each source.
Coordination and overlap limits are recorded in [discussion #1621](https://github.com/CrocSwap/integer-mult-bounds/discussions/1621).
Prepared by Arham Tahir with substantial OpenAI Codex assistance; no independent
human review or proof-assistant verification of these statements is claimed.
Apache-2.0.
