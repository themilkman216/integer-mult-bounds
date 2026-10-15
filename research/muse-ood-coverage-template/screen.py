#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact coverage/template frontier screen for the selected complex word.

Reuses the pinned exact interval engine in
research/complex-local-word-ceiling/ceiling.py (PR1240) without modification.
Every ceiling is a certified grid bracket [lo, hi] with relax(lo) < 1 <
relax(hi) under the stated (families, stages, centre, unpaid, R) hypotheses.
What-if R values beyond the halving guard use the same child_cost enclosures
with an explicitly overridden idle rank; they are replacement-model relaxations
requiring a new outer proof, not incumbent-model ceilings.

No construction and no new kappa are claimed. Standard library only.
Meta Muse (muse-wonder-full-1.0) assisted; see README.md.

usage: screen.py [--out RESULT.json]
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
A_COMPLEX = Q(67018507072324140917, 40000000000000000000000)
A_BIT = Q(1733427039589844234749, 1000000000000000000000000)
KAPPA = Q(836330098538459, 500000000000000000)


def dec(x, digits=12):
    return f"{float(x):.{digits}g}"


def frac(x):
    return f"{x.numerator}/{x.denominator}"


def cap(local, families, stages, centre=64, unpaid=1):
    lo, hi = C.ceiling(local, M, families, stages, centre, grid=GRID, unpaid=unpaid)
    return lo, hi


def relax_R(local, families, stages, centre, unpaid, a, R):
    """Exact enclosure of the per-call relaxation with idle rank R (any 1<=R<M)."""
    C.require(1 <= R < M, "idle rank range")
    w = Q(families, stages)
    total = (M - unpaid) * w + centre
    local_mass = sum(r * Q(n) for r, n in local.items())
    idle = total - local_mass
    C.require(idle >= 0, "local mass exceeds coverage total")
    lo = hi = Q(0)
    for r, n in local.items():
        c = C.child_cost(r, M, a)
        lo, hi = lo + Q(n) * c[0], hi + Q(n) * c[1]
    c = C.child_cost(R, M, a)
    k = idle / R
    lo, hi = lo + k * c[0], hi + k * c[1]
    return C.down(lo / w), C.up(hi / w)


def sign(enc):
    if enc[1] < 1:
        return -1
    if enc[0] > 1:
        return 1
    return 0


def root_R(local, families, stages, centre, unpaid, R):
    """Grid bracket for the custom-R relaxation root (bisection on certified signs)."""
    lo, hi = Q(0), Q(1, 20)
    C.require(sign(relax_R(local, families, stages, centre, unpaid, lo, R)) == -1,
              "custom-R relaxation has no positive saving")
    C.require(sign(relax_R(local, families, stages, centre, unpaid, hi, R)) == 1,
              "custom-R search window too small")
    while hi - lo > GRID:
        mid = Q(int((lo + hi) / 2 / GRID)) * GRID
        if mid <= lo:
            mid = lo + GRID
        s = sign(relax_R(local, families, stages, centre, unpaid, mid, R))
        C.require(s != 0, "enclosure too wide at grid point")
        if s == -1:
            lo = mid
        else:
            hi = mid
    return lo, hi


def max_added_mass(target_a, base_local, families, stages, centre, unpaid, add_rank,
                   step=Q(1, 10)):
    """Largest added rank mass L (grid `step`) with relax(target_a) < 1 certified.

    Added mass is billed as fractional children of rank `add_rank` inside the
    same coverage total (idle mass shrinks accordingly). Returns (L_pass,
    L_fail) adjacent grid points with certified opposite signs, or
    (None, 0) if even L=0 fails, or (Lmax, None) if the coverage bound is hit.
    """
    q = C.model(base_local, M, families, stages, centre, unpaid=unpaid)
    idle_max = q["idle_mass"]

    def passes(L):
        local = dict(base_local)
        local[add_rank] = Q(local.get(add_rank, 0)) + L / add_rank
        return sign(C.relax(local, M, families, stages, centre, target_a, unpaid=unpaid))

    if passes(Q(0)) != -1:
        return None, Q(0)
    # Bisection on integer multiples of step within [0, idle_max].
    n_max = int(idle_max / step)
    lo_n, hi_n = 0, n_max + 1  # lo passes; hi fails or is out of coverage range
    # Confirm the top grid point (if any) behaviour lazily inside bisection:
    # treat L > idle_max as failing by coverage.
    while hi_n - lo_n > 1:
        mid = (lo_n + hi_n) // 2
        L = mid * step
        if L > idle_max:
            hi_n = mid
            continue
        s = passes(L)
        C.require(s != 0, "enclosure too wide in added-mass search")
        if s == -1:
            lo_n = mid
        else:
            hi_n = mid
    L_pass = lo_n * step
    L_fail = hi_n * step if hi_n * step <= idle_max else None
    if L_fail is not None:
        C.require(passes(L_fail) == 1, "added-mass bracket upper sign")
    C.require(passes(L_pass) == -1, "added-mass bracket lower sign")
    return L_pass, L_fail


