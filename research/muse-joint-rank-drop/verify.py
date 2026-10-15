#!/usr/bin/env python3
"""Width-2 joint-rank lift (Track 4C): exact thresholds, cheapest-pair replay, lower-bound checks.

Default: recompute everything and compare with RESULT.json. --write: regenerate RESULT.json.
All acceptance arithmetic is exact rational intervals via the pinned predecessor engine
research/complex-local-word-ceiling/ceiling.py; symbolic dirty replay is over Fraction.
Checks use explicit exceptions (survive -O). Standard library only.
Prepared with Meta Muse (muse-wonder-full-1.0) assistance. Apache-2.0.
usage: verify.py [--write]
"""
import bisect, collections, copy, gzip, hashlib, io, json, sys, tarfile
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'research/complex-local-word-ceiling'))
sys.path.insert(0, str(ROOT / 'research/diagonal-batch-commutation'))
import ceiling as C  # noqa: E402
import batch as B  # noqa: E402  (touched/split_phases/is_r1 only; replays below are explicit)

M, FAM, ST, CENTRE = 73, 896, 9, 64
SEL = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}
T74 = {1: 2335, 2: 512, 3: 426, 4: 120, 5: 38, 8: 8}
KF = Q(16971949509, 10 ** 13)
AF = KF / (1 - KF)
AB = Q(1733427039589844234749, 1000000000000000000000000)  # ASSEMBLY bit_lower, checked below
GRID = Q(1, 10 ** 12)
ARCH_SHA = 'f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6'
MEM_SHA = {'LOCAL-PROGRAMS.json.gz': '241fde27d4e43f5a9cb6b128f9f76c5131a53d09f0371676163f914d0b0fef3a',
           'CANONICAL-WORD.json.gz': '16bc0ebb04b4be6c0ade74badc6a0c0cdba4215eda86e4ff9f13abf8ecebd219'}


def require(ok, why):
    if not ok:
        raise ValueError(why)


def sha_bytes(b):
    return hashlib.sha256(b).hexdigest()


def sha_path(p):
    return sha_bytes(Path(p).read_bytes())


def dec(x, d=12):
    return f'{float(x):.{d}g}'


def iv_dec(v):
    return [dec(v[0]), dec(v[1])]


def load_pinned():
    arch = ROOT / 'research/community-frontier1094-audit/selected-replay.tar.gz'
    raw = arch.read_bytes()
    require(sha_bytes(raw) == ARCH_SHA, 'archive pin')
    pins = {'archive_sha256': ARCH_SHA,
            'ceiling_py_sha256': sha_path(ROOT / 'research/complex-local-word-ceiling/ceiling.py'),
            'batch_py_sha256': sha_path(ROOT / 'research/diagonal-batch-commutation/batch.py'),
            'hpe_audit_sha256': sha_path(ROOT / 'research/complex-571-cold14-k492b/code/hpe_audit_local.py')}
    with tarfile.open(fileobj=io.BytesIO(raw), mode='r:gz') as tar:
        asm_raw = tar.extractfile('candidate/strict/ASSEMBLY.json').read()
        asm = json.loads(asm_raw)
        require(Q(asm['bit_lower']) == AB, 'bit endpoint pin')
        pins['ASSEMBLY.json'] = sha_bytes(asm_raw)
        own_raw = tar.extractfile('candidate/strict/global/audit/OWNERS-AND-PROFILE.json').read()
        pins['OWNERS-AND-PROFILE.json'] = sha_bytes(own_raw)
        owners_prof = json.loads(own_raw)
        tmpl_raw = tar.extractfile('candidate/strict/global/hosted/GLOBAL-TEMPLATE.json.gz').read()
        pins['GLOBAL-TEMPLATE.json.gz'] = sha_bytes(tmpl_raw)
        template = json.load(gzip.open(io.BytesIO(tmpl_raw)))
        mem = {}
        for name, want in MEM_SHA.items():
            d = tar.extractfile('candidate/strict/global/base/providers/gauge44/' + name).read()
            require(sha_bytes(d) == want, 'member pin ' + name)
            pins[name] = want
            mem[name] = d
    word = json.load(gzip.open(io.BytesIO(mem['CANONICAL-WORD.json.gz'])))
    prog = json.load(gzip.open(io.BytesIO(mem['LOCAL-PROGRAMS.json.gz'])))
    extra = dict(asm=asm, owners_prof=owners_prof, template=template)
    return pins, word, prog, extra


def span_set(basis):
    s = {0}
    for v in basis:
        s |= {x ^ v for x in s}
    return s


def contains_elim(frames, a, b):
    """span(frames[a]) subset span(frames[b]) by F2 elimination (batch.py method)."""
    for x in frames[a]:
        y = x
        for v in frames[b]:
            if y >> (v.bit_length() - 1) & 1:
                y ^= v
        if y:
            return False
    return True


