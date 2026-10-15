#!/usr/bin/env python3
"""Rank-16 local children (Track 4B): exact thresholds, fully charged break-evens, merge census.

Generates RESULT.json. All acceptance arithmetic is exact rational intervals via the pinned
predecessor engine research/complex-local-word-ceiling/ceiling.py; float values are diagnostics
only and are labelled as such in the output. Standard library only.
Prepared with Meta Muse (muse-wonder-full-1.0) assistance. Apache-2.0.
usage: screen.py [--out PATH]
"""
import collections, gzip, hashlib, io, json, math, sys, tarfile
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'research/complex-local-word-ceiling'))
sys.path.insert(0, str(ROOT / 'research/diagonal-batch-commutation'))
import ceiling as C  # noqa: E402
import batch as B  # noqa: E402

M, FAM, ST, CENTRE = 73, 896, 9, 64
SEL = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}
T74 = {1: 2335, 2: 512, 3: 426, 4: 120, 5: 38, 8: 8}
KF = Q(16971949509, 10 ** 13)          # #2374 conditional kappa 0.0016971949509 (unreviewed)
AF = KF / (1 - KF)                     # planning-transfer target a = kappa/(1-kappa)
GRID = Q(1, 10 ** 12)


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def dec(x, d=15):
    return f'{float(x):.{d}g}'


def ok(local, a, fam=FAM, m=M):
    try:
        return C.relax(local, m, fam, ST, CENTRE, a)[1] < 1
    except ValueError:
        return False


def relax_dec(local, a):
    try:
        v = C.relax(local, M, FAM, ST, CENTRE, a)
        return [dec(v[0]), dec(v[1])], v[1] < 1, v[0] > 1
    except ValueError as e:
        return str(e), False, True


def batched(W, n, src=1, per=16):
    L = dict(W)
    L[src] -= per * n
    L[16] = L.get(16, 0) + n
    return {r: v for r, v in L.items() if v != 0}


def min_batches(W, a, src=1, per=16):
    if ok(W, a):
        return 0
    mx = W[src] // per
    if not ok(batched(W, mx, src, per), a):
        return None
    lo, hi = 0, mx
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if ok(batched(W, mid, src, per), a):
            hi = mid
        else:
            lo = mid
    return hi


def min_mass(W, a, mk, cap):
    """Sharp 0.1-grid bracket (pass, fail) for converted mass; (0, None) if already passing."""
    if ok(mk(W, Q(0)), a):
        return Q(0), None
    if not ok(mk(W, Q(cap)), a):
        return None, Q(cap)
    lo, hi = Q(0), Q(cap)
    while hi - lo > Q(1, 10):
        mid = Q(int((lo + hi) / 2 * 10), 10)
        if mid <= lo:
            mid = lo + Q(1, 10)
        if ok(mk(W, mid), a):
            hi = mid
        else:
            lo = mid
    return hi, lo


def conv_r1(W, x):
    L = dict(W)
    L[1] = Q(W[1]) - x
    L[16] = x / 16
    return {r: v for r, v in L.items() if v != 0}


def conv_r12(W, x):
    tot = W[1] + 2 * W[2]
    f = x / tot
    L = {1: Q(W[1]) * (1 - f), 2: Q(W[2]) * (1 - f), 16: x / 16}
    for r in (3, 4, 5, 8):
        L[r] = W[r]
    return {r: v for r, v in L.items() if v != 0}


def max_overhead(W, n, a, shape):
    base = batched(W, n)
    if not ok(base, a):
        return None
    idle = C.model(W, M, FAM, ST, CENTRE)['idle_mass']
    def add(mass):
        L = dict(base)
        L[shape] = Q(L.get(shape, 0)) + mass / shape
        return L
    if ok(add(idle), a):
        return {'pass': str(idle), 'fail': None, 'coverage_bound': True}
    lo, hi = Q(0), idle
    while hi - lo > Q(1, 10):
        mid = Q(int((lo + hi) / 2 * 10), 10)
        if mid <= lo:
            mid = lo + Q(1, 10)
        if ok(add(mid), a):
            lo = mid
        else:
            hi = mid
    return {'pass': str(lo), 'fail': str(hi), 'per_batch_pass': dec(lo / n, 8),
            'per_register_pass': dec(lo / n / 16, 8)}


