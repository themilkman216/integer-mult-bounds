#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Cheapest decisive test for the surviving unpaid-coordinate lever.

Hypotheses (stated, favourable): selected PR1094 per-call word fixed, base
legal template (896 families, 9 stages, m=73, R=51), ceiling.py coverage
what-if total=(m-unpaid)w+centre. Target a=1/99 (round-1 planning target).
Tests: (T1) certified relax signs at 1/99 for unpaid 2/3 x centre 64/0;
(T2) sharp rank-1 deletion bracket: how much rank-1 mass/call a partner
rank-shape lever must remove for unpaid=2 to pass 1/99 (0.1 grid, certified
opposite signs); (T3) re-confirm round-1 unpaid-3 addition budget signs at
481.4/481.5 rank-1 mass/call. No construction, no new kappa. Stdlib only.
Meta Muse (muse-wonder-full-1.0) assisted; see README.md / UNPAID.md.
"""
import hashlib
import json
import sys
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ENGINE_DIR = ROOT / "research" / "complex-local-word-ceiling"
sys.path.insert(0, str(ENGINE_DIR))
import ceiling as C  # noqa: E402

M, FAM, ST = 73, 896, 9
WORD = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}
TARGET = Q(1, 99)
STEP = Q(1, 10)


def dec(x, digits=12):
    return f"{float(x):.{digits}g}"


def frac(x):
    return f"{x.numerator}/{x.denominator}"


def sign(enc):
    return -1 if enc[1] < 1 else (1 if enc[0] > 1 else 0)


def enc(local, centre, unpaid, a=TARGET):
    e = C.relax(local, M, FAM, ST, centre, a, unpaid=unpaid)
    return {"relax_lo": frac(e[0]), "relax_hi": frac(e[1]),
            "relax_lo_dec": dec(e[0]), "relax_hi_dec": dec(e[1]), "sign": sign(e)}


def deletion_bracket(centre, unpaid=2):
    def s(d):  # remove d rank-1 children (fractional ok)
        local = dict(WORD)
        local[1] = Q(local[1]) - d
        return sign(C.relax(local, M, FAM, ST, centre, TARGET, unpaid=unpaid))
    C.require(s(Q(0)) == 1, "unpaid=2 must fail at zero deletion")
    n_max = int(Q(WORD[1]) / STEP)
    lo_n, hi_n = 0, n_max  # lo fails(+1), hi passes(-1) expected
    C.require(s(hi_n * STEP) == -1, "deleting all rank-1 must pass (else no bracket)")
    while hi_n - lo_n > 1:
        mid = (lo_n + hi_n) // 2
        v = s(mid * STEP)
        C.require(v != 0, "enclosure too wide in deletion search")
        if v == 1:
            lo_n = mid
        else:
            hi_n = mid
    return {"d_fail_still_over": dec(lo_n * STEP), "d_pass_first_under": dec(hi_n * STEP),
            "grid": "0.1 rank-1 children per call"}


def main():
    out = {"status": "PASS_MUSE_OOD_TEMPLATE_K5_UNPAID",
           "scope": "Exact signs/brackets for unpaid>=2 what-if on selected word, base legal template. No construction, no new kappa.",
           "pins": {"base_commit": "0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2",
                    "engine_sha256": hashlib.sha256((ENGINE_DIR / "ceiling.py").read_bytes()).hexdigest(),
                    "selected_record_sha256": hashlib.sha256((ROOT / "certificates" / "selected-result.json").read_bytes()).hexdigest(),
                    "target_a": "1/99", "template": "896 families, 9 stages, m=73, R=51"},
           "T1_signs_at_1_99": {}, "T2_unpaid2_rank1_deletion_needed": {}, "T3_unpaid3_budget_signs": {}}
    for u in (2, 3):
        for c in (64, 0):
            out["T1_signs_at_1_99"][f"unpaid={u},centre={c}"] = enc(WORD, c, u)
    for c in (64, 0):
        out["T2_unpaid2_rank1_deletion_needed"][f"centre={c}"] = deletion_bracket(c)
    for L in (Q(4814, 10), Q(4815, 10)):
        local = dict(WORD)
        local[1] = Q(local[1]) + L
        out["T3_unpaid3_budget_signs"][f"unpaid=3,centre=64,+{dec(L)}_rank1"] = enc(local, 64, 3)
    p = HERE / "UNPAID.json"
    if "--out" in sys.argv:
        p = Path(sys.argv[sys.argv.index("--out") + 1])
    p.write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print(json.dumps(out, indent=1, sort_keys=True))
    print("PASS_MUSE_OOD_TEMPLATE_K5_UNPAID")


if __name__ == "__main__":
    main()
