#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact bit-side wall screen: helper skeletons, copy charge, data algebra.

Reuses the pinned exact interval engine in
research/complex-local-word-ceiling/ceiling.py (PR1240) at the selected
PR589 bit parameters (m=64, 888 families / 9 stages, copy charge 63),
cross-checked against the independent engine receipt of
research/bit-revision3-levers-seed03 (RESULT.json root bracket).
Every ceiling is a certified grid bracket [lo, hi] with relax(lo) < 1 <
relax(hi) under the stated local profile; idle mass sits at rank R
(R=45 legal, R=50/53 labelled halving-depth what-ifs). A ceiling bounds
every completion with that local profile under the coverage law; it is
not a construction and not an endpoint. The exact moment
(1/W) sum_r n_r (r/m)^(1-a) < 1 of a completed word remains the
acceptance test. No new supplier and no new kappa are claimed.

Standard library only. Meta Muse (muse-wonder-full-1.0) assisted;
see README.md.

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
M = 64
FAM, ST, CST = 888, 9, 63
# Per-call class split of the selected PR589 bit word, replayed in
# research/bit-revision3-levers-seed03 (RESULT.json replay.class_split);
# the split is asserted to sum to the recorded local histogram below.
SRC = {1: 317, 2: 209, 3: 10, 4: 3}
TGT = {1: 10, 2: 92, 5: 92, 6: 10, 7: 9}
HLP = {1: 969, 2: 1041, 3: 69, 4: 41, 5: 1, 6: 1, 7: 1}
TOT = {1: 27, 5: 9}
COP = {7: 9}
LOCAL = {1: 1323, 2: 1342, 3: 79, 4: 44, 5: 102, 6: 11, 7: 19}
A_BIT = Q(1733427039589844234749, 1000000000000000000000000)
A_COMPLEX = Q(67018507072324140917, 40000000000000000000000)
KAPPA = Q(836330098538459, 500000000000000000)


def add(*hs):
    out = {}
    for h in hs:
        for r, n in h.items():
            out[r] = out.get(r, Q(0)) + Q(n)
    return {r: n for r, n in out.items() if n}


def mass(h):
    return sum(r * Q(n) for r, n in h.items())


def dec(x, digits=12):
    return f"{float(x):.{digits}g}"


def frac(x):
    return f"{x.numerator}/{x.denominator}"


def cap(local, families=FAM, centre=CST):
    return C.ceiling(local, M, families, ST, centre, grid=GRID)


def sign(enc):
    if enc[1] < 1:
        return -1
    if enc[0] > 1:
        return 1
    return 0


def relax_R(local, families, centre, a, R):
    """Exact enclosure with idle rank R (R=50/53 need a new row bound)."""
    C.require(1 <= R < M, "idle rank range")
    w = Q(families, ST)
    idle = (M - 1) * w + Q(centre) - mass(local)
    C.require(idle >= 0, "local mass exceeds coverage total")
    lo = hi = Q(0)
    for r, n in local.items():
        c = C.child_cost(r, M, a)
        lo, hi = lo + Q(n) * c[0], hi + Q(n) * c[1]
    c = C.child_cost(R, M, a)
    lo, hi = lo + (idle / R) * c[0], hi + (idle / R) * c[1]
    return C.down(lo / w), C.up(hi / w)


def max_helpers(make_local, target_a, R=45, kmax=600):
    """Largest integer k in [0,kmax] with relax(target_a) < 1 certified.

    make_local(k) -> per-call profile. Returns (k_pass, k_fail) with
    certified opposite signs, (None, 0) if k=0 fails, (kmax, None) if
    every k up to kmax passes.
    """
    def passes(k):
        loc = make_local(k)
        try:
            if R == 45:
                return sign(C.relax(loc, M, FAM, ST, CST, target_a))
            return sign(relax_R(loc, FAM, CST, target_a, R))
        except ValueError:
            return 1  # exceeds the coverage law: no idle room left

    if passes(0) != -1:
        return None, 0
    if passes(kmax) == -1:
        return kmax, None
    lo, hi = 0, kmax
    while hi - lo > 1:
        mid = (lo + hi) // 2
        s = passes(mid)
        C.require(s != 0, "enclosure too wide in helper search")
        if s == -1:
            lo = mid
        else:
            hi = mid
    C.require(passes(lo) == -1 and passes(hi) == 1, "helper bracket signs")
    return lo, hi