def catalogue(word):
    frames, dims = word['frames'], [len(f) for f in word['frames']]
    spans = [span_set(f) for f in frames]
    for i, f in enumerate(frames):  # basis really is a basis of its span
        require(len(spans[i]) == 1 << dims[i], f'frame {i} basis size')
    require(len(frames) == 1004 and frames[0] == [] and dims[1] == 9, 'catalogue endpoints')
    require(frames[4] == [459] and spans[4] == {0, 459}, 'frame 4 line')
    require(frames[2] == [30] and frames[3] == [51], 'frames 2,3 lines')
    # two containment methods agree on every ordered pair among endpoint frames used below
    probe = [0, 1, 2, 3, 4, 37, 414, 426]
    for a in probe:
        for b in probe:
            require(contains_elim(frames, a, b) == (spans[a] <= spans[b]), f'contains methods {a},{b}')
    between = [i for i in range(len(frames)) if spans[0] <= spans[i] <= spans[4]]
    require(between == [0, 4], 'frames between 0 and 4')
    join23 = sorted((i for i in range(len(frames)) if spans[2] <= spans[i] and spans[3] <= spans[i]),
                     key=lambda i: dims[i])
    require(dims[join23[0]] == 4, 'smallest catalogue frame containing lines 2 and 3 has dim 4')
    hist = {str(k): v for k, v in sorted(collections.Counter(dims).items())}
    require(hist == {'0': 1, '1': 120, '2': 168, '3': 168, '4': 73, '5': 27,
                     '6': 168, '7': 152, '8': 126, '9': 1}, 'frame dim histogram')
    return dict(frames=frames, dims=dims, spans=spans, dim_hist=hist,
                between_0_4=between, join23_min_dim=dims[join23[0]],
                join23_first=join23[:3])


def thresholds():
    out = {}
    q = C.model(SEL, M, FAM, ST, CENTRE)
    R = q['R']
    require(R == 51, 'R(73)')

    def excess(a):
        cR = C.child_cost(R, M, a)

        def p(r):
            c = C.child_cost(r, M, a)
            return (c[0] - r * cR[1] / R, c[1] - r * cR[0] / R)
        p1, p2, p8 = p(1), p(2), p(8)
        g = (2 * p1[0] - p2[1], 2 * p1[1] - p2[0])
        ratio = (g[0] / p1[1], g[1] / p1[0])
        require(g[0] > 0 and p1[0] > 0, 'positive gap/excess')
        require(p1[0] > g[1], 'one rank-1 copy exceeds the whole width-2 saving')
        require(p8[0] / 8 > g[1], 'one mass unit at rank-8 shape exceeds the saving')
        require(ratio[1] < Q(9, 25), 'ratio below 0.36')
        f1, f2 = C.child_cost(1, M, a), C.child_cost(2, M, a)
        require(2 * f1[0] - f2[1] >= g[0] and 2 * f1[1] - f2[0] <= g[1] + Q(1, 10 ** 30),
                'g2 equals 2f1-f2 (idle terms cancel)')
        spend_lo = sum(n * p(r)[0] for r, n in SEL.items())
        b_hi = q['w'] - q['total_mass'] * cR[0] / R
        maxmass8 = (8 * g[0] / p8[1], 8 * g[1] / p8[0])  # staging mass/pair at rank-8 shape
        require(maxmass8[1] < 1, 'rank-8-shaped staging allowance below one mass unit')
        return dict(p1=iv_dec(p1), p2=iv_dec(p2), p8=iv_dec(p8), g2=iv_dec(g),
                    ratio=[dec(ratio[0]), dec(ratio[1])], ratio_hi_below='9/25',
                    max_staging_mass_shape8=[dec(maxmass8[0]), dec(maxmass8[1])],
                    overspend_sel_lower=dec(spend_lo - b_hi))
    for nm, a in (('kappa2374', KF), ('aF_planning', AF), ('a_bit', AB)):
        out[nm] = excess(a)
    # strict subadditivity and splitting costs more, all small ranks at aF
    f = {r: C.child_cost(r, M, AF) for r in range(1, 19)}
    for r1 in range(1, 10):
        for r2 in range(1, 10):
            require(f[r1][0] + f[r2][0] > f[r1 + r2][1], f'subadditivity {r1}+{r2}')

    def comps(n, lo=1):
        if n == 0:
            yield []
        for first in range(lo, n + 1):
            for rest in comps(n - first, lo):
                yield [first] + rest
    ncomp = 0
    for rho in range(2, 10):
        for parts in comps(rho):
            if len(parts) < 2:
                continue
            ncomp += 1
            require(sum(f[x][0] for x in parts) > f[rho][1], f'splitting {rho}={parts} costs more')
    out['subadditivity'] = dict(pairs_checked=81, compositions_checked=ncomp, at='aF_planning')
    return out


def ok_relax(local, a):
    try:
        return C.relax(local, M, FAM, ST, CENTRE, a)[1] < 1
    except ValueError:
        return False


def paired(W, n):
    L = dict(W)
    L[1] -= 2 * n
    L[2] = L.get(2, 0) + n
    return {r: v for r, v in L.items() if v != 0}


def min_pairs(W, a):
    if ok_relax(W, a):
        return 0
    mx = W[1] // 2
    require(ok_relax(paired(W, mx), a), 'all-paired profile passes target')
    lo, hi = 0, mx
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if ok_relax(paired(W, mid), a):
            hi = mid
        else:
            lo = mid
    require(ok_relax(paired(W, hi), a) and not ok_relax(paired(W, hi - 1), a), 'adjacent min-pairs bracket')
    return hi


