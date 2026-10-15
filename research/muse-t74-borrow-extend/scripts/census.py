#!/usr/bin/env python3
"""Static lender census for the 5 unaliased high helpers of #2269.

Replays the canonical (unborrowed) word in pr2226_replay order tracking only
frames (no values): precondition+compensation, A, target pins, cut, then B
with block helper-only corrections deferred to each block's first_input.
Records, per register, its frame dimension at every block deadline and its
last incident B index in replay order. A register L is a static candidate
lender for high helper H with deadline d if:
  * L is not removed/lent in witness_43, not H itself, not a Y target;
  * last_B_use(L) < d  (retired before handoff);
  * 1 <= dim(cur[L] at d) <= dim(F1), F1 = frame of H's first gate at/after d
    in replay order (deferred corrections included).
This is a necessary-condition screen only; the exact free-operator replay and
independent audit decide any nominated extension.
"""
import gzip, json, sys
from pathlib import Path

B = Path('research/gmx-t74-borrow43/new/borrow')
def span(basis):
    s = {0}
    for x in basis: s |= {t ^ x for t in list(s)}
    return frozenset(s)
def dim(s): return len(s).bit_length() - 1
def incident(e): return e[1:3] if e[0] == 'add' else e[1:2]

def census(canon, witname):
    w = json.loads(gzip.decompress((B / 'inputs' / canon).read_bytes()))
    blocks = json.loads((B / 'inputs/blocks.json').read_text())['sources'][0]['blocks']
    wit = json.loads((B / 'inputs' / witname).read_text())
    v, n = w['v'], 2 * w['v'] + w['R']
    frames = list(map(span, w['frames']))
    removed = {p['register'] for p in wit['pairs']}
    lent = {p['borrow_from'] for p in wit['pairs']}
    cur = {r: frames[w['start'][r]] for r in range(n)}
    def climb(e):
        f = frames[e[-1]]
        for r in incident(e):
            assert cur[r] <= f, ('nonnested', r)
            cur[r] = f
    for e in w['precondition'] + w['compensation']: climb(e)
    for e in w['A']: climb(e)
    levels = {r: w['start'][r] for r in range(v, 2 * v)}
    for e in w['precondition'] + w['compensation']:
        for r in incident(e):
            if v <= r < 2 * v: levels[r] = e[-1]
    for r, f in levels.items(): cur[r] = frames[f]
    # cut is unframed: no climbs
    deferred, skip = {}, set()
    for b in blocks:
        ss, part = set(b['helpers']), []
        for i in range(b['first_correction'], b['first_input']):
            e = w['B'][i]
            if set(incident(e)) <= ss: part.append(e); skip.add(i)
        deferred[b['first_input']] = part
    deadlines = sorted({b['first_input'] for b in blocks})
    snap = {}          # deadline -> {r: dim}
    last_use = {r: -1 for r in range(n)}
    first_gate = {}    # helper -> (replay index, frame dim) of first incident gate at/after its deadline
    missing = [606, 635, 637, 638, 639]
    dl = {h: next(b['first_input'] for b in blocks if h in b['helpers']) for h in missing}
    for i, e in enumerate(w['B']):
        if i in deadlines: snap[i] = {r: dim(cur[r]) for r in range(n)}
        seq = list(deferred.get(i, [])) + ([] if i in skip else [e])
        for g in seq:
            for r in incident(g):
                last_use[r] = i
                if r in dl and i >= dl[r] and r not in first_gate:
                    first_gate[r] = (i, dim(frames[g[-1]]), w['frames'][g[-1]])
            climb(g)
    out = {}
    for h in missing:
        d = dl[h]; f1d = first_gate[h][1]
        cand = []
        for L in range(n):
            if L in removed or L in lent or L == h or v <= L < 2 * v: continue
            if last_use[L] >= d: continue
            du = snap[d][L]
            if 1 <= du <= f1d: cand.append((L, du, last_use[L]))
        out[h] = dict(deadline=d, first_gate_dim=f1d, n_candidates=len(cand),
                      candidates=cand)
        print(f"helper {h} deadline={d} F1dim={f1d} candidates={len(cand)} "
              f"bydim={ {k: sum(1 for c in cand if c[1]==k) for k in range(1,10)} }")
        print('   ', cand[:24])
    # joint feasibility: greedy distinct-lender matching, latest deadline first
    used, assign = set(), {}
    for h in sorted(missing, key=lambda x: -dl[x]):
        pick = next((c for c in sorted(out[h]['candidates'], key=lambda c: -c[1]) if c[0] not in used), None)
        assign[h] = pick
        if pick: used.add(pick[0])
    print('greedy distinct assignment:', assign)
    return out, assign

res = {}
for canon, witn in [('gauge44.canonical.json.gz', 'witness_43_base.json'),
                    ('extra.canonical.json.gz', 'witness_43_extra.json')]:
    print('===', canon)
    o, a = census(canon, witn)
    res[canon] = dict(census={str(k): v for k, v in o.items()},
                      assignment={str(k): v for k, v in a.items()})
Path('research/muse-t74-borrow-extend/CENSUS.json').write_text(json.dumps(res, indent=1) + '\n')
print('wrote CENSUS.json')
