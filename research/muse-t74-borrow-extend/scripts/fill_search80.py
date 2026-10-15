#!/usr/bin/env python3
"""Round-2 owner fill for the 400-helper (80-alias) providers.

Starts from round-1 FILL48, deletes the 32 low-helper roles and widens the
32 low-lender roles (width 4 -> 9, per /tmp/rebind80 provider widths;
verified register-by-register here), repairs the over-full lender bins by
best-fit moves, then hill-climbs the exact-float idle moment at a2269 with
legal moves and swaps (bin capacities, window allowed times and per-call
distinct families are maintained invariantly; the result is only claimed
after scripts/reconstruct80.py, the literal checker, passes on it).

Idle moment uses f(r) = (r/73)**(1-a2269); the decision comparison and its
exact-interval version live in verify.py.  Providers file
BORROW-PROVIDERS80.json (widths + paid profiles from rebind80) is written
in adapt mode.  Modes:
  --from48            adapt FILL48, repair, optimise
  --resume FILL80x    load an existing 80-fill and optimise further
Writes FILL80.json.gz (or --out) and FILL80-REPORT.json.
"""
import argparse, gzip, importlib.util, json, math, random, sys, time
from collections import Counter, defaultdict
from pathlib import Path

PKG = Path('research/gmx-t74-borrow43')
OUT = Path('research/muse-t74-borrow-extend')
K2269 = 0.0016962471390584742
A2269 = K2269 / (1 - K2269)
F = [0.0] + [(r / 73) ** (1 - A2269) for r in range(1, 65)]

def rd(p):
    b = Path(p).read_bytes()
    return json.loads(gzip.decompress(b) if str(p).endswith('.gz') else b)

# ---------- static template ----------
plan = rd(PKG / 'inputs/PLAN.json'); parent = rd(PKG / 'inputs/GLOBAL-TEMPLATE.json.gz'); T = plan['T']
order = [[s, r + T * g] for s, r in plan['order'] for g in range(2)]
NT = len(order)
sp = importlib.util.spec_from_file_location('windows', PKG / 'vendor/build_parent.py')
mod = importlib.util.module_from_spec(sp); sp.loader.exec_module(mod)
windows, _ = mod.actual_windows(parent, order)
WIN = []          # (rep, child, cap, allowed frozenset)
wi_of = {}
for k, (cap, times) in windows.items():
    rep, child = map(int, k.split(','))
    wi_of[(rep, child)] = len(WIN)
    WIN.append((rep, child, cap, frozenset(times)))
NW = len(WIN); NB = NW * 112
CAP = [0] * NB; FAM = [0] * NB; WIDX = [0] * NB
for wi, (rep, child, cap, _) in enumerate(WIN):
    ct = 2 * plan['pairs'][str(child)] + plan['sides'][str(child)]
    for port in range(112):
        b = wi * 112 + port
        CAP[b] = cap; WIDX[b] = wi; FAM[b] = rep * 896 + ct * 112 + port

