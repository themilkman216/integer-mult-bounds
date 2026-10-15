#!/usr/bin/env python3
"""Window-refined dual lower bound for the owner fill (float, for discovery;
exact rational verification is separate).

Relaxation: pattern counts per window + item flow from calls to windows
(families ignored).  Dual variables: item prices p[t,w] (here piecewise
constant over time segments), window prices gamma.  For window k,
mu[k,w] = min_{t in allowed(k)} p[t,w]; gamma_k <= f(rem_P) + sum_w n_Pw
mu[k,w] for every pattern P of cap(k).  Lower bound:
  LB = sum_k 112*gamma_k - sum_{t,w} c_w p[t,w]
on the idle moment of ANY legal fill (c_w = per-call width counts).
Windows are grouped by (cap, set of segments hit); solved by constraint
generation over patterns with the self-contained simplex from patterns.py.
"""
import json, sys
from collections import Counter, defaultdict
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from model import load_base, load_case, OUT
import patterns as P

base = load_base(); win = base['win']

def solve_refined(case_which, segments, a, init_patterns=None, max_iter=60, verbose=True):
    """segments: list of (lo,hi) partition of [0,665]. Returns dict with bound."""
    case = load_case(base, case_which)
    wc = Counter(case['widths']['gauge44'])
    c_per_call = {w: wc[w] for w in P.WIDTHS}
    seg_of_t = {}
    for si, (lo, hi) in enumerate(segments):
        for t in range(lo, hi + 1):
            seg_of_t[t] = si
    # window classes: (cap, tuple of segment ids hit)
    wclass = {}
    class_bins = Counter()
    for (rep, child), (cap, times) in win.items():
        segs = tuple(sorted({seg_of_t[t] for t in times}))
        wclass[(rep, child)] = (cap, segs)
        class_bins[(cap, segs)] += 112
    classes = sorted(class_bins.keys(), key=str)
    class_id = {c: i for i, c in enumerate(classes)}
    S = len(segments); Cn = len(classes)
    # free variables: P[s][w] (S*5), gamma[class] (Cn), mu[class][w] (Cn*5)
    def vid(kind, i, j=0):
        if kind == 'P': return i * 5 + j
        if kind == 'G': return S * 5 + i
        if kind == 'M': return S * 5 + Cn + i * 5 + j
    nfree = S * 5 + Cn + Cn * 5
    # objective (max): sum_class bins*gamma - sum_{s,w} (seg_size*c_w) P[s,w]
    obj = [0.0] * nfree
    for i, c in enumerate(classes):
        obj[vid('G', i)] = class_bins[c]
    for si, (lo, hi) in enumerate(segments):
        for wi, w in enumerate(P.WIDTHS):
            obj[vid('P', si, wi)] = -(hi - lo + 1) * c_per_call[w]
    # fixed constraints: mu[class][w] - P[s][w] <= 0 for s in segs(class)
    fixed_A, fixed_b = [], []
    for i, (cap, segs) in enumerate(classes):
        for wi in range(5):
            for si in segs:
                row = {}
                row[vid('M', i, wi)] = 1.0; row[vid('P', si, wi)] = -1.0
                fixed_A.append(row); fixed_b.append(0.0)
    allpats = P.all_patterns()
    # pattern pool per cap: start with shipped + counting-LP patterns
    pool = {cap: set() for cap in P.CAPS}
    seed_pats = [ (8,(0,0,0,1,0)), (16,(0,0,0,0,1)), (16,(0,0,1,0,1)), (16,(0,0,0,2,0)),
                  (32,(1,0,0,0,3)), (32,(0,1,0,0,3)), (32,(0,0,0,0,3)), (32,(0,0,1,2,1)),
                  (32,(0,0,2,0,2)), (32,(0,0,0,4,0)), (48,(0,0,0,0,0)), (48,(0,0,0,0,5)),
                  (48,(0,0,0,0,4)), (32,(0,0,1,0,2)), (16,(0,0,1,0,0)) ]
    for cap, pat in seed_pats:
        if sum(n*w for n, w in zip(pat, P.WIDTHS)) <= cap:
            pool[cap].add(pat)
    if init_patterns:
        for cap, pat in init_patterns:
            pool[cap].add(tuple(pat))
    def build_and_solve():
        # assemble constraints: pattern rows gamma_c - sum_w n_w mu_cw <= f
        rows = list(fixed_A); rhs = list(fixed_b)
        for i, (cap, segs) in enumerate(classes):
            for pat in pool[cap]:
                load = sum(n * w for n, w in zip(pat, P.WIDTHS))
                row = {vid('G', i): 1.0}
                for wi, n in enumerate(pat):
                    if n:
                        row[vid('M', i, wi)] = -float(n)
                rows.append(row); rhs.append(P.f_float(cap - load, a))
        # convert free vars to pos/neg for simplex_max
        n2 = 2 * nfree
        A = []; 
        for row in rows:
            r = [0.0] * n2
            for j, v in row.items():
                r[2 * j] += v; r[2 * j + 1] -= v
            A.append(r)
        cvec = [0.0] * n2
        for j, v in enumerate(obj):
            cvec[2 * j] += v; cvec[2 * j + 1] -= v
        x, val = P.simplex_max(cvec, A, rhs)
        vals = [x[2 * j] - x[2 * j + 1] for j in range(nfree)]
        return vals, val
    vals = val = None
    for it in range(max_iter):
        vals, val = build_and_solve()
        # separation: for each class, min over ALL patterns of f + sum n mu
        added = 0
        worst = None
        for i, (cap, segs) in enumerate(classes):
            mu = [vals[vid('M', i, wi)] for wi in range(5)]
            g = vals[vid('G', i)]
            best_pat, best_val = None, float('inf')
            for pat in allpats[cap]:
                load = sum(n * w for n, w in zip(pat, P.WIDTHS))
                v = P.f_float(cap - load, a) + sum(n * m for n, m in zip(pat, mu))
                if v < best_val:
                    best_val, best_pat = v, pat
            if best_val < g - 1e-9:
                if best_pat not in pool[cap]:
                    pool[cap].add(best_pat); added += 1
                    if worst is None or best_val - g < worst[0]:
                        worst = (best_val - g, classes[i], best_pat)
        if verbose:
            print(f'  iter {it}: bound {val:.6f}, violated classes added {added}', flush=True)
        if not added:
            break
    Pvals = [[vals[vid('P', si, wi)] for wi in range(5)] for si in range(S)]
    return dict(bound=val, P=Pvals, classes=[[c[0], list(c[1])] for c in classes],
                gammas=[vals[vid('G', i)] for i in range(Cn)],
                mus=[[vals[vid('M', i, wi)] for wi in range(5)] for i in range(Cn)],
                pool={str(k): [list(p) for p in sorted(v)] for k, v in pool.items()},
                segments=segments, c_per_call=c_per_call)

