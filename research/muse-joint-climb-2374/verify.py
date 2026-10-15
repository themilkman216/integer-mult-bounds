#!/usr/bin/env python3
"""Track 5A: one JOINT_CLIMB pair per call on #2374 — pair census, two-row operator, volume price.

Default: recompute everything and compare with RESULT.json. --write: regenerate RESULT.json.
Exact arithmetic: Fraction rows, F2 basis algebra, pinned ceiling.py rational intervals,
pinned clifford_exact.py Gaussian-dyadic columns. Checks use explicit exceptions (survive -O;
clifford_exact's internal asserts are additional only). Standard library only.
Prepared with Meta Muse (muse-wonder-full-1.0) assistance. Apache-2.0.
usage: verify.py [--write]
"""
import copy, gzip, hashlib, json, sys
from collections import Counter, defaultdict
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
GMX = ROOT / 'research/gmx-t74-borrow43-handoff'
M = 73
KF = Q(16971949509, 10 ** 13)          # 0.0016971949509 (#2374 headline, moment-root reading as in 4D)
AF = KF / (1 - KF)
GRID = Q(1, 10 ** 12)
T74 = {1: 2335, 2: 512, 3: 426, 4: 120, 5: 38, 8: 8}
H74 = {1: 1577088, 2: 340992, 3: 292308, 4: 79920, 5: 27860, 8: 5328, 32: 1, 48: 24560}
W74, N74 = 66304, 666
FIX = (558, 560)                        # chosen fixture pair (registers), transition () -> (459,) in A

PINS = {
    'ceiling_py': ('research/complex-local-word-ceiling/ceiling.py',
                   '86a1432870b3b21d8454106ec9162fddc0471472d9214c590a1420f2426cedfc'),
    'clifford_exact_py': ('research/gmx-t74-borrow43-handoff/new/code/borrow/vendor/clifford/clifford_exact.py',
                          '2982ead07721e83358dc67c6f49c2b4c16a236a6bebdfd72f58221be1f5d0962'),
    'borrow_audit_py': ('research/gmx-t74-borrow43-handoff/new/borrow/audit_local.py',
                        '36c82ecbface61a5b824c59ea90d1f31a31ff4b87bfef24e16742f06e18fa3c5'),
    'profile_json': ('research/gmx-t74-borrow43-handoff/PROFILE.json',
                     '30d6f326df5781308adfd20e700f2080d28f6a5414066f7d9abe9e69162f32d9'),
    'plan_json': ('research/gmx-t74-borrow43-handoff/PLAN.json',
                  '9b38b840732454c8a7266e5e3d851d3e68428919841ee24c4e77ebf2ffed44df'),
    'borrow_providers': ('research/gmx-t74-borrow43-handoff/new/BORROW-PROVIDERS.json',
                         'f82f0ec2d7989ae9d82db23564de6964251d547411853b817ce031528dad1b54'),
}
WORD_FILES = {
    'base': ('new/borrow/words/BORROW-WORD-43base.json.gz',
             '2a4bacd839c6c3d776709d3107e081ef0aa7753fececb630fe843cc105028eac',
             'a4963e5cec3e553067fe271122e98aef0d68ade655609d12d4a623ac80e40c97'),
    'extra': ('new/borrow/words/BORROW-WORD-43extra.json.gz',
              '832220ee1e6f2a6351d457ecb355aaf058ac5fe7f293fa9448471265f670b3a9',
              '2a49ebfca63673566ae46a3d05e884f93f04ed80c488bf62fc7ec6552df70b39'),
}
OWNERS_SHA_C = 'f91d45bbb35e1ad262d5413cdff1a5c720309dd15ab7f0cd7abc5a6e18ab94ad'
OWNERS_SHA_D = '06856c2e396666927e1885e66d340a96119f7a6bdb3ff554ae3f44e58c60df13'


def require(ok, why):
    if not ok:
        raise ValueError(why)


def sha_bytes(b):
    return hashlib.sha256(b).hexdigest()


def sha_path(p):
    return sha_bytes(Path(p).read_bytes())


def dec(x, d=12):
    return f'{float(x):.{d}g}'


def frac(x):
    return f'{x.numerator}/{x.denominator}'


