#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Anticipatory dirty borrowing ported to the selected P111 bit word.

Exact F2 replay of the pinned word; Class-H alias census (handoff inside the
borrower's writes-only prefix); greedy iterated aliasing where every applied
alias is decided by a full endpoint replay of the modified word (D toggles
for monomial frame-zero compensation, C rebuilt as the reverse of the
aliased non-target gates); pricing by the pinned ceiling engine and by a
conditional exact global moment (288x local profile + pinned remainder,
freed mass re-hosted at rank at most 42 -- stated hypothesis, not a hosted
word). Writes RESULT.json. Standard library only.

Meta Muse (muse-wonder-full-1.0) assisted; see README.md.
"""
import copy
import gzip
import hashlib
import json
import sys
from collections import Counter, defaultdict
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORD_PATH = ROOT / "research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz"
WORD_FILE_SHA = "e3e301e62bc2b41dbf1ceac0acf3d35824ebeab1848c5a2142d4577b109da52f"
ENGINE_DIR = ROOT / "research/complex-local-word-ceiling"
ENGINE_SHA = "86a1432870b3b21d8454106ec9162fddc0471472d9214c590a1420f2426cedfc"
A_BIT = Q(1733427039589844234749, 10**24)
REM = {2: 13920, 4: 14208, 6: 14208, 7: 21312, 42: 288}  # fastc.py (tune/)
sys.path.insert(0, str(ENGINE_DIR))
import ceiling as C  # noqa: E402


def qrank(vecs):
    B = {}
    for rr in vecs:
        row = list(map(Q, rr))
        for c in sorted(B):
            q = row[c]
            row = [a - q * b for a, b in zip(row, B[c])]
        c = next((i for i, x in enumerate(row) if x), None)
        if c is not None:
            q = row[c]
            B[c] = [x / q for x in row]
    return len(B)


class Word:
    def __init__(self, w):
        self.w = w
        self.V, self.R0 = w["v"], w["R"]
        self.N = 2 * self.V + self.R0
        self.frames, self.start, self.final = w["frames"], w["start"], w["final"]
        self.fmask = [sum(1 << i for i in f) for f in self.frames]
        self.fdim = [qrank([w["lines"][i] for i in f]) for f in self.frames]
        self.full = next(i for i, m in enumerate(self.fmask) if m == (1 << self.V) - 1)
        self.ret, self.scatter = list(w["ret"]), w["scatter"]
        self.D = [[f, t, set(ss)] for f, t, ss in w["D"]]
        self.A = [[f, t, list(ss)] for f, t, ss in w["A"]]
        self.B = [[f, t, list(ss)] for f, t, ss in w["B"]]
        self.active = set(range(self.N))
        self.hosts = set()  # registers already hosting a removed helper

    def clone(self):
        c = Word.__new__(Word)
        c.__dict__.update(self.__dict__)
        c.D = [[f, t, set(ss)] for f, t, ss in self.D]
        c.A = copy.deepcopy(self.A)
        c.B = copy.deepcopy(self.B)
        c.active, c.hosts = set(self.active), set(self.hosts)
        return c

    def replay(self):
        """Full endpoint replay. Returns (profile, errors dict reg->mask)."""
        V, N = self.V, self.N
        val = {r: 1 << r for r in self.active}
        cur = {r: self.start[r] for r in self.active}
        prof = Counter()

        def climb(r, f):
            a = cur[r]
            assert self.fmask[a] & self.fmask[f] == self.fmask[a], ("nesting", r, a, f)
            if self.fdim[f] > self.fdim[a]:
                prof[self.fdim[f] - self.fdim[a]] += 1
            cur[r] = f

        def run(gates):
            for f, t, ss in gates:
                for r in [t, *ss]:
                    assert r in val, ("inactive incident", r)
                    climb(r, f)
                for s in ss:
                    val[t] ^= val[s]

        run([[f, t, sorted(ss)] for f, t, ss in self.D])
        run(self.A)
        tops = [self.fdim[cur[q]] for q in self.ret]
        snap = [val[q] for q in self.ret]
        for t, ks in enumerate(self.scatter):
            for k in ks:
                val[V + t] ^= snap[k]
        run(self.B)
        zgates = [g for g in self.A + self.B if g[1] < V or g[1] >= 2 * V]
        run([[self.full, t, list(ss)] for f, t, ss in reversed(zgates)])
        for r in self.active:
            climb(r, self.final[r])
        errors = {}
        for r in self.active:
            want = (1 << r) ^ (1 << (r - V)) if V <= r < 2 * V else (1 << r)
            if val[r] != want:
                errors[r] = val[r] ^ want
        return dict(sorted((prof + Counter(tops)).items())), errors

    # -- census -------------------------------------------------------------
    def events(self):
        return ([("A", k, g) for k, g in enumerate(self.A)]
                + [("S", -1, None)]
                + [("B", k, g) for k, g in enumerate(self.B)])

    def census(self):
        V, N = self.V, self.N
        ev = self.events()
        helpers = [r for r in range(2 * V, N) if r in self.active]
        inc, first, last = defaultdict(list), {}, {}
        for idx, (sec, k, g) in enumerate(ev):
            if sec == "S":
                for r in self.ret:
                    inc[r].append((idx, "src"))
                regs = list(self.ret) + list(range(V, 2 * V))
            else:
                f, t, ss = g
                inc[t].append((idx, "dst"))
                for s in ss:
                    inc[s].append((idx, "src"))
                regs = [t, *ss]
            for r in regs:
                if r not in first:
                    first[r] = idx
                last[r] = idx
        # forward values/cur (D cannot affect helper or X values: D writes Y)
        val = {r: 1 << r for r in self.active}
        cur = {r: self.start[r] for r in self.active}
        pre_val, pre_cur, term_val, term_cur = {}, {}, {}, {}
        for idx, (sec, k, g) in enumerate(ev):
            regs = (list(self.ret) + list(range(V, 2 * V))) if sec == "S" else [g[1], *g[2]]
            for r in regs:
                if r >= 2 * V:
                    pre_val[(r, idx)], pre_cur[(r, idx)] = val[r], cur[r]
            if sec == "S":
                snap = [val[q] for q in self.ret]
                for t, ks in enumerate(self.scatter):
                    for kk in ks:
                        val[V + t] ^= snap[kk]
            else:
                f, t, ss = g
                for r in [t, *ss]:
                    assert self.fmask[cur[r]] & self.fmask[f] == self.fmask[cur[r]]
                    cur[r] = f
                for s in ss:
                    val[t] ^= val[s]
            for r in regs:
                if r >= 2 * V and last[r] == idx:
                    term_val[r], term_cur[r] = val[r], cur[r]
        # Backward target reachability. reach_after[(r,idx)]: dependence of Y
        # finals on val[r] just AFTER event idx. reach_before[(r,idx)]: same
        # just BEFORE event idx (the correct injection pattern at a handoff).
        reach = {r: 0 for r in self.active}
        for t in range(V):
            reach[V + t] = 1 << t
        reach_after, reach_before = {}, {}
        for idx in range(len(ev) - 1, -1, -1):
            sec, k, g = ev[idx]
            regs = (list(self.ret) + list(range(V, 2 * V))) if sec == "S" else [g[1], *g[2]]
            for r in regs:
                reach_after[(r, idx)] = reach[r]
            if sec == "S":
                add = [0] * len(self.ret)
                for t, ks in enumerate(self.scatter):
                    for kk in ks:
                        add[kk] ^= reach[V + t]
                for kk, q in enumerate(self.ret):
                    reach[q] ^= add[kk]
            else:
                f, t, ss = g
                for s in ss:
                    reach[s] ^= reach[t]
            for r in regs:
                reach_before[(r, idx)] = reach[r]
        return (ev, helpers, inc, first, last, pre_val, pre_cur,
                term_val, term_cur, reach_before, reach_after)

    def candidates(self):
        """Class-G shortlist: handoff at any borrower incident event.

        Baseline pi drops input column j. Total target error at handoff t*:
        E_t = Epre_t + [t in P] * (pi(u) + pi(v_i)), where Epre accumulates
        deleted pre-handoff reads of j. D-compensable iff every E_t is
        helper-supported; checked here on X-parts only (forms never carry Y
        columns; the builder's full replay is the ground truth).
        """
        (ev, helpers, inc, first, last, pre_val, pre_cur,
         term_val, term_cur, reach_before, reach_after) = self.census()
        V, N = self.V, self.N
        xmask = (1 << V) - 1
        ymask = ((1 << (2 * V)) - 1) ^ xmask
        s_idx = next(idx for idx, e in enumerate(ev) if e[0] == "S")
        lenders = sorted(helpers, key=lambda i: last[i])
        by_x = defaultdict(list)
        for i in lenders:
            assert term_val[i] & ymask == 0
            by_x[term_val[i] & xmask].append(i)
        tax = Counter()
        out = []
        for j in helpers:
            lst = inc[j]
            epre_x = {}  # target -> X-part of prefix error form
            for k, (tstar, kind) in enumerate(lst):
                sec, kk, g = ev[tstar]
                if sec != "S" and not (j in self.ret and tstar >= s_idx):
                    tax["handoff_points"] += 1
                    Fj = g[0]
                    Pj = reach_before[(j, tstar)]
                    ux = pre_val[(j, tstar)] & xmask
                    clean_out = all(epre_x.get(t, 0) == 0
                                    for t in range(V) if not (Pj >> t) & 1)
                    in_parts = {epre_x.get(t, 0) for t in range(V) if (Pj >> t) & 1}
                    if clean_out and len(in_parts) <= 1:
                        need_x = ux ^ (next(iter(in_parts)) if in_parts else 0)
                        pool = lenders if Pj == 0 else by_x.get(need_x, [])
                        tax["handoff_compensable_x"] += 1
                        for i in pool:
                            if i == j or last[i] >= tstar:
                                continue
                            tax["chrono_triples"] += 1
                            if not (self.fmask[term_cur[i]] & self.fmask[Fj]
                                    == self.fmask[term_cur[i]]):
                                tax["seam_fail_equal_dim"
                                    if self.fdim[term_cur[i]] == self.fdim[Fj]
                                    else "seam_fail_other"] += 1
                                continue
                            tax["candidates"] += 1
                            out.append(dict(
                                lender=i, borrower=j, tstar=tstar,
                                handoff_section=sec, handoff_gate=kk,
                                prefix_incidents=k,
                                zero_response=bool(Pj == 0 and not epre_x),
                                targets_reached=bin(Pj).count("1")))
                if kind == "src" and sec != "S":
                    d = g[1]
                    form_x = pre_val[(j, tstar)] & xmask
                    ra = reach_after[(d, tstar)]
                    t = 0
                    m = ra
                    while m:
                        if m & 1:
                            epre_x[t] = epre_x.get(t, 0) ^ form_x
                        m >>= 1
                        t += 1
        return out, tax

    def taxonomy(self):
        """Base-word funnel over all Class-G handoffs x chrono lenders."""
        (ev, helpers, inc, first, last, pre_val, pre_cur,
         term_val, term_cur, reach_before, reach_after) = self.census()
        V = self.V
        xmask = (1 << V) - 1
        s_idx = next(idx for idx, e in enumerate(ev) if e[0] == "S")
        lenders = sorted(helpers, key=lambda i: last[i])
        T = Counter()
        borrowers_stage = defaultdict(set)
        best_paid = {}
        for j in helpers:
            epre_x = {}
            for k, (tstar, kind) in enumerate(inc[j]):
                sec, kk, g = ev[tstar]
                if sec != "S" and not (j in self.ret and tstar >= s_idx):
                    T["handoff_points"] += 1
                    borrowers_stage["handoff"].add(j)
                    Fj = g[0]
                    Pj = reach_before[(j, tstar)]
                    ux = pre_val[(j, tstar)] & xmask
                    if Pj == 0:
                        T["handoff_zero_response"] += 1
                    if not epre_x:
                        T["handoff_no_prefix_reads_classH"] += 1
                    clean_out = all(epre_x.get(t, 0) == 0
                                    for t in range(V) if not (Pj >> t) & 1)
                    in_parts = {epre_x.get(t, 0) for t in range(V) if (Pj >> t) & 1}
                    consistent = clean_out and len(in_parts) <= 1
                    need_x = ux ^ (next(iter(in_parts)) if in_parts else 0)
                    if not clean_out:
                        T["handoff_fail_epre_outside_P"] += 1
                    elif len(in_parts) > 1:
                        T["handoff_fail_epre_inconsistent_on_P"] += 1
                    for i in lenders:
                        if last[i] >= tstar:
                            break
                        if i == j:
                            continue
                        T["triples_chrono"] += 1
                        borrowers_stage["chrono"].add(j)
                        xclean = consistent and (Pj == 0 or (term_val[i] & xmask) == need_x)
                        if self.fmask[term_cur[i]] & self.fmask[Fj] == self.fmask[term_cur[i]]:
                            T["triples_seam_ok"] += 1
                            borrowers_stage["seam"].add(j)
                            if xclean:
                                T["triples_seam_ok_xclean"] += 1
                                borrowers_stage["candidate"].add(j)
                            else:
                                T["triples_seam_ok_xblocked"] += 1
                                dx = bin((term_val[i] & xmask) ^ need_x).count("1") if consistent else 999
                                key = (dx, bin(Pj).count("1"))
                                if j not in best_paid or key < best_paid[j]:
                                    best_paid[j] = key
                        else:
                            eq = self.fdim[term_cur[i]] == self.fdim[Fj]
                            T["triples_seam_fail_equal_dim" if eq else "triples_seam_fail_other"] += 1
                            if eq and xclean:
                                T["triples_warp_gated_xclean"] += 1
                                borrowers_stage["warp_gated"].add(j)
                if kind == "src" and sec != "S":
                    form_x = pre_val[(j, tstar)] & xmask
                    ra = reach_after[(g[1], tstar)]
                    t = 0
                    m = ra
                    while m:
                        if m & 1:
                            epre_x[t] = epre_x.get(t, 0) ^ form_x
                        m >>= 1
                        t += 1
        adds = Counter()
        for gates in (self.D, self.A, self.B):
            for f, t, ss in gates:
                adds[len(ss)] += 1
        return {"counts": dict(T),
                "distinct_borrowers": {k: len(v) for k, v in borrowers_stage.items()},
                "paid_comp_proxy_best_per_borrower": {
                    "borrowers_with_seam_ok_xblocked": len(best_paid),
                    "min_dx_distribution": dict(Counter(v[0] for v in best_paid.values())),
                    "best_examples": sorted(([j, v[0], v[1]] for j, v in best_paid.items()),
                                            key=lambda r: (r[1], r[2]))[:8]},
                "gray_tour_screen": {
                    "gate_source_count_hist": {str(k): v for k, v in sorted(adds.items())},
                    "total_row_adds_DAB": sum(k * v for k, v in adds.items()),
                    "note": "paid profile counts frame climbs only (replay()); row ADDs are not priced"}}

    # -- alias application ----------------------------------------------------
    def apply_alias(self, cand):
        """Apply alias; measure Y error; toggle D compensation; caller replays."""
        i, j, tstar = cand["lender"], cand["borrower"], cand["tstar"]
        ev = self.events()
        # positions: A gates keep order, S, B gates. Work per section with event idx.
        def transform(gates, secname, base):
            out = []
            for k, (f, t, ss) in enumerate(gates):
                idx = base + k
                if idx < tstar:
                    if t == j:
                        continue
                    ss = [s for s in ss if s != j]
                    if not ss:
                        continue
                    out.append([f, t, ss])
                else:
                    t2 = i if t == j else t
                    ss2 = [i if s == j else s for s in ss]
                    assert not (t2 == i and i in ss2), "alias self-incidence"
                    assert len(set(ss2)) == len(ss2), "alias duplicate source"
                    out.append([f, t2, ss2])
            return out

        self.A = transform(self.A, "A", 0)
        self.B = transform(self.B, "B", len(ev) - len(self.B))
        if j in self.ret:
            self.ret = [i if q == j else q for q in self.ret]
        for g in self.D:
            g[2].discard(j)
        self.active.discard(j)
        self.hosts.add(i)
        _, errors = self.replay()
        yerr = {r: m for r, m in errors.items() if self.V <= r < 2 * self.V}
        zerr = {r: m for r, m in errors.items() if not (self.V <= r < 2 * self.V)}
        assert not zerr, f"non-target restoration failed: {list(zerr)[:4]}"
        # monomial compensation: each error form must be helper-supported
        d_by_target = {t: g for _, t, g in [(g[0], g[1], g) for g in self.D]}
        comp = {}
        for r, m in yerr.items():
            supp = [c for c in range(self.N) if (m >> c) & 1]
            assert all(c >= 2 * self.V and c in self.active for c in supp), \
                f"error at target {r} not D-compensable: {supp}"
            for c in supp:
                d_by_target[r][2] ^= {c}
            comp[r] = supp
        return comp


def local_moment_float(local, a=0.0017334270395898442, m=64):
    return sum(n * (r / m) ** (1 - a) for r, n in local.items())


def global_profile(local, base_mass):
    mass = sum(r * n for r, n in local.items())
    freed = 288 * (base_mass - mass)
    g = {}
    for r, n in local.items():
        g[r] = g.get(r, 0) + 288 * n
    for r, n in REM.items():
        g[r] = g.get(r, 0) + n
    assert freed >= 0
    g[42] = g.get(42, 0) + freed // 42
    if freed % 42:
        g[freed % 42] = g.get(freed % 42, 0) + 1
    assert 64 * 28416 - sum(r * n for r, n in g.items()) == 10272
    return {r: n for r, n in sorted(g.items()) if n}


def moment_enc(gprof, a):
    lo = hi = Q(0)
    for r, n in gprof.items():
        c = C.child_cost(r, 64, a)
        lo, hi = lo + n * c[0], hi + n * c[1]
    return C.down(lo / 28416), C.up(hi / 28416)


def moment_root(gprof, grid=Q(1, 10**12)):
    lo, hi = Q(0), Q(1, 100)
    assert moment_enc(gprof, lo)[1] < 1 and moment_enc(gprof, hi)[0] > 1
    while hi - lo > grid:
        mid = Q(int((lo + hi) / 2 / grid)) * grid
        if mid <= lo:
            mid = lo + grid
        enc = moment_enc(gprof, mid)
        if enc[1] < 1:
            lo = mid
        elif enc[0] > 1:
            hi = mid
        else:
            raise ValueError("enclosure too wide")
    return lo, hi


def main():
    raw = WORD_PATH.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == WORD_FILE_SHA
    assert hashlib.sha256((ENGINE_DIR / "ceiling.py").read_bytes()).hexdigest() == ENGINE_SHA
    w = json.loads(gzip.decompress(raw))
    word = Word(w)
    base_profile, errors = word.replay()
    assert not errors, list(errors)[:4]
    assert base_profile == {1: 1323, 2: 1342, 3: 79, 4: 44, 5: 102, 6: 11, 7: 19}, base_profile
    base_mass = sum(r * n for r, n in base_profile.items())
    assert base_mass == 5129
    print("base replay PASS profile", base_profile)

    cands0, tax0 = word.candidates()
    funnel = word.taxonomy()
    print("base census:", dict(tax0), "candidates:", len(cands0))
    print("base funnel:", funnel)

    steps = []
    cur = word
    cur_score = local_moment_float(base_profile)
    while True:
        cands, _ = cur.candidates()
        best = None
        for cand in cands:
            trial = cur.clone()
            try:
                comp = trial.apply_alias(cand)
                prof, errs = trial.replay()
            except AssertionError as e:
                print("  infeasible", cand["lender"], "->", cand["borrower"], e)
                continue
            if errs:
                print("  endpoint fail", cand["lender"], "->", cand["borrower"], list(errs)[:3])
                continue
            score = local_moment_float(prof)
            if best is None or score < best[0]:
                best = (score, cand, comp, prof, trial)
        if best is None or best[0] >= cur_score - 1e-15:
            print("greedy stops:", "no candidates" if best is None else "no improvement")
            break
        score, cand, comp, prof, cur = best
        steps.append({**cand, "d_compensation": {str(k): v for k, v in comp.items()},
                      "profile_after": {str(k): v for k, v in prof.items()},
                      "mass_after": sum(r * n for r, n in prof.items()),
                      "helpers_after": 439 - len(steps) - 1})
        cur_score = score
        print(f"alias {len(steps)}: lender {cand['lender']} -> borrower {cand['borrower']} "
              f"@event {cand['tstar']} mass {steps[-1]['mass_after']} comp_targets {len(comp)}")

    final_profile, errors = cur.replay()
    assert not errors
    helpers_removed = len(steps)
    print("final profile", final_profile, "helpers removed", helpers_removed)

    grid = Q(1, 10**12)
    blo, bhi = C.ceiling(base_profile, 64, 888, 9, 63, grid=grid)
    flo, fhi = C.ceiling(final_profile, 64, 888, 9, 63, grid=grid)
    gbase, gfin = global_profile(base_profile, base_mass), global_profile(final_profile, base_mass)
    mblo, mbhi = moment_root(gbase)
    mflo, mfhi = moment_root(gfin)
    assert moment_enc(gbase, A_BIT)[1] < 1, "pinned endpoint must certify on base global profile"

    def fr(x):
        return f"{x.numerator}/{x.denominator}"

    def dec(x):
        return f"{float(x):.15g}"

    # Sensitivity (labelled histogram what-if): how many further aliases of
    # the observed shape (-1 rank-1, -1 rank-7 per alias) would the
    # conditional moment need to reach the #2226 complex ceiling a?
    a_2226 = Q(175433154694, 10**14)
    sens_k = None
    for k in range(0, 200):
        prof_k = dict(base_profile)
        prof_k[1] -= k
        prof_k[7] -= k
        if min(prof_k.values()) < 0:
            break
        if moment_enc(global_profile(prof_k, base_mass), a_2226)[1] < 1:
            sens_k = k
            break

    result = {
        "status": "PASS_MUSE_BIT_DIRTY_BORROWING_BUILD",
        "scope": ("Exact F2 alias construction on the pinned selected P111 bit word with "
                  "D-section monomial (frame-zero) compensation and rebuilt reverse cleanup; "
                  "exact ceiling brackets; conditional exact global moment under the stated "
                  "re-hosting of freed mass at rank<=42. No hosted outer assembly, no new kappa "
                  "admitted; planning-transfer kappa caps only."),
        "pins": {
            "base_commit": "0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2",
            "word": "research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz",
            "word_file_sha256": WORD_FILE_SHA,
            "engine": "research/complex-local-word-ceiling/ceiling.py",
            "engine_sha256": ENGINE_SHA,
            "selected_kappa": "836330098538459/500000000000000000",
            "a_bit_selected": fr(A_BIT),
            "pr2226_head": "dacaf3d81f1936bb55b8454b1244e5d014272754",
            "pr2271_head": "95fd439596f72575d3869277c2d01aca1ca6ab6a",
        },
        "base_census_taxonomy": dict(tax0),
        "base_funnel_classG": funnel,
        "base_candidates": cands0,
        "aliases_applied": steps,
        "helpers_before": 439,
        "helpers_removed": helpers_removed,
        "helpers_after": 439 - helpers_removed,
        "local_profile_before": {str(k): v for k, v in base_profile.items()},
        "local_profile_after": {str(k): v for k, v in final_profile.items()},
        "local_mass_before": base_mass,
        "local_mass_after": sum(r * n for r, n in final_profile.items()),
        "ceiling_bit_params": {"m": 64, "families": 888, "stages": 9, "centre_copies": 63, "grid": "1/10^12"},
        "ceiling_before": {"a_lo": fr(blo), "a_hi": fr(bhi), "a_hi_dec": dec(bhi)},
        "ceiling_after": {"a_lo": fr(flo), "a_hi": fr(fhi), "a_hi_dec": dec(fhi)},
        "conditional_moment": {
            "hypothesis": "global = 288*local + REM(fastc) + freed mass as rank-42 children (+1 remainder child); deficit fixed at 10272",
            "W": 28416, "m": 64,
            "root_before": {"a_lo": fr(mblo), "a_hi": fr(mbhi), "a_lo_dec": dec(mblo)},
            "root_after": {"a_lo": fr(mflo), "a_hi": fr(mfhi), "a_lo_dec": dec(mflo)},
            "certified_a_bit_after_dec": dec(mflo),
            "kappa_cap_bit_limited_after_dec": dec(mflo / (1 + mflo)),
            "kappa_cap_bit_limited_before_dec": dec(A_BIT / (1 + A_BIT)),
            "vs_pr2269_kappa_dec": "0.0016962471390584742",
            "vs_pr2226_complex_ceiling_a_dec": "0.001754331546940",
            "gap_a_to_2226_ceiling_after_dec": dec(a_2226 - mflo),
            "sensitivity_aliases_of_observed_shape_for_2226_ceiling": sens_k,
        },
    }
    (HERE / "RESULT.json").write_text(json.dumps(result, indent=1) + "\n")
    print("ceiling before", dec(bhi), "after", dec(fhi))
    print("moment root before", dec(mblo), "after", dec(mflo))
    print("PASS_MUSE_BIT_DIRTY_BORROWING_BUILD wrote RESULT.json")


if __name__ == "__main__":
    main()