if __name__ == '__main__':
    a_dec = 0.0016962471390584742; a = a_dec / (1 - a_dec)
    segsets = {
        'one': [(0, 665)],
        'prefix26': [(0, 26), (27, 665)],
        'prefix38': [(0, 38), (39, 665)],
        'pre-suf': [(0, 26), (27, 38), (39, 586), (587, 665)],
        'fine-early': [(0, 26), (27, 38), (39, 100), (101, 300), (301, 500), (501, 586), (587, 644), (645, 665)],
        'fine2': [(0, 26), (27, 38), (39, 50), (51, 70), (71, 100), (101, 150), (151, 250), (251, 400), (401, 540), (541, 586), (587, 620), (621, 644), (645, 665)],
    }
    out = {}
    for name in sys.argv[1].split(','):
        for which in ('43', '48'):
            case = load_case(base, which)
            ship = P.primal_cost_of_fill(base, case, a)
            print(f'== segments {name}, case {which}: shipped idle {ship:.6f}')
            r = solve_refined(which, segsets[name], a)
            print(f'   refined bound {r["bound"]:.6f}  gap-to-shipped {ship - r["bound"]:.6f}')
            out[f'{name}-{which}'] = r
    (OUT / 'REFINED-DUAL.json').write_text(json.dumps(out, indent=1) + '\n')