def max_added_mass(target_a, base_local, add_rank, step=Q(1, 10)):
    """Largest added rank mass L (grid `step`) with relax(target_a) < 1.

    Same convention as the round-1 package: added work is billed as
    fractional rank-`add_rank` children inside the coverage total.
    """
    q = C.model(base_local, M, FAM, ST, CST)
    idle_max = q["idle_mass"]

    def passes(L):
        local = dict(base_local)
        local[add_rank] = Q(local.get(add_rank, 0)) + L / add_rank
        return sign(C.relax(local, M, FAM, ST, CST, target_a))

    if passes(Q(0)) != -1:
        return None, Q(0)
    n_max = int(idle_max / step)
    lo_n, hi_n = 0, n_max + 1
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
    C.require(passes(L_pass) == -1, "added-mass lower sign")
    if L_fail is not None:
        C.require(passes(L_fail) == 1, "added-mass upper sign")
    return L_pass, L_fail


def req_a(kappa_t):
    return kappa_t / (1 - kappa_t)


DATA_SHIP = add(SRC, TGT)
BASE_S = add(DATA_SHIP, TOT, COP)          # + k rank-8 helpers (totals shipped)


def local_s(k):
    """Shipped data + shipped totals + copies + k single-climb rank-8 helpers.

    Shipped value is k=430 fragmented helpers (mass 3440); here the same
    count is billed as 430 rank-8 children (mass 3440). Total helper
    registers = k + 9 (the retained totals).
    """
    return add(BASE_S, {8: k})


def local_i(K):
    """Ideal data (222 rank-7) + copies (9 rank-7) + K rank-8 helpers.

    Seed03 joint-surface convention: totals idealised into the K count.
    """
    return add({7: 231}, {8: K})


