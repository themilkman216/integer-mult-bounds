#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Cheapest decisive test for the round-1 K=5 template lever.

Round 1 (research/muse-ood-coverage-template/screen.py) priced K pairs /
(2K+1) stages with the window dimension frozen at m=73. PR2052 Theorem S
prices schedules at the legal shared stage window m = 1 + 8s. This script
isolates that single changed hypothesis on round 1's own word (the selected
PR1094 per-call word, centre 64, unpaid 1): exact pinned-engine brackets at
(K, s, m) = (4, 9, 73) [base], (5, 11, 73) [round-1 frozen window], and
(5, 11, 89) [legal window], each compared against the bit endpoint.

No construction and no new kappa are claimed. Standard library only.
Meta Muse (muse-wonder-full-1.0) assisted; see README.md.
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

GRID = Q(1, 10**12)
WORD = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}
A_BIT = Q(1733427039589844234749, 1000000000000000000000000)
KAPPA = Q(836330098538459, 500000000000000000)


def dec(x, digits=12):
    return f"{float(x):.{digits}g}"


def frac(x):
    return f"{x.numerator}/{x.denominator}"


def main():
    engine_sha = hashlib.sha256((ENGINE_DIR / "ceiling.py").read_bytes()).hexdigest()
    selected_sha = hashlib.sha256((ROOT / "certificates" / "selected-result.json").read_bytes()).hexdigest()
    points = {}
    for tag, K, m in (("K4_s9_m73_base", 4, 73), ("K5_s11_m73_frozen", 5, 73), ("K5_s11_m89_legal", 5, 89),
                      ("K6_s13_m105_legal", 6, 105)):
        fam, st = 2 * K * 112, 2 * K + 1
        lo, hi = C.ceiling(WORD, m, fam, st, 64, grid=GRID, unpaid=1)
        q = C.model(WORD, m, fam, st, 64, unpaid=1)
        points[tag] = {"K": K, "stages": st, "families": fam, "m": m, "R": q["R"],
                       "w": dec(q["w"]), "idle_mass": dec(q["idle_mass"]),
                       "a_lo": frac(lo), "a_hi": frac(hi), "a_hi_dec": dec(hi),
                       "bracket_above_bit_endpoint": bool(lo > A_BIT)}
    base_hi = Q(*[int(t) for t in points["K4_s9_m73_base"]["a_hi"].split("/")])
    for p in points.values():
        p["x_base_hi"] = dec(Q(*[int(t) for t in p["a_hi"].split("/")]) / base_hi)
    legal = points["K5_s11_m89_legal"]
    verdict = ("K5 legal-window bracket does NOT exceed the bit endpoint and does not beat the "
               "K4 base ceiling: the round-1 182.0 overhead budget is moot on the selected word"
               if not legal["bracket_above_bit_endpoint"] and Q(legal["x_base_hi"]) <= 1
               else "K5 legal-window bracket survives on the selected word; instantiate overhead vs budget")
    result = {"status": "PASS_MUSE_OOD_TEMPLATE_K5_REPRICE",
              "scope": "Exact favorable relaxations isolating m=73 frozen vs m=1+8s legal window on the selected word. No construction, no new kappa.",
              "pins": {"base_commit": "0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2",
                       "engine": "research/complex-local-word-ceiling/ceiling.py",
                       "engine_sha256": engine_sha, "selected_record_sha256": selected_sha,
                       "grid": "1/10^12", "word_per_call": {str(r): n for r, n in sorted(WORD.items())},
                       "a_bit_selected": frac(A_BIT), "kappa_selected": frac(KAPPA)},
              "points": points, "verdict": verdict}
    out = HERE / "RESULT.json"
    if "--out" in sys.argv:
        out = Path(sys.argv[sys.argv.index("--out") + 1])
    out.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n")
    print(json.dumps(result, indent=1, sort_keys=True))
    print("PASS_MUSE_OOD_TEMPLATE_K5_REPRICE")


if __name__ == "__main__":
    main()
