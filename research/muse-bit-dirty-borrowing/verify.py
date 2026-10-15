#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Verifier for research/muse-bit-dirty-borrowing.

Re-pins the word and ceiling engine, cross-checks the base paid profile
with the predecessor's own wlib replay, rebuilds the aliased word from
RESULT.json with an independently written value/frame replay, recomputes
the exact ceiling brackets and conditional moment roots, and runs tamper
controls T1-T6 (each mutates a value and must be rejected). Standard
library only. Meta Muse (muse-wonder-full-1.0) assisted; see README.md.
"""
import gzip
import hashlib
import importlib.util
import json
import sys
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORD_PATH = ROOT / "research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz"
WLIB_PATH = ROOT / "research/e8-bit-p111-tuned/tune/wlib.py"
ENGINE_DIR = ROOT / "research/complex-local-word-ceiling"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ENGINE_DIR))
import build as B  # noqa: E402  (global_profile/moment pricing helpers)


def req(ok, why):
    if not ok:
        raise RuntimeError(why)
import ceiling as C  # noqa: E402


def load_wlib():
    sp = importlib.util.spec_from_file_location("wlib_predecessor", WLIB_PATH)
    mod = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(mod)
    return mod


def transform_word(w, steps):
    """Independently rebuild D/A/B gate lists from RESULT alias steps.

    Apply steps in order; per step, event order is A-gates, scatter, B-gates
    of the CURRENT lists; handoff tstar indexes that order. Returns
    (D, A, B, ret, active) with D sources as sets incl. recorded comp.
    """
    V = w["v"]
    D = [[f, t, set(ss)] for f, t, ss in w["D"]]
    A = [[f, t, list(ss)] for f, t, ss in w["A"]]
    Bg = [[f, t, list(ss)] for f, t, ss in w["B"]]
    ret = list(w["ret"])
    active = set(range(2 * V + w["R"]))
    for st in steps:
        i, j, tstar = st["lender"], st["borrower"], st["tstar"]

        def tr(gates, base):
            out = []
            for k, (f, t, ss) in enumerate(gates):
                if base + k < tstar:
                    if t == j:
                        continue
                    ss = [s for s in ss if s != j]
                    if ss:
                        out.append([f, t, ss])
                else:
                    out.append([f, i if t == j else t,
                                [i if s == j else s for s in ss]])
            return out

        n_ev = len(A) + 1 + len(Bg)
        A = tr(A, 0)
        Bg = tr(Bg, n_ev - len(Bg))
        ret = [i if q == j else q for q in ret]
        for g in D:
            g[2].discard(j)
        for tgt, supp in st["d_compensation"].items():
            g = next(g for g in D if g[1] == int(tgt))
            for c in supp:
                g[2] ^= {c}
        active.discard(j)
    return D, A, Bg, ret, active


def replay2(w, D, A, Bg, ret, active):
    """Fresh endpoint/profile replay (no build.Word). Returns (prof, errs)."""
    V = w["v"]
    fmask = [sum(1 << x for x in f) for f in w["frames"]]
    fdim = [B.qrank([w["lines"][x] for x in f]) for f in w["frames"]]
    full = next(k for k, m in enumerate(fmask) if m == (1 << V) - 1)
    val = {r: 1 << r for r in active}
    cur = {r: w["start"][r] for r in active}
    prof = Counter()

    def climb(r, f):
        req(fmask[cur[r]] & fmask[f] == fmask[cur[r]], f"nesting fails at register {r}")
        if fdim[f] > fdim[cur[r]]:
            prof[fdim[f] - fdim[cur[r]]] += 1
        cur[r] = f

    def run(gates):
        for f, t, ss in gates:
            ss = sorted(ss)
            req(len({t, *ss}) == 1 + len(ss), "gate incidence not distinct")
            for r in [t, *ss]:
                req(r in val, f"inactive register {r} incident to a gate")
                climb(r, f)
            for s in ss:
                val[t] ^= val[s]

    run(D)
    run(A)
    tops = [fdim[cur[q]] for q in ret]
    snap = [val[q] for q in ret]
    for t, ks in enumerate(w["scatter"]):
        for k in ks:
            val[V + t] ^= snap[k]
    run(Bg)
    zg = [g for g in A + Bg if g[1] < V or g[1] >= 2 * V]
    run([[full, t, list(ss)] for f, t, ss in reversed(zg)])
    for r in active:
        climb(r, w["final"][r])
    errs = {}
    for r in active:
        want = (1 << r) ^ (1 << (r - V)) if V <= r < 2 * V else (1 << r)
        if val[r] != want:
            errs[r] = val[r] ^ want
    return dict(sorted((prof + Counter(tops)).items())), errs


def main():
    R = json.loads((HERE / "RESULT.json").read_text())
    req(hashlib.sha256(WORD_PATH.read_bytes()).hexdigest() == R["pins"]["word_file_sha256"], "word pin")
    req(hashlib.sha256((ENGINE_DIR / "ceiling.py").read_bytes()).hexdigest() == R["pins"]["engine_sha256"], "engine pin")
    w = json.loads(gzip.decompress(WORD_PATH.read_bytes()))

    # Base profile by predecessor wlib (independent).
    paid = load_wlib().paid(w)
    req({str(k): v for k, v in paid.items()} == R["local_profile_before"], "wlib base profile mismatch")

    # Rebuild aliased word + independent replay.
    D, A, Bg, ret, active = transform_word(w, R["aliases_applied"])
    prof, errs = replay2(w, D, A, Bg, ret, active)
    req(not errs, f"aliased endpoint fails at {list(errs)[:4]}")
    req({str(k): v for k, v in prof.items()} == R["local_profile_after"], "final profile mismatch")
    req(sum(r * n for r, n in prof.items()) == R["local_mass_after"], "final mass mismatch")
    req(439 - len(R["aliases_applied"]) == R["helpers_after"], "helper count mismatch")

    # Exact pricing recomputation.
    grid = Q(1, 10**12)
    lp = lambda d: {int(k): v for k, v in d.items()}  # noqa: E731
    for name, loc in (("before", lp(R["local_profile_before"])),
                      ("after", lp(R["local_profile_after"]))):
        lo, hi = C.ceiling(loc, 64, 888, 9, 63, grid=grid)
        rec = R[f"ceiling_{name}"]
        req(f"{lo.numerator}/{lo.denominator}" == rec["a_lo"], f"ceiling lo {name}")
        req(f"{hi.numerator}/{hi.denominator}" == rec["a_hi"], f"ceiling hi {name}")
        g = B.global_profile(loc, R["local_mass_before"])
        mlo, mhi = B.moment_root(g)
        recm = R["conditional_moment"][f"root_{name}"]
        req(f"{mlo.numerator}/{mlo.denominator}" == recm["a_lo"], f"moment lo {name}")
        req(f"{mhi.numerator}/{mhi.denominator}" == recm["a_hi"], f"moment hi {name}")
    req(B.moment_enc(B.global_profile(lp(R["local_profile_before"]),
                                      R["local_mass_before"]), B.A_BIT)[1] < 1,
        "pinned endpoint fails on base global profile")

    # ---- tamper controls (each must be rejected) ---------------------------
    tamper = {}
    st0 = R["aliases_applied"][0]

    def trial(step):
        """True iff the mutated single-alias word passes the full endpoint."""
        try:
            Dt, At, Bt, rett, actt = transform_word(w, [step])
            _, e = replay2(w, Dt, At, Bt, rett, actt)
            return not e
        except (RuntimeError, AssertionError, KeyError, ValueError, StopIteration):
            return False

    tamper["T1_wrong_lender_rejected"] = not trial(dict(st0, lender=471))
    tamper["T2_wrong_handoff_rejected"] = not trial(dict(st0, tstar=2064))
    D3 = [[f, t, set(ss)] for f, t, ss in D]
    D3[0][2] ^= {470}
    _, e3 = replay2(w, D3, A, Bg, ret, active)
    tamper["T3_flipped_D_source_rejected"] = bool(e3)
    tamper["T4_omitted_alias_profile_mismatch"] = (
        {str(k): v for k, v in paid.items()} != R["local_profile_after"])
    base = B.Word(w)
    ev, helpers, inc, first, last, pv, pc, tv, tc, rb, ra = base.census()
    j, tstar = st0["borrower"], st0["tstar"]
    Fj = ev[tstar][2][0]
    bad_i = next(i for i in helpers
                 if i != j and last[i] < tstar
                 and not (base.fmask[tc[i]] & base.fmask[Fj] == base.fmask[tc[i]]))
    tamper["T5_seam_illegal_lender_rejected"] = not trial(dict(st0, lender=bad_i))
    tamper["T6_mutated_result_detected"] = (
        R["local_mass_after"] + 1 != sum(r * n for r, n in prof.items()))
    req(all(tamper.values()), f"tamper controls not all rejected: {tamper}")

    print(f"PASS_MUSE_BIT_DIRTY_BORROWING_VERIFY aliases={len(R['aliases_applied'])} "
          f"helpers {R['helpers_before']}->{R['helpers_after']} "
          f"mass {R['local_mass_before']}->{R['local_mass_after']} "
          f"a_bit_cond {R['conditional_moment']['certified_a_bit_after_dec']} "
          f"tamper={sum(tamper.values())}/6 rejected")


if __name__ == "__main__":
    main()