def main():
    out_path = HERE / "RESULT.json"
    if "--out" in sys.argv:
        out_path = Path(sys.argv[sys.argv.index("--out") + 1])

    C.require(add(SRC, TGT, HLP, TOT, COP) == {r: Q(n) for r, n in LOCAL.items()},
              "class split must sum to the recorded local histogram")
    C.require(mass(LOCAL) == 5129 and mass(HLP) + mass(TOT) == 3512
              and mass(DATA_SHIP) == 1554, "class masses 5129 = 1554 + 3512 + 63")

    pins = {
        "base_commit": "0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2",
        "engine": "research/complex-local-word-ceiling/ceiling.py",
        "engine_sha256": hashlib.sha256((ENGINE_DIR / "ceiling.py").read_bytes()).hexdigest(),
        "seed03_result": "research/bit-revision3-levers-seed03/RESULT.json",
        "seed03_result_sha256": hashlib.sha256(
            (ROOT / "research/bit-revision3-levers-seed03/RESULT.json").read_bytes()).hexdigest(),
        "selected_record": "certificates/selected-result.json",
        "selected_record_sha256": hashlib.sha256(
            (ROOT / "certificates/selected-result.json").read_bytes()).hexdigest(),
        "grid": "1/10^12",
        "bit_word_per_call": {str(r): n for r, n in sorted(LOCAL.items())},
        "a_bit_selected": frac(A_BIT),
        "a_complex_selected": frac(A_COMPLEX),
        "kappa_selected": frac(KAPPA),
    }

    targets = {
        "bit_endpoint": A_BIT,
        "kappa_x1.05_required_a": req_a(KAPPA * Q(21, 20)),
        "kappa_x1.10_required_a": req_a(KAPPA * Q(11, 10)),
        "kappa_x2_required_a": req_a(KAPPA * 2),
        "a_0.003": Q(3, 1000),
        "a_0.005": Q(1, 200),
        "planning_1_99": Q(1, 99),
    }

    # --- B0: base reproduction and controls ---------------------------------
    base_lo, base_hi = cap(LOCAL)
    C.require(A_BIT < base_lo, "selected bit endpoint below relaxation bracket")
    worse = dict(LOCAL)
    worse[1] += 1
    _, worse_hi = cap(worse)
    C.require(worse_hi < base_hi, "control: one extra rank-1 child lowers the ceiling")
    for a_test in (A_BIT, base_lo, Q(1, 99)):
        C.require(C.relax(LOCAL, M, FAM, ST, CST, a_test)
                  == relax_R(LOCAL, FAM, CST, a_test, 45),
                  "custom-R relax must equal pinned relax at R=45")
    seed03 = json.loads((ROOT / pins["seed03_result"]).read_text())
    s03_lo, s03_hi = Q(seed03["levers"][0]["root_lo"]), Q(seed03["levers"][0]["root_hi"])
    C.require(max(base_lo, s03_lo) < min(base_hi, s03_hi) or base_lo == s03_lo,
              "independent seed03 engine bracket must meet the pinned-engine bracket")
    ratio = A_BIT / base_hi
    targets["kappa_x1.10_ratio_adjusted_ceiling"] = targets["kappa_x1.10_required_a"] / ratio

    def entry(lo, hi):
        return {
            "a_lo": frac(lo), "a_hi": frac(hi), "a_hi_dec": dec(hi),
            "x_bit_endpoint_hi": dec(hi / A_BIT),
            "x_base_ceiling_hi": dec(hi / base_hi),
            "kappa_cap_if_bit_binds": dec(hi / (1 + hi)),
            "partner_kappa_multiple_at_most": dec((hi / (1 + hi)) / KAPPA),
        }

    result = {
        "status": "PASS_MUSE_OOD_BIT_WALL_SCREEN",
        "scope": (
            "Exact favorable relaxations of the selected PR589 bit local word "
            "under named changed hypotheses (helper skeleton, descent charge, "
            "copy charge / unit, data algebra, connector dilution, schedule). "
            "Planning budgets only: no construction, hosting, precision or "
            "supplier admission. Kappa readings use the retained planning "
            "transfer kappa=a/(1+a); the exact moment of a completed "
            "construction remains the acceptance test. Ceilings above the "
            "format-limits X(9) fence additionally escape its (Sch) slot "
            "premises and are flagged, not claimed inside that model."
        ),
        "pins": pins,
        "targets": {k: {"a": frac(v), "a_dec": dec(v), "x_bit_endpoint": dec(v / A_BIT)}
                    for k, v in targets.items()},
        "B0_base": {
            **entry(base_lo, base_hi),
            "seed03_independent_bracket": [frac(s03_lo), frac(s03_hi)],
            "realization_ratio_endpoint_over_ceiling_hi": dec(ratio),
            "one_extra_rank1_hi_dec": dec(worse_hi),
            "controls": "endpoint below bracket; extra rank-1 lowers ceiling; "
                        "custom-R == pinned relax at R=45 (3 points); seed03 bracket meets ours",
            "reading": "Ratio-adjusted partner target = required a / realization ratio: "
                       "the ceiling a word needs if it keeps the shipped endpoint/ceiling "
                       "loss. Heuristic margin, not a bound.",
        },
    }

    # --- B1: helper skeleton (chosen scope test) ----------------------------
    b1 = {"hypothesis": (
        "Shipped fragmented helper climbs (430 helpers: 969 rank-1 + 1041 rank-2 "
        "+ ... children, mass 3440) replaced by k single rank-8 climbs (mass 8k); "
        "removed helper mass becomes idle at R. Variant S keeps shipped data "
        "ladders and shipped totals; variant I idealises data to single rank-7 "
        "climbs (seed03 convention). Copies (63) kept. Monotone, drop-free: "
        "format-limits section D floors (212 sink-only / 138 strict / 222 with "
        "shipped ladders, helper registers incl. totals) still apply and are "
        "compared, not assumed away. Single-climb realisability (frames, "
        "windows, hosting) is NOT charged beyond rank shape; B2 prices descents."
    ), "ceilings_S_shipped_data": {}, "ceilings_I_ideal_data": {}, "thresholds": {}}
    for k in (430, 350, 300, 258, 222, 203, 171, 129, 0):
        lo, hi = cap(local_s(k))
        b1["ceilings_S_shipped_data"][f"k={k}"] = {
            "helper_registers_incl_totals": k + 9, **entry(lo, hi)}
    for K in (439, 332, 267, 222, 212, 180, 138, 0):
        lo, hi = cap(local_i(K))
        b1["ceilings_I_ideal_data"][f"K={K}"] = {
            "helper_registers_incl_totals": K, **entry(lo, hi)}
    thr_targets = ("kappa_x1.10_required_a", "kappa_x1.10_ratio_adjusted_ceiling",
                   "kappa_x2_required_a", "a_0.003", "planning_1_99")
    for name in thr_targets:
        ta = targets[name]
        ks, kf = max_helpers(local_s, ta)
        Ki, Kf = max_helpers(local_i, ta)
        b1["thresholds"][name] = {
            "S_shipped_data": {"k_pass": ks, "k_fail": kf,
                               "registers_pass_incl_totals": None if ks is None else ks + 9},
            "I_ideal_data": {"K_pass": Ki, "K_fail": Kf},
        }
    for R in (50, 53):
        ks, kf = max_helpers(local_s, targets["kappa_x2_required_a"], R=R)
        b1["thresholds"][f"kappa_x2_required_a_R{R}_whatif"] = {
            "S_shipped_data": {"k_pass": ks, "k_fail": kf,
                               "registers_pass_incl_totals": None if ks is None else ks + 9},
            "note": "idle cap beyond the record guard; needs the elementary-cover row bound",
        }
    b1["floors_helper_registers"] = {
        "sink_only": 212, "strict": 138, "with_shipped_data_ladders": 222, "shipped": 439,
        "source": "research/format-limits section D (drop-free monotone-chain model; "
                  "crossing lemma argued, cover numbers checked there)"}
    result["B1_helper_skeleton"] = b1

    # --- B2: descent break-evens (below-floor sibling) ----------------------
    b2 = {"hypothesis": (
        "Helpers below the monotone floors pay descents. Added work billed as "
        "fractional rank-r children inside the coverage total (0.1 mass grid, "
        "certified opposite signs). Format-limits C.7 prices a rank-1 descent "
        "at 2 mass units per call; the descent-count reading divides the "
        "rank-1-shaped budget by 2 (pessimistic shape) and is labelled as such."
    ), "budgets_at_kappa_x2": {}}
    for k in (203, 171, 141, 129):
        row = {"helper_registers_incl_totals": k + 9}
        for r in (1, 8):
            Lp, Lf = max_added_mass(targets["kappa_x2_required_a"], local_s(k), r)
            row[f"add_rank{r}"] = {
                "L_pass": None if Lp is None else dec(Lp),
                "L_fail": None if Lf is None else dec(Lf),
                "note": ("even zero added mass fails" if Lp is None else
                         "coverage-bound hit" if Lf is None else "sharp adjacent-grid bracket"),
            }
        b2["budgets_at_kappa_x2"][f"S_k={k}"] = row
    result["B2_descent_breakeven"] = b2

    # --- B3: copy charge and deeper-puncture unit ---------------------------
    b3 = {"hypothesis": (
        "Copy charge c carried as c/7 rank-7 copies (seed03 premise; rank-8 "
        "carriage changes no seed03 conclusion). Same-unit reductions below 63 "
        "must escape the pairing-rank floor (#446 Thm C, cited in format-limits "
        "A.6: bit 111/63 status argued for punctures p<=25 only) and are shown "
        "as a price curve, not as available. Puncture row scales every non-copy "
        "count by 102/111, sets copies to 54 and families to 816 (format-limits "
        "A.6 outside-scope unit x=54/102); existence of that puncture is unproved."
    ), "cst_sweep_v111": {}}
    for c in (63, 56, 49, 42, 35, 28, 21, 14, 7, 0):
        loc = dict(LOCAL)
        loc[7] = Q(LOCAL[7] - 9) + Q(c, 7)
        lo, hi = cap(loc, centre=c)
        b3["cst_sweep_v111"][f"cst={c}"] = entry(lo, hi)
    s102 = Q(102, 111)
    scaled = add({r: Q(n) * s102 for r, n in SRC.items()},
                 {r: Q(n) * s102 for r, n in TGT.items()},
                 {r: Q(n) * s102 for r, n in HLP.items()},
                 {r: Q(n) * s102 for r, n in TOT.items()},
                 {7: Q(54, 7)})
    plo, phi = cap(scaled, families=816, centre=54)
    b3["puncture_102_54_scaled"] = {"families": 816, "w_dec": dec(Q(816, 9)), **entry(plo, phi)}
    b3["deficit_arithmetic"] = {
        "shipped_D": 28416 - 63 * 288,
        "per_replica_unit_D_111_63": 8 * 111 - 9 * 63,
        "per_replica_unit_D_102_54": 8 * 102 - 9 * 54,
        "delta_D_per_replica_unit": (8 * 102 - 9 * 54) - (8 * 111 - 9 * 63),
        "reading": "D = T[(s-1)v - s.cst] at s=9; puncturing 9 more lines at "
                   "delta-cst 9 gains only +9 per replica unit before w shrinkage",
    }
    result["B3_copy_charge_unit"] = b3

    # --- B4: data-algebra absolute bounds (register scope) ------------------
    free_data = add(HLP, TOT, COP)
    data_ideal_only = add({7: 222}, HLP, TOT, COP)
    b4 = {"hypothesis": (
        "Any register-algebra saving can only remove or reshape data-register "
        "work (sources+targets, mass 1554). free_data deletes it entirely: an "
        "absolute ceiling for every data-side algebra with shipped helpers and "
        "copies. data_ideal_only reshapes it to single rank-7 climbs."
    )}
    for label, loc in (("free_data", free_data), ("data_ideal_only", data_ideal_only)):
        lo, hi = cap(loc)
        b4[label] = {**entry(lo, hi), "verdicts": {
            name: sign(C.relax(loc, M, FAM, ST, CST, targets[name]))
            for name in ("kappa_x1.10_required_a", "kappa_x2_required_a", "planning_1_99")}}
    result["B4_data_algebra_bound"] = b4

    # --- B5: connector generous dilution bound ------------------------------
    b5 = {"hypothesis": (
        "Generous fiction: a fraction f of ALL local mass is five-source "
        "connector work whose query saving converts rank-1 mass to idle at no "
        "leaf cost. f=2/74 is the #2056 query saving (74->72; its leaf bill "
        "ties 182=182, so the true conversion is smaller); f=1/10 is a "
        "robustness fiction. No connector instance inside the selected bit "
        "supplier is identified by #2056/#2060/#2063/#2065 or here."
    )}
    for label, f in (("f=2/74", Q(1, 37)), ("f=1/10", Q(1, 10))):
        loc = dict(LOCAL)
        loc[1] = Q(LOCAL[1]) - f * mass(LOCAL)
        C.require(loc[1] > 0, "connector fiction keeps rank-1 count positive")
        lo, hi = cap(loc)
        b5[label] = entry(lo, hi)
    result["B5_connector_dilution"] = b5

    # --- B6: schedule arithmetic (Theorem S fence, unreviewed #2052) --------
    import math
    bound_dw = 1 - Q(63, 111) * Q(9, 8)
    b6 = {"hypothesis": (
        "Shear-type local words under the coverage law; any pairs per stage, "
        "mixed orientations, arbitrary block-diagonal bridges, any pair-level "
        "signed rho (#2052 Theorem S model, complex T74 pricing; bit fence "
        "checked here only as exact fraction arithmetic). Escapes named there: "
        "non-shear word, rho through a third bank class (coverage-law change), "
        "even-s attainment beyond (K=3,s=4)."
    ),
        "D_over_W_bound_s9": frac(bound_dw), "D_over_W_bound_dec": dec(bound_dw),
        "D_over_W_shipped": frac(Q(10272, 28416)), "D_over_W_shipped_dec": dec(Q(10272, 28416)),
        "attains_bound": bool(bound_dw == Q(10272, 28416)),
        "N_bound": {f"K={K},s={s}": 2 * K + math.ceil(Q(2 * K, s - 1))
                    for (K, s) in ((4, 9), (3, 4), (7, 8), (5, 11))},
        "reading": "Shipped B_K attains the per-port deficit bound at s=9; "
                   "multi-pair bit schedules inside the model cannot raise D/W",
    }
    result["B6_schedule_fence"] = b6

    text = json.dumps(result, indent=1, sort_keys=True) + "\n"
    out_path.write_text(text)
    print(result["status"])
    print("base bit a_hi", dec(base_hi), "ratio", dec(ratio))
    print("wrote", out_path)


if __name__ == "__main__":
    main()