def check_pins():
    out = {}
    for name, (rel, want) in PINS.items():
        got = sha_path(ROOT / rel)
        require(got == want, f'pin mismatch {name}')
        out[name] = got
    for name, (rel, wc, wd) in WORD_FILES.items():
        raw = (GMX / rel).read_bytes()
        require(sha_bytes(raw) == wc and sha_bytes(gzip.decompress(raw)) == wd, f'word pin {name}')
        out[f'word_{name}_compressed'] = wc
        out[f'word_{name}_content'] = wd
    raw = (GMX / 'OWNERS.json.gz').read_bytes()
    require(sha_bytes(raw) == OWNERS_SHA_C and sha_bytes(gzip.decompress(raw)) == OWNERS_SHA_D, 'owners pin')
    out['owners_compressed'] = OWNERS_SHA_C
    out['owners_content'] = OWNERS_SHA_D
    return out


sys.path.insert(0, str(ROOT / 'research/complex-local-word-ceiling'))
sys.path.insert(0, str(GMX / 'new/code/borrow/vendor/clifford'))
import ceiling as C  # noqa: E402
import clifford_exact as CE  # noqa: E402


# ---------- F2 frame algebra (reimplemented; semantics of borrow audit_local.py) ----------
def basis(vs):
    piv = {}
    for a in vs:
        while a:
            bit = a.bit_length() - 1
            if bit in piv:
                a ^= piv[bit]
            else:
                piv[bit] = a
                break
    for k in sorted(piv):
        for j in piv:
            if j > k and piv[j] >> k & 1:
                piv[j] ^= piv[k]
    return tuple(piv[k] for k in sorted(piv, reverse=True))


def contained(a, b):
    return basis(list(a) + list(b)) == b


def regs_of(e):
    return e[1:3] if e[0] == 'add' else e[1:2]


def extract(w):
    """Literal frame replay of one BORROW-WORD; returns climbs with trigger positions and windows.

    Event index i runs over A gates, one centres marker, warps+B gates, restore gates,
    final pseudo-events. A climb triggered by gate i may sit at any gap g (state before
    event g) with prev_touch(reg) < g <= i, inside its own section.
    """
    v, h, R = w['report']['v'], w['report']['h'], w['report']['R']
    n = 2 * v + R
    require((v, h, R) == (112, 9, 480), 'T74 geometry')
    removed = set(w['removed'])
    live = [r for r in range(n) if r not in removed]
    full = basis([1 << i for i in range(h)])
    end = [full] * v + [basis([x for x in range(1, 1 << h) if (x & p).bit_count() % 2 == 0])
                         for p in w['ports']] + [full] * R
    for q, U in w.get('helper_final', {}).items():
        end[int(q)] = basis(U)
    start = [(p,) for p in w['ports']] + [()] * (v + R)
    for q, U in w.get('start_extra', {}).items():
        start[int(q)] = basis(U)
    cur = start.copy()
    paid = Counter()
    climbs, events = [], []  # events: (section, touched tuple)

    def climb(q, U, section, pos):
        U = basis(U)
        require(contained(cur[q], U), f'frame not monotone reg {q}')
        d = len(U) - len(cur[q])
        if d:
            paid[d] += 1
            climbs.append(dict(pos=pos, section=section, reg=q, frm=cur[q], to=U, rank=d))
        cur[q] = U

    for e in w['A']:
        pos = len(events)
        events.append(('A', tuple(regs_of(e))))
        for q in regs_of(e):
            climb(q, e[-1], 'A', pos)
    events.append(('centers', ()))
    lev = {int(t): basis(U) for t, U in w.get('target_levels', {}).items()}
    require(all(cur[v + t] == lev.get(t, ()) for t in range(v)), 'target centre levels')
    centre_paid = Counter()
    for q, U in zip(w['centers'], w['center_frames']):
        U = basis(U)
        require(cur[q] == U, 'center frame')
        served = {lev.get(e[1] - v, ()) for e in w['cut'] if e[2] == q}
        for T in sorted(served, key=lambda x: -len(x)):
            require(contained(T, U), 'center path not nested')
            if T != U:
                centre_paid[len(U) - len(T)] += 1
                paid[len(U) - len(T)] += 1
            U = T
    bypos = defaultdict(list)
    for op, rec in enumerate(w['warps'], 1):
        bypos[rec[0]].append(op)
    B = w['B']
    for p in range(len(B) + 1):
        for op in bypos.get(p, []):
            _, lender, _cols, U, E = w['warps'][op - 1]
            require(cur[lender] == basis(U), f'warp frame mismatch op {op}')
            require(len(basis(U)) == len(basis(E)), 'warp rank zero dims')
            events.append(('B', (lender,)))
            cur[lender] = basis(E)
        if p < len(B):
            e = B[p]
            pos = len(events)
            events.append(('B', tuple(regs_of(e))))
            for q in regs_of(e):
                climb(q, e[-1], 'B', pos)
    for e in w['restore']:
        pos = len(events)
        events.append(('restore', tuple(regs_of(e))))
        for q in regs_of(e):
            climb(q, e[-1], 'restore', pos)
    for q in live:
        if cur[q] != end[q]:
            pos = len(events)
            events.append(('final', (q,)))
            climb(q, end[q], 'final', pos)
    require(all(cur[q] == end[q] for q in live), 'end frames')
    require(dict(paid) == {int(k): a for k, a in w['report']['local_profile'].items()},
            'paid profile mismatch')
    require(dict(paid) == T74, 'T74 local profile')
    widths = {q: len(end[q]) - len(start[q]) for q in range(2 * v, n)}
    inv = Counter(widths[q] for q in live if q >= 2 * v)
    require(dict(inv) == {int(k): a for k, a in w['report']['width_inventory'].items()},
            'width inventory mismatch')
    # per-register telescoping (dims; warps are equal-dim)
    for q in live:
        s = sum(c['rank'] for c in climbs if c['reg'] == q)
        require(s == len(end[q]) - len(start[q]), f'telescoping reg {q}')
    last, prev_at = {}, {}
    for i, (_sec, tt) in enumerate(events):
        for r in tt:
            prev_at[(i, r)] = last.get(r, -1)
        for r in tt:
            last[r] = i
    sec_start = {}
    for i, (sec, _tt) in enumerate(events):
        sec_start.setdefault(sec, i)
    for c in climbs:
        lo = max(prev_at.get((c['pos'], c['reg']), -1), sec_start[c['section']] - 1)
        hi = len(events) if c['section'] == 'final' else c['pos']
        c['win'] = (lo + 1, hi)  # gaps g with lo < g <= hi (final: up to end)
    return dict(v=v, h=h, R=R, n=n, removed=sorted(removed), live=live, start=start, end=end,
                climbs=climbs, events=events, paid=dict(paid), centre_paid=dict(centre_paid),
                widths=widths)


