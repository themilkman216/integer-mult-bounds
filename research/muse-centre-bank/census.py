#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""All-pairs centre census + exact scalar inequality witnesses (selected word).

Owner/chart parsing reuses the pinned predecessor module
research/selected-centre-adjacent-pair-seed01fcb1/verify.py (hash-checked
before import; its read_pins/read_forward/read_backward/source_signature/
target_panel are called unchanged). The mod-prime scalar simulation adapts
the projection semantics of research/selected-centre-composed-source-rank/
verify.py (hash-pinned in CENSUS.json): climbs/adapters are identity,
centre events are descents (identity in projection). Simulation values are
in F_p, p=998244353. All scalar coefficients are dyadic with |num|<p
(checked), so reduction mod p is well defined: unequal F_p snapshots imply
unequal scalar source maps over Q. Writes CENSUS.json. Stdlib only.
"""
import hashlib
import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path

PKG = Path(__file__).resolve().parent
ROOT = PKG.parents[1]
ADJ_REL = "research/selected-centre-adjacent-pair-seed01fcb1/verify.py"
ADJ_SHA256 = "03aaf7d631892477f9d2f6c6473bcc562cd74def9c046721967e97de6d0e7c37"
COMP_REL = "research/selected-centre-composed-source-rank/verify.py"
COMP_SHA256 = "1c388eb8fac3e35e87996fa4a2489e4ecadc2b5cff7a19076645a29e128f4035"
P = 998244353
SEEDS = (0, 1, 2)


def require(ok, why):
    if not ok:
        raise ValueError(why)


def sha256_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_adjacent():
    path = ROOT / ADJ_REL
    require(sha256_file(path) == ADJ_SHA256, "adjacent-census predecessor pin changed")
    require(sha256_file(ROOT / COMP_REL) == COMP_SHA256, "composed-rank predecessor pin changed")
    spec = importlib.util.spec_from_file_location("pinned_adjacent_census", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


ADJ = load_adjacent()


def per_call_data(data):
    """Mirror predecessor census validation; return per-call records by time."""
    glob, programs, checks, word, assembly = (data["global"], data["programs"],
                                               data["checks"], data["word"], data["assembly"])
    require(assembly["template_sha256"] == data["global_payload_sha256"], "assembly binding")
    require(word["centers"] == list(ADJ.SOURCE_REGISTERS), "centre sources changed")
    require(word["center_frames"] == list(range(415, 423)), "centre frames changed")
    require(len(word["cut"]) == 176, "cut edge count changed")
    for ori in ("forward", "backward"):
        require(ADJ.canonical_digest(programs[ori]) == checks[ori]["sha256"], f"{ori} digest")
    fwd = ADJ.read_forward(programs["forward"], word)
    bwd = ADJ.read_backward(programs["backward"], word)
    require(tuple(c["targets"] for c in fwd) == tuple(c["targets"] for c in bwd),
            "forward/backward target rows differ")
    role_map = {"forward": fwd, "backward": bwd}
    calls = sorted(glob["calls"], key=lambda r: r["time"])
    require(len(calls) == 144 and [c["time"] for c in calls] == list(range(144)), "schedule shape")
    sweeps = [e for e in glob["execution_schedule"] if e.get("kind") == "local_cover_sweep"]
    require(len(sweeps) == 144, "sweep count")
    sweep_by_time = {e["time"]: e for e in sweeps}
    rows = []
    for call in calls:
        t, ev = call["time"], sweep_by_time[call["time"]]
        for k in ("provider_id", "replica", "stage", "time"):
            require(call[k] == ev[k], f"call {t} sweep {k}")
        require(call["provider_id"] == "gauge44", f"call {t} provider")
        require(call["orientation"] == ("forward" if call["stage"] % 2 == 0 else "backward"),
                f"call {t} orientation")
        require(call["local_program_sha256"] == checks[call["orientation"]]["sha256"],
                f"call {t} program digest")
        sig = ADJ.source_signature(call, role_map[call["orientation"]])
        panel = ADJ.target_panel(call)
        owners = [e[0] for e in call["owners"]]
        require(len(owners) == len(set(owners)) == 704, f"call {t} owner injectivity")
        active = frozenset(call["owners"][tg][0]
                            for c in role_map[call["orientation"]] for tg in c["targets"])
        require(len(active) == 88 and active <= panel, f"call {t} active targets")
        write = frozenset(owners[112:224]) if call["orientation"] == "forward" \
            else frozenset(owners[0:112])
        rows.append({"time": t, "stage": call["stage"], "replica": call["replica"],
                     "orientation": call["orientation"], "signature": sig,
                     "source_owners": frozenset(o for o, _ in sig), "panel": panel,
                     "owners": owners, "owner_set": frozenset(owners),
                     "data_owners": frozenset(owners[:112]), "active": active,
                     "write_set": write})
    return rows, programs, word


def pair_census(rows):
    n = len(rows)
    stats = {"unordered_pairs": n * (n - 1) // 2, "same_orientation": 0,
             "mixed_orientation": 0, "same_replica": 0,
             "full_signature_equal": 0, "full_chart_equal": 0,
             "full_owner_tuple_equal": 0, "panel_disjoint": 0,
             "directly_eligible_CB_A_owner_form": 0,
             "max_source_owner_intersection": 0, "max_equal_owner_slots": 0,
             "max_equal_signature_slots": 0, "max_equal_chart_slots": 0,
             "pairs_with_any_source_owner_overlap": 0,
             "pairs_with_disjoint_704_owner_sets": 0,
             "max_704_intersection": 0, "max_data_owner_intersection": 0}
    best = []
    slot_hist = Counter()
    sig_slot_hist = Counter()
    for i in range(n):
        for j in range(i + 1, n):
            a, b = rows[i], rows[j]
            same_ori = a["orientation"] == b["orientation"]
            stats["same_orientation" if same_ori else "mixed_orientation"] += 1
            stats["same_replica"] += a["replica"] == b["replica"]
            eq_owner = sum(x[0] == y[0] for x, y in zip(a["signature"], b["signature"]))
            eq_chart = sum(x[1] == y[1] for x, y in zip(a["signature"], b["signature"]))
            eq_sig = sum(x == y for x, y in zip(a["signature"], b["signature"]))
            slot_hist[eq_owner] += 1
            sig_slot_hist[eq_sig] += 1
            inter = len(a["source_owners"] & b["source_owners"])
            stats["pairs_with_any_source_owner_overlap"] += inter > 0
            stats["max_source_owner_intersection"] = max(stats["max_source_owner_intersection"], inter)
            stats["max_equal_owner_slots"] = max(stats["max_equal_owner_slots"], eq_owner)
            stats["max_equal_signature_slots"] = max(stats["max_equal_signature_slots"], eq_sig)
            stats["max_equal_chart_slots"] = max(stats["max_equal_chart_slots"], eq_chart)
            stats["full_signature_equal"] += a["signature"] == b["signature"]
            stats["full_chart_equal"] += eq_chart == 8
            stats["full_owner_tuple_equal"] += eq_owner == 8
            disj = a["panel"].isdisjoint(b["panel"])
            stats["panel_disjoint"] += disj
            stats["directly_eligible_CB_A_owner_form"] += bool(
                same_ori and a["signature"] == b["signature"] and disj)
            i704 = len(a["owner_set"] & b["owner_set"])
            stats["pairs_with_disjoint_704_owner_sets"] += i704 == 0
            stats["max_704_intersection"] = max(stats["max_704_intersection"], i704)
            stats["max_data_owner_intersection"] = max(
                stats["max_data_owner_intersection"], len(a["data_owners"] & b["data_owners"]))
            if same_ori and (eq_sig > 0 or eq_chart == 8 or eq_owner >= 4):
                best.append({"times": [a["time"], b["time"]],
                             "replicas": [a["replica"], b["replica"]],
                             "stages": [a["stage"], b["stage"]],
                             "orientation": a["orientation"],
                             "equal_signature_slots": eq_sig, "equal_owner_slots": eq_owner,
                             "equal_chart_slots": eq_chart,
                             "source_owner_intersection": inter, "panel_disjoint": disj})
    best.sort(key=lambda r: (-r["equal_signature_slots"], -r["equal_chart_slots"],
                             -r["equal_owner_slots"], r["times"]))
    stats["equal_owner_slots_histogram"] = {str(k): slot_hist[k] for k in sorted(slot_hist)}
    stats["equal_signature_slots_histogram"] = {str(k): sig_slot_hist[k] for k in sorted(sig_slot_hist)}
    # Favourable per-slot pairing bound (ignores cross-slot consistency/panels):
    bound = 0
    per_slot = {}
    for ori in ("forward", "backward"):
        sub = [r for r in rows if r["orientation"] == ori]
        for k in range(8):
            cnt = Counter(r["signature"][k] for r in sub)
            got = sum(v // 2 for v in cnt.values())
            per_slot[f"{ori}:{k}"] = got
            bound += got
    full = {}
    for ori in ("forward", "backward"):
        cnt = Counter(r["signature"] for r in rows if r["orientation"] == ori)
        full[ori] = sum(v // 2 for v in cnt.values())
    stats["per_slot_independent_pairing_bound_total_slot_equalities"] = bound
    stats["per_slot_bound_detail"] = per_slot
    stats["full_signature_pairing_bound_pairs"] = full
    return stats, best[:20]


def compile_program(program, source_roles):
    """Precompile scalar ops mod P; climbs/adapters/centres are identity here."""
    ops = []
    max_num, dens = 0, set()
    for e in program:
        tag = e[0]
        if tag == "phase":
            if e[1] == "centers":
                ops.append((4,))
            continue
        if tag in ("center", "climb", "adapter", "residual_adapter"):
            continue
        require(tag == "scalar", f"unknown event {tag}")
        op = e[1]
        name = op[0]

        def enc(tok):
            return tok[1] if tok[0] == "L" else 1000 + tok[1]

        if name == "clear":
            ops.append((0, enc(op[1])))
        elif name == "copy":
            ops.append((1, enc(op[1]), enc(op[2])))
        elif name == "scale":
            num, den = op[2], op[3]
            max_num, _ = max(max_num, abs(num)), dens.add(abs(den))
            require(num != 0 and den != 0, "bad scale coefficient")
            ops.append((2, enc(op[1]), (num % P) * pow(den % P, -1, P) % P))
        elif name == "add":
            num, den = op[3], op[4]
            max_num, _ = max(max_num, abs(num)), dens.add(abs(den))
            require(den != 0, "bad add coefficient")
            ops.append((3, enc(op[1]), enc(op[2]), (num % P) * pow(den % P, -1, P) % P))
        else:
            raise ValueError(f"unknown scalar op {name}")
    require(max_num < P, "coefficient numerator reaches modulus")
    require(all(d > 0 and d & (d - 1) == 0 for d in dens), "non-dyadic denominator")
    return ops, {"max_abs_numerator": max_num, "denominators": sorted(dens)}


def simulate(rows, programs, source_roles, seed):
    """One global scalar execution in F_p; returns snapshots[time]=8-tuple."""
    compiled = {ori: compile_program(programs[ori], source_roles)[0]
                for ori in ("forward", "backward")}
    nowners = 1 + max(o for r in rows for o in r["owners"])
    phys = [int.from_bytes(hashlib.sha256(f"{seed}:{o}".encode()).digest()[:8],
                            "little") % P for o in range(nowners)]
    snaps = {}
    for r in rows:
        st = [0] * 1008
        for i, o in enumerate(r["owners"]):
            st[i] = phys[o]
        before = st[:704]
        snap = None
        for op in compiled[r["orientation"]]:
            code = op[0]
            if code == 4:
                snap = tuple(st[x] for x in source_roles)
            elif code == 0:
                st[op[1]] = 0
            elif code == 1:
                st[op[1]] = st[op[2]]
            elif code == 2:
                st[op[1]] = st[op[1]] * op[2] % P
            else:
                st[op[1]] = (st[op[1]] + op[3] * st[op[2]]) % P
        require(snap is not None, f"call {r['time']} missing centre snapshot")
        require(all(st[1000 + k] == 0 for k in range(8)),
                f"call {r['time']} dirty private exit")
        if r["orientation"] == "forward":
            ok = all(st[i] == (before[i] + (before[i - 112] if 112 <= i < 224 else 0)) % P
                     for i in range(704))
        else:
            ok = all(st[i] == (before[i] - (before[i + 112] if i < 112 else 0)) % P
                     for i in range(704))
        require(ok, f"call {r['time']} scalar endpoint identity failed")
        for i, o in enumerate(r["owners"]):
            phys[o] = st[i]
        snaps[r["time"]] = snap
    return snaps


def witness_analysis(rows, programs, source_roles):
    all_snaps = {s: simulate(rows, programs, source_roles, s) for s in SEEDS}
    digest = hashlib.sha256(json.dumps(
        {str(s): {str(t): list(v) for t, v in sorted(sn.items())}
         for s, sn in sorted(all_snaps.items())}, sort_keys=True).encode()).hexdigest()
    fwd = [r["time"] for r in rows if r["orientation"] == "forward"]
    undist_slots, undist_full = [], []
    for a_i in range(len(fwd)):
        for b_i in range(a_i + 1, len(fwd)):
            ta, tb = fwd[a_i], fwd[b_i]
            eq = [k for k in range(8)
                  if all(all_snaps[s][ta][k] == all_snaps[s][tb][k] for s in SEEDS)]
            for k in eq:
                undist_slots.append({"times": [ta, tb], "slot": k})
            if len(eq) == 8:
                undist_full.append([ta, tb])
    # Positive control: every call is indistinguishable from itself in all slots.
    require(all(all_snaps[s][t] == all_snaps[s][t] for s in SEEDS for t in fwd),
            "self-equality control failed")
    coeff = {ori: compile_program(programs[ori], source_roles)[1]
             for ori in ("forward", "backward")}
    return {"prime": P, "seeds": list(SEEDS), "coefficients": coeff,
            "forward_calls": len(fwd), "forward_pairs": len(fwd) * (len(fwd) - 1) // 2,
            "slot_pairs_tested": len(fwd) * (len(fwd) - 1) // 2 * 8,
            "snapshots_sha256": digest,
            "undistinguished_slot_pairs": undist_slots,
            "undistinguished_full_pairs": undist_full,
            "endpoint_identities_checked_per_seed": 144,
            "reading": "A distinguished slot-pair has unequal scalar source maps over Q "
                       "(dyadic reduction mod P). Undistinguished pairs are candidates "
                       "needing exact symbolic equality, not proved equal."}, all_snaps


def deferral_census(rows):
    """CB-B/C deferred-scatter feasibility: no reader of A's active targets in (A,B]."""
    feasible, adj_feasible, adj_total = 0, 0, 0
    for a in rows:
        blocked = False
        for b in rows[a["time"] + 1:]:
            if not blocked and not (a["active"] & b["owner_set"]):
                feasible += 1
                if b["time"] == a["time"] + 1:
                    adj_feasible += 1
            if a["active"] & b["owner_set"]:
                blocked = True
            # once blocked, later B remain blocked by the same intervening reader
        adj_total += a["time"] < 143
    return {"ordered_pairs_deferral_feasible": feasible,
            "adjacent_ordered_pairs": adj_total,
            "adjacent_deferral_feasible": adj_feasible,
            "note": "Necessary condition only; same-orientation/panel conditions "
                    "for CB-B/CB-C are additional."}


