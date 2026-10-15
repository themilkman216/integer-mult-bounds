#!/usr/bin/env python3
"""Diagnostic: BFS reachability of seven-chains from each rem-7 [9] bin to a
cap32 [7,7,9,9] bin, reporting depth/visited, with and without family filter."""
import json, random, sys
from collections import defaultdict, deque
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from model import load_base, load_case, width_of, fam, OUT

base = load_base(); win = base['win']
case = load_case(base, sys.argv[1] if len(sys.argv) > 1 else '43')
rows = [list(r) for r in case['fill']['rows']]
bins = defaultdict(list)
for idx, r in enumerate(rows):
    bins[(r[2], r[3], r[4])].append(idx)
def w(idx):
    r = rows[idx]; return width_of(base, case, r[0], r[1])
def btype(b):
    return win[(b[0], b[1])][0], tuple(sorted((w(i) for i in bins[b]), reverse=True))
call_fams = defaultdict(set)
for r in rows:
    call_fams[r[0]].add(fam(base, r[2], r[3], r[4]))
by_tw = defaultdict(list)
for idx, r in enumerate(rows):
    by_tw[(r[0], w(idx))].append(idx)
def bin_of(idx):
    r = rows[idx]; return (r[2], r[3], r[4])

Abins = [b for b in bins if btype(b) == (16, (9,))]
def bfs(hole, use_family, max_depth=8):
    came = {hole: None}; q = deque([hole]); depth = {hole: 0}
    while q:
        hb = q.popleft()
        if depth[hb] >= max_depth: continue
        fam_h = fam(base, *hb)
        for t in win[(hb[0], hb[1])][1]:
            for idx in by_tw[(t, 7)]:
                src = bin_of(idx)
                if src in came: continue
                if use_family:
                    own = fam(base, *src)
                    if fam_h in call_fams[t] and fam_h != own: continue
                came[src] = (hb, idx); depth[src] = depth[hb] + 1
                if btype(src) == (32, (9, 9, 7, 7)):
                    return depth[src], len(came)
                q.append(src)
    return None, len(came)

res = []
for ab in Abins:
    d1, v1 = bfs(ab, True)
    d2, v2 = bfs(ab, False)
    res.append(dict(bin=list(ab), window=list(ab[:2]), depth_family=d1, visited_family=v1,
                    depth_nofamily=d2, visited_nofamily=v2))
ok_f = sum(1 for r in res if r['depth_family'])
ok_n = sum(1 for r in res if r['depth_nofamily'])
print(f'A bins {len(Abins)}; reachable with family {ok_f}, without {ok_n}')
from collections import Counter
print('depth_family hist', Counter(r['depth_family'] for r in res))
print('depth_nofamily hist', Counter(r['depth_nofamily'] for r in res))
print('by window:', {str(k): (sum(1 for r in res if r["window"] == list(k) and r["depth_family"]),
                              sum(1 for r in res if r["window"] == list(k)))
                     for k in {(r["window"][0], r["window"][1]) for r in res}})
(OUT / 'CHAIN-DIAG.json').write_text(json.dumps(res, indent=1) + '\n')