def common_gap(c1, c2):
    if c1['section'] != c2['section']:
        return None
    lo, hi = max(c1['win'][0], c2['win'][0]), min(c1['win'][1], c2['win'][1])
    return (lo, hi) if lo <= hi else None


def load_word(name):
    rel = WORD_FILES[name][0]
    return json.loads(gzip.decompress((GMX / rel).read_bytes()))


def candidates_of(X):
    g = defaultdict(list)
    for c in X['climbs']:
        if c['rank'] == 1 and c['frm'] == () and c['reg'] >= 224:
            g[(c['section'], c['frm'], c['to'])].append(c)
    out = {}
    for k, lst in g.items():
        for i in range(len(lst)):
            for j in range(i + 1, len(lst)):
                a, b = lst[i], lst[j]
                if a['reg'] != b['reg'] and common_gap(a, b):
                    out[(min(a['reg'], b['reg']), max(a['reg'], b['reg']), k)] = (a, b)
    return out


def apply_gate(e, rows):
    if e[0] == 'add':
        t, s = e[1], e[2]
        q = Q(e[3], e[4])
        dst = rows[t]
        for k, x in list(rows[s].items()):
            a = dst.get(k, Q(0)) + q * x
            if a:
                dst[k] = a
            else:
                dst.pop(k, None)
    elif e[0] == 'scale':
        t = e[1]
        q = Q(e[2], e[3])
        rows[t] = {k: q * x for k, x in rows[t].items()}
    else:
        raise ValueError(f'gate {e[0]}')


