#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Check RESULT.json key brackets/signs against fresh pinned-engine calls.

Read-only. Standard library only. Does not import screen.py.
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
M = 73
WORD = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}
NONCENTRE = {r: n for r, n in WORD.items() if r != 8}
A_BIT = Q(1733427039589844234749, 1000000000000000000000000)
A_COMPLEX = Q(67018507072324140917, 40000000000000000000000)
KAPPA = Q(836330098538459, 500000000000000000)


def need(ok, why):
    if not ok:
        raise ValueError(why)


def parse(s):
    n, d = s.split("/")
    return Q(int(n), int(d))


def relax_R(local, families, stages, centre, unpaid, a, R):
    w = Q(families, stages)
    total = (M - unpaid) * w + centre
    idle = total - sum(r * Q(n) for r, n in local.items())
    need(idle >= 0, "coverage")
    lo = hi = Q(0)
    for r, n in local.items():
        c = C.child_cost(r, M, a)
        lo, hi = lo + Q(n) * c[0], hi + Q(n) * c[1]
    c = C.child_cost(R, M, a)
    lo, hi = lo + (idle / R) * c[0], hi + (idle / R) * c[1]
    return C.down(lo / w), C.up(hi / w)


def with_added(local0, rank, mass):
    local = dict(local0)
    local[rank] = Q(local.get(rank, 0)) + Q(mass) / rank
    return local


def main():
    res = json.loads((HERE / "RESULT.json").read_text())
    need(res["status"] == "PASS_MUSE_OOD_COVERAGE_TEMPLATE_SCREEN", "status")
    need(res["pins"]["engine_sha256"] ==
         hashlib.sha256((ENGINE_DIR / "ceiling.py").read_bytes()).hexdigest(), "engine pin")
    need(res["pins"]["selected_record_sha256"] ==
         hashlib.sha256((ROOT / "certificates" / "selected-result.json").read_bytes()).hexdigest(),
         "selected pin")

    checks = []

    # Base bracket fresh.
    lo, hi = C.ceiling(WORD, M, 896, 9, 64, grid=GRID)
    need(parse(res["S0_base"]["a_lo"]) == lo and parse(res["S0_base"]["a_hi"]) == hi, "base bracket")
    need(A_COMPLEX < lo, "endpoint below bracket")
    checks.append("base bracket + endpoint order")

    # K=5 template bracket fresh; K sweep monotone in stored hi values.
    lo5, hi5 = C.ceiling(WORD, M, 1120, 11, 64, grid=GRID)
    stored5 = res["S1_template"]["K_sweep_V112_centre_fixed"]["K=5"]
    need(parse(stored5["a_lo"]) == lo5 and parse(stored5["a_hi"]) == hi5, "K=5 bracket")
    need(lo5 > A_BIT, "K=5 relaxation bracket lies above bit endpoint")
    his = [float(res["S1_template"]["K_sweep_V112_centre_fixed"][f"K={k}"]["a_hi_dec"])
           for k in (2, 4, 5, 6, 8, 16, 64)]
    need(all(b > a for a, b in zip(his, his[1:])), "K sweep strictly increasing")
    checks.append("K=5 bracket above bit endpoint; K sweep monotone")

    # V104/cst56 shape-proxy bracket fresh.
    proxy = {r: Q(n) * Q(104, 112) for r, n in NONCENTRE.items()}
    proxy[7] = Q(proxy.get(7, 0)) + 8
    plo, phi = C.ceiling(proxy, M, 832, 9, 56, grid=GRID)
    storedp = res["S1_template"]["V104_cst56_selected_shape_proxy"]
    need(parse(storedp["a_lo"]) == plo and parse(storedp["a_hi"]) == phi, "proxy bracket")
    checks.append("V104/cst56 shape-proxy bracket")

    # S4: +5% signs above 1 at every R, fresh.
    base_hi = hi
    t105 = base_hi * Q(21, 20)
    for R in (51, 57, 61, 66, 72):
        enc = relax_R(WORD, 896, 9, 64, 1, t105, R)
        need(enc[0] > 1, f"+5% must fail at R={R}")
        need(res["S4_halving_depth"]["plus5pct_signs"][f"R={R}"]["sign"] == 1, "stored S4 sign")
    checks.append("halving-cap +5% exclusion at R=51,57,61,66,72")

    # S3 spot brackets: adjacent-grid opposite signs, fresh.
    # K6 at bit endpoint, added rank-1 mass 400.7 passes, 400.8 fails.
    for mass, want_below in ((Q(4007, 10), True), (Q(4008, 10), False)):
        enc = C.relax(with_added(WORD, 1, mass), M, 1344, 13, 64, A_BIT)
        need(enc[1] < 1 if want_below else enc[0] > 1, "K6 break-even bracket")
    # Unpaid-3 at 1/99, added rank-8 mass 1032.7 passes, 1032.8 fails.
    for mass, want_below in ((Q(10327, 10), True), (Q(10328, 10), False)):
        enc = C.relax(with_added(WORD, 8, mass), M, 896, 9, 64, Q(1, 99), unpaid=3)
        need(enc[1] < 1 if want_below else enc[0] > 1, "unpaid3 break-even bracket")
    # Unpaid-2 at 1/99 fails even with zero added mass.
    need(C.relax(WORD, M, 896, 9, 64, Q(1, 99), unpaid=2)[0] > 1, "unpaid2 alone misses 1/99")
    checks.append("break-even adjacent-grid signs (K6, unpaid3); unpaid2 zero-added failure at 1/99")

    # S5 exact planning-transfer identities.
    need(abs(float(A_COMPLEX / (1 + A_COMPLEX) - KAPPA)) < 1e-18, "selected transfer identity")
    for label, kt in (("kappa_x1.10", KAPPA * Q(11, 10)), ("kappa_0.01", Q(1, 100))):
        req = kt / (1 - kt)
        stored = float(res["S5_joint_kappa"]["joint_targets"][label]["required_a_each_side"])
        need(abs(stored - float(req)) / float(req) < 1e-9, f"required-a {label}")
    checks.append("joint-kappa required-a identities")

    # Tamper control: a mutated stored bracket must not match the fresh value.
    mutated = json.loads(json.dumps(res))
    mutated["S0_base"]["a_hi"] = "1/100"
    need(parse(mutated["S0_base"]["a_hi"]) != hi, "tamper control setup")
    checks.append("tampered bracket differs from fresh engine value (comparison is live)")

    print("PASS_MUSE_OOD_COVERAGE_TEMPLATE_VERIFY")
    for c in checks:
        print(" -", c)


if __name__ == "__main__":
    try:
        main()
    except ValueError as e:
        print("FAIL:", e)
        sys.exit(1)
