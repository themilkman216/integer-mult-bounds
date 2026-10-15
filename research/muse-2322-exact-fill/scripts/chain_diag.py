#!/usr/bin/env python3
"""Seven-chain BFS diagnostics on #2322's shipped fill (exact integer BFS).

For representative cap-16 [9] bins (holes), BFS over width-7 relocations:
a width-7 item whose call t lies in the hole window may move into the hole,
leaving its source bin as the new hole.  Success = reaching a cap-32
[9,9,7,7] bin (can donate both sevens toward a pattern unit and take a 9).
Families ignored in the main run (a superset of legal chains; families
collapse to per-bin distinct calls, analyze.py), so unreachability here is a
valid obstruction for seven-chains, reachability is only a lead.  Also
diagnoses direct (depth-1) width-7 availability for every [9] bin.
Writes CHAIN-DIAG.json.
"""
import json, sys
from collections import Counter, defaultdict, deque
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from model2322 import load_all, OUT

base = load_all()
win, rows = base['win'], base['rows']
bins = defaultdict(list)
for idx, z in enumerate(rows):
    bins[(z['owner_replica'], z['child'], z['port'])].append(idx)
def btype(b):
    return win[(b[0], b[1])][0], tuple(sorted((rows[i]['width'] for i in bins[b]), reverse=True))
by_tw = defaultdict(list)
for idx, z in enumerate(rows):
    by_tw[(z['time'], z['width'])].append(idx)
def bin_of(idx):
    z = rows[idx]
    return (z['owner_replica'], z['child'], z['port'])

Abins = [b for b in bins if btype(b) == (16, (9,))]
print('A bins [9]16:', len(Abins), Counter((b[0], b[1]) for b in Abins))

def direct_sevens(hole):
    """width-7 items (by source pattern) whose call is in the hole window."""
    n = Counter()
    for t in win[(hole[0], hole[1])][1]:
        for idx in by_tw[(t, 7)]:
            n[btype(bin_of(idx))] += 1
    return n

def bfs(hole, max_depth=10):
    came = {hole}; q = deque([(hole, 0)])
    while q:
        hb, d = q.popleft()
        if d >= max_depth:
            continue
        for t in win[(hb[0], hb[1])][1]:
            for idx in by_tw[(t, 7)]:
                src = bin_of(idx)
                if src in came:
                    continue
                came.add(src)
                if btype(src) == (32, (9, 9, 7, 7)):
                    return d + 1, len(came)
                q.append((src, d + 1))
    return None, len(came)

res = {}
reps = {}
for b in Abins:
    reps.setdefault((b[0], b[1]), b)
for key, rep in sorted(reps.items()):
    d, v = bfs(rep)
    ds = direct_sevens(rep)
    res[f'{key[0]},{key[1]}'] = dict(rep_bin=list(rep), depth=d, visited=v,
        direct7_by_source_pattern={f'{c}:{ws}': n for (c, ws), n in ds.most_common()},
        n_A_bins_in_window=sum(1 for b in Abins if (b[0], b[1]) == key))
    print(key, 'depth', d, 'visited', v, 'direct7', dict(ds.most_common(8)))
(OUT / 'CHAIN-DIAG.json').write_text(json.dumps(res, indent=1, default=str) + '\n')
