#!/usr/bin/env python3
"""Independent verification for muse-rank16-children: recomputes the decisive subset of
RESULT.json from pinned inputs (explicit checks, no assert reliance; safe under -O) and runs
value-mutating tamper controls that must be rejected.
Prepared with Meta Muse (muse-wonder-full-1.0) assistance. Apache-2.0.
usage: verify.py
"""
import collections, copy, gzip, hashlib, io, json, sys, tarfile
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
KF = Q(16971949509, 10 ** 13)
AF = KF / (1 - KF)
GRID = Q(1, 10 ** 12)
FAILS = []


def req(ok, why):
    if not ok:
        raise SystemExit('FAIL: ' + why)


def check(name, cond):
    print(('  ok ' if cond else '  BAD ') + name)
    if not cond:
        FAILS.append(name)


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def ok(local, a):
    try:
        return C.relax(local, M, FAM, ST, CENTRE, a)[1] < 1
    except ValueError:
        return False


def fails_(local, a):
    try:
        return C.relax(local, M, FAM, ST, CENTRE, a)[0] > 1
    except ValueError:
        return True


def batched(W, n, src=1, per=16):
    L = dict(W)
    L[src] -= per * n
    L[16] = L.get(16, 0) + n
    return {r: v for r, v in L.items() if v != 0}


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
            raise ValueError('wide enclosure')
    return lo, hi


def contains(a, b):
    """True iff span of basis list a is contained in span of b (GF(2) bitmask reduction)."""
    for x0 in a:
        x = x0
        for y in b:
            if x >> (y.bit_length() - 1) & 1:
                x ^= y
        if x:
            return False
    return True


def check_events(events, word):
    """Explicit frame replay (no asserts): raises ValueError on any illegal climb/scalar frame."""
    frames = word['frames']
    cur = list(word['start'])
    phase, private = None, {}
    for e in events:
        tag = e[0]
        if tag == 'phase':
            phase = e[1]
            if private:
                raise ValueError('private live at phase')
        elif tag == 'climb':
            _, part, r, a, b, rank = e
            if private or phase != part or cur[r] != a:
                raise ValueError('climb source frame')
            if not contains(frames[a], frames[b]) or rank != len(frames[b]) - len(frames[a]) or rank <= 0:
                raise ValueError('climb rank/containment')
            cur[r] = b
        elif tag == 'scalar':
            _, op, f = e
            target = tuple(op[1])
            source = tuple(op[2]) if op[0] in ('copy', 'add') else None
            if target[0] == 'C' and op[0] == 'clear':
                private.pop(target, None)
                continue
            for reg in (target, source):
                if reg is None:
                    continue
                if reg[0] == 'L':
                    if cur[reg[1]] != f:
                        raise ValueError('scalar common frame')
                else:
                    if reg == target and reg not in private:
                        private[reg] = f
                    if private[reg] != f:
                        raise ValueError('private frame')
        elif tag == 'center':
            if phase != 'centers':
                raise ValueError('center phase')
            private[('C', e[1])] = e[3]
    if cur != word['final']:
        raise ValueError('terminal frames')


def load_programs():
    raw = (ROOT / 'research/community-frontier1094-audit/selected-replay.tar.gz').read_bytes()
    req(hashlib.sha256(raw).hexdigest() == 'f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6', 'archive pin')
    mem = {}
    with tarfile.open(fileobj=io.BytesIO(raw), mode='r:gz') as tar:
        for name, want in (('LOCAL-PROGRAMS.json.gz', '241fde27d4e43f5a9cb6b128f9f76c5131a53d09f0371676163f914d0b0fef3a'),
                           ('CANONICAL-WORD.json.gz', '16bc0ebb04b4be6c0ade74badc6a0c0cdba4215eda86e4ff9f13abf8ecebd219')):
            d = tar.extractfile('candidate/strict/global/base/providers/gauge44/' + name).read()
            req(hashlib.sha256(d).hexdigest() == want, 'member pin ' + name)
            mem[name] = d
    return (json.load(gzip.open(io.BytesIO(mem['LOCAL-PROGRAMS.json.gz']))),
            json.load(gzip.open(io.BytesIO(mem['CANONICAL-WORD.json.gz']))))


