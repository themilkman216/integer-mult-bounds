#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent recomputation + value-mutating tamper controls for muse-centre-bank.

Default mode is read-only: recomputes decisive ceiling brackets/signs, the
rank-8 break-even bracket, the all-pairs census counts and the full F_p
witness simulation, compares them with SCREEN.json/CENSUS.json/RESULT.json,
and runs tamper controls that mutate real values (word, target, snapshots,
signatures, stored brackets, pins) and require detection. `--write` first
assembles RESULT.json from SCREEN.json+CENSUS.json, then verifies it.
Standard library only; checks use require(), never assert (safe under -O).
"""
import copy
import hashlib
import importlib.util
import json
import sys
from fractions import Fraction as Q
from pathlib import Path

PKG = Path(__file__).resolve().parent
ROOT = PKG.parents[1]
GRID = Q(1, 10**12)
M, FAM, ST, NCALLS = 73, 896, 9, 144
WORD = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}
SHARED = {**WORD, 8: 4}
FUSED = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 16: 4}


def require(ok, why):
    if not ok:
        raise ValueError(why)


def sha256_file(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def load_module(name, path, expected_sha):
    require(sha256_file(path) == expected_sha, f"{name} pin changed: {path}")
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


SCREEN = json.loads((PKG / "SCREEN.json").read_text())
CENSUS = json.loads((PKG / "CENSUS.json").read_text())
CEIL = load_module("pinned_ceiling_verify", ROOT / SCREEN["pins"]["ceiling_py"],
                   SCREEN["pins"]["ceiling_py_sha256"])
K_SEL, A_SEL = Q(SCREEN["targets"]["kappa_selected"]), Q(SCREEN["targets"]["a_selected"])
K_LEAD, A_LEAD = Q(SCREEN["targets"]["kappa_lead_2374_unreviewed"]), Q(SCREEN["targets"]["a_lead"])
require(A_SEL == K_SEL / (1 - K_SEL) and A_LEAD == K_LEAD / (1 - K_LEAD), "target algebra")


def bracket(local, centre):
    lo, hi = CEIL.ceiling(local, M, FAM, ST, centre, grid=GRID)
    return str(lo), str(hi)


def sign_at(local, centre, a):
    lo, hi = CEIL.relax(local, M, FAM, ST, centre, a)
    require(hi < 1 or lo > 1, "unseparated sign")
    return "PASS_below_1" if hi < 1 else "FAIL_above_1", str(lo), str(hi)


def check_screen():
    require(SCREEN["status"] == "PASS_MUSE_CENTRE_BANK_SCREEN", "screen status")
    require(SCREEN["word"]["local_mass"] == 5586, "word mass")
    for key, prof, cen in (("base_centre64", WORD, 64),
                           ("ideal_shared_centre32", SHARED, 32),
                           ("fused16_centre64_CB_C_free", FUSED, 64)):
        lo, hi = bracket(prof, cen)
        got = SCREEN["ceilings"][key]
        require((lo, hi) == (got["a_lo"], got["a_hi"]), f"{key} bracket drift")
        s, slo, shi = sign_at(prof, cen, A_LEAD)
        skey = {"base_centre64": "base", "ideal_shared_centre32": "ideal_shared",
                "fused16_centre64_CB_C_free": "fused16_CB_C_free"}[key]
        require(s == SCREEN["signs_at_a_lead"][skey]["sign"], f"{key} sign drift")
        require((slo, shi) == (SCREEN["signs_at_a_lead"][skey]["relax_lo"],
                               SCREEN["signs_at_a_lead"][skey]["relax_hi"]),
                f"{key} relax interval drift")
    require(SCREEN["signs_at_a_lead"]["base"]["sign"] == "FAIL_above_1", "base must fail lead")
    require(SCREEN["signs_at_a_lead"]["fused16_CB_C_free"]["sign"] == "FAIL_above_1",
            "CB-C must fail lead")
    require(Q(SCREEN["ceilings"]["fused16_centre64_CB_C_free"]["a_hi"]) < A_LEAD,
            "CB-C ceiling must sit below a_lead")
    # Full rank-8 break-even recomputation (binary search on tenths).
    stored = SCREEN["breakeven_overhead_on_shared"]["at_a_lead"]["8"]
    lp, lf = Q(stored["L_pass"]), Q(stored["L_fail"])
    require(lf - lp == Q(1, 10), "break-even grid step")

    def passes(mass):
        prof = dict(SHARED)
        prof[8] = Q(prof[8]) + mass / 8
        return CEIL.relax(prof, M, FAM, ST, 32 + mass, A_LEAD)[1] < 1

    def fails(mass):
        prof = dict(SHARED)
        prof[8] = Q(prof[8]) + mass / 8
        return CEIL.relax(prof, M, FAM, ST, 32 + mass, A_LEAD)[0] > 1

    require(passes(lp) and fails(lf), "stored break-even signs do not recompute")
    lo_t, hi_t = 0, 640
    require(passes(Q(0)) and fails(Q(64)), "break-even search endpoints")
    while hi_t - lo_t > 1:
        mid = (lo_t + hi_t) // 2
        if passes(Q(mid, 10)):
            lo_t = mid
        else:
            require(fails(Q(mid, 10)), "break-even monotonicity")
            hi_t = mid
    require(Q(lo_t, 10) == lp and Q(hi_t, 10) == lf, "break-even bracket drift")
    # Net-saving threshold: ideal removal is 576 rank-8 children over 144 calls.
    tot = SCREEN["breakeven_overhead_on_shared"]["integer_totals_over_144_calls_at_a_lead"]["8"]
    require(tot["T_pass"] == 572 and tot["T_fail"] == 573, "integer break-even drift")
    require(576 - tot["T_pass"] == 4, "net rank-8 threshold must be 4 children")


def check_census_and_witness():
    require(CENSUS["status"] == "PASS_MUSE_CENTRE_BANK_CENSUS", "census status")
    cen = load_module("centre_bank_census", PKG / "census.py",
                      sha256_file(PKG / "census.py"))  # self-consistency load
    data = cen.ADJ.read_pins()
    rows, programs, _word = cen.per_call_data(data)
    stats, _best = cen.pair_census(rows)
    for k in ("unordered_pairs", "same_orientation", "mixed_orientation", "same_replica",
              "full_signature_equal", "full_chart_equal", "full_owner_tuple_equal",
              "panel_disjoint", "directly_eligible_CB_A_owner_form",
              "max_source_owner_intersection", "max_equal_owner_slots",
              "max_equal_signature_slots", "max_equal_chart_slots",
              "pairs_with_any_source_owner_overlap",
              "per_slot_independent_pairing_bound_total_slot_equalities"):
        require(stats[k] == CENSUS["all_pairs"][k], f"census count drift: {k}")
    require(stats["full_signature_equal"] == 0 and stats["max_equal_signature_slots"] == 0,
            "signature falsification core changed")
    witness, snaps = cen.witness_analysis(rows, programs, list(cen.ADJ.SOURCE_REGISTERS))
    stored = CENSUS["forward_value_witness"]
    require(witness["snapshots_sha256"] == stored["snapshots_sha256"], "snapshot digest drift")
    require(witness["undistinguished_slot_pairs"] == [] == stored["undistinguished_slot_pairs"],
            "forward witness must distinguish every slot pair")
    require(witness["slot_pairs_tested"] == 25280, "witness coverage")
    return cen, rows, programs, snaps


def tamper_controls(cen, rows, snaps):
    done = []
    # 1. Mutated word (+1 rank-1 child) must strictly lower the base ceiling.
    _, hi_mut = bracket({**WORD, 1: WORD[1] + 1}, 64)
    require(Q(hi_mut) < Q(SCREEN["ceilings"]["base_centre64"]["a_hi"]),
            "control 1: mutated word not detected")
    done.append("mutated_word_lowers_ceiling")
    # 2. Mutated leaderboard target digits must change a_lead (stored value rejected).
    mut_k = Q("0.0016971949519")
    require(mut_k / (1 - mut_k) != A_LEAD, "control 2: mutated target not detected")
    done.append("mutated_target_rejected")
    # 3. Mutating one snapshot slot to another call's value creates an
    #    undistinguished slot under the same equality test (test has power).
    fwd = [r["time"] for r in rows if r["orientation"] == "forward"]
    ta, tb = fwd[0], fwd[1]
    mut = copy.deepcopy(snaps)
    for s in cen.SEEDS:
        lst = list(mut[s][tb])
        lst[0] = mut[s][ta][0]
        mut[s][tb] = tuple(lst)
    require(all(mut[s][ta][0] == mut[s][tb][0] for s in cen.SEEDS),
            "control 3 setup failed")
    require(not all(snaps[s][ta][0] == snaps[s][tb][0] for s in cen.SEEDS),
            "control 3: unmutated pair unexpectedly equal")
    mut_digest = hashlib.sha256(json.dumps(
        {str(s): {str(t): list(v) for t, v in sorted(sn.items())}
         for s, sn in sorted(mut.items())}, sort_keys=True).encode()).hexdigest()
    require(mut_digest != CENSUS["forward_value_witness"]["snapshots_sha256"],
            "control 3: mutated snapshots keep stored digest")
    done.append("mutated_snapshot_detected")
    # 4. Mutating one signature owner+chart forces a signature-slot equality.
    rows_mut = copy.deepcopy(rows)
    sig = list(rows_mut[1]["signature"])
    sig[0] = rows_mut[0]["signature"][0]
    rows_mut[1]["signature"] = tuple(sig)
    stats_mut, _ = cen.pair_census(rows_mut)
    require(stats_mut["max_equal_signature_slots"] >= 1,
            "control 4: mutated signature not detected")
    done.append("mutated_signature_detected")
    # 5. Tampered break-even (claim L_fail passes) must fail sign recomputation.
    stored = SCREEN["breakeven_overhead_on_shared"]["at_a_lead"]["8"]
    lf = Q(stored["L_fail"])
    prof = dict(SHARED)
    prof[8] = Q(prof[8]) + lf / 8
    s, _, _ = sign_at(prof, 32 + lf, A_LEAD)
    require(s == "FAIL_above_1", "control 5: tampered break-even accepted")
    done.append("tampered_breakeven_rejected")
    # 6. Wrong pin hash must be rejected before any module code runs.
    try:
        load_module("bad_pin", ROOT / SCREEN["pins"]["ceiling_py"], "0" * 64)
    except ValueError:
        done.append("wrong_pin_rejected")
    else:
        raise ValueError("control 6: wrong pin accepted")
    # 7. CB-C with centre charge tampered 64->32 (free mass deletion) would
    #    pass; require the honest C=64 sign to differ (invoice sensitivity).
    s_free, _, _ = sign_at(FUSED, 32, A_LEAD)
    s_honest, _, _ = sign_at(FUSED, 64, A_LEAD)
    require(s_free == "PASS_below_1" and s_honest == "FAIL_above_1",
            "control 7: centre-charge tamper indistinguishable")
    done.append("centre_charge_tamper_distinguished")
    return done


def assemble_result(controls):
    return {
        "status": "PASS_MUSE_CENTRE_BANK_VERIFY",
        "verdict": {
            "CB_A_forward": "FALSIFIED on fixed schedule: 0/25280 forward slot pairs "
                            "undistinguished (exact F_p witnesses); attainable saving 0 "
                            "rank-8 children vs >=4 required (relaxation) to beat #2374.",
            "CB_A_reverse": "FALSIFIED stronger: max equal (owner,chart) slots 0/8 over "
                            "all 10296 pairs; PR1748 shared-sink condition never met.",
            "CB_B": "ZERO GAIN by construction (16 R8/pair retained); deferral timing "
                    "feasible for 1712 ordered pairs, so accounting, not timing, kills it.",
            "CB_C": "FALSIFIED at relaxation: free universal fused ceiling "
                    "a_hi=0.001693625548 < a_lead=0.001700080319 (certified FAIL sign).",
            "construction_attempted": False,
            "reason": "No contract survives its cheapest test; stop rule applies.",
        },
        "screen_file_sha256": sha256_file(PKG / "SCREEN.json"),
        "census_file_sha256": sha256_file(PKG / "CENSUS.json"),
        "screen": SCREEN, "census": CENSUS, "tamper_controls": controls,
    }


def main():
    check_screen()
    cen, rows, _programs, snaps = check_census_and_witness()
    controls = tamper_controls(cen, rows, snaps)
    result = assemble_result(controls)
    if "--write" in sys.argv:
        (PKG / "RESULT.json").write_text(json.dumps(result, indent=1, sort_keys=True) + "\n")
        print("WROTE RESULT.json")
    else:
        stored = json.loads((PKG / "RESULT.json").read_text())
        require(stored == result, "RESULT.json drift (rerun screen/census, then --write)")
    print(f"PASS_MUSE_CENTRE_BANK_VERIFY controls={len(controls)} "
          f"sig_slots_max=0 undist_slots=0 fused=FAIL no_new_kappa")
    return 0


if __name__ == "__main__":
    sys.exit(main())