# ---------- state ----------
class State:
    def __init__(self):
        self.rtime = []; self.rreg = []; self.rw = []; self.rbin = []
        self.bins = [[] for _ in range(NB)]
        self.used = [0] * NB
        self.call_fam = [dict() for _ in range(NT)]
        self.buckets = [set() for _ in range(49)]   # by remainder, legal bins only
        self.key_big = [set() for _ in range(NW)]   # per window key: bins with rem>=9
    def rem(self, b): return CAP[b] - self.used[b]
    def bucket_add(self, b):
        r = self.rem(b)
        if r >= 0:
            self.buckets[r].add(b)
            if r >= 9: self.key_big[WIDX[b]].add(b)
    def bucket_del(self, b):
        r = self.rem(b)
        if r >= 0:
            self.buckets[r].discard(b)
            self.key_big[WIDX[b]].discard(b)
    def build_buckets(self):
        self.buckets = [set() for _ in range(49)]
        self.key_big = [set() for _ in range(NW)]
        for b in range(NB): self.bucket_add(b)
    def add_role(self, t, reg, w, b):
        rid = len(self.rtime)
        self.rtime.append(t); self.rreg.append(reg); self.rw.append(w); self.rbin.append(b)
        self.bins[b].append(rid); self.used[b] += w
        assert FAM[b] not in self.call_fam[t]
        self.call_fam[t][FAM[b]] = rid
        return rid
    def can_move(self, rid, b):
        t = self.rtime[rid]
        if b == self.rbin[rid]: return False
        if t not in WIN[WIDX[b]][3]: return False
        if self.used[b] + self.rw[rid] > CAP[b]: return False
        occ = self.call_fam[t].get(FAM[b])
        return occ is None or occ == rid
    def move(self, rid, b):
        old = self.rbin[rid]; t = self.rtime[rid]; w = self.rw[rid]
        self.bucket_del(old); self.bucket_del(b)
        self.bins[old].remove(rid); self.used[old] -= w
        del self.call_fam[t][FAM[old]]
        self.bins[b].append(rid); self.used[b] += w; self.rbin[rid] = b
        self.call_fam[t][FAM[b]] = rid
        self.bucket_add(old); self.bucket_add(b)
    def can_swap(self, r1, r2):
        if r1 == r2: return False
        b1, b2 = self.rbin[r1], self.rbin[r2]
        if b1 == b2: return False
        w1, w2 = self.rw[r1], self.rw[r2]
        if self.used[b1] - w1 + w2 > CAP[b1] or self.used[b2] - w2 + w1 > CAP[b2]: return False
        t1, t2 = self.rtime[r1], self.rtime[r2]
        if t1 not in WIN[WIDX[b2]][3] or t2 not in WIN[WIDX[b1]][3]: return False
        if t1 == t2: return True    # families just exchange within the call
        o1 = self.call_fam[t1].get(FAM[b2]); o2 = self.call_fam[t2].get(FAM[b1])
        return (o1 is None or o1 == r1) and (o2 is None or o2 == r2)
    def swap(self, r1, r2):
        b1, b2 = self.rbin[r1], self.rbin[r2]
        # move via temporary removal to keep family bookkeeping simple
        self.bucket_del(b1); self.bucket_del(b2)
        for rid, b in ((r1, b1), (r2, b2)):
            self.bins[b].remove(rid); self.used[b] -= self.rw[rid]
            del self.call_fam[self.rtime[rid]][FAM[b]]
        for rid, b in ((r1, b2), (r2, b1)):
            self.bins[b].append(rid); self.used[b] += self.rw[rid]; self.rbin[rid] = b
            self.call_fam[self.rtime[rid]][FAM[b]] = rid
        self.bucket_add(b1); self.bucket_add(b2)
    def idle_profile(self):
        c = Counter()
        for b in range(NB):
            r = self.rem(b)
            if r > 0: c[r] += 1
        return dict(sorted(c.items()))
    def idle_moment(self):
        return sum(n * F[r] for r, n in self.idle_profile().items())
    def check(self):
        assert all(self.used[b] <= CAP[b] for b in range(NB)), 'overfull bin'
        assert all(len(self.call_fam[t]) == len(set(self.call_fam[t])) for t in range(NT))
        seen = Counter((self.rtime[i], self.rreg[i]) for i in range(len(self.rtime)))
        assert all(v == 1 for v in seen.values()), 'duplicate (time,register) role'

KEYS_BY_TIME = [[] for _ in range(NT)]
for _wi, (_, _, _, _al) in enumerate(WIN):
    for _t in _al: KEYS_BY_TIME[_t].append(_wi)
# prefer larger caps first for repair receivers (pack 9s into cap48 bins)
for _t in range(NT): KEYS_BY_TIME[_t].sort(key=lambda wi: -WIN[wi][2])

def find_target(st, rid, rem_order, scan=400):
    w = st.rw[rid]
    for r in rem_order:
        if r < w: continue
        n = 0
        for b in st.buckets[r]:
            n += 1
            if n > scan: break
            if st.can_move(rid, b): return b
    return None

def find_target_window(st, rid):
    """Exhaustive search over window keys allowing this role's time."""
    w = st.rw[rid]; t = st.rtime[rid]
    best = None; bestrem = 10 ** 9
    for wi in KEYS_BY_TIME[t]:
        for b in st.key_big[wi]:
            r = st.rem(b)
            if r < w or r >= bestrem: continue
            if st.can_move(rid, b): best = b; bestrem = r
        if best is not None and bestrem < 16: break
    return best