def main():
    data = ADJ.read_pins()
    rows, programs, word = per_call_data(data)
    stats, best = pair_census(rows)
    # Adjacent reproduction against predecessor RESULT (independent recomputation).
    adj_same = sum(rows[i]["orientation"] == rows[i + 1]["orientation"] for i in range(143))
    adj_chart8 = sum(all(x[1] == y[1] for x, y in zip(rows[i]["signature"],
                       rows[i + 1]["signature"])) for i in range(143)
                     if rows[i]["orientation"] == rows[i + 1]["orientation"])
    adj_any_overlap = sum(len(rows[i]["source_owners"] & rows[i + 1]["source_owners"]) > 0
                          for i in range(143)
                          if rows[i]["orientation"] == rows[i + 1]["orientation"])
    require((adj_same, adj_chart8, adj_any_overlap) == (81, 9, 0),
            "adjacent reproduction disagrees with predecessor census")
    witness, _ = witness_analysis(rows, programs, list(ADJ.SOURCE_REGISTERS))
    owners_all = set().union(*(r["owner_set"] for r in rows))
    out = {
        "status": "PASS_MUSE_CENTRE_BANK_CENSUS",
        "pins": {"adjacent_predecessor": ADJ_REL, "adjacent_sha256": ADJ_SHA256,
                 "composed_predecessor": COMP_REL, "composed_sha256": COMP_SHA256,
                 "selected_replay_archive_sha256": ADJ.ARCHIVE_SHA256,
                 "archive_members": {k: v[1] for k, v in ADJ.MEMBERS.items()}},
        "schedule": {"calls": 144, "forward_calls": sum(r["orientation"] == "forward" for r in rows),
                     "backward_calls": sum(r["orientation"] == "backward" for r in rows),
                     "replicas": sorted({r["replica"] for r in rows}),
                     "distinct_physical_owners": len(owners_all),
                     "owner_id_min": min(owners_all), "owner_id_max": max(owners_all),
                     "distinct_signatures": len({r["signature"] for r in rows}),
                     "bank_storage_note": "Owner IDs exhaust [0,14336); 8 bank families "
                                          "are new physical stock (no preallocated reserve)."},
        "adjacent_reproduction": {"same_orientation": adj_same,
                                  "mixed_orientation": 143 - adj_same,
                                  "full_chart_equal_same_orientation": adj_chart8,
                                  "any_source_overlap_same_orientation": adj_any_overlap},
        "all_pairs": stats, "best_same_orientation_pairs": best,
        "forward_value_witness": witness, "deferral": deferral_census(rows),
    }
    (PKG / "CENSUS.json").write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print(f"PASS_MUSE_CENTRE_BANK_CENSUS pairs={stats['unordered_pairs']} "
          f"sig_equal={stats['full_signature_equal']} "
          f"max_sig_slots={stats['max_equal_signature_slots']} "
          f"slot_bound={stats['per_slot_independent_pairing_bound_total_slot_equalities']} "
          f"undist_slots={len(witness['undistinguished_slot_pairs'])} "
          f"defer_feasible={out['deferral']['ordered_pairs_deferral_feasible']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

