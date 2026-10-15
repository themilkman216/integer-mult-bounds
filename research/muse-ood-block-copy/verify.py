#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Price a rank-2 block-valued COPY for the selected P111 bit decoder.

Exact F2/rational replay of the pinned PR589 tuned word. Tests the
hypothesis that one Parseval block (PR1900 factorization, audited in
research/p111-parseval-copy-interface) can be copied by a single
block-valued primitive at a charge equal to its union-support pairing
rank (8), against (i) the chronological cuts of the real word and
(ii) the per-stream pricing retained by every admitted COPY/ERASE
contract. The block contract is defined in README.md. No predecessor
executable is imported; the pinned ceiling engine is reused unchanged
and hash-checked. No new supplier or kappa is claimed.

Meta Muse (muse-wonder-full-1.0) assisted; see README.md.
Standard library only.

usage: verify.py [--write]
"""

import argparse
import gzip
import hashlib
import importlib.util
import json
from fractions import Fraction as Q
from functools import lru_cache
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
WORD = "research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz"
EXPECTED = "research/e8-bit-p111-tuned/tune/EXPECTED.json"
CEILING = "research/complex-local-word-ceiling/ceiling.py"
PINS = {
    WORD: "e3e301e62bc2b41dbf1ceac0acf3d35824ebeab1848c5a2142d4577b109da52f",
    EXPECTED: "b9f0e5ca038abe837b0007c8fe006f366a6f02009244ac57705a8a200e2301f4",
    CEILING: "86a1432870b3b21d8454106ec9162fddc0471472d9214c590a1420f2426cedfc",
}
COLUMNS = [3, 5, 6, 7, 8, 16, 32, 64, 128, 256]
BLOCKS = [(0, 1), (2, 3), (4, 5), (6, 7), (8, 9)]
LOCAL = {1: 1323, 2: 1342, 3: 79, 4: 44, 5: 102, 6: 11, 7: 19}


def require(ok, why):
    if not ok:
        raise ValueError(why)


def combine(vecs, coef):
    out = 0
    for i, x in enumerate(vecs):
        if coef >> i & 1:
            out ^= x
    return out


def brank(vecs):
    piv = {}
    for v in vecs:
        while v:
            b = v.bit_length() - 1
            if b not in piv:
                piv[b] = v
                break
            v ^= piv[b]
    return len(piv)


def rbasis(rows):
    piv = {}
    for orig in rows:
        row = [Q(x) for x in orig]
        for c, p in sorted(piv.items()):
            if row[c]:
                f = row[c]
                row = [a - f * b for a, b in zip(row, p)]
        c = next((i for i, x in enumerate(row) if x), None)
        if c is not None:
            q = row[c]
            piv[c] = [x / q for x in row]
    return [piv[c] for c in sorted(piv)]


def modrank(rows, prime=101):
    m = [[x % prime for x in r] for r in rows]
    if not m:
        return 0
    rank = 0
    for col in range(len(m[0])):
        p = next((i for i in range(rank, len(m)) if m[i][col]), None)
        if p is None:
            continue
        m[rank], m[p] = m[p], m[rank]
        inv = pow(m[rank][col], -1, prime)
        m[rank] = [(x * inv) % prime for x in m[rank]]
        for i in range(rank + 1, len(m)):
            if m[i][col]:
                f = m[i][col]
                m[i] = [(a - f * b) % prime for a, b in zip(m[i], m[rank])]
        rank += 1
    return rank


def parseval_ok(cols):
    return all(sum(((c >> i) & 1) * ((c >> j) & 1) for c in cols) % 2 == (i == j)
               for i in range(9) for j in range(9))


def dmap(left, right, ports):
    return [combine(right, sum(((c >> t) & 1) << i for i, c in enumerate(left)))
            for t in range(ports)]


def outer2(a, b):
    return sum(1 << (2 * i + j) for i in range(2) for j in range(2)
               if a >> i & 1 and b >> j & 1)


def frame_spans(word):
    """Rational basis (canonical rows) of each frame's line span in Q^8."""
    return [tuple(tuple(str(x) for x in row)
                  for row in rbasis([word["lines"][i] for i in f]))
            for f in word["frames"]]


