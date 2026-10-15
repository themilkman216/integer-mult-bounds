#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact ceiling screen for two-call centre sharing on the selected word.

All acceptance signs are exact rational intervals from the pinned
research/complex-local-word-ceiling/ceiling.py (hash-checked, imported
unchanged). Floats appear only as display decimals derived from Fractions.
Writes SCREEN.json next to this file. Standard library only.
Meta Muse (muse-wonder-full-1.0) assisted; see README credit.
"""
import hashlib
import importlib.util
import json
import sys
from fractions import Fraction as Q
from pathlib import Path

PKG = Path(__file__).resolve().parent
ROOT = PKG.parents[1]
CEILING_REL = "research/complex-local-word-ceiling/ceiling.py"
CEILING_SHA256 = "86a1432870b3b21d8454106ec9162fddc0471472d9214c590a1420f2426cedfc"
SELECTED_REL = "certificates/selected-result.json"
SELECTED_SHA256 = "10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32"
ASSEMBLY_REL = "research/community-frontier1094-audit/ASSEMBLY.json"
GRID = Q(1, 10**12)
M, FAM, ST = 73, 896, 9
WORD = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}
NCALLS = 144


def require(ok, why):
    if not ok:
        raise ValueError(why)


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_ceiling():
    path = ROOT / CEILING_REL
    require(sha256(path) == CEILING_SHA256, "ceiling.py pin changed")
    spec = importlib.util.spec_from_file_location("pinned_ceiling", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


C = load_ceiling()
require(sha256(ROOT / SELECTED_REL) == SELECTED_SHA256, "selected record pin changed")
SEL = json.loads((ROOT / SELECTED_REL).read_text())
require(SEL["kappa"] == "836330098538459/500000000000000000", "selected kappa changed")
K_SEL = Q(SEL["kappa"])
A_SEL = K_SEL / (1 - K_SEL)
K_LEAD = Q("0.0016971949509")  # #2374, unreviewed target as stated in assignment
A_LEAD = K_LEAD / (1 - K_LEAD)
ASM = json.loads((ROOT / ASSEMBLY_REL).read_text())
A_BIT = Q(ASM["bit_lower"])  # predecessor pin for the whole-bound cap context
require(A_SEL < A_LEAD < A_BIT, "target ordering changed")


def dec(x):
    return f"{float(x):.15f}"


def bracket(local, centre):
    lo, hi = C.ceiling(local, M, FAM, ST, centre, grid=GRID)
    return {"a_lo": str(lo), "a_hi": str(hi), "a_hi_decimal": dec(hi),
            "kappa_cap_decimal": dec(hi / (1 + hi))}


def sign(local, centre, a):
    lo, hi = C.relax(local, M, FAM, ST, centre, a)
    if hi < 1:
        s = "PASS_below_1"
    elif lo > 1:
        s = "FAIL_above_1"
    else:
        raise ValueError("enclosure does not separate 1")
    return {"relax_lo": str(lo), "relax_hi": str(hi),
            "relax_lo_decimal": dec(lo), "relax_hi_decimal": dec(hi), "sign": s}


def passes(local, centre, a):
    return C.relax(local, M, FAM, ST, centre, a)[1] < 1


def fails(local, centre, a):
    return C.relax(local, M, FAM, ST, centre, a)[0] > 1


def with_overhead(local, rank, mass):
    """Add overhead of total rank-mass `mass` (Fraction) as rank-`rank` children."""
    out = dict(local)
    if mass:
        out[rank] = Q(out.get(rank, 0)) + Q(mass) / rank
    return out


def breakeven_tenths(local, centre, rank, a, max_tenths):
    """Largest t/10 overhead mass passing at a (overhead raises centre charge).

    Overhead children are *additional* paid work: local mass and the coverage
    centre term both grow by L, so idle mass stays at its shared value. (Holding
    centre fixed would let overhead displace ideal idle mass for free and is
    not the predecessor overhead-budget model.)
    """
    def prof(mass):
        return with_overhead(local, rank, mass), centre + mass

    require(passes(local, centre, a), "zero-overhead profile does not pass target")
    pmax, cmax = prof(Q(max_tenths, 10))
    if passes(pmax, cmax, a):
        return {"kind": "search_bound", "max_mass": str(Q(max_tenths, 10))}
    lo, hi = 0, max_tenths  # lo passes, hi fails
    while hi - lo > 1:
        mid = (lo + hi) // 2
        pm, cm = prof(Q(mid, 10))
        if passes(pm, cm, a):
            lo = mid
        else:
            require(fails(pm, cm, a), "non-monotone or unseparated overhead sign")
            hi = mid
    lp, lf = Q(lo, 10), Q(hi, 10)
    pp, cp = prof(lp)
    pf, cf = prof(lf)
    return {"kind": "bracket", "L_pass": str(lp), "L_pass_decimal": dec(lp),
            "L_fail": str(lf), "L_fail_decimal": dec(lf),
            "pass_sign": sign(pp, cp, a), "fail_sign": sign(pf, cf, a)}


def breakeven_integer_total(local, centre, rank, a):
    """Largest integer T of rank-`rank` overhead children over NCALLS calls passing.

    As in breakeven_tenths, overhead raises the per-call centre term by
    T*rank/NCALLS. Search bound: overhead mass 64/call (twice the ideal saving).
    """
    max_total = (64 * NCALLS) // rank

    def prof(t):
        out = dict(local)
        out[rank] = Q(out.get(rank, 0)) + Q(t, NCALLS)
        return out, centre + Q(t * rank, NCALLS)

    p0, c0 = prof(0)
    require(passes(p0, c0, a), "zero-overhead profile does not pass target")
    pm, cm = prof(max_total)
    if passes(pm, cm, a):
        return {"kind": "search_bound", "max_total_children": max_total}
    lo, hi = 0, max_total
    while hi - lo > 1:
        mid = (lo + hi) // 2
        pm, cm = prof(mid)
        if passes(pm, cm, a):
            lo = mid
        else:
            require(fails(pm, cm, a), "non-monotone integer overhead sign")
            hi = mid
    return {"kind": "bracket", "T_pass": lo, "T_fail": hi,
            "mass_per_call_pass": str(Q(lo * rank, NCALLS)),
            "mass_per_call_pass_decimal": dec(Q(lo * rank, NCALLS))}


def main():
    shared = {**WORD, 8: 4}
    fused = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 16: 4}
    # Partial sharing: j of 8 slots equal in every pair -> per-call rank-8 count 8-j/2.
    partial = {}
    for j in (1, 2, 4):
        prof = {**WORD, 8: Q(16 - j, 2)}
        partial[str(j)] = {"profile_rank8_per_call": str(Q(16 - j, 2)),
                           "centre": 64 - 4 * j, "bracket": bracket(prof, 64 - 4 * j),
                           "sign_at_a_lead": sign(prof, 64 - 4 * j, A_LEAD)}
    idle_shared = C.model(shared, M, FAM, ST, 32)["idle_mass"]
    max_tenths = 640  # overhead search bound: 64.0 mass/call = twice the ideal saving
    out = {
        "status": "PASS_MUSE_CENTRE_BANK_SCREEN",
        "pins": {"base_commit": "0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2",
                 "ceiling_py": CEILING_REL, "ceiling_py_sha256": CEILING_SHA256,
                 "selected_result_sha256": SELECTED_SHA256,
                 "assembly": ASSEMBLY_REL},
        "targets": {"kappa_selected": str(K_SEL), "a_selected": str(A_SEL),
                    "a_selected_decimal": dec(A_SEL),
                    "kappa_lead_2374_unreviewed": str(K_LEAD), "a_lead": str(A_LEAD),
                    "a_lead_decimal": dec(A_LEAD), "a_bit_lower_pin": str(A_BIT),
                    "a_bit_decimal": dec(A_BIT),
                    "bit_fixed_kappa_cap_decimal": dec(A_BIT / (1 + A_BIT))},
        "word": {"profile": {str(k): v for k, v in WORD.items()},
                 "local_mass": sum(r * n for r, n in WORD.items()),
                 "m": M, "families": FAM, "stages": ST, "w": str(Q(FAM, ST)),
                 "idle_mass_base": str(C.model(WORD, M, FAM, ST, 64)["idle_mass"]),
                 "idle_mass_shared": str(idle_shared)},
        "ceilings": {
            "base_centre64": bracket(WORD, 64),
            "ideal_shared_centre32": bracket(shared, 32),
            "fused16_centre64_CB_C_free": bracket(fused, 64),
        },
        "signs_at_a_lead": {
            "base": sign(WORD, 64, A_LEAD),
            "ideal_shared": sign(shared, 32, A_LEAD),
            "fused16_CB_C_free": sign(fused, 64, A_LEAD),
            "ideal_shared_at_a_bit": sign(shared, 32, A_BIT),
        },
        "partial_slots_equal_every_pair": partial,
        "breakeven_overhead_on_shared": {
            "note": "Added paid children on the ideal-shared profile; overhead mass L "
                    "raises the centre term 32->32+L (idle mass unchanged), matching "
                    "the predecessor actual-profile overhead model.",
            "at_a_lead": {str(r): breakeven_tenths(shared, 32, r, A_LEAD, max_tenths)
                          for r in (1, 8, 51)},
            "at_a_selected": {str(r): breakeven_tenths(shared, 32, r, A_SEL, max_tenths)
                              for r in (1, 8)},
            "integer_totals_over_144_calls_at_a_lead": {
                str(r): breakeven_integer_total(shared, 32, r, A_LEAD) for r in (1, 8)},
        },
        "controls": {
            "one_extra_rank1_lowers_base_ceiling": (
                C.ceiling({**WORD, 1: WORD[1] + 1}, M, FAM, ST, 64, grid=GRID)[1]
                < C.ceiling(WORD, M, FAM, ST, 64, grid=GRID)[1]),
        },
    }
    require(out["controls"]["one_extra_rank1_lowers_base_ceiling"],
            "monotonicity control failed")
    (PKG / "SCREEN.json").write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print("PASS_MUSE_CENTRE_BANK_SCREEN "
          f"base_hi={out['ceilings']['base_centre64']['a_hi_decimal']} "
          f"shared_hi={out['ceilings']['ideal_shared_centre32']['a_hi_decimal']} "
          f"fused_hi={out['ceilings']['fused16_centre64_CB_C_free']['a_hi_decimal']} "
          f"a_lead={dec(A_LEAD)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
