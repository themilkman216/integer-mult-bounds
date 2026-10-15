#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Recompute UNPAID.json endpoint signs independently of stored decimals."""
import json
import sys
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "research" / "complex-local-word-ceiling"))
import ceiling as C  # noqa: E402

M, FAM, ST, TARGET = 73, 896, 9, Q(1, 99)
WORD = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}


def sign(e):
    return -1 if e[1] < 1 else (1 if e[0] > 1 else 0)


def main():
    r = json.loads((HERE / "UNPAID.json").read_text())
    assert r["status"] == "PASS_MUSE_OOD_TEMPLATE_K5_UNPAID"
    for tag, u, c in (("unpaid=2,centre=0", 2, 0), ("unpaid=2,centre=64", 2, 64),
                      ("unpaid=3,centre=64", 3, 64)):
        assert sign(C.relax(WORD, M, FAM, ST, c, TARGET, unpaid=u)) == r["T1_signs_at_1_99"][tag]["sign"]
    for c, d_fail, d_pass in ((64, "1975.8", "1975.9"), (0, "396.1", "396.2")):
        for d, want in ((Q(d_fail), 1), (Q(d_pass), -1)):
            local = dict(WORD)
            local[1] = Q(local[1]) - d
            assert sign(C.relax(local, M, FAM, ST, c, TARGET, unpaid=2)) == want, (c, d)
    print("PASS_MUSE_OOD_TEMPLATE_K5_UNPAID_VERIFY")


if __name__ == "__main__":
    main()