def moment(H, W, a):
    lo = hi = Q(0)
    for r, n in H.items():
        c = C.child_cost(r, M, a)
        lo += Q(n) * c[0]
        hi += Q(n) * c[1]
    return lo / W, hi / W


def endpoint(H, W):
    lo, hi = Q(0), Q(1, 100)
    while hi - lo > GRID:
        mid = Q(int((lo + hi) / 2 / GRID)) * GRID
        if mid <= lo:
            mid = lo + GRID
        v = moment(H, W, mid)
        if v[1] < 1:
            lo = mid
        elif v[0] > 1:
            hi = mid
        else:
            raise ValueError('enclosure too wide')
    return lo, hi


def excess(a):
    """Budget form at a: relax<=1 iff sum n_r p_r <= B; p_r = excess over ideal idle (R=51)."""
    q = C.model(SEL, M, FAM, ST, CENTRE)
    R = q['R']
    cR = C.child_cost(R, M, a)
    Bnd = (q['w'] - q['total_mass'] * cR[1] / R, q['w'] - q['total_mass'] * cR[0] / R)
    def p(r):
        c = C.child_cost(r, M, a)
        return (c[0] - r * cR[1] / R, c[1] - r * cR[0] / R)
    spend = (sum(n * p(r)[0] for r, n in SEL.items()), sum(n * p(r)[1] for r, n in SEL.items()))
    p1, p16 = p(1), p(16)
    g = (16 * p1[0] - p16[1], 16 * p1[1] - p16[0])  # spend saved per zero-charge batch
    return dict(budget_B=[dec(Bnd[0]), dec(Bnd[1])], spend=[dec(spend[0]), dec(spend[1])],
                overspend_lower=dec(spend[0] - Bnd[1]), p1=[dec(p1[0]), dec(p1[1])],
                p16=[dec(p16[0]), dec(p16[1])], p16_positive=p16[0] > 0,
                gain_per_batch=[dec(g[0]), dec(g[1])],
                max_staging_rank1_per_batch=[dec(g[0] / p1[1], 8), dec(g[1] / p1[0], 8)],
                one_copy_per_register_16_exceeds_cap=bool(g[1] / p1[0] < 16))


