#!/usr/bin/env python3
"""Window-refined dual bound for #2322's fill (float, discovery only).

Adapted from research/prior-muse-t74-exact-fill/scripts/refined_dual.py
with #2322 windows and per-call width counts.  Item prices are piecewise
constant over time segments; mu[k,w] = min segment price over the window's
segments; LB = sum_k 112*gamma_k - sum_{t,w} c_w p[t,w] lower-bounds the
idle moment of any window-legal fill (families ignored).  Writes
REFINED-DUAL.json for the segment sets named on the command line
(default: one,p51,p57).
"""
import json, sys
from collections import Counter
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from model2322 import load_all, PER_CALL, OUT
import patterns as P

base = load_all(); win = base['win']
A = float(P.B2322)
SHIP = sum(n_ * P.f_float(r, A) for r, n_ in P.SHIPPED_IDLE.items())

def solve_refined(segments, max_iter=60):
    seg_of_t = {}
    for si, (lo, hi) in enumerate(segments):
        for t in range(lo, hi + 1):
            seg_of_t[t] = si
    class_bins = Counter()
    for (rep, child), (cap, times) in win.items():
        segs = tuple(sorted({seg_of_t[t] for t in times}))
        class_bins[(cap, segs)] += 112
    classes = sorted(class_bins.keys(), key=str)
    S = len(segments); Cn = len(classes)
    def vid(kind, i, j=0):
        if kind == 'P': return i * 5 + j
        if kind == 'G': return S * 5 + i
        if kind == 'M': return S * 5 + Cn + i * 5 + j
    nfree = S * 5 + Cn + Cn * 5
    obj = [0.0] * nfree
    for i, c in enumerate(classes):
        obj[vid('G', i)] = class_bins[c]
    for si, (lo, hi) in enumerate(segments):
        for wi, w in enumerate(P.WIDTHS):
            obj[vid('P', si, wi)] = -(hi - lo + 1) * PER_CALL[w]
    fixed_A, fixed_b = [], []
    for i, (cap, segs) in enumerate(classes):
        for wi in range(5):
            for si in segs:
                fixed_A.append({vid('M', i, wi): 1.0, vid('P', si, wi): -1.0})
                fixed_b.append(0.0)
    allpats = P.all_patterns()
    pool = {cap: set() for cap in P.CAPS}
    seed = [(8, (0, 0, 0, 1, 0)), (16, (0, 0, 0, 0, 1)), (16, (0, 0, 1, 0, 1)),
            (16, (0, 0, 0, 2, 0)), (32, (1, 0, 0, 0, 3)), (32, (0, 1, 0, 0, 3)),
            (32, (0, 0, 0, 0, 3)), (32, (0, 0, 1, 2, 1)), (32, (0, 0, 2, 0, 2)),
            (32, (0, 0, 0, 4, 0)), (48, (0, 0, 0, 0, 0)), (48, (0, 0, 0, 0, 5)),
            (48, (1, 0, 0, 1, 4)), (48, (0, 0, 0, 1, 4))]
    for cap, pat in seed:
        if sum(n * w for n, w in zip(pat, P.WIDTHS)) <= cap:
            pool[cap].add(pat)
    def build_and_solve():
        rows = list(fixed_A); rhs = list(fixed_b)
        for i, (cap, segs) in enumerate(classes):
            for pat in pool[cap]:
                load = sum(n * w for n, w in zip(pat, P.WIDTHS))
                row = {vid('G', i): 1.0}
                for wi, n in enumerate(pat):
                    if n:
                        row[vid('M', i, wi)] = -float(n)
                rows.append(row); rhs.append(P.f_float(cap - load, A))
        n2 = 2 * nfree; Am = []
        for row in rows:
            r = [0.0] * n2
            for j, v in row.items():
                r[2 * j] += v; r[2 * j + 1] -= v
            Am.append(r)
        cvec = [0.0] * n2
        for j, v in enumerate(obj):
            cvec[2 * j] += v; cvec[2 * j + 1] -= v
        x, val = P.simplex_max(cvec, Am, rhs)
        return [x[2 * j] - x[2 * j + 1] for j in range(nfree)], val
    vals = val = None; converged = False
    for it in range(max_iter):
        vals, val = build_and_solve()
        added = 0
        for i, (cap, segs) in enumerate(classes):
            mu = [vals[vid('M', i, wi)] for wi in range(5)]; g = vals[vid('G', i)]
            best_pat, best_val = None, float('inf')
            for pat in allpats[cap]:
                load = sum(n * w for n, w in zip(pat, P.WIDTHS))
                v = P.f_float(cap - load, A) + sum(n * m for n, m in zip(pat, mu))
                if v < best_val:
                    best_val, best_pat = v, pat
            if best_val < g - 1e-9 and best_pat not in pool[cap]:
                pool[cap].add(best_pat); added += 1
        print(f'  iter {it}: bound {val:.6f} gap-to-shipped {SHIP - val:.6f} added {added}', flush=True)
        if not added:
            converged = True; break
    return dict(bound=val, converged=converged, segments=segments,
                P=[[vals[vid('P', si, wi)] for wi in range(5)] for si in range(S)],
                classes=[[c[0], list(c[1])] for c in classes],
                n_classes=Cn)

if __name__ == '__main__':
    segsets = {
        'one': [(0, 665)],
        'p51': [(0, 51), (52, 665)],
        'p57': [(0, 57), (58, 665)],
        'early': [(0, 51), (52, 100), (101, 665)],
    }
    names = (sys.argv[1] if len(sys.argv) > 1 else 'one,p51,p57').split(',')
    out = {}
    for name in names:
        print('==', name, 'shipped idle', SHIP, flush=True)
        out[name] = solve_refined(segsets[name])
        print(' bound', out[name]['bound'], 'gap', SHIP - out[name]['bound'])
    (OUT / 'REFINED-DUAL.json').write_text(json.dumps(out, indent=1) + '\n')
