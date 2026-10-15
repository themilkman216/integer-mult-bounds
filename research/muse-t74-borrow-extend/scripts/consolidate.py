#!/usr/bin/env python3
"""Greedy idle-remainder consolidation for FILL48.

A move takes a width-5 role from a donor bin with remainder r>=1 into a
freed bin with remainder 5 (created by dropping a newly removed helper's
role), when the role's time is allowed in the target window and the target
family is unused in the role's call. Effect on the idle histogram:
-1 rank-5, -1 rank-r, +1 rank-(r+5): strictly cheaper in the moment since
(r/m)^(1-a)/r decreases in r. Paid profile unchanged. Legality is decided
by re-running reconstruct48.py (the literal checker) on the result.
Output: FILL48C.json.gz + CONSOLIDATE.json (moves, idle histograms).
"""
import gzip, importlib.util, json
from collections import defaultdict, Counter
from pathlib import Path

PKG = Path('research/gmx-t74-borrow43').resolve()
OUT = Path('research/muse-t74-borrow-extend')
def rd(p):
    b = Path(p).read_bytes()
    return json.loads(gzip.decompress(b) if str(p).endswith('.gz') else b)

plan = rd(PKG / 'inputs/PLAN.json'); parent = rd(PKG / 'inputs/GLOBAL-TEMPLATE.json.gz'); T = plan['T']
order = [[s, r + T * g] for s, r in plan['order'] for g in range(2)]
sp = importlib.util.spec_from_file_location('windows', PKG / 'vendor/build_parent.py')
mod = importlib.util.module_from_spec(sp); sp.loader.exec_module(mod)
windows, _ = mod.actual_windows(parent, order)
prov = rd(OUT / 'BORROW-PROVIDERS48.json')
widths = {p: d['widths'] for p, d in prov.items()}
fill = rd(OUT / 'FILL48.json.gz')
fill43 = rd(PKG / 'new/borrow-fill/FILL.json.gz')
dispatch = {(s, r + T * g): pid for s, r, pid in rd(PKG / 'inputs/DISPATCH.json') for g in range(2)}
for s_, r_, p_ in fill['dispatch_overrides']: dispatch[s_, r_] = p_
pairs, sides = plan['pairs'], plan['sides']
def fam(rep, child, port): return rep * 896 + (2 * pairs[str(child)] + sides[str(child)]) * 112 + port
def width(row):
    stage, replica = order[row[0]]
    return widths[dispatch[stage, replica]][row[1]]

rows = [list(r) for r in fill['rows']]
bins = defaultdict(list)
for row in rows: bins[(row[2], row[3], row[4])].append(row)
def remainder(b):
    cap, _ = windows[f'{b[0]},{b[1]}']
    return cap - sum(width(r) for r in bins[b])
rem = {b: remainder(b) for b in bins}
# every (rep,child,port) bin exists in windows even if empty in fill
allbins = {(int(k.split(',')[0]), int(k.split(',')[1]), p) for k in windows for p in range(112)}
for b in allbins:
    if b not in rem: rem[b] = windows[f'{b[0]},{b[1]}'][0]
idle0 = Counter(r for r in rem.values() if r)
# freed bins: bins of dropped roles in the 43-fill
drop_idx = {376, 396, 398, 399, 400}
freed = {(rep, child, port) for _, h, rep, child, port, _ in fill43['rows'] if h in drop_idx}
print('freed bins', len(freed), 'their remainders', Counter(rem[b] for b in freed))
call_fams = defaultdict(set)
for row in rows: call_fams[row[0]].add(fam(row[2], row[3], row[4]))
donors = defaultdict(list)   # width-4 roles in donor bins with remainder 3/5/7:
# move into freed rem-5 bin gives {1, r+4} from {5, r}: strictly cheaper idle
# moment (remainder cost r^(1-a) is concave, concentration wins).
for b, rs in bins.items():
    if rem[b] in (3, 5, 7) and b not in freed:
        for row in rs:
            if width(row) == 4: donors[b].append(row)
moves = 0; moved_rows = set()
targets = sorted((b for b in freed if rem[b] == 5))
donor_bins = sorted(donors, key=lambda b: -rem[b])
for tb in targets:
    if rem[tb] != 5: continue
    tcap, tallowed = windows[f'{tb[0]},{tb[1]}']
    tf = fam(*tb)
    done = False
    for db in donor_bins:
        if done: break
        if rem[db] < 1 or db == tb: continue
        for row in list(donors[db]):
            if id(row) in moved_rows: continue
            if row[0] not in tallowed: continue
            if tf in call_fams[row[0]]: continue
            # perform move
            call_fams[row[0]].discard(fam(row[2], row[3], row[4])); call_fams[row[0]].add(tf)
            bins[db].remove(row); donors[db].remove(row)
            row[2], row[3], row[4] = tb
            bins[tb].append(row); moved_rows.add(id(row))
            rem[tb] -= 4; rem[db] += 4; moves += 1; done = True
            break
print('moves', moves)
# repack offsets
for b, rs in bins.items():
    rs.sort(key=lambda x: x[5]); off = 0
    for row in rs: row[5] = off; off += width(row)
idle1 = Counter(r for r in rem.values() if r)
out = dict(columns=fill['columns'], rows=sorted(rows), dispatch_overrides=fill['dispatch_overrides'])
(OUT / 'FILL48C.json.gz').write_bytes(gzip.compress(json.dumps(out, separators=(',', ':')).encode(), mtime=0))
rep = dict(moves=moves, targets=len(targets),
           idle_before={str(k): v for k, v in sorted(idle0.items())},
           idle_after={str(k): v for k, v in sorted(idle1.items())})
(OUT / 'CONSOLIDATE.json').write_text(json.dumps(rep, indent=1) + '\n')
print(rep)