def census():
    arch = ROOT / 'research/community-frontier1094-audit/selected-replay.tar.gz'
    raw = arch.read_bytes()
    pins = dict(archive_sha256=hashlib.sha256(raw).hexdigest())
    C.require(pins['archive_sha256'] == 'f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6', 'archive pin')
    mem = {}
    with tarfile.open(fileobj=io.BytesIO(raw), mode='r:gz') as tar:
        for name, want in (('LOCAL-PROGRAMS.json.gz', '241fde27d4e43f5a9cb6b128f9f76c5131a53d09f0371676163f914d0b0fef3a'),
                           ('CANONICAL-WORD.json.gz', '16bc0ebb04b4be6c0ade74badc6a0c0cdba4215eda86e4ff9f13abf8ecebd219')):
            d = tar.extractfile('candidate/strict/global/base/providers/gauge44/' + name).read()
            pins[name] = hashlib.sha256(d).hexdigest()
            C.require(pins[name] == want, 'member pin ' + name)
            mem[name] = d
    programs = json.load(gzip.open(io.BytesIO(mem['LOCAL-PROGRAMS.json.gz'])))
    word = json.load(gzip.open(io.BytesIO(mem['CANONICAL-WORD.json.gz'])))
    dims = [len(f) for f in word['frames']]
    out = dict(pins=pins, frames=len(dims), frame_dim_hist={str(k): v for k, v in sorted(collections.Counter(dims).items())},
               max_frame_dim=max(dims), registers=len(word['start']), orientations={})
    for orient, events in sorted(programs.items()):
        B.replay_frames(events, word)  # positive control
        climbs = [e for e in events if e[0] == 'climb']
        byrank = collections.Counter(e[5] for e in climbs)
        C.require(dict(byrank) == {r: n for r, n in SEL.items() if r != 8}, 'climb hist = local minus centre')
        r1 = [e for e in climbs if e[5] == 1]
        trans = collections.Counter((e[3], e[4]) for e in r1)
        ub_phase, batches, per_phase = 0, [], {}
        for ph, body in B.split_phases(events):
            c = collections.Counter((e[3], e[4]) for e in body if B.is_r1(e))
            ub_phase += sum(v // 16 for v in c.values())
            _, bts, n1, _ = B.batch_phase(body)
            batches += bts
            if n1:
                per_phase[ph[1]] = len(bts)
        pairs = 0
        for ph, body in B.split_phases(events):
            last = {}
            for e in body:
                for reg in B.touched(e):
                    if reg[0] != 'L':
                        continue
                    if e[0] == 'climb' and reg[1] in last and last[reg[1]][0] == 'climb':
                        pairs += 1
                    last[reg[1]] = e
        def shist(batch):
            h = collections.Counter()
            for e in batch:
                d = dims[e[3]]
                h[d] += 1
                h[d + 1] += 1
            return h
        infos = sorted(((sum(r * n for r, n in shist(b).items()), shist(b)) for b in batches), key=lambda x: x[0])
        agg = collections.Counter()
        for _, h in infos:
            agg.update(h)
        staged = {}
        for nb in (3, 7, 8, 12):
            h = collections.Counter()
            for _, hh in infos[:nb]:
                h.update(hh)
            L = batched(SEL, nb)
            for r, n in h.items():
                if r > 0:
                    L[r] = L.get(r, 0) + n
            staged[str(nb)] = dict(staging_mass=sum(r * n for r, n in h.items()), relax_aF=relax_dec(L, AF)[0],
                                   passes_aF=relax_dec(L, AF)[1])
        out['orientations'][orient] = dict(
            climbs_by_rank={str(k): v for k, v in sorted(byrank.items())},
            rank1_dim_from_hist={str(k): v for k, v in sorted(collections.Counter(dims[e[3]] for e in r1).items())},
            distinct_transitions=len(trans), top_transitions=[str(t) for t in trans.most_common(3)],
            identical_transition_batch_ub_per_phase=ub_phase,
            identical_transition_batch_ub_global=sum(v // 16 for v in trans.values()),
            same_register_adjacent_climb_pairs=pairs, batches=len(batches), batches_per_phase=per_phase,
            distinct_transitions_per_batch=dict(min=min(len({(e[3], e[4]) for e in b}) for b in batches),
                                                max=max(len({(e[3], e[4]) for e in b}) for b in batches),
                                                mean=dec(Q(sum(len({(e[3], e[4]) for e in b}) for b in batches), len(batches)), 8)),
            staging_frame_dim_hist={str(k): v for k, v in sorted(agg.items())},
            staging_frame_dim_mass=sum(r * n for r, n in agg.items()), staged_cheapest=staged)
    return out


def main():
    out_path = Path(sys.argv[sys.argv.index('--out') + 1]) if '--out' in sys.argv else HERE / 'RESULT.json'
    rec = json.loads((ROOT / 'certificates/selected-result.json').read_text())
    asm = json.loads((ROOT / rec['certificate']).read_text())
    ind = json.loads((ROOT / 'research/community-frontier1094-audit/INDEPENDENT1094.json').read_text())
    AB, BSEL = Q(asm['bit_lower']), Q(asm['complex_lower'])
    Hsel = {int(r): n for r, n in asm['complex_profile'].items()}
    Nsel, Wsel = ind['price']['calls'], ind['price']['live']
    # Frontier #2374 global profile (refs/upr/2374 PROFILE.json, sha in pins); words are #2322's.
    H74 = {1: 1577088, 2: 340992, 3: 292308, 4: 79920, 5: 27860, 8: 5328, 32: 1, 48: 24560}
    W74, N74 = 66304, 666
    C.require(sum(r * n for r, n in H74.items()) == 72 * W74 + 64 * N74, 'H2374 coverage identity')
    C.require(sum(r * n for r, n in Hsel.items()) == 72 * Wsel + 64 * Nsel, 'selected coverage identity')

    def ceil_frac(W):
        lo, hi = C.ceiling(W, M, FAM, ST, CENTRE, grid=GRID)
        return [str(lo), str(hi)], dec(hi)
    base_sel, base_sel_dec = ceil_frac(SEL)
    gate = Q(105, 100) * Q(base_sel[1])
    targets = {'kappa2374_as_a': (KF, 'frontier moment-root reading'),
               'aF_planning': (AF, 'kappa/(1-kappa) retained-transfer reading'),
               'a_bit': (AB, 'selected bit endpoint (ASSEMBLY bit_lower)')}
    S1 = {}
    for nm, W in (('selected', SEL), ('t74_2322', T74)):
        row = {}
        for tn, (a, _) in targets.items():
            mb = min_batches(W, a)
            p1 = min_mass(W, a, conv_r1, W[1])
            p12 = min_mass(W, a, conv_r12, W[1] + 2 * W[2])
            row[tn] = dict(min_rank1_batches=mb,
                           rank1_mass_pass=None if p1[0] is None else str(p1[0]),
                           rank1_mass_fail=None if p1[1] is None else str(p1[1]),
                           rank1_frac_pass=None if p1[0] is None else dec(p1[0] / W[1], 8),
                           r12_mass_pass=None if p12[0] is None else str(p12[0]),
                           r12_mass_fail=None if p12[1] is None else str(p12[1]),
                           r12_pool_frac_pass=None if p12[0] is None else dec(p12[0] / (W[1] + 2 * W[2]), 8),
                           min_rank2_batches=min_batches(W, a, src=2, per=8))
        S1[nm] = row
    diag = {}
    for nm, W in (('selected', SEL), ('t74_2322', T74)):
        q = C.model(W, M, FAM, ST, CENTRE)
        El = sum(n * r * math.log(73 / r) for r, n in W.items())
        Ef = El + float(q['idle_mass']) * math.log(73 / 51)
        diag[nm] = dict(floats_only=True, local_mass=sum(r * n for r, n in W.items()),
                        idle_mass=str(q['idle_mass']), deficit_D=str(q['deficit']),
                        E_local=f'{El:.2f}', E_full_ideal_idle=f'{Ef:.2f}',
                        effective_rank_full=f"{73 * math.exp(-Ef / float(q['total_mass'])):.4f}",
                        rank1_share_E_local=f"{W[1] * math.log(73) / El:.4f}",
                        rank12_share_E_local=f"{(W[1] * math.log(73) + 2 * W[2] * math.log(73 / 2)) / El:.4f}")
    # actual-H zero-charge minima (selected) at both frontier readings
    def sel_actual_minB(a):
        for n in range(0, 151):
            L = dict(Hsel)
            L[1] -= 16 * n * Nsel
            L[16] = L.get(16, 0) + n * Nsel
            if moment(L, Wsel, a)[1] < 1:
                return n
        return None
    act = {}
    for tn, a in (('kappa2374_as_a', KF), ('aF_planning', AF)):
        n = sel_actual_minB(a)
        def mm(k):
            L = dict(Hsel)
            L[1] -= 16 * k * Nsel
            L[16] = L.get(16, 0) + k * Nsel
            v = moment(L, Wsel, a)
            return [dec(v[0]), dec(v[1])]
        act[tn] = dict(min_batches_per_call=n, moment_at_min_minus_1=mm(n - 1), moment_at_min=mm(n))
    e74 = endpoint(H74, W74)
    e74b = {}
    for n in (1, 2):
        H = dict(H74)
        H[1] -= 16 * n * N74
        H[16] = n * N74
        e = endpoint(H, W74)
        e74b[str(n)] = dict(endpoint=[str(e[0]), str(e[1])], hi_decimal=dec(e[1]))
    # H2374 overhead break-even at a=KF, overhead displaces rank-48 idle mass (favourable)
    def h74_max_overhead(n):
        def mok(x):
            H = dict(H74)
            H[1] = Q(H[1] - 16 * n * N74) + N74 * x
            H[16] = n * N74
            H[48] = Q(H[48]) - N74 * x / 48
            return moment(H, W74, KF)[1] < 1
        lo, hi = Q(0), Q(2000)
        while hi - lo > Q(1, 10):
            mid = Q(int((lo + hi) / 2 * 10), 10)
            if mid <= lo:
                mid = lo + Q(1, 10)
            if mok(mid):
                lo = mid
            else:
                hi = mid
        return {'pass_per_call': str(lo), 'fail_per_call': str(hi), 'per_batch_pass': dec(lo / n, 8)}
    mass_sel = sum(r * n for r, n in SEL.items())
    res = dict(
        status='PASS_MUSE_RANK16_CHILDREN_SCREEN',
        pins=dict(main='0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2',
                  ceiling_py_sha256=sha(ROOT / 'research/complex-local-word-ceiling/ceiling.py'),
                  batch_py_sha256=sha(ROOT / 'research/diagonal-batch-commutation/batch.py'),
                  selected_result_sha256=sha(ROOT / 'certificates/selected-result.json'),
                  assembly_sha256=sha(ROOT / rec['certificate']),
                  independent_sha256=sha(ROOT / 'research/community-frontier1094-audit/INDEPENDENT1094.json'),
                  frontier_profile2374='refs/upr/2374 (5449da65d) research/gmx-t74-borrow43-handoff/PROFILE.json sha256 30d6f326df5781308adfd20e700f2080d28f6a5414066f7d9abe9e69162f32d9',
                  t74_claim2322='refs/upr/2322 (002304ef0) research/t74-joint-owner-hillclimb/CLAIM.json sha256 439ded151e7897b8e7d5ef9ad47f3cd8d1daf0b69219ef507a922519c7003530'),
        model=dict(m=M, families_per_replica=FAM, stages=ST, centre_per_call=CENTRE, idle_cap_R=C.max_idle_rank(M),
                   note='Rank 16 < R(73)=51: no halving-guard change. Overhead displaces idle mass; coverage total fixed.'),
        targets=dict(kappa2374=str(KF), kappa2374_decimal=dec(KF), aF_planning=str(AF), aF_decimal=dec(AF),
                     a_bit=str(AB), a_bit_decimal=dec(AB), b_selected=str(BSEL), b_selected_decimal=dec(BSEL)),
        S0_baseline=dict(selected_ceiling=base_sel, selected_ceiling_hi=base_sel_dec,
                         t74_ceiling=ceil_frac(T74)[0], t74_ceiling_hi=ceil_frac(T74)[1],
                         gate_plus5=str(gate), gate_decimal=dec(gate), diagnostics=diag,
                         all_local_mass_rank16_ceiling=ceil_frac({16: Q(mass_sel, 16)})[0],
                         all_local_mass_rank16_hi=ceil_frac({16: Q(mass_sel, 16)})[1],
                         ceilings_by_batches_selected={str(n): ceil_frac(batched(SEL, n))[1] for n in (3, 8, 12, 134)}),
        S1_zero_charge_thresholds=S1,
        S2_actual_global_profiles=dict(selected=act, selected_calls=Nsel, selected_live=Wsel,
                                       frontier2374_endpoint=[str(e74[0]), str(e74[1])], frontier2374_endpoint_hi=dec(e74[1]),
                                       frontier2374_plus_batches=e74b, frontier_calls=N74, frontier_live=W74,
                                       frontier2374_overhead_breakeven_at_kappa={str(n): h74_max_overhead(n) for n in (1, 2)}),
        S3_fully_charged=dict(excess_at_kappa2374=excess(KF), excess_at_aF=excess(AF),
                              breakeven_overhead_selected={
                                  f'B{n}_aF_shape{sh}': max_overhead(SEL, n, AF, sh) for n in (3, 8, 12, 134) for sh in (1, 8)},
                              breakeven_B134_gate_shape1=max_overhead(SEL, 134, gate, 1)),
        S4_census=census(),
        scope='Favourable relaxations and exact finite censuses. Zero-charge rows assume a rank-16 child '
              'realises 16 rank-1 children at (16/73)^(1-a) with no staging (interface B2). Staged rows '
              '(B1) add census-priced copies displacing idle. No supplier is constructed; the exact moment '
              'of a completed construction remains the acceptance test. Frontier values are unreviewed.')
    res['S5_verdict_inputs'] = dict(
        common_frame_ub_below_actual_min=bool(
            max(v['identical_transition_batch_ub_per_phase'] for v in res['S4_census']['orientations'].values())
            < act['aF_planning']['min_batches_per_call']),
        same_register_fusion_zero=all(v['same_register_adjacent_climb_pairs'] == 0 for v in res['S4_census']['orientations'].values()),
        staged_cheapest_all_fail_aF=all(not s['passes_aF'] for v in res['S4_census']['orientations'].values() for s in v['staged_cheapest'].values()),
        staging_total_exceeds_idle=bool(res['S4_census']['orientations']['backward']['staging_frame_dim_mass'] > 1646))
    out_path.write_text(json.dumps(res, indent=1, sort_keys=True) + '\n')
    print(res['status'], 'written', out_path)


if __name__ == '__main__':
    main()
