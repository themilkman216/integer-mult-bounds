#!/usr/bin/env python3
"""Pattern-count relaxation of the 80-fill idle moment.

Aggregates the bins of a fill (default FILL80-START) into pattern counts
(cap, sorted width multiset) and hill-climbs in pattern-count space with
maximal-multiplicity move/swap exchanges between pattern groups.  Window
allowed-times and per-call family constraints are DROPPED, so every value
reported here is a relaxation of the true fill problem: if even this
relaxation cannot beat the idle budget, no legal fill can (modulo the
local-search nature of the climb, which is stated in the output).
Objective: idle moment at a2269, sum count * (rem/73)**(1-a).
Output: PATTERN-BOUND.json.
"""
import gzip, importlib.util, json, sys
from collections import Counter, defaultdict
from pathlib import Path

PKG = Path('research/gmx-t74-borrow43'); OUT = Path('research/muse-t74-borrow-extend')
K = 0.0016962471390584742; A = K / (1 - K)
def F(r): return (r / 73) ** (1 - A) if r else 0.0
def rd(p):
    b = Path(p).read_bytes()
    return json.loads(gzip.decompress(b) if str(p).endswith('.gz') else b)

plan = rd(PKG / 'inputs/PLAN.json'); parent = rd(PKG / 'inputs/GLOBAL-TEMPLATE.json.gz'); T = plan['T']
order = [[s, r + T * g] for s, r in plan['order'] for g in range(2)]
sp = importlib.util.spec_from_file_location('windows', PKG / 'vendor/build_parent.py')
mod = importlib.util.module_from_spec(sp); sp.loader.exec_module(mod)
windows, _ = mod.actual_windows(parent, order)
CAPOF = {(int(k.split(',')[0]), int(k.split(',')[1])): v[0] for k, v in windows.items()}
CAPS = Counter(v[0] for v in windows.values())
CAPS = {c: n * 112 for c, n in CAPS.items()}

fillname = sys.argv[1] if len(sys.argv) > 1 else 'FILL80-START.json.gz'
if fillname == 'VARIANTB':
    # hand-constructed feasible pattern allocation (exact role/bin totals)
    counts = Counter({(8, (8,)): 49728, (16, (8, 8)): 3108, (16, (9, 7)): 23976,
                      (16, (9,)): 6068, (32, (9, 9, 9, 5)): 2664, (32, (9, 9, 9, 4)): 2664,
                      (32, (9, 9, 9)): 27824, (48, (9, 9, 9, 9, 9)): 10330,
                      (48, (9, 9)): 1, (48, ()): 22821})
else:
    prov = rd(OUT / 'BORROW-PROVIDERS80.json')['gauge44']['widths']
    fill = rd(OUT / fillname)
    bins = defaultdict(list)
    for t, hi, rep, child, port, off in fill['rows']:
        bins[(rep, child, port)].append(prov[hi])
    counts = Counter()
    for (rep, child, port), ws in bins.items():
        counts[(CAPOF[(rep, child)], tuple(sorted(ws, reverse=True)))] += 1
    for c, total in CAPS.items():
        have = sum(v for (cap, _), v in counts.items() if cap == c)
        if total > have: counts[(c, ())] += total - have

def rem(p): return p[0] - sum(p[1])
def moment(ct): return sum(n * F(rem(p)) for p, n in ct.items())
def show(ct, tag):
    idle = Counter()
    for p, n in ct.items():
        if rem(p): idle[rem(p)] += n
    print(tag, 'moment', round(moment(ct), 4), 'idle', dict(sorted(idle.items())))
show(counts, 'start')
start_mom = moment(counts)

def patterns_with(ct, w):
    return [p for p in list(ct) if w in p[1] and ct[p] > 0]

iters = 0
while True:
    pats = [p for p, n in counts.items() if n > 0]
    best = None  # (delta, kind, X, Y, Xn, Yn, mult)
    for X in pats:
        for Y in pats:
            # moves X -> Y for each distinct width in X
            for w in set(X[1]):
                if rem(Y) < w: continue
                wx = list(X[1]); wx.remove(w); Xn = (X[0], tuple(sorted(wx, reverse=True)))
                Yn = (Y[0], tuple(sorted(Y[1] + (w,), reverse=True)))
                if Xn == X and Yn == Y: continue
                d = F(rem(Xn)) + F(rem(Yn)) - F(rem(X)) - F(rem(Y))
                if d < -1e-15 and (best is None or d < best[0]):
                    m = min(counts[X], counts[Y]) if X != Y else counts[X] // 2
                    if m > 0: best = (d, 'move', X, Y, Xn, Yn, m)
            # swaps X <-> Y
            for w1 in set(X[1]):
                for w2 in set(Y[1]):
                    if w1 == w2: continue
                    ux = sum(X[1]) - w1 + w2; uy = sum(Y[1]) - w2 + w1
                    if ux > X[0] or uy > Y[0]: continue
                    wx = list(X[1]); wx.remove(w1); wx.append(w2)
                    wy = list(Y[1]); wy.remove(w2); wy.append(w1)
                    Xn = (X[0], tuple(sorted(wx, reverse=True)))
                    Yn = (Y[0], tuple(sorted(wy, reverse=True)))
                    d = F(rem(Xn)) + F(rem(Yn)) - F(rem(X)) - F(rem(Y))
                    if d < -1e-15 and (best is None or d < best[0]):
                        m = min(counts[X], counts[Y]) if X != Y else counts[X] // 2
                        if m > 0: best = (d, 'swap', X, Y, Xn, Yn, m)
    if best is None: break
    d, kind, X, Y, Xn, Yn, m = best
    if X == Y:
        counts[X] -= 2 * m
    else:
        counts[X] -= m; counts[Y] -= m
    counts[Xn] = counts.get(Xn, 0) + m
    counts[Yn] = counts.get(Yn, 0) + m
    for p in (X, Y):
        if counts.get(p) == 0: del counts[p]
    iters += 1
    if iters % 20 == 0: show(counts, f'iter {iters}')
    if iters > 5000: break

show(counts, 'final')
roles = Counter()
for p, n in counts.items():
    for w in p[1]: roles[w] += n
out = dict(fill=fillname, iterations=iters, start_moment=start_mom,
           relaxed_moment=moment(counts), budget=17977.06775088235,
           margin=17977.06775088235 - moment(counts),
           patterns={f'{cap}:{list(ws)}': n for (cap, ws), n in sorted(counts.items(), key=lambda kv: -kv[1])},
           role_counts={str(k): v for k, v in sorted(roles.items())},
           caveat='Pattern-count hill climb (moves+swaps, maximal multiplicity) of the window/family-relaxed problem; a local optimum of this relaxation, not a proved global lower bound.')
(OUT / 'PATTERN-BOUND.json').write_text(json.dumps(out, indent=1) + '\n')
print('relaxed moment', moment(counts), 'margin vs budget', out['margin'])
print('top patterns:', dict(list(out['patterns'].items())[:15]))