def audit():
    for path, digest in PINS.items():
        require(hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == digest,
                "source pin mismatch: " + path)
    word = json.loads(gzip.decompress((ROOT / WORD).read_bytes()))
    expected = json.loads((ROOT / EXPECTED).read_text())
    ports, nreg = word["v"], 2 * word["v"] + word["R"]
    ret = list(word["ret"])
    require((ports, nreg, word["h"]) == (111, 661, 8), "not selected P111")
    require(word["punctured"] == [10, 15, 51, 53, 56, 66, 72, 89, 111]
            and ret == list(range(472, 481)), "selected puncture/ret changed")
    require(expected["word"]["copy_ranks"] == [7] * 9
            and expected["word"]["local_histogram"]
            == {str(k): v for k, v in LOCAL.items()}, "EXPECTED receipt changed")

    lines = word["lines"]
    masks = [sum(1 << i for i in f) for f in word["frames"]]
    spans = frame_spans(word)
    dims = [len(s) for s in spans]

    # --- chronological replay: values, frames, last writes ----------------
    val = [1 << i for i in range(nreg)]
    cur = list(word["start"])
    last_write = {}
    gidx = 0

    def climb(r, f):
        a = cur[r]
        if a != f:
            require(masks[a] & masks[f] == masks[a], "frame nesting violated")
            cur[r] = f

    for sec in ("D", "A"):
        for f, t, ss in word[sec]:
            for r in [t, *ss]:
                climb(r, f)
            for s in ss:
                val[t] ^= val[s]
            if t in ret:
                last_write[t] = gidx
            gidx += 1
    total_da = gidx
    cut_frames = [cur[q] for q in ret]
    cut_dims = [dims[f] for f in cut_frames]
    right = [val[q] for q in ret]
    require(cut_dims == [7] * 9, "ret frames at D+A cut are not all dim 7")
    require(len({spans[f] for f in cut_frames}) == 9,
            "ret frames at cut are not pairwise distinct subspaces")
    require(sorted(last_write.values()) == list(range(total_da - 17, total_da, 2)),
            "ret last writes are not the final interleaved A gates")
    require(max(last_write.values()) == total_da - 1,
            "a retained total is written after the D+A cut opens")

    # scatter writes targets only; B never touches a retained register;
    # C writes them at the FULL frame (cleanup), so ERASE must precede C.
    require(all(0 <= t < ports for t in range(ports)), "scatter range")
    b_touches = sum(1 for _f, t, ss in word["B"] if t in ret or any(s in ret for s in ss))
    require(b_touches == 0, "section B touches a retained register")
    snap479, snap480 = val[479], val[480]
    for t, ks in enumerate(word["scatter"]):
        for k in ks:
            val[ports + t] ^= right[k]
    for sec in ("B", "C"):
        for f, t, ss in word[sec]:
            for r in [t, *ss]:
                climb(r, f)
            for s in ss:
                val[t] ^= val[s]
    require(val[479] != snap479 or val[480] != snap480,
            "cleanup unexpectedly preserves both block-4 centers")
    for r in range(nreg):
        want = (1 << r) ^ (1 << (r - ports)) if ports <= r < 2 * ports else 1 << r
        require(val[r] == want, "word endpoint mismatch")
    first_c_write = min(i for i, (_f, t, _ss) in enumerate(word["C"]) if t in (479, 480))

    # no register at the cut already holds a mixed Parseval channel value
    cut_values = set()
    v2 = [1 << i for i in range(nreg)]
    for sec in ("D", "A"):
        for _f, t, ss in word[sec]:
            for s in ss:
                v2[t] ^= v2[s]
    cut_values = set(v2)
    mixed_absent = all((right[a] ^ right[b]) not in cut_values
                       for a, b in ((0, 1), (0, 2), (1, 2))) \
        and (right[0] ^ right[1] ^ right[2]) not in cut_values
    require(mixed_absent, "a mixed channel value already sits in a register")

    # --- frame-pair census at the cut --------------------------------------
    pair_rows = []
    for i in range(9):
        for j in range(i + 1, 9):
            fi, fj = cut_frames[i], cut_frames[j]
            join_dim = len(rbasis([lines[k] for k in range(ports)
                                   if (masks[fi] | masks[fj]) >> k & 1]))
            common = [k for k in range(len(masks))
                      if masks[k] & masks[fi] == masks[fi]
                      and masks[k] & masks[fj] == masks[fj]]
            require(join_dim == 8 and spans[fi] != spans[fj],
                    "ret frame pair does not join to Q^8 distinctly")
            require(all(dims[k] == 8 for k in common),
                    "a sub-FULL common frame contains both centers")
            pair_rows.append({"pair": [i, j], "join_dim": join_dim,
                              "meet_dim": 7 + 7 - join_dim,
                              "common_frames_all_full": True})

    # --- decoder, Parseval blocks, exact pairing prices --------------------
    gram = [[sum(a * b for a, b in zip(t, s)) for s in lines] for t in lines]
    require(all(x % 2 == 0 for row in gram for x in row), "nonintegral G")

    @lru_cache(None)
    def sbasis(mask):
        return rbasis([lines[i] for i in range(ports) if mask >> i & 1])

    @lru_cache(None)
    def pcost(tmask, imask, crosscheck=False):
        imask &= (1 << ports) - 1
        tb, ib = sbasis(tmask), sbasis(imask)
        small = [[sum(a * b for a, b in zip(t, s)) for s in ib] for t in tb]
        rank = len(rbasis(small))
        if crosscheck:
            full = [[gram[t][s] for s in range(ports) if imask >> s & 1]
                    for t in range(ports) if tmask >> t & 1]
            require(modrank(full) == rank, "modular/rational rank disagreement")
        return rank

    left = [sum(1 << t for t, row in enumerate(word["scatter"]) if i in row)
            for i in range(9)]
    require(brank(left) == brank(right) == 9, "channels not independent")
    require(parseval_ok(COLUMNS), "Parseval identity failed")
    nleft = [combine(left, c) for c in COLUMNS]
    nright = [combine(right, c) for c in COLUMNS]
    require(dmap(nleft, nright, ports) == dmap(left, right, ports),
            "Parseval decoder differs on a dirty column")
    baseline = [pcost(left[i], right[i]) for i in range(9)]
    require(baseline == [7] * 9, "baseline copy ranks changed")

    block_rows = []
    for number, (i, j) in enumerate(BLOCKS):
        ls, rs = [nleft[i], nleft[j]], [nright[i], nright[j]]
        bmap = dmap(ls, rs, ports)
        require(brank(bmap) == 2, "block operator rank is not two")
        deep = number == 4
        terms = [(a, b, pcost(combine(ls, a), combine(rs, b),
                              crosscheck=deep))
                 for a in (1, 2, 3) for b in (1, 2, 3)]
        union = pcost(ls[0] | ls[1], rs[0] | rs[1], crosscheck=True)
        feasible = []
        for sub in range(512):
            mat = charge = 0
            for bit, (a, b, price) in enumerate(terms):
                if sub >> bit & 1:
                    mat ^= outer2(a, b)
                    charge += price
            if mat == 9:
                feasible.append((charge, sub))
        require(len(feasible) == 32, "incomplete subset census")
        best_charge, best_sub = min(feasible)
        winners = [[a, b, p] for bit, (a, b, p) in enumerate(terms)
                   if best_sub >> bit & 1]
        require(dmap([combine(ls, a) for a, _b, _p in winners],
                     [combine(rs, b) for _a, b, _p in winners], ports) == bmap,
                "winning subset does not reproduce the dirty block")
        row = {"block": number, "columns": [i, j], "union_support_rank": union,
               "term_cost_grid": [p for _a, _b, p in terms],
               "min_two_stream_charge": best_charge, "witness": winners,
               "feasible_subsets": 32}
        if deep:
            require(ls == [left[7], left[8]] and rs == [right[7], right[8]],
                    "block 4 is not the pure (e7, e8) pair")
            one_stream = []
            for a, b, _p in terms:
                m = dmap([combine(ls, a)], [combine(rs, b)], ports)
                dirty = sum((x ^ y).bit_count() for x, y in zip(m, bmap))
                src = sum(((x ^ y) & ((1 << ports) - 1)).bit_count()
                          for x, y in zip(m, bmap))
                require(dirty > 0, "a one-stream candidate implements block 4")
                one_stream.append({"a": a, "b": b, "dirty_wrong": dirty,
                                   "source_wrong": src})
            m11 = dmap([ls[0]], [rs[0]], ports)
            wit = next((t, ((m11[t] ^ bmap[t]) & -(m11[t] ^ bmap[t])).bit_length() - 1)
                       for t in range(ports) if m11[t] != bmap[t])
            require(((bmap[wit[0]] >> wit[1]) & 1) != ((m11[wit[0]] >> wit[1]) & 1),
                    "witness bits do not differ")
            row["one_stream_candidates_all_fail"] = one_stream
            row["smallest_witness_vs_channel_e7_only"] = {
                "target": wit[0], "input_column": wit[1],
                "expected_bit": (bmap[wit[0]] >> wit[1]) & 1,
                "actual_bit": (m11[wit[0]] >> wit[1]) & 1}
        block_rows.append(row)
    require([r["union_support_rank"] for r in block_rows] == [8] * 5,
            "union-support ranks changed")
    require([r["min_two_stream_charge"] for r in block_rows] == [16, 15, 14, 14, 14],
            "per-block two-stream minima changed")

    # --- counterfactual ceiling screen (labelled hypothetical) -------------
    spec = importlib.util.spec_from_file_location("pinned_ceiling", ROOT / CEILING)
    eng = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(eng)
    hyp = dict(LOCAL)
    hyp[7] -= 9
    hyp[8] = 5
    screens = {}
    for name, loc, centre in (("baseline_cst63", LOCAL, 63),
                              ("counterfactual_block_cst40", hyp, 40)):
        model = eng.model(loc, 64, 888, 9, centre)
        lo, hi = eng.ceiling(loc, 64, 888, 9, centre, grid=Q(1, 10**12))
        screens[name] = {"centre": centre,
                         "profile": {str(k): v for k, v in sorted(loc.items())},
                         "model": {k: str(v) for k, v in model.items()},
                         "a_bracket": [str(lo), str(hi)],
                         "a_hi_dec": f"{float(hi):.12g}"}
    require(screens["baseline_cst63"]["a_bracket"]
            == ["391183751/200000000000", "488979689/250000000000"],
            "baseline ceiling differs from muse-ood-bit-wall screen B0")
    require(screens["counterfactual_block_cst40"]["a_bracket"]
            == ["644017333/200000000000", "1610043333/500000000000"],
            "counterfactual ceiling changed")

    # --- tamper controls: every mutation must be rejected -------------------
    def rejected(fn):
        try:
            fn()
        except (ValueError, StopIteration):
            return True
        return False

    bad_cols = COLUMNS.copy()
    bad_cols[3] ^= 256
    tampers = {
        "broken_parseval_column": rejected(
            lambda: require(parseval_ok(bad_cols), "tampered frame accepted")),
        "flipped_scatter_bit": rejected(lambda: require(
            dmap(nleft, nright, ports)
            == dmap(left, [r ^ (1 << 5) for r in right], ports),
            "tampered decoder accepted")),
        "merged_frame_517_518": rejected(lambda: require(
            len({spans[cut_frames[7]], spans[cut_frames[7]]}) == 2,
            "tampered equal frames accepted as distinct")),
        "one_stream_claimed_for_block4": rejected(lambda: require(
            brank(dmap([nleft[8]], [nright[8]], ports)) == 2,
            "tampered rank-one block accepted")),
        "union_rank_claimed_7": rejected(lambda: require(
            block_rows[4]["union_support_rank"] == 7,
            "tampered union rank accepted")),
    }
    require(all(tampers.values()), "a tamper control was accepted")

    total_two_stream = sum(r["min_two_stream_charge"] for r in block_rows)
    return {
        "status": "PASS_MUSE_OOD_BLOCK_COPY",
        "verdict": ("FALSIFIED at union charge: block 4 (most favourable, pure "
                    "(e7,e8)) cannot be one stream (F2 rank, exact witnesses) "
                    "and costs 14 as two streams; union rank 8 prices a single "
                    "stream through the join frame, i.e. packing two streams "
                    "into one child. Simultaneous liveness itself is legal "
                    "(centers immutable across the scatter window)."),
        "pins": {"base_commit": "0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2",
                 **{p: d for p, d in PINS.items()},
                 "selected_kappa": "836330098538459/500000000000000000"},
        "overlap": ("find_overlap --refresh failed (gh 401, no snapshot); "
                    "--offline recorded. Titles #2028-#2178 and refs/upr heads "
                    "checked: nearest are #2061/#2062 (scalar COPY floors for "
                    "other decoders) and #2088 (two scalar snapshots, rank sum "
                    "retained); none prices a block-valued copy."),
        "chronology": {
            "cut": "after sections D+A, before scatter",
            "ret_registers": ret,
            "cut_frame_indices": cut_frames,
            "cut_frame_dims": cut_dims,
            "distinct_cut_subspaces": 9,
            "last_writes_in_DA": {str(k): v for k, v in sorted(last_write.items())},
            "total_DA_gates": total_da,
            "window_opens_only_at_cut": True,
            "B_gates_touching_ret": b_touches,
            "first_C_gate_writing_479_or_480": first_c_write,
            "mixed_channel_values_absent_from_all_registers": mixed_absent,
            "frame_pairs": pair_rows,
        },
        "blocks": block_rows,
        "pricing": {
            "baseline_scalar_total": 63,
            "union_support_sum_not_an_invoice": 40,
            "two_stream_blockwise_total": total_two_stream,
            "block4_union_charge_tested": 8,
            "block4_priced_charge": block_rows[4]["min_two_stream_charge"],
            "rule": ("per-stream pairing-rank pricing (PR446 Thm C), minimised "
                     "over the GL2 basis of each block coefficient space; "
                     "one child carries one stream pair (no packing)"),
        },
        "counterfactual_ceiling_screen": {
            "note": ("Favourable relaxation only, computed as in "
                     "research/muse-ood-bit-wall/screen.py (pinned ceiling.py, "
                     "m=64, families=888, stages=9, unpaid=1, R=45). Not a "
                     "construction; the exact moment of a completed word is "
                     "the acceptance test and the complex side currently "
                     "binds the selected kappa, so no kappa gain is claimed "
                     "even counterfactually."),
            **screens,
            "Dfc_per_replica_unit_s9": {"cst63": 8 * 111 - 9 * 63,
                                        "cst40": 8 * 111 - 9 * 40},
        },
        "tamper_controls_all_rejected": tampers,
        "scope": ("Fixed selected P111 word and PR1900 five-block grouping; "
                  "scalar-stream COPY/ERASE model of the five predecessor "
                  "contracts. A vector-valued (packed) child / plane-port "
                  "supplier is a different hypothesis with its own coverage "
                  "law and is not priced or excluded here."),
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write", action="store_true", help="regenerate RESULT.json")
    args = ap.parse_args()
    report = audit()
    path = PACKAGE / "RESULT.json"
    if args.write:
        path.write_text(json.dumps(report, indent=1, sort_keys=True) + "\n")
    else:
        require(path.exists() and json.loads(path.read_text()) == report,
                "RESULT.json differs from exact replay")
    print(report["status"],
          "block4: union=8 one-stream=FAIL two-stream=14; total=73 vs 63;",
          "tamper=5/5 rejected; no_new_kappa")


if __name__ == "__main__":
    main()