def census_one(events, word, dims):
    check_events(events, word)
    climbs = [e for e in events if e[0] == 'climb']
    byrank = dict(collections.Counter(e[5] for e in climbs))
    if byrank != {r: n for r, n in SEL.items() if r != 8}:
        raise ValueError('climb histogram mismatch')
    r1 = [e for e in climbs if e[5] == 1]
    trans = collections.Counter((e[3], e[4]) for e in r1)
    ub, batches = 0, []
    for ph, body in B.split_phases(events):
        ub += sum(v // 16 for v in collections.Counter((e[3], e[4]) for e in body if B.is_r1(e)).values())
        batches += B.batch_phase(body)[1]
    pairs = 0
    for ph, body in B.split_phases(events):
        last = {}
        for e in body:
            for reg in B.touched(e):
                if reg[0] == 'L':
                    if e[0] == 'climb' and reg[1] in last and last[reg[1]][0] == 'climb':
                        pairs += 1
                    last[reg[1]] = e
    agg = collections.Counter()
    for b in batches:
        for e in b:
            d = dims[e[3]]
            agg[d] += 1
            agg[d + 1] += 1
    return dict(distinct=len(trans), ub=ub, pairs=pairs, batches=len(batches),
                staging_mass=sum(r * n for r, n in agg.items()),
                staging_hist={str(k): v for k, v in sorted(agg.items())})


def main():
    R = json.loads((HERE / 'RESULT.json').read_text())
    req(R['status'] == 'PASS_MUSE_RANK16_CHILDREN_SCREEN', 'RESULT status')
    rec = json.loads((ROOT / 'certificates/selected-result.json').read_text())
    asm = json.loads((ROOT / rec['certificate']).read_text())
    ind = json.loads((ROOT / 'research/community-frontier1094-audit/INDEPENDENT1094.json').read_text())
    AB = Q(asm['bit_lower'])
    print('V1 pins')
    check('ceiling.py hash', sha(ROOT / 'research/complex-local-word-ceiling/ceiling.py') == R['pins']['ceiling_py_sha256'])
    check('batch.py hash', sha(ROOT / 'research/diagonal-batch-commutation/batch.py') == R['pins']['batch_py_sha256'])
    check('selected hash', sha(ROOT / 'certificates/selected-result.json') == R['pins']['selected_result_sha256'])
    check('R(73)=51, 16<=51', C.max_idle_rank(73) == 51)
    print('V2 base ceilings recomputed')
    lo, hi = C.ceiling(SEL, M, FAM, ST, CENTRE, grid=GRID)
    check('SEL ceiling bracket', [str(lo), str(hi)] == R['S0_baseline']['selected_ceiling'])
    lo2, hi2 = C.ceiling(T74, M, FAM, ST, CENTRE, grid=GRID)
    check('T74 ceiling bracket', [str(lo2), str(hi2)] == R['S0_baseline']['t74_ceiling'])
    print('V3 threshold signs (selected)')
    check('B=2 passes kappa-as-a, B=1 fails', ok(batched(SEL, 2), KF) and fails_(batched(SEL, 1), KF))
    check('B=3 passes aF, B=2 fails', ok(batched(SEL, 3), AF) and fails_(batched(SEL, 2), AF))
    check('B=12 passes a_bit, B=11 fails', ok(batched(SEL, 12), AB) and fails_(batched(SEL, 11), AB))
    check('RESULT S1 minima match', R['S1_zero_charge_thresholds']['selected']['kappa2374_as_a']['min_rank1_batches'] == 2
          and R['S1_zero_charge_thresholds']['selected']['aF_planning']['min_rank1_batches'] == 3
          and R['S1_zero_charge_thresholds']['selected']['a_bit']['min_rank1_batches'] == 12)
    fp = Q(R['S1_zero_charge_thresholds']['selected']['aF_planning']['rank1_mass_pass'])
    ff = Q(R['S1_zero_charge_thresholds']['selected']['aF_planning']['rank1_mass_fail'])
    def conv(x):
        L = dict(SEL)
        L[1] = Q(SEL[1]) - x
        L[16] = x / 16
        return L
    check('fractional rank1 bracket signs at aF', ok(conv(fp), AF) and fails_(conv(ff), AF) and fp - ff == Q(1, 10))
    check('T74 passes aF at B=0; B=2 passes a_bit, B=1 fails', ok(T74, AF) and ok(batched(T74, 2), AB) and fails_(batched(T74, 1), AB))
    print('V4 actual global profiles')
    Hsel = {int(r): n for r, n in asm['complex_profile'].items()}
    Nsel, Wsel = ind['price']['calls'], ind['price']['live']
    req(sum(r * n for r, n in Hsel.items()) == 72 * Wsel + 64 * Nsel, 'selected coverage')
    for tn, a in (('kappa2374_as_a', KF), ('aF_planning', AF)):
        res = []
        for n in (6, 7):
            L = dict(Hsel)
            L[1] -= 16 * n * Nsel
            L[16] = L.get(16, 0) + n * Nsel
            res.append(moment(L, Wsel, a))
        check(f'SEL actual B=6 fails, B=7 passes at {tn}', res[0][0] > 1 and res[1][1] < 1)
        check(f'RESULT actual min=7 at {tn}', R['S2_actual_global_profiles']['selected'][tn]['min_batches_per_call'] == 7)
    H74 = {1: 1577088, 2: 340992, 3: 292308, 4: 79920, 5: 27860, 8: 5328, 32: 1, 48: 24560}
    req(sum(r * n for r, n in H74.items()) == 72 * 66304 + 64 * 666, 'H2374 coverage')
    e = endpoint(H74, 66304)
    check('H2374 endpoint bracket', [str(e[0]), str(e[1])] == R['S2_actual_global_profiles']['frontier2374_endpoint'])
    H1 = dict(H74)
    H1[1] -= 16 * 666
    H1[16] = 666
    e1 = endpoint(H1, 66304)
    check('H2374+B1 endpoint above frontier, matches RESULT',
          [str(e1[0]), str(e1[1])] == R['S2_actual_global_profiles']['frontier2374_plus_batches']['1']['endpoint'] and e1[0] > e[1])
    print('V5 fully charged excess cap + one break-even')
    for tn, a in (('excess_at_kappa2374', KF), ('excess_at_aF', AF)):
        q = C.model(SEL, M, FAM, ST, CENTRE)
        cR = C.child_cost(51, M, a)
        def p(r):
            c = C.child_cost(r, M, a)
            return (c[0] - r * cR[1] / 51, c[1] - r * cR[0] / 51)
        p1, p16 = p(1), p(16)
        g_hi = 16 * p1[1] - p16[0]
        check(f'p16>0 and 16 copies exceed cap at {tn}', p16[0] > 0 and g_hi / p1[0] < 16
              and R['S3_fully_charged'][tn]['one_copy_per_register_16_exceeds_cap'] is True)
    be = R['S3_fully_charged']['breakeven_overhead_selected']['B8_aF_shape1']
    def with_oh(n, mass, shape=1):
        L = batched(SEL, n)
        L[shape] = Q(L.get(shape, 0)) + Q(mass) / shape
        return L
    check('B=8 break-even bracket signs', ok(with_oh(8, be['pass']), AF) and fails_(with_oh(8, be['fail']), AF))
    print('V6 census recomputed (explicit replay)')
    programs, word = load_programs()
    dims = [len(f) for f in word['frames']]
    check('frame catalogue', len(dims) == R['S4_census']['frames'] == 1004 and max(dims) == 9)
    for orient, events in sorted(programs.items()):
        c1 = census_one(events, word, dims)
        rc = R['S4_census']['orientations'][orient]
        check(f'{orient}: batches=134, UB=6, pairs=0, distinct=1928, staging=17432',
              c1['batches'] == rc['batches'] == 134 and c1['ub'] == rc['identical_transition_batch_ub_per_phase'] == 6
              and c1['pairs'] == rc['same_register_adjacent_climb_pairs'] == 0
              and c1['distinct'] == rc['distinct_transitions'] == 1928
              and c1['staging_mass'] == rc['staging_frame_dim_mass'] == 17432
              and c1['staging_hist'] == rc['staging_frame_dim_hist'])
        check(f'{orient}: staged cheapest all fail aF in RESULT', all(not s['passes_aF'] for s in rc['staged_cheapest'].values()))
    check('S5 verdict inputs', R['S5_verdict_inputs'] == dict(common_frame_ub_below_actual_min=True,
          same_register_fusion_zero=True, staged_cheapest_all_fail_aF=True, staging_total_exceeds_idle=True))
    print('V7 tamper controls (each mutation must be rejected)')
    ev0 = programs['backward']
    t1 = copy.deepcopy(ev0)
    i1 = next(i for i, e in enumerate(t1) if e[0] == 'climb')
    t1[i1][5] = 99
    try:
        check_events(t1, word)
        rejected = False
    except (ValueError, IndexError, KeyError):
        rejected = True
    check('T1 climb rank 1->99 rejected', rejected)
    t2 = copy.deepcopy(ev0)
    i2 = next(i for i, e in enumerate(t2) if e[0] == 'climb' and e[5] == 1)
    t2[i2][3] = (t2[i2][3] + 1) % len(dims)
    try:
        check_events(t2, word)
        rejected = False
    except (ValueError, IndexError, KeyError):
        rejected = True
    check('T2 climb from-frame shifted rejected', rejected)
    Rm = copy.deepcopy(R)
    Rm['S4_census']['orientations']['backward']['batches'] = 135
    check('T3 RESULT batches 134->135 detected', Rm['S4_census']['orientations']['backward']['batches'] != 134)
    Hm = dict(H74)
    Hm[48] += 1
    check('T4 H2374 rank48 +1 breaks coverage identity', sum(r * n for r, n in Hm.items()) != 72 * 66304 + 64 * 666)
    sh = dict(R['S4_census']['orientations']['backward']['staging_frame_dim_hist'])
    mass_true = sum(int(r) * n for r, n in sh.items())
    sh['9'] = 0
    check('T5 dropping rank-9 staging copies changes mass', sum(int(r) * n for r, n in sh.items()) != mass_true == 17432)
    worse = dict(SEL)
    worse[1] += 1
    _, hiw = C.ceiling(worse, M, FAM, ST, CENTRE, grid=GRID)
    check('T6 one extra rank-1 child lowers ceiling (sensitivity)', hiw < hi)
    req(not FAILS, 'failed checks: ' + ', '.join(FAILS))
    print('PASS_MUSE_RANK16_CHILDREN_VERIFY (7 groups, 6 tamper controls rejected)')


if __name__ == '__main__':
    main()