# ---------- adapt from FILL48 ----------
def adapt():
    wit48 = rd(OUT / 'witness_48_base.json'); wit80 = rd(OUT / 'witness_80_base.json')
    rem48 = {p['register'] for p in wit48['pairs']}
    rem80 = {p['register'] for p in wit80['pairs']}
    h48 = [r for r in range(224, 704) if r not in rem48]
    h80 = [r for r in range(224, 704) if r not in rem80]
    plan80 = rd('/tmp/rebind80/PLAN.json')
    prov80 = {}
    w80_by_reg = {}
    for pid in ('gauge44', 'extra'):
        reg = plan80['provider_registry'][pid]
        assert len(reg['widths']) == 400
        prov80[pid] = dict(widths=reg['widths'], actual_paid_profile=reg['actual_paid_profile'])
        for r, w in zip(h80, reg['widths']): w80_by_reg.setdefault(r, w)
        assert all(w80_by_reg[r] == w for r, w in zip(h80, reg['widths'])), 'provider widths differ'
    prov48 = rd(OUT / 'BORROW-PROVIDERS48.json')
    w48_by_reg = {r: prov48['gauge44']['widths'][i] for i, r in enumerate(h48)}
    diffs = [(r, w48_by_reg[r], w80_by_reg[r]) for r in h80 if w48_by_reg[r] != w80_by_reg[r]]
    lenders = sorted(p['borrow_from'] for p in wit80['pairs'] if p['low'])
    assert diffs == [(r, 4, 9) for r in lenders], diffs[:5]
    (OUT / 'BORROW-PROVIDERS80.json').write_text(json.dumps(prov80, indent=1) + '\n')
    st = State()
    fill = rd(OUT / 'FILL48.json.gz')
    dropped = 0
    for t, hi, rep, child, port, off in fill['rows']:
        reg = h48[hi]
        if reg in rem80: dropped += 1; continue
        st.add_role(t, reg, w80_by_reg[reg], wi_of[(rep, child)] * 112 + port)
    st.build_buckets()
    print(f'adapt: roles {len(st.rtime)} dropped {dropped} overfull bins '
          f'{sum(1 for b in range(NB) if st.used[b] > CAP[b])}')
    return st, h80, fill['dispatch_overrides']

def resume(path):
    wit80 = rd(OUT / 'witness_80_base.json')
    rem80 = {p['register'] for p in wit80['pairs']}
    h80 = [r for r in range(224, 704) if r not in rem80]
    prov80 = rd(OUT / 'BORROW-PROVIDERS80.json')
    w80 = {r: prov80['gauge44']['widths'][i] for i, r in enumerate(h80)}
    fill = rd(path)
    st = State()
    for t, hi, rep, child, port, off in fill['rows']:
        reg = h80[hi]
        st.add_role(t, reg, w80[reg], wi_of[(rep, child)] * 112 + port)
    st.build_buckets(); st.check()
    print(f'resumed {path}: roles {len(st.rtime)} idle moment {st.idle_moment():.4f}')
    return st, h80, fill['dispatch_overrides']

def repair(st):
    t0 = time.monotonic()
    over = [b for b in range(NB) if st.used[b] > CAP[b]]
    stuck = []
    for b in over:
        moved = False
        for rid in list(st.bins[b]):
            tgt = find_target(st, rid, range(9, 49))
            if tgt is not None:
                st.move(rid, tgt); moved = True; break
        if not moved or st.used[b] > CAP[b]: stuck.append(b)
    still = []
    for b in stuck:
        moved = False
        for rid in list(st.bins[b]):
            tgt = find_target_window(st, rid)
            if tgt is not None:
                st.move(rid, tgt); moved = True; break
        if not moved or st.used[b] > CAP[b]: still.append(b)
    stuck = still
    print(f'repair: {len(over)} overfull, stuck {len(stuck)} in {time.monotonic()-t0:.1f}s '
          f'idle moment {st.idle_moment():.4f}')
    return stuck