def optimistic():
    def ceil_hi(W):
        lo, hi = C.ceiling(W, M, FAM, ST, CENTRE, grid=GRID)
        return [str(lo), str(hi)], dec(hi)
    out = {}
    for nm, W in (('selected', SEL), ('t74_2322', T74)):
        base, base_dec = ceil_hi(W)
        allp, allp_dec = ceil_hi(paired(W, W[1] // 2))
        out[nm] = dict(base_ceiling=base, base_ceiling_hi=base_dec,
                       all_paired_ceiling=allp, all_paired_ceiling_hi=allp_dec,
                       min_pairs={'kappa2374': min_pairs(W, KF), 'aF_planning': min_pairs(W, AF),
                                  'a_bit': min_pairs(W, AB)})
    require(out['selected']['min_pairs'] == {'kappa2374': 64, 'aF_planning': 90, 'a_bit': 379},
            'selected min pairs')
    require(out['t74_2322']['min_pairs']['a_bit'] == 34, 't74 min pairs to bit endpoint')
    return out


def frame_replay(events, word, cat):
    """Explicit cur/private replay (no asserts). Returns (hist, per-register climb sums, phase census)."""
    frames, dims, spans = cat['frames'], cat['dims'], cat['spans']
    cur, private, phase = list(word['start']), {}, None
    hist, sums = collections.Counter(), collections.Counter()
    climb_ph, adap_ph, center_ph = collections.Counter(), collections.Counter(), collections.Counter()
    for e in events:
        tag = e[0]
        if tag == 'phase':
            require(not private, 'private live at phase boundary')
            phase = e[1]
        elif tag == 'climb':
            _, part, r, a, b, rank = e
            require(not private and phase == part and cur[r] == a, 'climb precondition')
            require(spans[a] <= spans[b] and rank == dims[b] - dims[a] > 0, 'climb span/rank')
            require(contains_elim(frames, a, b), 'climb span (elimination agrees)')
            hist[rank] += 1
            sums[r] += rank
            cur[r] = b
            climb_ph[part] += 1
        elif tag == 'center':
            _, k, a, b, rank = e
            require(phase == 'centers' and private == {('C', k): a}, 'center precondition')
            require((spans[a] <= spans[b] or spans[b] <= spans[a]) and rank == abs(dims[a] - dims[b]) > 0,
                    'center nested/rank')
            private[('C', k)] = b
            hist[rank] += 1
            center_ph[phase] += 1
        elif tag == 'scalar':
            _, op, f = e
            target = tuple(op[1])
            source = tuple(op[2]) if op[0] in ('copy', 'add') else None
            if target[0] == 'C' and op[0] == 'clear':
                require(private.get(target, f) == f, 'private clear frame')
                private.pop(target, None)
                continue
            for reg in (target, source):
                if reg is None:
                    continue
                if reg[0] == 'L':
                    require(cur[reg[1]] == f, 'scalar common frame')
                else:
                    if reg == target and reg not in private:
                        private[reg] = f
                    require(private.get(reg) == f, 'private common frame')
        elif tag in ('adapter', 'residual_adapter'):
            adap_ph[(tag, phase)] += 1  # records wrappers; cur unchanged (checked by phase census)
        else:
            raise ValueError('unknown event tag ' + str(tag))
    require(cur == word['final'] and not private, 'terminal frames/private')
    return hist, sums, climb_ph, adap_ph, center_ph


def census(word, prog, cat):
    dims = cat['dims']
    out = {'orientations': {}}
    for orient, events in sorted(prog.items()):
        hist, sums, climb_ph, adap_ph, center_ph = frame_replay(events, word, cat)
        require(dict(hist) == SEL, f'{orient} paid histogram = selected local profile')
        for r in range(len(word['start'])):
            require(sums[r] == dims[word['final'][r]] - dims[word['start'][r]],
                    f'{orient} telescoping register {r}')
        require(set(climb_ph) <= {'A', 'B', 'cleanup_tail', 'final'}, 'climb phases')
        require(set(ph for _, ph in adap_ph) <= {'entry_adapters', 'exit_adapters', 'full_frame_cleanup'},
                'adapter phases (none inside climb phases)')
        require(dict(center_ph) == {'centers': 8}, 'center phase census')
        r1 = [e for e in events if e[0] == 'climb' and e[5] == 1]
        require(len(r1) == 2412, 'rank-1 climbs')
        staging = [dims[e[3]] + dims[e[4]] for e in r1]
        require(min(staging) == 1 and sum(1 for s in staging if s == 1) == 352,
                'minimum staging mass 1/register, attained 352x (zero frame)')
        require(all(s == 2 * dims[e[3]] + 1 for s, e in zip(staging, r1)), 'staging = 2dim(a)+1')
        trans = collections.Counter((e[3], e[4]) for e in r1 if e[3] == 0)
        require(trans[(0, 3)] == 32 and trans[(0, 2)] == 32, 'zero-frame transitions (0,3),(0,2)')
        pair_ev = [e for e in events if e[0] == 'climb' and e[2] in (546, 560) and e[3] == 0 and e[4] == 4]
        require(sorted(e[2] for e in pair_ev) == [546, 560], 'cheapest pair events exist')
        # windows in phase A via the pinned touched/split rules
        win_pair = {}
        for ph, body in B.split_phases(events):
            if not ph or ph[1] != 'A':
                continue
            skel = [e for e in body if not B.is_r1(e)]
            s, climbs, gap = len(skel), [], 0
            for e in body:
                if B.is_r1(e):
                    climbs.append((gap, e))
                else:
                    gap += 1
            touch = collections.defaultdict(list)
            for i, e in enumerate(skel):
                for reg in B.touched(e):
                    touch[reg].append(i)
            for g, e in climbs:
                if e[2] in (546, 560) and e[3] == 0:
                    pos = touch[('L', e[2])]
                    j = bisect.bisect_left(pos, g)
                    win_pair[e[2]] = [g, (pos[j - 1] + 1 if j > 0 else 0), (pos[j] if j < len(pos) else s)]
        require(win_pair == {546: [1190, 0, 1190], 560: [1191, 0, 1191]}, f'cheapest pair windows {win_pair}')
        require(max(win_pair[546][1], win_pair[560][1]) <= min(win_pair[546][2], win_pair[560][2]),
                'cheapest pair windows overlap (co-live at a common gap)')
        # symbolic rows at the pair cut: the abstract (X1,X2)=(e1,e2) model is literal or rank-2
        rows = {('L', r): {r: Q(1)} for r in range(len(word['start']))}
        at_cut = {}
        for idx, e in enumerate(events):
            if e[0] == 'climb' and e[2] in (546, 560) and e[3] == 0 and e[4] == 4 and e[2] not in at_cut:
                at_cut[e[2]] = (idx, dict(rows[('L', e[2])]))
            if len(at_cut) == 2:
                break
            if e[0] != 'scalar':
                continue
            _, op, _f = e
            kind, t = op[0], tuple(op[1])
            s = tuple(op[2]) if kind in ('copy', 'add') else None
            if kind == 'clear':
                rows[t] = {}
            elif kind == 'copy':
                rows[t] = dict(rows[s])
            elif kind == 'scale':
                qq = Q(op[2], op[3])
                rows[t] = {j: qq * x for j, x in rows[t].items() if qq * x}
            elif kind == 'add':
                qq = Q(op[3], op[4])
                row = rows.setdefault(t, {})
                for j, x in list(rows[s].items()):
                    z = row.get(j, Q(0)) + qq * x
                    if z:
                        row[j] = z
                    else:
                        row.pop(j, None)
        require(sorted(at_cut) == [546, 560], 'pair rows at cut found')
        ra, rb = at_cut[546][1], at_cut[560][1]
        ks = sorted(set(ra) | set(rb))
        minor = None
        for i in range(len(ks)):
            for j in range(i + 1, len(ks)):
                det = ra.get(ks[i], Q(0)) * rb.get(ks[j], Q(0)) - ra.get(ks[j], Q(0)) * rb.get(ks[i], Q(0))
                if det:
                    minor = [ks[i], ks[j], str(det)]
                    break
            if minor:
                break
        require(minor is not None, 'rows at pair cut are independent (rank 2 over Q)')
        if orient == 'forward':
            require(ra == {546: Q(1)} and rb == {560: Q(1)}, 'forward rows at cut are basis vectors')
        rows_rec = {'indices': {str(k): v[0] for k, v in at_cut.items()},
                    'nnz': {str(k): len(v[1]) for k, v in at_cut.items()}, 'minor': minor}
        out['orientations'][orient] = dict(
            hist={str(k): v for k, v in sorted(hist.items())},
            climb_phases={str(k): v for k, v in sorted(climb_ph.items())},
            adapter_phases=[[t, p, n] for (t, p), n in sorted(adap_ph.items())],
            telescoping_registers=len(word['start']), rank1=2412, zero_frame_rank1=352,
            rows_at_pair_cut=rows_rec,
            cheapest_pair={'registers': [546, 560], 'transition': [0, 4],
                           'gap_window': {str(k): v for k, v in win_pair.items()}})
    _f = {k: v for k, v in out['orientations']['forward'].items() if k != 'rows_at_pair_cut'}
    _b = {k: v for k, v in out['orientations']['backward'].items() if k != 'rows_at_pair_cut'}
    require(_f == _b, 'orientations agree apart from rows at cut')
    return out


class Mini:
    """Symbolic dirty replay on the cheapest pair. Rows over Q in basis (X1, X2, H)."""

    def __init__(self, cat, helper_row=None):
        self.dims, self.spans = cat['dims'], cat['spans']
        self.cur = {'r1': 0, 'r2': 0, 'h': 0, 'P': None}
        self.rows = {'r1': {0: Q(1)}, 'r2': {1: Q(1)},
                     'h': dict(helper_row) if helper_row else {}, 'P': {}}
        self.hist = collections.Counter()
        self.p_live = False

    def _frame(self, reg, f):
        require(self.cur[reg] == f, f'common frame: {reg} at {self.cur[reg]} != {f}')

    def add(self, dst, src, f, q=Q(1)):
        self._frame(dst, f)
        self._frame(src, f)
        row = dict(self.rows[dst])
        for j, x in self.rows[src].items():
            z = row.get(j, Q(0)) + q * x
            if z:
                row[j] = z
            else:
                row.pop(j, None)
        self.rows[dst] = row

    def copy(self, dst, src, f):
        if dst == 'P' and self.cur['P'] is None:
            self.cur['P'] = f  # first private touch allocates at f (hpe semantics)
        self._frame(dst, f)
        self._frame(src, f)
        self.rows[dst] = dict(self.rows[src])
        if dst == 'P':
            self.p_live = True

    def clear(self, reg, f):
        self._frame(reg, f)
        self.rows[reg] = {}
        if reg == 'P':
            self.p_live = False

    def climb(self, reg, b):
        require(reg != 'P' and not self.p_live, 'climb requires no private live')
        a = self.cur[reg]
        require(self.spans[a] <= self.spans[b] and self.dims[b] - self.dims[a] > 0, 'climb span/rank')
        self.hist[self.dims[b] - self.dims[a]] += 1
        self.cur[reg] = b

    def center_step(self, b):
        require(self.p_live and self.cur['P'] is not None, 'center step needs live private')
        a = self.cur['P']
        require((self.spans[a] <= self.spans[b] or self.spans[b] <= self.spans[a])
                and abs(self.dims[b] - self.dims[a]) > 0, 'center nested/rank')
        self.hist[abs(self.dims[b] - self.dims[a])] += 1
        self.cur['P'] = b

    def endpoint(self, helper_row=None):
        require(self.cur['r1'] == 4 and self.cur['r2'] == 4, f"endpoint frames {self.cur}")
        require(self.rows['r1'] == {0: Q(1)} and self.rows['r2'] == {1: Q(1)}, 'endpoint rows = identity')
        require(self.rows['h'] == (dict(helper_row) if helper_row else {}), 'helper dirt restored')
        require(self.cur['h'] == 0, 'helper frame restored (drop-in fragment)')
        require(not self.p_live and self.rows['P'] == {}, 'private erased')
        return True


def expect_fail(fn, needle):
    try:
        fn()
    except ValueError as e:
        require(needle in str(e), f'failure reason {e!r} lacks {needle!r}')
        return str(e)
    raise ValueError('candidate unexpectedly accepted (wanted: ' + needle + ')')


def candidates(cat):
    out = {}

    def separate(mutate=None):
        m = Mini(cat)
        m.climb('r1', 4)
        if mutate != 'drop_second':
            m.climb('r2', 4)
        m.endpoint()
        return dict(m.hist)
    require(separate() == {1: 2}, 'positive control hist')
    out['separate'] = {'hist': {'1': 2}, 'verdict': 'PASS'}
    out['single_climb'] = {'verdict': expect_fail(lambda: separate('drop_second'), 'endpoint frames')}

    def sum_climb(copyback=True):
        m = Mini(cat)
        m.add('r2', 'r1', 0)          # S = X1+X2 at common zero frame (free scalar)
        m.climb('r2', 4)              # one rank-1 climb of the sum (cheaper than joint claim)
        if copyback:
            m.copy('r1', 'r2', 4)     # needs cur[r1]==4, still 0
        m.endpoint()
        return m
    out['sum_climb_frame'] = {'verdict': expect_fail(sum_climb, 'common frame')}
    m = Mini(cat)
    m.add('r2', 'r1', 0)
    bcast = [[m.rows['r2'].get(j, Q(0)) for j in (0, 1)]] * 2  # delivering S to both registers
    require(bcast == [[Q(1), Q(1)], [Q(1), Q(1)]] and bcast != [[Q(1), Q(0)], [Q(0), Q(1)]],
            'broadcast matrix is rank-1 all-ones, not I2')
    require(bcast[0][0] * 1 + bcast[0][1] * 0 == 1 and bcast[1][0] * 1 + bcast[1][1] * 0 == 1,
            'witness input (1,0) maps to (1,1)')
    out['sum_climb_value'] = {'broadcast': [['1', '1'], ['1', '1']], 'witness_in': [1, 0], 'witness_out': [1, 1]}

    def staged(complete=False):
        m = Mini(cat)                 # helper h clean zero at frame 0 (favourable)
        m.copy('h', 'r1', 0)
        m.add('h', 'r2', 0)           # packed sum in helper
        m.climb('h', 4)               # staged joint climb on helper
        if not complete:
            m.copy('r1', 'h', 4)      # scatter: r1 still at frame 0
        else:
            m.climb('r1', 4)
            m.climb('r2', 4)          # registers climb anyway; values already correct
            m.clear('h', 4)           # value restored, frame not (climbs cannot descend)
        m.endpoint()
        return m
    out['staged_scatter'] = {'verdict': expect_fail(lambda: staged(False), 'common frame')}
    try:
        staged(True)
        raise ValueError('staged completion accepted')
    except ValueError as e:
        require('helper frame restored' in str(e), 'staged completion failure reason')
        out['staged_completion'] = {'hist': {'1': 3}, 'verdict': str(e),
                                    'note': 'hist {1:3} excess 3p1 > separate 2p1 even before frame restoration'}

    def private_transfer():
        m = Mini(cat)
        m.copy('P', 'r1', 0)
        m.center_step(4)              # private frame moves, billed rank 1
        m.clear('P', 4)
        m.endpoint()                  # L frames never moved
        return m
    out['private_transfer'] = {'verdict': expect_fail(private_transfer, 'endpoint frames')}

    def dirty_helper():
        m = Mini(cat, helper_row={2: Q(1)})   # helper carries independent dirt H
        m.copy('h', 'r1', 0)                  # destroys H
        m.climb('r1', 4)
        m.climb('r2', 4)
        m.endpoint(helper_row={2: Q(1)})
        return m
    out['dirty_helper_overwrite'] = {'verdict': expect_fail(dirty_helper, 'helper dirt restored')}
    return out


H74 = {1: 1577088, 2: 340992, 3: 292308, 4: 79920, 5: 27860, 8: 5328, 32: 1, 48: 24560}
W74, N74 = 66304, 666
H74_SRC = ('refs/upr/2374 research/gmx-t74-borrow43-handoff/PROFILE.json '
           'sha256 30d6f326df5781308adfd20e700f2080d28f6a5414066f7d9abe9e69162f32d9')


def check_coverage(H, W, N):
    require(sum(r * n for r, n in H.items()) == 72 * W + 64 * N, 'coverage identity 72W+64N')
    require(W - 64 * N > 0, 'positive deficit W-64N')


def check_owners(calls):
    require(len(calls) == 144, 'global template call count')
    for c in calls:
        own = c['owners']
        require(len(own) == 704, 'owners per call')
        require(len({o[0] for o in own}) == 704, 'distinct physical owners per call')
        require(own[546][0] != own[560][0], 'fixture registers have distinct physical owners')
    return True


def fixture_layout(word, prog, extra, census_res):
    """Track 4D S7: literal two-family layout and coverage recount on the 546/560 fixture."""
    require(word['R'] == 480 and word['v'] == 112 and word['h'] == 9, 'word R/v/h metadata')
    require(len(word['ports']) == 112 and 546 not in word['ports'] and 560 not in word['ports'],
            'fixture registers are helpers, not ports')
    require(546 not in word['centers'] and 560 not in word['centers'], 'fixture registers are not centres')
    require(word['start'][546] == 0 and word['start'][560] == 0
            and word['final'][546] == 1 and word['final'][560] == 1, 'fixture start/final frames')
    chains = {}
    for orient, events in sorted(prog.items()):
        chains[orient] = {}
        for r in (546, 560):
            ch = [[i, e[1], e[3], e[4], e[5]] for i, e in enumerate(events)
                  if e[0] == 'climb' and e[2] == r]
            require(sum(x[4] for x in ch) == 9 and ch[0][1:] == ['A', 0, 4, 1],
                    f'{orient} fixture climb chain register {r}')
            chains[orient][str(r)] = ch
    for r in ('546', '560'):
        require([x[1:] for x in chains['forward'][r]] == [x[1:] for x in chains['backward'][r]],
                f'fixture chain orientation agreement register {r}')
    gap = census_res['orientations']['forward']['cheapest_pair']['gap_window']
    lo = max(gap['546'][1], gap['560'][1])
    hi = min(gap['546'][2], gap['560'][2])
    require([lo, hi] == [0, 1190], 'common skeleton gap interval')
    tmpl, prof, asm = extra['template'], extra['owners_prof'], extra['asm']
    require(tmpl['m'] == 73 and tmpl['live'] == 14336 and tmpl['physical'] == 14826, 'template m/live/physical')
    require(tmpl['hosting']['max_helpers_per_physical_family_per_call'] == 1, 'hosting rule one helper per family')
    check_owners(tmpl['calls'])
    c0 = tmpl['calls'][0]
    require(c0['owners'][546] == [1134, [3, 0, 0]] and c0['owners'][560] == [1129, [3, 0, 0]],
            'call0 literal fixture owners')
    chart_eq = sum(1 for c in tmpl['calls'] if c['owners'][546][1] == c['owners'][560][1])
    require(chart_eq == 117, 'fixture owner-chart equality count')
    live, calls_n = prof['live'], len(tmpl['calls'])
    require(live == 14336 == 16 * 896 and calls_n == 144 == 16 * 9, 'replica factoring live/calls')
    require(prof['rank_mass'] == 1041408 and prof['deficit'] == 5120, 'global rank mass/deficit values')
    Hsel = {int(r): n for r, n in asm['complex_profile'].items()}
    require(Hsel == {1: 349604, 2: 60192, 3: 62585, 4: 20448, 5: 11808, 7: 7, 8: 1152, 48: 4866},
            'selected global profile')
    require(prof['paid_profile'] == asm['complex_profile'], 'owners profile = assembly profile')
    check_coverage(Hsel, live, calls_n)
    check_coverage(H74, W74, N74)
    idle = collections.Counter(c['rank'] for c in tmpl['idle_children'])
    require(dict(idle) == {48: 4866, 1: 2276, 3: 377, 7: 7}, 'global idle histogram')
    require(sum(r * n for r, n in idle.items()) == 1646 * 144, 'global idle mass')
    for r in set(Hsel) | set(SEL) | set(idle):
        require(Hsel.get(r, 0) == 144 * SEL.get(r, 0) + idle.get(r, 0),
                f'global = 144*local + idle at rank {r}')
    for n in (0, 1, 90, 196, 221, 1206):  # pairing preserves the coverage identity exactly
        H = dict(Hsel)
        H[1] -= 2 * n * 144
        H[2] += n * 144
        check_coverage(H, live, calls_n)
    trans_ub = {}
    for orient, events in sorted(prog.items()):
        r1 = [e for e in events if e[0] == 'climb' and e[5] == 1]
        tot = collections.Counter((e[3], e[4]) for e in r1)
        per_phase = {}
        for ph in ('A', 'B', 'cleanup_tail', 'final'):
            cnt = collections.Counter((e[3], e[4]) for e in r1 if e[1] == ph)
            per_phase[ph] = sum(v // 2 for v in cnt.values())
        zub = sum(v // 2 for (a, _b), v in tot.items() if a == 0)
        ub = sum(v // 2 for v in tot.values())
        require(ub == 387 and zub == 176, f'{orient} identical-transition pair upper bounds')
        trans_ub[orient] = dict(identical_transition_ub=ub, zero_frame_ub=zub, per_phase_ub=per_phase)
    return dict(
        registers=[546, 560], chains=chains,
        common_gap=dict(interval=[lo, hi], representative=1190),
        call0_owners={'546': [1134, [3, 0, 0]], '560': [1129, [3, 0, 0]]},
        distinct_owners_all_calls=True, chart_equal_calls=chart_eq, calls_total=144,
        credit_support_size=2,
        global_accounting=dict(live=live, physical=14826, calls=calls_n, replicas=16,
                               rank_mass=1041408, deficit=5120,
                               per_replica=dict(families=896, stages=9, deficit=320),
                               per_call_w='896/9', per_call_deficit='320/9',
                               idle_hist={str(k): v for k, v in sorted(idle.items())}),
        transition_pair_upper_bounds=trans_ub)


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


def paired_global(H, calls, n):
    L = dict(H)
    L[1] -= 2 * n * calls
    L[2] = L.get(2, 0) + n * calls
    return L


def min_pairs_actual(H, W, calls, a, local_r1):
    if moment(H, W, a)[1] < 1:
        return 0, None
    mx = local_r1 // 2
    require(moment(paired_global(H, calls, mx), W, a)[1] < 1, 'all-paired actual profile passes target')
    lo, hi = 0, mx
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if moment(paired_global(H, calls, mid), W, a)[1] < 1:
            hi = mid
        else:
            lo = mid
    vm = moment(paired_global(H, calls, hi - 1), W, a)
    vp = moment(paired_global(H, calls, hi), W, a)
    require(vm[0] > 1 and vp[1] < 1, 'adjacent actual min-pairs bracket')
    return hi, dict(moment_at_min_minus_1_lo=dec(vm[0]), moment_at_min_hi=dec(vp[1]))


def actual_pairs(extra):
    """Track 4D S8: exact pairs/call on actual global profiles + collapse-branch repricing."""
    Hsel = {int(r): n for r, n in extra['asm']['complex_profile'].items()}
    out = dict(frontier_source=H74_SRC)
    for nm, H, W, calls, lr1 in (('selected', Hsel, 14336, 144, SEL[1]),
                                 ('frontier2374', H74, W74, N74, T74[1])):
        row = {}
        for tn, a in (('kappa2374', KF), ('aF_planning', AF), ('a_bit', AB)):
            n, br = min_pairs_actual(H, W, calls, a, lr1)
            row[tn] = dict(min_pairs_per_call=n, bracket=br)
        out[nm] = row
    require(out['selected']['kappa2374']['min_pairs_per_call'] == 196, 'selected actual pairs at kappa2374')
    require(out['selected']['aF_planning']['min_pairs_per_call'] == 221, 'selected actual pairs at aF')
    require(out['frontier2374']['kappa2374']['min_pairs_per_call'] == 0, 'frontier passes its own kappa at 0')
    require(out['frontier2374']['aF_planning']['min_pairs_per_call'] == 26, 'frontier actual pairs at aF')
    require(out['selected']['a_bit']['min_pairs_per_call'] > 221
            and out['frontier2374']['a_bit']['min_pairs_per_call'] > 26, 'bit target needs more pairs')
    e_sel = endpoint(Hsel, 14336)
    e_sel_all = endpoint(paired_global(Hsel, 144, 1206), 14336)
    e_74 = endpoint(H74, W74)
    require(e_74[0] <= KF <= e_74[1], 'frontier endpoint bracket contains kappa2374')
    e_74_1 = endpoint(paired_global(H74, N74, 1), W74)
    require(e_74_1[0] > e_74[1], 'one pair per call strictly raises the frontier endpoint')
    out['endpoints'] = dict(
        selected_n0=[str(e_sel[0]), str(e_sel[1])], selected_n0_hi=dec(e_sel[1]),
        selected_all_paired=[str(e_sel_all[0]), str(e_sel_all[1])], selected_all_paired_hi=dec(e_sel_all[1]),
        frontier_n0=[str(e_74[0]), str(e_74[1])], frontier_n0_hi=dec(e_74[1]),
        frontier_one_pair=[str(e_74_1[0]), str(e_74_1[1])], frontier_one_pair_hi=dec(e_74_1[1]))
    def vdbl(Wd, n):
        L = dict(Wd)
        L[1] -= 2 * n
        L[2] = L.get(2, 0) + 2 * n
        return {r: v for r, v in L.items() if v}
    coll = {}
    for nm, a in (('kappa2374', KF), ('aF_planning', AF)):
        base = C.relax(SEL, M, FAM, ST, CENTRE, a)
        surv = C.relax(paired(SEL, 1), M, FAM, ST, CENTRE, a)
        dead = C.relax(paired(SEL, 1), M, FAM, ST, CENTRE + 1, a)
        dead90 = C.relax(paired(SEL, 90), M, FAM, ST, CENTRE + 90, a)
        vd = C.relax(vdbl(SEL, 1), M, FAM, ST, CENTRE, a)
        require(surv[1] < base[0], 'survive recount: one pair strictly helps')
        require(dead[0] > base[1] and dead90[0] > base[1], 'collapse recount: every pair strictly hurts')
        require(vd[0] > base[1], 'volume-doubled billing: one pair strictly hurts')
        coll[nm] = dict(survive_delta=[dec(surv[0] - base[1]), dec(surv[1] - base[0])],
                        collapse_delta_lo=dec(dead[0] - base[1]),
                        volume_doubled_delta_lo=dec(vd[0] - base[1]))
    out['recount_branches'] = coll
    return out


def tampers(word, prog, cat, result, extra):
    """Real value-mutating controls; each mutated object must be rejected by a live check."""
    rejected = []

    def reject(name, fn, needle):
        rejected.append(name + ': ' + expect_fail(fn, needle))

    ev = copy.deepcopy(prog['forward'])
    next(e for e in ev if e[0] == 'climb')[5] = 99
    reject('climb_rank_99', lambda: frame_replay(ev, word, cat), 'climb span/rank')

    ev2 = copy.deepcopy(prog['forward'])
    i = next(i for i, e in enumerate(ev2) if e[0] == 'climb' and e[2] == 560 and e[3] == 0)
    ev2.pop(i)
    reject('dropped_pair_climb', lambda: frame_replay(ev2, word, cat), 'scalar common frame')

    w2 = copy.deepcopy(word)
    w2['frames'][4] = [458]
    reject('frame4_basis_flip', lambda: catalogue(w2), 'frame 4 line')

    def bad_coeff():
        m = Mini(cat)
        m.add('r2', 'r1', 0, q=Q(2))   # mutated scalar coefficient, claimed identity endpoint
        m.climb('r1', 4)
        m.climb('r2', 4)
        m.endpoint()
    reject('scalar_coeff_2', bad_coeff, 'endpoint rows')

    def bcast_claim():
        require([[Q(1), Q(1)], [Q(1), Q(1)]] == [[Q(1), Q(0)], [Q(0), Q(1)]], 'broadcast = identity')
    reject('broadcast_as_identity', bcast_claim, 'broadcast = identity')

    def result_mut():
        bad = copy.deepcopy(result)
        bad['S2_thresholds']['aF_planning']['ratio'][1] = '0.99'
        require(bad == result, 'RESULT replay comparison')
    reject('result_ratio_mutated', result_mut, 'RESULT replay comparison')

    def minpairs_mut():
        n = result['S3_optimistic']['selected']['min_pairs']['aF_planning']
        require(ok_relax(paired(SEL, n - 1), AF), 'min-pairs minus one claimed passing')
    reject('min_pairs_minus_one', minpairs_mut, 'min-pairs minus one claimed passing')

    def extra_child_same_ceiling():
        lo0, hi0 = C.ceiling(SEL, M, FAM, ST, CENTRE, grid=GRID)
        lo1, hi1 = C.ceiling({**SEL, 1: SEL[1] + 1}, M, FAM, ST, CENTRE, grid=GRID)
        require(hi1 >= hi0, 'extra rank-1 child claimed not to lower ceiling')
    rejected.append('extra_rank1_lowers_ceiling: ' + expect_fail(extra_child_same_ceiling,
                                                                  'extra rank-1 child claimed'))

    calls_bad = copy.deepcopy(extra['template']['calls'])
    calls_bad[0]['owners'][560] = list(calls_bad[0]['owners'][546])
    reject('owner_merge_546_560', lambda: check_owners(calls_bad), 'distinct physical owners')

    Hsel = {int(r): n for r, n in extra['asm']['complex_profile'].items()}
    reject('live_minus_one', lambda: check_coverage(Hsel, 14335, 144), 'coverage identity')

    H74_bad = dict(H74)
    H74_bad[48] += 1
    reject('h74_extra_rank48', lambda: check_coverage(H74_bad, W74, N74), 'coverage identity')

    def actual_minus_one():
        n = result['S8_actual_pairs']['selected']['aF_planning']['min_pairs_per_call']
        require(moment(paired_global(Hsel, 144, n - 1), 14336, AF)[1] < 1,
                'actual min-pairs minus one claimed passing')
    reject('actual_min_pairs_minus_one', actual_minus_one, 'actual min-pairs minus one claimed passing')

    def collapse_better():
        base = C.relax(SEL, M, FAM, ST, CENTRE, AF)
        dead = C.relax(paired(SEL, 1), M, FAM, ST, CENTRE + 1, AF)
        require(dead[1] < base[0], 'collapse recount claimed better than separate')
    reject('collapse_claimed_better', collapse_better, 'collapse recount claimed better')

    def s7_mut():
        bad = copy.deepcopy(result)
        bad['S7_fixture_recount']['chart_equal_calls'] = 144
        require(bad == result, 'RESULT replay comparison (S7)')
    reject('result_S7_mutated', s7_mut, 'RESULT replay comparison (S7)')
    return rejected


def build_result():
    pins, word, prog, extra = load_pinned()
    cat_full = catalogue(word)
    cat = {k: cat_full[k] for k in ('frames', 'dims', 'spans')}
    cen = census(word, prog, cat)
    res = {
        'status': 'PASS_MUSE_JOINT_RANK_DROP',
        'pins': pins,
        'targets': {'kappa2374': str(KF), 'aF_planning': str(AF), 'a_bit': str(AB),
                    'aF_decimal': dec(AF), 'a_bit_decimal': dec(AB)},
        'S1_catalogue': {k: cat_full[k] for k in ('dim_hist', 'between_0_4', 'join23_min_dim', 'join23_first')},
        'S2_thresholds': thresholds(),
        'S3_optimistic': optimistic(),
        'S4_census': cen,
        'S5_candidates': candidates(cat),
        'S7_fixture_recount': fixture_layout(word, prog, extra, cen),
        'S8_actual_pairs': actual_pairs(extra),
    }
    res['S6_tamper_controls'] = tampers(word, prog, cat, res, extra)
    return res


def main():
    write = '--write' in sys.argv
    res = build_result()
    path = HERE / 'RESULT.json'
    if write:
        path.write_text(json.dumps(res, indent=1, sort_keys=True) + '\n')
        print('WROTE', path)
    else:
        require(path.exists(), 'RESULT.json missing (run with --write)')
        stored = json.loads(path.read_text())
        require(stored == res, 'RESULT.json replay comparison failed')
    r = res['S2_thresholds']['aF_planning']['ratio']
    s8 = res['S8_actual_pairs']
    print(f"PASS_MUSE_JOINT_RANK_DROP ratio(aF)<={r[1]} min_pairs_sel_aF="
          f"{res['S3_optimistic']['selected']['min_pairs']['aF_planning']} "
          f"cheapest_pair=[546,560] tamper={len(res['S6_tamper_controls'])}/"
          f"{len(res['S6_tamper_controls'])} rejected; no_new_kappa "
          f"4D: recount=survives actual_pairs_sel_aF="
          f"{s8['selected']['aF_planning']['min_pairs_per_call']} "
          f"frontier_aF={s8['frontier2374']['aF_planning']['min_pairs_per_call']}; no_new_kappa")


if __name__ == '__main__':
    main()