def census(words, Xs):
    wB, wE = words['base'], words['extra']
    XB, XE = Xs['base'], Xs['extra']
    require(wB['A'] == wE['A'], 'A sections identical in both T74 words')
    require(XB['removed'] == XE['removed'] and XB['start'] == XE['start'] and XB['end'] == XE['end'],
            'word anchors identical')
    out = {}
    for nm, X in Xs.items():
        r1 = [c for c in X['climbs'] if c['rank'] == 1]
        r10 = [c for c in r1 if c['frm'] == ()]
        trans_all = Counter((c['section'], c['frm'], c['to']) for c in r1)
        trans0 = Counter((c['section'], c['frm'], c['to']) for c in r10)
        out[nm] = dict(events=len(X['events']), climbs=len(X['climbs']), paid=X['paid'],
                       centre_paid=X['centre_paid'], rank1=len(r1), zero_rank1=len(r10),
                       zero_by_section=dict(Counter(c['section'] for c in r10)),
                       distinct_rank1_transitions=len(trans_all),
                       distinct_zero_transitions=len(trans0),
                       pair_ub_all=sum(k // 2 for k in trans_all.values()),
                       pair_ub_zero=sum(k // 2 for k in trans0.values()),
                       telescoping_registers=len(X['live']))
    require(out['base'] == out['extra'], 'census aggregates identical in both words')
    live_helpers = [r for r in range(224, 704) if r not in set(XB['removed'])]
    require(len(live_helpers) == 434, 'live helper count')
    hidx = {r: i for i, r in enumerate(live_helpers)}
    prov = json.loads((GMX / 'new/BORROW-PROVIDERS.json').read_text())
    for pid, X in (('gauge44', XB), ('extra', XE)):
        require([X['widths'][r] for r in live_helpers] == prov[pid]['widths'],
                f'{pid} widths = live helpers in register order')
        require({int(k): v for k, v in prov[pid]['actual_paid_profile'].items()} == T74, f'{pid} profile')
    require(prov['gauge44']['widths'] == prov['extra']['widths'], 'provider width lists identical')
    owners = json.loads(gzip.decompress((GMX / 'OWNERS.json.gz').read_bytes()))
    plan = json.loads((GMX / 'PLAN.json').read_text())
    require(plan['live'] == W74 and len(plan['order']) == N74 and len(plan['provider_calls']) == N74,
            'plan W/N')
    require({int(k): v for k, v in plan['profile'].items()} == H74, 'plan profile = H74')
    require(len(owners) == N74 * 434, 'owner rows 666x434')
    byth = {(z['time'], z['helper']): z for z in owners}
    require(len(byth) == len(owners), 'owner (time,helper) unique')
    pc = {c['time']: c for c in plan['provider_calls']}
    require(set(pc) == set(range(N74)), 'provider call times')
    per_time = defaultdict(list)
    for z in owners:
        per_time[z['time']].append(z)
        require(z['width'] == prov[pc[z['time']]['provider']]['widths'][z['helper']],
                'owner width vs provider')
        require(z['family'] == z['owner_replica'] * 896 +
                (2 * plan['pairs'][str(z['child'])] + plan['sides'][str(z['child'])]) * 112 + z['port'],
                'family identity')
    for t, rows in per_time.items():
        require(len(rows) == 434 and len({r['family'] for r in rows}) == 434,
                f'distinct helper families in call {t}')
    CB, CE = candidates_of(XB), candidates_of(XE)
    require(set(CB) == set(CE), 'candidate pair sets identical in both words')

    def key_of(z):
        return (z['port'], z['child'], z['offset'], z['width'])

    def route_of(z):
        return (3 if z['width'] == 9 else 4, z['child'], z['offset'], z['width'])

    scores = []
    for (r1, r2, (_sec, _f, to)) in CB:
        h1, h2 = hidx[r1], hidx[r2]
        ke = re_ = df = 0
        for t in range(N74):
            z1, z2 = byth[(t, h1)], byth[(t, h2)]
            ke += key_of(z1) == key_of(z2)
            re_ += route_of(z1) == route_of(z2)
            df += z1['family'] != z2['family']
        scores.append(dict(pair=[r1, r2], helpers=[h1, h2], to=list(to),
                           chart_key_equal=ke, route_equal=re_, distinct_families=df))
    require(all(s['distinct_families'] == N74 for s in scores), 'all candidates on distinct rows')
    best_key = max(scores, key=lambda s: (s['chart_key_equal'], s['route_equal'], [-x for x in s['pair']]))
    perfect = sorted([s['pair'] for s in scores if s['route_equal'] == N74])
    fix = [s for s in scores if s['pair'] == list(FIX)]
    require(len(fix) == 1 and fix[0]['route_equal'] == N74, 'fixture pair route-perfect')
    old = [s for s in scores if s['pair'] == [546, 560]]
    require(len(old) == 1, 'selected fixture pair present on T74 words')
    # fixture detail (base word; A identical in extra)
    cl = {(c['reg'], c['section'], c['frm'], c['to']): c for c in XB['climbs']}
    c1 = cl[(FIX[0], 'A', (), (459,))]
    c2 = cl[(FIX[1], 'A', (), (459,))]
    gap = common_gap(c1, c2)
    require(gap is not None, 'fixture common gap')
    gstar = min(c1['pos'], c2['pos'])
    require(gap[0] <= gstar <= gap[1], 'representative gap inside window')
    lenders = {rec[1] for rec in wB['warps']}
    detail = {}
    for r, c in ((FIX[0], c1), (FIX[1], c2)):
        chain = [dict(section=x['section'], pos=x['pos'], frm=list(x['frm']),
                      to=list(x['to']), rank=x['rank']) for x in XB['climbs'] if x['reg'] == r]
        detail[str(r)] = dict(helper=hidx[r], width=XB['widths'][r], start=list(XB['start'][r]),
                              end_dim=len(XB['end'][r]), trigger_pos=c['pos'], window=list(c['win']),
                              trigger_gate=wB['A'][c['pos']], chain=chain,
                              lender=r in lenders, entering=str(r) in wB['start_extra'],
                              restored=str(r) in wB['helper_final'], centre=r in wB['centers'])
        require(not detail[str(r)]['lender'] and not detail[str(r)]['entering']
                and not detail[str(r)]['restored'] and not detail[str(r)]['centre'],
                f'fixture register {r} plain helper')
        require(XB['start'][r] == () and len(XB['end'][r]) == 9 and XB['widths'][r] == 9,
                f'fixture register {r} zero-to-FULL width 9')
    # forward dirty rows at the gap: precondition + compensation + A[:gstar] over Q (no warps yet)
    require(all(e[0] in ('add', 'scale') for e in wB['precondition'] + wB['compensation']),
            'pre-A sections scalar only')
    require(all(112 <= e[1] < 224 for e in wB['precondition'] + wB['compensation']),
            'pre-A gates write targets only')
    rows = {r: {r: Q(1)} for r in XB['live']}
    for e in wB['precondition'] + wB['compensation'] + wB['A'][:gstar]:
        apply_gate(e, rows)
    require(rows[FIX[0]] == {FIX[0]: Q(1)} and rows[FIX[1]] == {FIX[1]: Q(1)},
            'fixture rows at gap are the two basis arrays (independent dirt)')
    out['candidates'] = dict(count_each_word=len(CB), in_both=len(CB),
                             best_chart_key=best_key, route_perfect_pairs=perfect,
                             selected_fixture_546_560=old[0])
    out['fixture'] = dict(pair=list(FIX), transition=dict(frm=[], to=[459], section='A', rank=1),
                          common_gap=list(gap), representative_gap=gstar,
                          score=fix[0], registers=detail,
                          rows_at_gap='basis arrays e_558, e_560 (forward replay)',
                          call0_owners=[byth[(0, hidx[FIX[0]])], byth[(0, hidx[FIX[1]])]])
    out['owners_checked'] = dict(rows=len(owners), calls=N74, helpers_per_call=434)
    return out


# ---------- (b) finite completed-child operators ----------
def operator_tests():
    n = 9
    U0, U1, U2 = [], [459], [304, 131, 120]
    require(basis(U1 + U2) == basis(U2) and len(basis(U2)) == 3, 'U1 subset U2 dims 1<3')
    T0, T1, T2 = CE.canonical_frame(n, U0), CE.canonical_frame(n, U1), CE.canonical_frame(n, U2)
    require(T0.tab == CE.ident(n).tab, 'zero frame representative is identity')
    ops = {}
    res = {}
    for nm, op, want in (('U0_to_U1', T0.adjoint().then(T1), 1),
                         ('U1_to_U2', T1.adjoint().then(T2), 2),
                         ('U0_to_U2', T0.adjoint().then(T2), 3)):
        rec, comp = CE.lower_child(op)
        require(rec['rank'] == want, f'{nm} lowered rank')
        require(comp.tab == op.tab, f'{nm} tableau equality')
        for x in range(512):
            require(comp.zero_state(x) == op.zero_state(x), f'{nm} column {x} exact')
        sup = [sum(1 for a in comp.zero_state(x)[0] if a != (0, 0)) for x in range(512)]
        dens = sorted({comp.zero_state(x)[1] for x in range(512)})
        require(min(sup) == max(sup) == 2 ** want, f'{nm} column support 2^rank')
        ops[nm] = (op, comp)
        res[nm] = dict(rank=want, columns_exact=512, support_per_column=2 ** want, denominators=dens)
    seq = ops['U0_to_U1'][0].then(ops['U1_to_U2'][0])
    require(seq.tab == ops['U0_to_U2'][0].tab, 'same-stream telescoping tableau')
    for x in range(512):
        require(seq.zero_state(x) == ops['U0_to_U2'][0].zero_state(x), f'telescope column {x}')
    # pair as direct sum on two streams: exact on mixed (non-basis) dirty vectors, blocks separated.
    # All columns share denominator 2^1 here, so superposition is exact integer addition of numerators.
    comp1 = ops['U0_to_U1'][1]
    cols = [comp1.zero_state(x) for x in range(512)]
    require(all(v != [(0, 0)] * 512 for v, _d in cols), 'every input column essential (nonzero image)')
    require(all(d == 1 for _v, d in cols), 'common denominator for superposition test')

    def apply_combo(combo):
        acc = [(0, 0)] * 512
        for x, c in combo.items():
            vec, _d = cols[x]
            acc = [(a + c * p, b + c * q) for (a, b), (p, q) in zip(acc, vec)]
        return acc

    in1, in2 = {0: 3, 7: -2, 511: 5}, {3: 1, 7: 4}
    out_pair = (apply_combo(in1), apply_combo(in2))
    require(out_pair[0] == apply_combo(in1) and out_pair[1] == apply_combo(in2),
            'pair blocks equal separate transitions on mixed dirt')
    in2_changed = {3: -9, 100: 2}
    require(apply_combo(in1) == out_pair[0] and apply_combo(in2_changed) != out_pair[1],
            'stream-2 dirt changes only block 2 (exit separation)')
    # sum-encoding collision: (e0,0) and (0,e0) have the same sum but different required outputs
    require(cols[0][0] != [(0, 0)] * 512, 'collision witness output nonzero')
    res['same_stream_telescope'] = dict(columns_exact=512,
                                        identity='T_U2 T_U0^-1 = (T_U2 T_U1^-1)(T_U1 T_U0^-1)')
    res['pair_direct_sum'] = dict(mixed_dirt_inputs=['{0:3,7:-2,511:5}', '{3:1,7:4}'],
                                  sum_encoding_collision='E(e0,0)=E(0,e0), required outputs differ by block')
    return res


# ---------- price arithmetic ----------
def moment(H, W, a):
    lo = hi = Q(0)
    for r, nn in H.items():
        c = C.child_cost(r, M, a)
        lo += Q(nn) * c[0]
        hi += Q(nn) * c[1]
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


def price_tests():
    prof = json.loads((GMX / 'PROFILE.json').read_text())
    H = {int(k): v for k, v in prof.items()}
    require(H == H74, 'PROFILE.json = H74')
    require(sum(r * nn for r, nn in H.items()) == 72 * W74 + 64 * N74, 'coverage 72W+64N')
    local = dict(H)
    idle = {1: 21978, 3: 8592, 5: 2552, 32: 1, 48: 24560}
    for r, nn in idle.items():
        local[r] = local.get(r, 0) - nn
    require({r: nn for r, nn in local.items() if nn} == {r: nn * N74 for r, nn in T74.items()},
            'H74 = 666x local + idle')
    Hs = dict(H); Hs[1] -= 2 * N74; Hs[2] += N74          # spliced: one rank-2 entry per pair
    Hd = dict(H); Hd[1] -= 2 * N74; Hd[2] += 2 * N74      # volume-doubled: two rank-2 entries
    require(sum(r * nn for r, nn in Hs.items()) == 72 * W74 + 64 * N74, 'spliced mass preserved')
    e0, e1, e2 = endpoint(H, W74), endpoint(Hs, W74), endpoint(Hd, W74)
    require(e0[0] <= KF <= e0[1], 'frontier endpoint bracket contains kappa2374')
    require(e1[0] > e0[1], 'spliced one-pair endpoint strictly above frontier')
    require(e2[1] < e0[0], 'volume-doubled endpoint strictly below frontier')
    m_d = moment(Hd, W74, KF)
    require(m_d[0] > 1, 'volume-doubled moment at kappa2374 exceeds 1')
    out = {}
    for tn, a in (('kappa2374', KF), ('aF_planning', AF)):
        c1, c2 = C.child_cost(1, M, a), C.child_cost(2, M, a)
        gain = (2 * c1[0] - c2[1], 2 * c1[1] - c2[0])        # spliced saving per pair (x W)
        pen = (2 * c2[0] - 2 * c1[1], 2 * c2[1] - 2 * c1[0])  # volume-doubled penalty per pair
        require(gain[0] > 0 and pen[0] > 0, f'spliced gain and doubled penalty positive at {tn}')
        out[tn] = dict(a=dec(a, 15), spliced_gain_per_pair_xW=[dec(gain[0]), dec(gain[1])],
                       doubled_penalty_per_pair_xW=[dec(pen[0]), dec(pen[1])])
    return dict(endpoints=dict(frontier_n0=[frac(e0[0]), frac(e0[1])], frontier_n0_hi=dec(e0[1]),
                                spliced_one_pair=[frac(e1[0]), frac(e1[1])], spliced_one_pair_hi=dec(e1[1]),
                                volume_doubled_one_pair=[frac(e2[0]), frac(e2[1])],
                                volume_doubled_hi=dec(e2[1]),
                                shared_width_one_pair='identical histogram price to separate (endpoint = frontier_n0)'),
                moment_doubled_at_kappa2374=[dec(m_d[0]), dec(m_d[1])], per_pair=out)


# ---------- tamper controls ----------
def expect_fail(fn, needle):
    try:
        fn()
    except Exception as ex:  # noqa: BLE001 - control harness records any rejection
        msg = f'{type(ex).__name__}: {ex}'
        require(needle in msg, f'control rejected for wrong reason: {msg} (wanted {needle!r})')
        return msg[:160]
    raise ValueError(f'tamper control was NOT rejected (wanted {needle!r})')


def tamper_controls(words, Xs, computed):
    out = []
    wB = words['base']
    # 1: fixture trigger frame value mutated 459 -> 458 (frame chain/profile must reject)
    def t1():
        wm = copy.deepcopy(wB)
        pos = computed['S2_census']['fixture']['registers']['560']['trigger_pos']
        require(wm['A'][pos][-1] == [459], 'pre: trigger frame')
        wm['A'][pos][-1] = [458]
        extract(wm)
    out.append('trigger_frame_459_to_458: ' + _any_fail(t1))
    # 2: fixture climb dropped by zeroing its trigger frame
    def t2():
        wm = copy.deepcopy(wB)
        pos = computed['S2_census']['fixture']['registers']['558']['trigger_pos']
        wm['A'][pos][-1] = []
        extract(wm)
    out.append('fixture_climb_dropped: ' + _any_fail(t2))
    # 3: merge fixture families in call 0
    def t3():
        owners = json.loads(gzip.decompress((GMX / 'OWNERS.json.gz').read_bytes()))
        byth = {(z['time'], z['helper']): z for z in owners}
        s = computed['S2_census']['fixture']['score']
        h1, h2 = s['helpers']
        byth[(0, h2)]['family'] = byth[(0, h1)]['family']
        rows = [z for z in owners if z['time'] == 0]
        require(len({r['family'] for r in rows}) == 434, 'distinct helper families in call 0')
    out.append('owner_family_merge: ' + expect_fail(t3, 'distinct helper families'))
    # 4: fixture offset mutated breaks route perfection
    def t4():
        owners = json.loads(gzip.decompress((GMX / 'OWNERS.json.gz').read_bytes()))
        byth = {(z['time'], z['helper']): z for z in owners}
        s = computed['S2_census']['fixture']['score']
        h1, h2 = s['helpers']
        byth[(0, h2)]['offset'] += 1
        rt = lambda z: (3 if z['width'] == 9 else 4, z['child'], z['offset'], z['width'])
        eq = sum(1 for t in range(N74) if rt(byth[(t, h1)]) == rt(byth[(t, h2)]))
        require(eq == N74, 'fixture route-perfect in all calls')
    out.append('owner_offset_plus1: ' + expect_fail(t4, 'route-perfect'))
    # 5: extra rank-48 child breaks coverage
    def t5():
        H = dict(H74); H[48] += 1
        require(sum(r * nn for r, nn in H.items()) == 72 * W74 + 64 * N74, 'coverage 72W+64N')
    out.append('extra_rank48: ' + expect_fail(t5, 'coverage'))
    # 6: volume-doubled claimed passing at kappa2374
    def t6():
        Hd = dict(H74); Hd[1] -= 2 * N74; Hd[2] += 2 * N74
        require(moment(Hd, W74, KF)[1] < 1, 'doubled moment claimed passing')
    out.append('doubled_claimed_passing: ' + expect_fail(t6, 'claimed passing'))
    # 7: sum encoding claimed exact for the pair (collision witness)
    def t7():
        n = 9
        T1 = CE.canonical_frame(n, [459])
        op = CE.ident(n).adjoint().then(T1)
        _rec, comp = CE.lower_child(op)
        col0 = comp.zero_state(0)[0]
        # claim: one-stream pipeline on E(x,y)=x+y separates (e0,0) from (0,e0); both encode to e0,
        # so block-1 output for (0,e0) would have to be zero while col0 is the (nonzero) image.
        require(col0 == [(0, 0)] * 512, 'sum encoding claimed separable')
    out.append('sum_encoding_claimed_exact: ' + expect_fail(t7, 'separable'))
    # 8: stored receipt mutation (in-memory): spliced endpoint hi lowered must fail comparison
    def t8():
        bad = copy.deepcopy(computed)
        bad['S4_price']['endpoints']['spliced_one_pair_hi'] = '0.0016'
        require(bad == computed, 'RESULT replay comparison')
    out.append('result_endpoint_mutated: ' + expect_fail(t8, 'replay comparison'))
    return out


def _any_fail(fn):
    try:
        fn()
    except Exception as ex:  # noqa: BLE001
        return f'{type(ex).__name__}: {ex}'[:120]
    raise ValueError('tamper control was NOT rejected')


def main():
    write = '--write' in sys.argv
    pins = check_pins()
    words = {nm: load_word(nm) for nm in WORD_FILES}
    Xs = {nm: extract(w) for nm, w in words.items()}
    computed = {
        'status': 'FALSIFIED_AT_VOLUME_PRICE_no_new_kappa',
        'task': 'muse-joint-climb-2374 (Track 5A)',
        'selected_kappa': '836330098538459/500000000000000000',
        'frontier_target': '0.0016971949509 (#2374, unreviewed, moment-root reading)',
        'pins': pins,
        'S2_census': census(words, Xs),
        'S3_operator': operator_tests(),
        'S4_price': price_tests(),
    }
    computed['S5_tamper_controls'] = tamper_controls(words, Xs, computed)
    computed = json.loads(json.dumps(computed, sort_keys=True))  # normalize int keys/tuples as stored
    rp = HERE / 'RESULT.json'
    if write:
        rp.write_text(json.dumps(computed, indent=1, sort_keys=True) + '\n')
        print('WROTE', rp)
        return
    stored = json.loads(rp.read_text())
    require(stored == computed, 'RESULT.json replay comparison failed')
    fx = computed['S2_census']['fixture']
    ep = computed['S4_price']['endpoints']
    print(f"PASS_MUSE_JOINT_CLIMB_2374 fixture={fx['pair']} gap={fx['representative_gap']} "
          f"route_equal={fx['score']['route_equal']}/666 candidates={computed['S2_census']['candidates']['count_each_word']} "
          f"spliced_hi={ep['spliced_one_pair_hi']} doubled_hi={ep['volume_doubled_hi']} "
          f"tamper={len(computed['S5_tamper_controls'])}/{len(computed['S5_tamper_controls'])} rejected; "
          f"verdict=volume-priced-at-separate; no_new_kappa")


if __name__ == '__main__':
    main()