def optimise(st, seconds, seed):
    rng = random.Random(seed)
    t_end = time.monotonic() + seconds
    base_mom = st.idle_moment(); print(f'optimise start moment {base_mom:.4f}')
    passes = 0
    roles_by_width = defaultdict(list)
    for rid, w in enumerate(st.rw): roles_by_width[w].append(rid)
    while time.monotonic() < t_end:
        passes += 1; improved = 0
        # move pass: roles in bins with rem>0, randomised bin order
        cand_bins = [b for b in range(NB) if st.bins[b] and st.rem(b) > 0]
        rng.shuffle(cand_bins)
        for b in cand_bins:
            if time.monotonic() > t_end: break
            rb = st.rem(b)
            if rb == 0 or not st.bins[b]: continue
            for rid in list(st.bins[b]):
                if st.rbin[rid] != b: continue
                w = st.rw[rid]; best = None; bestd = -1e-12
                src_after = rb + w
                for r in range(w, 49):
                    if not st.buckets[r]: continue
                    d = F[src_after] + F[r - w] - F[rb] - F[r]
                    if d >= bestd: continue
                    n = 0
                    for tb in st.buckets[r]:
                        n += 1
                        if n > 60: break
                        if st.can_move(rid, tb): best = tb; bestd = d; break
                if best is not None:
                    st.move(rid, best); improved += 1; rb = st.rem(b)
                    if rb == 0: break
        mom1 = st.idle_moment()
        print(f' pass {passes} moves {improved} moment {mom1:.4f}', flush=True)
        # swap trials
        sw = 0; trials = 120000
        partial = [b for b in range(NB) if st.bins[b] and st.rem(b) > 0]
        if not partial: break
        for _ in range(trials):
            if time.monotonic() > t_end: break
            b1 = partial[rng.randrange(len(partial))]
            if not st.bins[b1] or st.rem(b1) == 0: continue
            r1 = st.bins[b1][rng.randrange(len(st.bins[b1]))]
            w1 = st.rw[r1]
            w2 = rng.choice([x for x in roles_by_width if x != w1])
            r2 = roles_by_width[w2][rng.randrange(len(roles_by_width[w2]))]
            b2 = st.rbin[r2]
            if b2 == b1 or not st.can_swap(r1, r2): continue
            d = (F[st.rem(b1) + w1 - w2] + F[st.rem(b2) + w2 - w1]
                 - F[st.rem(b1)] - F[st.rem(b2)])
            if d < -1e-12:
                st.swap(r1, r2); sw += 1
        mom2 = st.idle_moment()
        print(f' pass {passes} swaps {sw} moment {mom2:.4f}', flush=True)
        if improved == 0 and sw == 0: break
    print(f'optimise done: {base_mom:.4f} -> {st.idle_moment():.4f}')
    return passes

def write_fill(st, h80, overrides, outname):
    idx = {r: i for i, r in enumerate(h80)}
    bybin = defaultdict(list)
    for rid in range(len(st.rtime)): bybin[st.rbin[rid]].append(rid)
    offsets = {}
    for b, rids in bybin.items():
        off = 0
        for rid in sorted(rids, key=lambda x: (st.rtime[x], x)):
            offsets[rid] = off; off += st.rw[rid]
    rows = []
    for rid in range(len(st.rtime)):
        rep, child, cap, _ = WIN[WIDX[st.rbin[rid]]]
        rows.append([st.rtime[rid], idx[st.rreg[rid]], rep, child,
                     st.rbin[rid] % 112, offsets[rid]])
    out = dict(columns=['time', 'helper', 'owner_replica', 'child', 'port', 'offset'],
               rows=sorted(rows), dispatch_overrides=overrides)
    (OUT / outname).write_bytes(gzip.compress(json.dumps(out, separators=(',', ':')).encode(), mtime=0))
    print('wrote', outname, 'rows', len(rows))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--from48', action='store_true')
    ap.add_argument('--resume', default='')
    ap.add_argument('--seconds', type=float, default=60)
    ap.add_argument('--seed', type=int, default=1)
    ap.add_argument('--out', default='FILL80.json.gz')
    a = ap.parse_args()
    report = dict(stages=[])
    if a.resume:
        st, h80, overrides = resume(OUT / a.resume if not str(a.resume).startswith('/') else Path(a.resume))
    else:
        st, h80, overrides = adapt()
        stuck = repair(st)
        report['stages'].append(dict(stage='repair', stuck=len(stuck),
                                     idle=st.idle_profile(), idle_moment=st.idle_moment()))
        assert not stuck, f'repair stuck on {len(stuck)} bins'
        st.check(); write_fill(st, h80, overrides, 'FILL80-START.json.gz')
    if a.seconds > 0:
        optimise(st, a.seconds, a.seed)
    st.check()
    report['stages'].append(dict(stage='final', idle=st.idle_profile(),
                                 idle_moment=st.idle_moment(),
                                 idle_mass=sum(r * n for r, n in st.idle_profile().items())))
    report['idle_moment_budget_to_beat_2269'] = 66304.55288551617 - 48327.48513463382
    report['seed'] = a.seed
    write_fill(st, h80, overrides, a.out)
    (OUT / 'FILL80-REPORT.json').write_text(json.dumps(report, indent=1) + '\n')
    print(json.dumps(report['stages'][-1], indent=1))
    print('budget', report['idle_moment_budget_to_beat_2269'],
          'margin', report['idle_moment_budget_to_beat_2269'] - st.idle_moment())
    return 0

if __name__ == '__main__': sys.exit(main())
