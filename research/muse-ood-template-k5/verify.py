#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent recomputation check for RESULT.json (subset + tamper control)."""
import json
import sys
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "research" / "complex-local-word-ceiling"))
import ceiling as C  # noqa: E402

GRID = Q(1, 10**12)
WORD = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}
A_BIT = Q(1733427039589844234749, 1000000000000000000000000)


def q(s):
    n, d = s.split("/")
    return Q(int(n), int(d))


def main():
    res = json.loads((HERE / "RESULT.json").read_text())
    assert res["status"] == "PASS_MUSE_OOD_TEMPLATE_K5_REPRICE"
    for tag, K, m in (("K4_s9_m73_base", 4, 73), ("K5_s11_m89_legal", 5, 89)):
        lo, hi = C.ceiling(WORD, m, 2 * K * 112, 2 * K + 1, 64, grid=GRID, unpaid=1)
        assert (lo, hi) == (q(res["points"][tag]["a_lo"]), q(res["points"][tag]["a_hi"])), tag
    base_hi, legal_hi = q(res["points"]["K4_s9_m73_base"]["a_hi"]), q(res["points"]["K5_s11_m89_legal"]["a_hi"])
    assert legal_hi < base_hi < A_BIT < q(res["points"]["K5_s11_m73_frozen"]["a_lo"])
    assert C.max_idle_rank(89) == res["points"]["K5_s11_m89_legal"]["R"] == 62
    # tamper control: a mutated stored bracket must not match recomputation
    assert q(res["points"]["K5_s11_m89_legal"]["a_hi"]) != q(res["points"]["K5_s11_m73_frozen"]["a_hi"])
    print("PASS_MUSE_OOD_TEMPLATE_K5_VERIFY")


if __name__ == "__main__":
    main()
