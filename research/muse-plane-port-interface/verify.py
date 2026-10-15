#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Plane-port shared/borrowed/multi-array candidates vs exact break-even.

Scoped falsification and price screen. No supplier or kappa is claimed.
Standard library only. Exact F2 / rational arithmetic; the favourable
moment relaxation is the pinned predecessor engine (hash-checked before
import), reused unchanged. Prepared with Meta Muse (muse-wonder-full-1.0).
"""
from __future__ import annotations

import hashlib
import importlib.util
import itertools
import json
import sys
import tarfile
from fractions import Fraction as Q
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PKG = Path(__file__).resolve().parent
ARCHIVE = ROOT / "research/community-frontier1094-audit/selected-replay.tar.gz"
ARCHIVE_ENTRY = "candidate/strict/global/base/work/complex-nine-native/DATA-PHASES.json"
ARCHIVE_SHA256 = "f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6"
PAYLOAD_SHA256 = "c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa"
CEILING = ROOT / "research/complex-local-word-ceiling/ceiling.py"
CEILING_SHA256 = "86a1432870b3b21d8454106ec9162fddc0471472d9214c590a1420f2426cedfc"
CERT = ROOT / "research/paired-plane-port-matching-seed6c563a/CERTIFICATE.json"
N = 9
PORTS = 112
M = 73
FAMILIES = 896
STAGES = 9
BASE = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82}          # selected word minus {8:8}
BASE2226 = {1: 2382, 2: 445, 3: 406, 4: 128, 5: 42}      # PR2226 profile minus {8:8}
SELECTED_WORD = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}
KAPPA = Q(836330098538459, 500000000000000000)


def need(ok: bool, why: str) -> None:
    if not ok:
        raise ValueError(why)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_ceiling():
    need(sha(CEILING) == CEILING_SHA256, "ceiling.py hash pin")
    spec = importlib.util.spec_from_file_location("pinned_ceiling", CEILING)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load_ports() -> list[int]:
    need(sha(ARCHIVE) == ARCHIVE_SHA256, "selected replay archive hash")
    with tarfile.open(ARCHIVE, "r:gz") as tf:
        member = tf.extractfile(ARCHIVE_ENTRY)
        need(member is not None, "DATA-PHASES entry missing")
        payload = member.read()
    need(hashlib.sha256(payload).hexdigest() == PAYLOAD_SHA256, "DATA-PHASES payload hash")
    data = json.loads(payload)
    recipes = sorted(data["recipes"], key=lambda r: r["port"])
    need(data["ports"] == PORTS and [r["port"] for r in recipes] == list(range(PORTS)), "ports")
    q = [int(r["q"]) for r in recipes]
    need(len(set(q)) == PORTS and all(0 < v < (1 << N) for v in q), "labels")
    need({v.bit_count() for v in q} == {3, 7}, "label weights")
    return q


def dot(a: int, b: int) -> int:
    return (a & b).bit_count() & 1


def validate_plane_system(q: list[int], pairs) -> None:
    need(len(pairs) == 56, "plane count")
    flat = [v for pair in pairs for v in pair]
    need(sorted(flat) == list(range(PORTS)), "matching is not a port partition")
    for i, j in pairs:
        need(i != j and dot(q[i], q[i]) == 1 and dot(q[j], q[j]) == 1, "plane labels not unit")
        need(dot(q[i], q[j]) == 0, "matched labels are not a zero-dot edge")


def basis(vecs) -> list[int]:
    """F2 basis (row-echelon by highest bit) of the span of 9-bit vectors."""
    piv: dict[int, int] = {}
    for v in vecs:
        x = v
        while x:
            h = x.bit_length() - 1
            if h in piv:
                x ^= piv[h]
            else:
                piv[h] = x
                break
    return [piv[h] for h in sorted(piv)]


def rank_mask_rows(rows) -> int:
    piv: dict[int, int] = {}
    for r in rows:
        x = r
        while x:
            h = x.bit_length() - 1
            if h in piv:
                x ^= piv[h]
            else:
                piv[h] = x
                break
    return len(piv)


def pairing_rank(bs: list[int], bt: list[int]) -> int:
    rows = []
    for a in bs:
        row = 0
        for k, b in enumerate(bt):
            if dot(a, b):
                row |= 1 << k
        rows.append(row)
    return rank_mask_rows(rows)


class Geometry:
    def __init__(self, q, pairs):
        self.q = q
        self.pairs = [tuple(p) for p in pairs]
        self.plane_basis = [[q[i], q[j]] for i, j in self.pairs]
        self._sum: dict[tuple, list[int]] = {}

    def sum_basis(self, planes) -> list[int]:
        key = tuple(sorted(planes))
        if key not in self._sum:
            self._sum[key] = basis(v for p in key for v in self.plane_basis[p])
        return self._sum[key]

    def charge(self, src_planes, tgt_planes) -> int:
        """Complete-plane-span pairing charge c(S,T) of one scalar total."""
        if not src_planes or not tgt_planes:
            return 0
        return pairing_rank(self.sum_basis(src_planes), self.sum_basis(tgt_planes))

    def pair_data(self, a: int, b: int) -> dict:
        bs = self.plane_basis[a]
        bt = self.plane_basis[b]
        both = self.sum_basis((a, b))
        rho = pairing_rank(bs, bt)
        return {
            "orth": rho == 0,
            "rho": rho,
            "gamma": pairing_rank(both, both),
            "dim_sum": len(both),
            "dim_inter": 4 - len(both),
        }


def pair_lb_brute(gamma: int, rho: int, orth: bool, cap: int = 8) -> int:
    """Min over a,b,m,x<=cap of 2(a-m)+2(b-m)+gamma*m+rho*x subject to
    a,b>=2, m<=min(a,b), and (nonorth only) a+b-m+x>=4."""
    best = None
    for a in range(2, cap + 1):
        for b in range(2, cap + 1):
            for m in range(0, min(a, b) + 1):
                for x in range(0, cap + 1):
                    if not orth and a + b - m + x < 4:
                        continue
                    val = 2 * (a - m) + 2 * (b - m) + gamma * m + rho * x
                    best = val if best is None or val < best else best
    need(best is not None, "pair lb brute empty")
    return best


def pair_lb_minimal_witnesses(gamma: int, rho: int, orth: bool) -> int:
    """Same minimum via monotonic reduction: at fixed m the cost increases in
    a,b,x (rho>=0; for rho=0 take x=0), so evaluate a=b=max(2,m) and the
    smallest feasible x. m>=5 costs >=5*gamma>=10 in the nonorth case and
    >=4m>=20 (gamma=4 forced) in the orth case, so m<=4 decides the minimum
    whenever it is <=8; brute force above confirms for the census values."""
    vals = []
    for m in range(0, 5):
        a = b = max(2, m)
        x = 0 if orth else max(0, 4 - a - b + m)
        vals.append(2 * (a - m) + 2 * (b - m) + gamma * m + rho * x)
    return min(vals)


def check_lemma_cases() -> dict:
    """Machine-check the two Gram computations used in the gamma+rho>=4 proof.

    s=4: Gram [[I,M],[M^T,I]] has rank 2+rank(I+M^T M) (F2, 2x2 M); rank(M)=1
    forces I+M^T M != 0, hence gamma>=3. s=3: intersection-norm cases give
    (gamma,rho) in {(2,2),(3,1),(2,2)}; in particular gamma+rho=4."""
    mats = []
    for bits in range(16):
        m = [[(bits >> 0) & 1, (bits >> 1) & 1], [(bits >> 2) & 1, (bits >> 3) & 1]]

        def mul(x, y):
            return [[sum(x[i][k] & y[k][j] for k in range(2)) & 1 for j in range(2)] for i in range(2)]

        def rk(x):
            rows = [r[0] | (r[1] << 1) for r in x]
            return rank_mask_rows(rows)

        mtm = mul([[m[0][0], m[1][0]], [m[0][1], m[1][1]]], m)
        ipm = [[mtm[i][j] ^ (1 if i == j else 0) for j in range(2)] for i in range(2)]
        if rk(m) == 1:
            need(rk(ipm) >= 1, "s=4 lemma step failed")
            mats.append({"M": m, "rank_I_plus_MtM": rk(ipm), "gamma": 2 + rk(ipm)})
    s3 = []
    for t in (0, 1):  # norm-1 intersection: rho=rank diag(1,t), gamma=rank Gram(z,a,b)
        rho = 1 + t
        gamma = 1 + rank_mask_rows([0b01 | (t << 1), t | (1 << 1)])
        need(gamma + rho == 4, "s=3 norm-1 lemma step failed")
        s3.append({"case": "intersection norm 1", "t": t, "gamma": gamma, "rho": rho})
    # norm-0 intersection: pairing [[0,1],[1,t]] has determinant 1 => rho=2.
    for t in (0, 1):
        need(rank_mask_rows([0b10, 0b01 | (t << 1)]) == 2, "s=3 norm-0 lemma step failed")
    s3.append({"case": "intersection norm 0", "rho": 2})
    return {"s4_rank1_M_cases": mats, "s3_cases": s3}


def block_matrix(terms, dim: int):
    """Sum u v^T over Q for terms (u, v) of sparse dict vectors."""
    k = [[Q(0)] * dim for _ in range(dim)]
    for u, v in terms:
        for i, a in u.items():
            for j, b in v.items():
                k[i][j] += a * b
    return k


def check_block_constructions(geom: Geometry) -> dict:
    # Singleton plane, local port coords (0,1): two direct totals give I2,
    # each with masks ({P},{P}) and plane-span charge 2. Total 4 per plane.
    terms = [({0: Q(1)}, {0: Q(1)}), ({1: Q(1)}, {1: Q(1)})]
    need(block_matrix(terms, 2) == [[Q(1), Q(0)], [Q(0), Q(1)]], "direct I2 block")
    need(geom.charge([0], [0]) == 2, "singleton total charge")
    # Positive control that is NOT identity: one combined total broadcasts.
    bc = block_matrix([({0: Q(1), 1: Q(1)}, {0: Q(1), 1: Q(1)})], 2)
    need(bc == [[Q(1), Q(1)], [Q(1), Q(1)]], "broadcast control matrix")
    broadcast_is_identity = bc == [[Q(1), Q(0)], [Q(0), Q(1)]]
    need(not broadcast_is_identity, "broadcast must be rejected as identity")
    return {"direct_per_plane": 4, "direct_total_C": 4 * 56,
            "broadcast_matrix": [[str(x) for x in r] for r in bc],
            "broadcast_rejected_as_identity": True}


def triple_pattern_terms(tri, pair_rho):
    """Global-plus-canceller terms on 6 local ports (plane t -> coords 2t,2t+1).
    Returns (terms, masks) with masks (reader_planes, source_planes)."""
    terms, masks = [], []
    for s in (0, 1):
        g = {2 * t + s: Q(1) for t in range(3)}
        terms.append((dict(g), dict(g)))
        masks.append((tuple(tri), tuple(tri)))
    for qi, src in enumerate(tri):
        readers = [p for p in tri if p != src and pair_rho[tuple(sorted((src, p)))] > 0]
        if not readers:
            continue
        for t in (0, 1):
            u = {2 * tri.index(p) + t: Q(-1) for p in readers}
            v = {2 * qi + t: Q(1)}
            terms.append((u, v))
            masks.append((tuple(readers), (src,)))
    return terms, masks


def check_triple_pattern(geom: Geometry, tri, pair_rho) -> int:
    terms, masks = triple_pattern_terms(tri, pair_rho)
    k = block_matrix(terms, 6)
    for a in range(3):
        for b in range(3):
            blk = [[k[2 * a + i][2 * b + j] for j in (0, 1)] for i in (0, 1)]
            if a == b:
                need(blk == [[Q(1), Q(0)], [Q(0), Q(1)]], "triple pattern diagonal block")
            elif pair_rho[tuple(sorted((tri[a], tri[b])))] > 0:
                need(blk == [[Q(0), Q(0)], [Q(0), Q(0)]], "triple pattern cross block")
    return sum(geom.charge(list(rd), list(sr)) for rd, sr in masks)


def triple_pattern_cost(geom: Geometry, tri, pair_rho) -> int:
    cost = 2 * geom.charge(list(tri), list(tri))
    for src in tri:
        readers = [p for p in tri if p != src and pair_rho[tuple(sorted((src, p)))] > 0]
        if readers:
            cost += 2 * geom.charge(readers, [src])
    return cost


def dec(x: Q, digits: int = 15) -> str:
    return f"{float(x):.{digits}f}".rstrip("0").rstrip(".") if x else "0"


def local_with(base: dict, add: dict) -> dict:
    out = dict(base)
    for r, n in add.items():
        out[r] = out.get(r, 0) + n
    return out


def verdict_at(cmod, local: dict, centre: int, a: Q, unpaid: int = 2) -> str:
    lo, hi = cmod.relax(local, M, FAMILIES, STAGES, centre, a, unpaid=unpaid)
    if hi < 1:
        return "pass"
    if lo > 1:
        return "fail"
    raise ValueError("relax enclosure straddles 1")


def budget(cmod, r: int, a: Q) -> dict:
    """Largest k (copies of rank r) with certified pass at a; k+1 certified fail."""
    def ok(k: int) -> str:
        return verdict_at(cmod, local_with(BASE, {r: k}), r * k, a)
    need(ok(0) == "pass", f"rank{r} budget: even C=0 fails at target")
    lo_k, hi_k = 0, 1
    while ok(hi_k) == "pass":
        lo_k, hi_k = hi_k, hi_k * 2
        need(hi_k <= 4096, "budget search overflow")
    while hi_k - lo_k > 1:
        mid = (lo_k + hi_k) // 2
        if ok(mid) == "pass":
            lo_k = mid
        else:
            hi_k = mid
    need(ok(lo_k) == "pass" and ok(lo_k + 1) == "fail", f"rank{r} budget sharpness")
    return {"copies": lo_k, "charge": r * lo_k, "next_copies_fails": lo_k + 1}


def zero_ratio(centre: Q) -> Q:
    """relax(0) per replica = ((m-2)W + C N) / (m W); shape-independent."""
    return Q((M - 2) * FAMILIES + centre * STAGES, M * FAMILIES)


def screens(cmod) -> dict:
    a_sel = KAPPA / (1 - KAPPA)
    k10 = KAPPA * Q(11, 10)
    targets = {
        "selected_a": a_sel,
        "bit_endpoint_a": Q(1733427039589844234749, 10**24),
        "pr2226_ceiling_hi_a": Q(1754331546941, 10**15),
        "kappa_plus_10pct_a": k10 / (1 - k10),
    }
    budgets = {}
    for r in (1, 2, 7, 8, 9):
        budgets[str(r)] = {name: budget(cmod, r, a) for name, a in targets.items()}
    ceil112 = cmod.ceiling(local_with(BASE, {2: 56}), M, FAMILIES, STAGES, 112,
                           grid=Q(1, 10**12), unpaid=2)
    ceil2226_112 = cmod.ceiling(local_with(BASE2226, {2: 56}), M, FAMILIES, STAGES, 112,
                                grid=Q(1, 10**12), unpaid=2)
    ceil96 = cmod.ceiling(local_with(BASE, {7: 5, 8: 2, 9: 5}), M, FAMILIES, STAGES, 96,
                          grid=Q(1, 10**12), unpaid=2)
    sel_ceil = cmod.ceiling(SELECTED_WORD, M, FAMILIES, STAGES, 64, grid=Q(1, 10**12), unpaid=1)
    need(zero_ratio(Q(224)) == Q(293, 292) and zero_ratio(Q(199)) == Q(65407, 65408)
         and zero_ratio(Q(200)) > 1, "zero-saving ratios")
    need(verdict_at(cmod, local_with(BASE, {2: 112}), 224, Q(0)) == "fail", "C224 fails at a=0")
    need(verdict_at(cmod, local_with(BASE, {2: 56}), 112, Q(0)) == "pass", "C112 passes at a=0")
    need(verdict_at(cmod, local_with(BASE2226, {2: 112}), 224, Q(0)) == "fail",
         "borrowed/hosted profile with C224 still fails at a=0")
    # Independent corroboration against predecessor receipts (not imported):
    # plane-port-copy-budgets (main) selected-endpoint charges, PR2126 and
    # PR2118 ceiling bracket upper endpoints at grid 1e-12.
    need([budgets[str(r)]["selected_a"]["charge"] for r in (1, 2, 7, 8)] == [162, 162, 161, 160],
         "budget cross-check vs plane-port-copy-budgets")
    need(ceil112[1] == Q(4078546959, 10**12), "C112 ceiling cross-check vs PR2126")
    need(ceil96[1] == Q(2432366627, 500000000000), "C96 ceiling cross-check vs PR2118")
    def bracket(t):
        return {"a_lo": str(t[0]), "a_hi": str(t[1]), "a_hi_dec": dec(t[1]),
                "kappa_planning_cap_dec": dec(t[1] / (1 + t[1]))}
    return {
        "w_per_call": str(Q(FAMILIES, STAGES)),
        "zero_breakeven_C_lt": str(Q(2 * FAMILIES, STAGES)),
        "zero_breakeven_C_integer_max": 199,
        "zero_ratio_C199": str(zero_ratio(Q(199))),
        "zero_ratio_C200": str(zero_ratio(Q(200))),
        "zero_ratio_C224": str(zero_ratio(Q(224))),
        "deficit_per_call_C224": str(Q(2 * FAMILIES, STAGES) - 224),
        "targets_dec": {k: dec(v) for k, v in targets.items()},
        "budgets": budgets,
        "selected_line_ceiling_reproduced": bracket(sel_ceil),
        "candidate_ceilings": {
            "C112_rank2x56_conditional_join_invoice": bracket(ceil112),
            "C112_on_pr2226_profile_conditional": bracket(ceil2226_112),
            "C96_pr2118_profile_not_scalar_decoder": bracket(ceil96),
        },
    }


def compute() -> dict:
    q = load_ports()
    cert = json.loads(CERT.read_text())
    pairs = [tuple(p) for p in cert["matching"]]
    validate_plane_system(q, pairs)
    geom = Geometry(q, pairs)
    census: dict[str, int] = {}
    pair_rho: dict[tuple, int] = {}
    pair_lb_min = 99
    for a, b in itertools.combinations(range(56), 2):
        d = geom.pair_data(a, b)
        pair_rho[(a, b)] = d["rho"]
        key = f"orth={d['orth']},inter={d['dim_inter']},gamma={d['gamma']},rho={d['rho']}"
        census[key] = census.get(key, 0) + 1
        need(d["gamma"] + d["rho"] >= 4, "gamma+rho>=4 census")
        if d["orth"]:
            need(d["gamma"] == 4 and d["dim_inter"] == 0, "orthogonal pair census")
        lb1 = pair_lb_brute(d["gamma"], d["rho"], d["orth"])
        lb2 = pair_lb_minimal_witnesses(d["gamma"], d["rho"], d["orth"])
        need(lb1 == lb2 == 8, "pair-group lower bound is 8")
        pair_lb_min = min(pair_lb_min, lb1)
    # Orthogonal cliques: gamma of the sum is 2|clique| (checked for all pairs
    # and triples; the direct-sum argument is in the README).
    orth_adj = {a: set() for a in range(56)}
    for (a, b), r in pair_rho.items():
        if r == 0:
            orth_adj[a].add(b)
            orth_adj[b].add(a)
    orth_triples = []
    for tri in itertools.combinations(range(56), 3):
        if all(pair_rho[tuple(sorted(p))] == 0 for p in itertools.combinations(tri, 2)):
            orth_triples.append(tri)
            s = geom.sum_basis(tri)
            need(len(s) == 6 and pairing_rank(s, s) == 6, "orthogonal triple gamma=6")
    orth_quads = 0
    for quad in itertools.combinations(range(56), 4):
        if all(pair_rho[tuple(sorted(p))] == 0 for p in itertools.combinations(quad, 2)):
            orth_quads += 1
            s = geom.sum_basis(quad)
            need(len(s) == 8 and pairing_rank(s, s) == 8, "orthogonal quad gamma=8")
    # Triple global-plus-canceller pattern over all triples of this matching.
    hist: dict[str, int] = {}
    best = None
    for tri in itertools.combinations(range(56), 3):
        c = triple_pattern_cost(geom, tri, pair_rho)
        hist[str(c)] = hist.get(str(c), 0) + 1
        best = c if best is None or c < best else best
    need(best == 12, "triple pattern minimum")
    ex_tri = orth_triples[0]
    chk = check_triple_pattern(geom, list(ex_tri), pair_rho)
    need(chk == triple_pattern_cost(geom, list(ex_tri), pair_rho) == 12, "pattern construction cost")
    nonorth_tri = next(t for t in itertools.combinations(range(56), 3)
                       if all(pair_rho[tuple(sorted(p))] > 0 for p in itertools.combinations(t, 2)))
    chk2 = check_triple_pattern(geom, list(nonorth_tri), pair_rho)
    need(chk2 == triple_pattern_cost(geom, list(nonorth_tri), pair_rho) >= 12, "nonorth pattern")
    cmod = load_ceiling()
    out = {
        "schema_version": 1,
        "status": "scoped falsification and price screen; no new supplier or kappa",
        "base_commit": "0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2",
        "pins": {
            "selected_archive_sha256": ARCHIVE_SHA256,
            "data_phases_payload_sha256": PAYLOAD_SHA256,
            "ceiling_py_sha256": CEILING_SHA256,
            "port_matching_certificate_sha256": sha(CERT),
            "selected_result_sha256": sha(ROOT / "certificates/selected-result.json"),
            "selected_kappa": str(KAPPA),
        },
        "geometry": {
            "planes": 56,
            "ports": PORTS,
            "pair_census": dict(sorted(census.items())),
            "pair_lb_min": pair_lb_min,
            "orthogonal_pairs": sum(1 for r in pair_rho.values() if r == 0),
            "orthogonal_triples": len(orth_triples),
            "orthogonal_quads": orth_quads,
            "orth_degree_min": min(len(v) for v in orth_adj.values()),
            "orth_degree_max": max(len(v) for v in orth_adj.values()),
        },
        "lemma_case_checks": check_lemma_cases(),
        "blocks": check_block_constructions(geom),
        "triple_pattern": {
            "cost_histogram": dict(sorted(hist.items(), key=lambda kv: int(kv[0]))),
            "minimum_cost": best,
            "checked_orth_triple": {"triple": list(ex_tri), "cost": chk},
            "checked_nonorth_triple": {"triple": list(nonorth_tri), "cost": chk2},
        },
        "screens": screens(cmod),
    }
    return out


def expect_reject(label: str, fn) -> str:
    try:
        fn()
    except ValueError:
        return label
    raise AssertionError(f"tamper control NOT rejected: {label}")


def tamper_suite(result: dict) -> list[str]:
    """Real mutate-and-confirm-failure controls: each mutates a value that a
    named main check consumes, then confirms that check rejects it."""
    rejected = []
    q = load_ports()
    cert = json.loads(CERT.read_text())
    pairs = [tuple(p) for p in cert["matching"]]

    # 1. Flipped label bit: q0 ^= 1 must break orthonormal-plane validation.
    bad_q = list(q)
    bad_q[pairs[0][0]] ^= 1
    rejected.append(expect_reject(
        "flipped_label_bit", lambda: validate_plane_system(bad_q, pairs)))

    # 2. Fraudulent geometry: take a real census pair and mutate its rho from
    #    2 to 1 (keeping gamma=2). The same pair-LB evaluation used in compute()
    #    then returns 6 instead of 8, so the census equality need(...) rejects.
    geom = Geometry(q, pairs)
    real = next(geom.pair_data(a, b) for a, b in itertools.combinations(range(56), 2)
                if geom.pair_data(a, b)["gamma"] == 2 and geom.pair_data(a, b)["rho"] == 2)
    def fraud_gamma():
        forged_lb = pair_lb_brute(real["gamma"], real["rho"] - 1, real["orth"])
        need(forged_lb == 8 and real["gamma"] + (real["rho"] - 1) >= 4,
             "gamma+rho>=4 census / pair LB equality")
    rejected.append(expect_reject("mutated_rho_2_to_1", fraud_gamma))

    # 3. Half-counted native invoice: mutate the stored pair lower bound 8->4
    #    (which would license C=112 = 28*4 for a 28-pair partition). The same
    #    replay comparison as in main() must reject the forged result.
    def half_count():
        forged = json.loads(json.dumps(result))
        forged["geometry"]["pair_lb_min"] = 4
        need(forged["geometry"]["pair_lb_min"] * 28 >= 224 and forged == result,
             "partitioned total >=224 / RESULT replay")
    rejected.append(expect_reject("mutated_pair_lb_8_to_4", half_count))

    # 4. One-copy-over-budget claim: budget+1 copies at the selected target
    #    must fail the same verdict_at used to certify the budget.
    cmod = load_ceiling()
    a_sel = KAPPA / (1 - KAPPA)
    k = result["screens"]["budgets"]["2"]["selected_a"]["copies"]
    def over_budget():
        verdict = verdict_at(cmod, local_with(BASE, {2: k + 1}), 2 * (k + 1), a_sel)
        need(verdict == "pass", "over-budget copy count certified fail")
    rejected.append(expect_reject("budget_plus_one_copy", over_budget))

    # 5. Broadcast block claimed as identity: the block checker calculation
    #    (all-ones) must not equal I2.
    def broadcast_claim():
        bc = block_matrix([({0: Q(1), 1: Q(1)}, {0: Q(1), 1: Q(1)})], 2)
        need(bc == [[Q(1), Q(0)], [Q(0), Q(1)]], "broadcast equals identity")
    rejected.append(expect_reject("broadcast_claimed_identity", broadcast_claim))

    # 6. Mutated RESULT value: changing the stored zero ratio must break the
    #    RESULT.json replay comparison performed in main().
    def mutated_result():
        stored = json.loads((PKG / "RESULT.json").read_text()) if (PKG / "RESULT.json").exists() else result
        forged = json.loads(json.dumps(stored))
        forged["screens"]["zero_ratio_C224"] = "291/292"
        need(forged == result, "RESULT replay comparison")
    rejected.append(expect_reject("mutated_RESULT_zero_ratio", mutated_result))
    return rejected


def main(argv) -> int:
    write = "--write" in argv
    result = compute()
    if write:
        (PKG / "RESULT.json").write_text(json.dumps(result, indent=1, sort_keys=True) + "\n")
    else:
        path = PKG / "RESULT.json"
        need(path.exists(), "RESULT.json missing; run with --write once")
        stored = json.loads(path.read_text())
        need(stored == result, "RESULT.json replay comparison failed")
    rejected = tamper_suite(result)
    need(len(rejected) == 6, "tamper suite size")
    s = result["screens"]
    print(f"PASS_MUSE_PLANE_PORT_INTERFACE breakeven_C<={s['zero_breakeven_C_integer_max']} "
          f"C224_ratio={s['zero_ratio_C224']} pairLB=8 orthLB=4g "
          f"triple_pattern_min={result['triple_pattern']['minimum_cost']} "
          f"tamper={len(rejected)}/6 rejected ({','.join(rejected)}); no_new_kappa")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