def scaled_local(V, centre_fixed=True):
    """Per-call local profile at port count V: non-centre counts scale by V/112."""
    s = Q(V, 112)
    local = {r: Q(n) * s for r, n in NONCENTRE.items()}
    if centre_fixed:
        local[8] = Q(8)
        centre = Q(64)
    else:
        local[8] = Q(8) * s
        centre = Q(64) * s
    return local, centre


def hd_cap(m, hd):
    R = 0
    while 2 * (R + 1) ** hd < m**hd:
        R += 1
    return R


def main():
    out_path = HERE / "RESULT.json"
    if "--out" in sys.argv:
        out_path = Path(sys.argv[sys.argv.index("--out") + 1])

    engine_sha = hashlib.sha256((ENGINE_DIR / "ceiling.py").read_bytes()).hexdigest()
    selected_sha = hashlib.sha256((ROOT / "certificates" / "selected-result.json").read_bytes()).hexdigest()

    # --- S0: base reproduction and controls ---------------------------------
    base_lo, base_hi = cap(WORD, 896, 9, 64, 1)
    C.require(A_COMPLEX < base_lo, "selected complex endpoint must lie below relaxation bracket")
    worse = dict(WORD)
    worse[1] += 1
    _, worse_hi = cap(worse, 896, 9, 64, 1)
    C.require(worse_hi < base_hi, "control: one extra rank-1 child lowers the ceiling")
    # Custom-R engine agrees with pinned relax at the legal cap R=51.
    for a_test in (A_COMPLEX, base_lo, Q(1, 99)):
        e1 = C.relax(WORD, M, 896, 9, 64, a_test)
        e2 = relax_R(WORD, 896, 9, 64, 1, a_test, 51)
        C.require(e1 == e2, "custom-R relax must equal pinned relax at R=51")

    def entry(lo, hi):
        return {
            "a_lo": frac(lo), "a_hi": frac(hi),
            "a_hi_dec": dec(hi), "x_base_hi": dec(hi / base_hi),
            "kappa_cap_if_complex_binds": dec(hi / (1 + hi)),
            "kappa_cap_bit_fixed": dec(min(hi, A_BIT) / (1 + min(hi, A_BIT))),
        }

    result = {
        "status": "PASS_MUSE_OOD_COVERAGE_TEMPLATE_SCREEN",
        "scope": (
            "Exact favorable relaxations of the selected complex local word under "
            "parameterized template/coverage/halving hypotheses. Planning budgets "
            "only: no construction, hosting, precision or supplier admission. "
            "Kappa translations use the retained planning transfer kappa=a/(1+a) "
            "with a=min(bit,complex); the exact moment of a completed construction "
            "remains the acceptance test."
        ),
        "pins": {
            "base_commit": "0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2",
            "engine": "research/complex-local-word-ceiling/ceiling.py",
            "engine_sha256": engine_sha,
            "selected_record": "certificates/selected-result.json",
            "selected_record_sha256": selected_sha,
            "grid": "1/10^12",
            "word_per_call": {str(r): n for r, n in sorted(WORD.items())},
            "a_complex_selected": frac(A_COMPLEX),
            "a_bit_selected": frac(A_BIT),
            "kappa_selected": frac(KAPPA),
        },
        "S0_base": {
            **entry(base_lo, base_hi),
            "one_extra_rank1_hi_dec": dec(worse_hi),
            "controls": "endpoint below bracket; extra rank-1 lowers ceiling; custom-R == pinned relax at R=51 (3 points)",
        },
    }

    # --- S1: template scaling (K pairs, 2K+1 stages; port count V) ----------
    s1 = {"hypothesis": (
        "Per-call word reused across K pairs; non-centre counts scale with V/112. "
        "centre_fixed keeps eight rank-8 centre children and charge 64 per call "
        "(most favorable); centre_scaled scales both with V (pessimistic bracket). "
        "Bridge/terminal overhead varying with K is NOT charged here; S3 prices "
        "the overhead budget that would erase the gain. A changed template needs "
        "a new hosting/owner proof."
    ), "K_sweep_V112_centre_fixed": {}, "V_sweep_K4": {}}
    for K in (2, 4, 5, 6, 8, 16, 64):
        fam, st = 2 * K * 112, 2 * K + 1
        lo, hi = cap(WORD, fam, st, 64, 1)
        s1["K_sweep_V112_centre_fixed"][f"K={K}"] = {
            "families": fam, "stages": st, "w": dec(Q(fam, st)), **entry(lo, hi)}
    for V in (96, 104, 111, 112, 120):
        fam, st = 2 * 4 * V, 9
        row = {"families": fam, "stages": st, "w": dec(Q(fam, st))}
        for tag, fixed in (("centre_fixed", True), ("centre_scaled", False)):
            local, centre = scaled_local(V, fixed)
            lo, hi = cap(local, fam, st, centre, 1)
            row[tag] = entry(lo, hi)
        s1["V_sweep_K4"][f"V={V}"] = row
    # Selected-shape proxy at V=104 with COPY56 billed as eight rank-7 children.
    # This isolates (V, cst) arithmetic only; it is NOT the P104 word, whose
    # local shape, correction and hosting differ (see README candidate A).
    proxy_local = {r: Q(n) * Q(104, 112) for r, n in NONCENTRE.items()}
    proxy_local[7] = Q(proxy_local.get(7, 0)) + 8
    plo, phi = cap(proxy_local, 2 * 4 * 104, 9, 56, 1)
    s1["V104_cst56_selected_shape_proxy"] = {
        "families": 832, "stages": 9, "centre": 56, **entry(plo, phi),
        "warning": "shape proxy only; not a P104 supplier screen",
    }
    result["S1_template"] = s1

    # --- S2: unpaid x centre frontier at the base template ------------------
    s2 = {"hypothesis": (
        "Selected word fixed; unpaid>1 is the coverage-law what-if of ceiling.py "
        "(total mass (m-unpaid)w+centre). Realizing it needs a progress-preserving "
        "endpoint contract; S3 bounds what the extra advancement may cost."
    ), "points": {}}
    for unpaid in (1, 2, 3):
        for centre in (64, 32, 8, 0):
            local = dict(WORD)
            local[8] = Q(centre, 8)
            lo, hi = cap(local, 896, 9, centre, unpaid)
            s2["points"][f"unpaid={unpaid},centre={centre}"] = entry(lo, hi)
    result["S2_unpaid_centre"] = s2

    # --- S3: break-even added-mass budgets (sharp grid brackets) ------------
    t105 = base_hi * Q(21, 20)
    targets = {
        "bit_endpoint": A_BIT,
        "plus5pct_complex_ceiling": t105,
        "a_0.003": Q(3, 1000),
        "a_0.005": Q(1, 200),
        "planning_1_99": Q(1, 99),
    }
    s3 = {"hypothesis": (
        "Added work billed as fractional rank-r children inside the same coverage "
        "total. L_fail-L_pass is one 0.1 mass grid step with certified opposite "
        "relaxation signs. Rank 1 is the most expensive shape per unit mass, "
        "rank 51 the cheapest; a real mechanism must price its actual shape."
    ), "targets_dec": {k: dec(v) for k, v in targets.items()}, "budgets": {}}
    contexts = {
        "unpaid2_centre64_base_template": (WORD, 896, 9, 64, 2),
        "unpaid2_centre0_base_template": ({r: n for r, n in WORD.items() if r != 8}, 896, 9, 0, 2),
        "unpaid3_centre64_base_template": (WORD, 896, 9, 64, 3),
        "unpaid1_centre64_K5_template": (WORD, 2 * 5 * 112, 2 * 5 + 1, 64, 1),
        "unpaid1_centre64_K6_template": (WORD, 2 * 6 * 112, 2 * 6 + 1, 64, 1),
        "unpaid1_centre64_K64_template": (WORD, 2 * 64 * 112, 2 * 64 + 1, 64, 1),
        "unpaid1_centre32_base_template": ({**WORD, 8: 4}, 896, 9, 32, 1),
    }
    for cname, (local0, fam, st, centre, unpaid) in contexts.items():
        s3["budgets"][cname] = {}
        for tname, ta in targets.items():
            s3["budgets"][cname][tname] = {}
            for r in (1, 8, 51):
                Lp, Lf = max_added_mass(ta, local0, fam, st, centre, unpaid, r)
                s3["budgets"][cname][tname][f"add_rank{r}"] = {
                    "L_pass": None if Lp is None else dec(Lp),
                    "L_fail": None if Lf is None else dec(Lf),
                    "note": ("even zero added mass fails" if Lp is None else
                             "coverage-bound hit (no failing grid point in range)" if Lf is None else
                             "sharp adjacent-grid bracket"),
                }
    result["S3_breakeven"] = s3

    # --- S4: halving-depth / idle-cap what-ifs (outside incumbent model) -----
    s4 = {"hypothesis": (
        "Idle cap R(HD)=max{R: 2R^HD < m^HD}. HD>2 needs a new outer row bound "
        "(cf. bit HD discussion in research/bit-revision3-levers-seed03). "
        "R=72 is the absolute child-rank limit m-1, beyond every HD. Signs are "
        "certified with pinned child_cost enclosures."
    ), "caps_m73": {f"HD={hd}": hd_cap(73, hd) for hd in (1, 2, 3, 4, 5, 8)},
        "caps_m64": {f"HD={hd}": hd_cap(64, hd) for hd in (1, 2, 3, 4, 5, 8)},
        "plus5pct_signs": {}, "roots": {}}
    for R in (51, 57, 61, 66, 72):
        enc = relax_R(WORD, 896, 9, 64, 1, t105, R)
        s4["plus5pct_signs"][f"R={R}"] = {
            "relax_at_plus5pct": [dec(enc[0]), dec(enc[1])],
            "sign": sign(enc),
            "reading": "above 1: +5% impossible even at this R" if sign(enc) == 1 else "see root",
        }
    for R in (57, 72):
        lo, hi = root_R(WORD, 896, 9, 64, 1, R)
        s4["roots"][f"R={R}"] = entry(lo, hi)
    result["S4_halving_depth"] = s4

    # --- S5: joint two-sided kappa translation -------------------------------
    s5 = {"hypothesis": (
        "Planning transfer kappa=a/(1+a), a=min(bit,complex) (beta=10^-24 and "
        "seven-step slacks neglected; exact at the selected point to <10^-18). "
        "Required a for target kappa is kappa/(1-kappa)."
    ), "selected_check": {
        "a_complex_over_1plus": dec(A_COMPLEX / (1 + A_COMPLEX), 18),
        "kappa_selected": dec(KAPPA, 18),
        "bit_limited_kappa_cap": dec(A_BIT / (1 + A_BIT), 18),
        "bit_limited_gain": dec((A_BIT / (1 + A_BIT)) / KAPPA),
    }, "joint_targets": {}}
    for label, kt in (
        ("kappa_x1.05", KAPPA * Q(21, 20)), ("kappa_x1.10", KAPPA * Q(11, 10)),
        ("kappa_x2", KAPPA * 2), ("kappa_x6", KAPPA * 6), ("kappa_0.01", Q(1, 100)),
    ):
        req = kt / (1 - kt)
        s5["joint_targets"][label] = {
            "kappa_target": dec(kt), "required_a_each_side": dec(req),
            "complex_multiplier_needed": dec(req / A_COMPLEX),
            "bit_multiplier_needed": dec(req / A_BIT),
        }
    result["S5_joint_kappa"] = s5

    text = json.dumps(result, indent=1, sort_keys=True) + "\n"
    out_path.write_text(text)
    print(result["status"])
    print("base a_hi", dec(base_hi), "bit-limited kappa gain", s5["selected_check"]["bit_limited_gain"])
    print("wrote", out_path)


if __name__ == "__main__":
    main()
