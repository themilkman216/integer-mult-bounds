#!/usr/bin/env python3
"""Build an improving legal fill on #2322's shipped fill by pattern units.

A unit is the exchange  10x[9]16 + 5x[7,7,9,9]32 + 1x[9x5]48
-> 10x[7,9]16 + 5x[9,9,9]32 + 1x[]48, realised as explicit legal item
relocations: each [9] hole is filled by a width-7 ejection chain (BFS over
bins, per-bin distinct calls and the active-data-family exclusion enforced
at every move) ending at a [7,7,9,9] donor; each donor pair of chains is
closed by relocating one width-9 item from a designated [9x5] cap-48 bin.
After 8 full units (k: 87 -> 7), 3 further donor pairs use one more cap-48
bin (k -> 1); every pair step strictly lowers the float idle moment, and
the final fill is rechecked with #2322's owners_check before writing.

Writes CANDIDATE-OWNERS.json.gz (11-field rows, offsets repacked per bin)
and SEARCH.json (move log summary).  Deterministic: bins scanned in index
order, BFS in index order, no randomness except a fixed-seed retry path
that the shipped instance does not use.
"""
import gzip, json, sys, time
from collections import Counter, defaultdict, deque
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from model2322 import load_all, OUT, fam

t_start = time.time()
base = load_all()
plan, rows0, win = base['plan'], base['rows'], base['win']
order = base['order']; stage_pair = base['stage_pair']; pairs_d = base['pairs']

winlist = []; widx = {}
for (rep, ch), (cap, ts) in win.items():
    widx[(rep, ch)] = len(winlist)
    winlist.append((rep, ch, cap, min(ts), max(ts)))
W = len(winlist); NB = W * 112
cap_of = [0] * NB; win_of_bin = [0] * NB
for wi, (rep, ch, cap, lo, hi) in enumerate(winlist):
    for port in range(112):
        cap_of[wi * 112 + port] = cap; win_of_bin[wi * 112 + port] = wi

N = len(rows0)
it_t = [z['time'] for z in rows0]; it_w = [z['width'] for z in rows0]
it_bin = [0] * N; bin_items = [[] for _ in range(NB)]; bin_load = [0] * NB
for i, z in enumerate(rows0):
    b = widx[(z['owner_replica'], z['child'])] * 112 + z['port']
    it_bin[i] = b; bin_items[b].append(i); bin_load[b] += z['width']
items_tw = defaultdict(list)
for i in range(N):
    items_tw[(it_t[i], it_w[i])].append(i)
forbid = [set() for _ in range(666)]
for t, (s, r) in enumerate(order):
    for wi, (rep, ch, cap, lo, hi) in enumerate(winlist):
        if rep == r and pairs_d[ch] == stage_pair[s]:
            forbid[t].add(wi)

A = 0.001697060296258836
f = [0.0] * 49
for r in range(1, 49):
    f[r] = (r / 73.0) ** (1 - A)
def total_cost():
    return sum(f[cap_of[b] - bin_load[b]] for b in range(NB))
def pattern(b):
    return tuple(sorted((it_w[i] for i in bin_items[b]), reverse=True))
def calls(b):
    return {it_t[i] for i in bin_items[b]}
def move(i, b2):
    b1 = it_bin[i]
    bin_items[b1].remove(i); bin_items[b2].append(i); it_bin[i] = b2
    bin_load[b1] -= it_w[i]; bin_load[b2] += it_w[i]
def snapshot():
    return (list(it_bin), [list(x) for x in bin_items], list(bin_load))
def restore(s):
    it_bin[:] = s[0]
    for b in range(NB):
        bin_items[b][:] = s[1][b]
    bin_load[:] = s[2]

def find_chain(hole, target_pred, max_depth=12):
    """BFS width-7 ejection chain. Returns ([(item, dst_bin)], donor_bin)."""
    came = {hole: (None, -1)}; q = deque([(hole, -1, 0)]); visited = {hole}
    while q:
        b, donated, d = q.popleft()
        if d >= max_depth:
            continue
        wi = win_of_bin[b]; rep, ch, cap, lo, hi = winlist[wi]
        bcalls = calls(b)
        if donated >= 0:
            bcalls.discard(it_t[donated])
        for t in range(lo, hi + 1):
            if t in bcalls or wi in forbid[t]:
                continue
            for idx in items_tw.get((t, 7), ()):
                src = it_bin[idx]
                if src == b or src in visited:
                    continue
                visited.add(src); came[src] = (b, idx)
                if target_pred(src):
                    pairs = []; x = src
                    while came[x][1] >= 0:
                        pairs.append((came[x][1], came[x][0])); x = came[x][0]
                    pairs.reverse(); return pairs, src
                q.append((src, idx, d + 1))
    return None, None

def do_pairs(prs):
    for idx, dst in prs:
        assert it_w[idx] == 7 and it_t[idx] not in calls(dst)
        assert bin_load[dst] + 7 <= cap_of[dst]
        move(idx, dst)

def find_9(donor, Gbins):
    wi = win_of_bin[donor]; rep, ch, cap, lo, hi = winlist[wi]; dc = calls(donor)
    for G in Gbins:
        for idx in list(bin_items[G]):
            t = it_t[idx]
            if it_w[idx] == 9 and lo <= t <= hi and t not in dc and wi not in forbid[t]:
                return idx, G
    return None, None

def holes_now():
    return [b for b in range(NB) if pattern(b) == (9,) and cap_of[b] == 16]

def do_pair(h1, h2, Glist, log):
    p1, donor = find_chain(h1, lambda b: pattern(b) == (9, 9, 7, 7) and cap_of[b] == 32)
    if p1 is None:
        return False
    do_pairs(p1)
    assert pattern(donor) == (9, 9, 7)
    p2, _ = find_chain(h2, lambda b, donor=donor: b == donor)
    if p2 is None:
        return False
    do_pairs(p2)
    assert pattern(donor) == (9, 9)
    idx9, _G = find_9(donor, Glist)
    if idx9 is None:
        return False
    move(idx9, donor)
    assert pattern(donor) == (9, 9, 9)
    log.append(dict(chain_lens=[len(p1), len(p2)]))
    return True

cost0 = total_cost()
log = dict(cost_initial=cost0, units=[], extra_pairs=[])
print('initial float idle cost', cost0, 'holes', len(holes_now()), flush=True)
# Phase 1: eight full units
for u in range(8):
    snap = snapshot(); before = total_cost()
    hs = holes_now()[:10]
    Gcands = [b for b in range(NB) if pattern(b) == (9, 9, 9, 9, 9) and cap_of[b] == 48]
    ok = False
    for G in Gcands[:20]:
        restore(snap)
        ulog = []
        if all(do_pair(hs[2 * j], hs[2 * j + 1], [G], ulog) for j in range(5)):
            ok = True; break
    assert ok, f'unit {u} failed'
    log['units'].append(dict(G_bin=G, pairs=ulog, gain=before - total_cost()))
    print(f'unit {u + 1}: cost {total_cost():.6f} holes {len(holes_now())}', flush=True)
# Phase 2: three extra pairs on one more cap-48 bin (k -> 1)
snap = snapshot(); before = total_cost()
hs = holes_now()[:6]
Gcands = [b for b in range(NB) if pattern(b) == (9, 9, 9, 9, 9) and cap_of[b] == 48]
ok = False
for G in Gcands[:20]:
    restore(snap)
    plog = []
    if all(do_pair(hs[2 * j], hs[2 * j + 1], [G], plog) for j in range(3)):
        ok = True; break
assert ok, 'extra pairs failed'
log['extra_pairs'] = dict(G_bin=G, pairs=plog, gain=before - total_cost(),
                          G_final_pattern=list(pattern(G)))
print(f'extra pairs: cost {total_cost():.6f} holes {len(holes_now())}', flush=True)

# Emit candidate rows: repack offsets per bin (stable by shipped offset)
new_rows = [dict(z) for z in rows0]
by_bin = defaultdict(list)
for i in range(N):
    by_bin[it_bin[i]].append(i)
moved = 0
for b, idxs in by_bin.items():
    wi = win_of_bin[b]; rep, ch, cap, lo, hi = winlist[wi]; port = b % 112
    idxs.sort(key=lambda i: (rows0[i]['offset'], rows0[i]['helper']))
    off = 0
    for i in idxs:
        z = new_rows[i]
        if (z['owner_replica'], z['child'], z['port']) != (rep, ch, port):
            moved += 1
        z['owner_replica'] = rep; z['child'] = ch; z['port'] = port
        z['offset'] = off; off += z['width']
        z['copy'] = rep * 112 + port
        z['family'] = fam(base, rep, ch, port)
H, idle = base['verify'].owners_check(new_rows, plan, base['contract'])
print('owners_check PASS; idle', dict(sorted(idle.items())))
print('H', dict(sorted(H.items())))
log.update(cost_final=total_cost(), gain_total=cost0 - total_cost(), moved_items=moved,
           idle={str(k): v for k, v in sorted(idle.items())},
           H={str(k): v for k, v in sorted(H.items())},
           seconds=time.time() - t_start)
data = gzip.compress(json.dumps(new_rows, sort_keys=True, separators=(',', ':')).encode(), mtime=0)
(OUT / 'CANDIDATE-OWNERS.json.gz').write_bytes(data)
(OUT / 'SEARCH.json').write_text(json.dumps(log, indent=1) + '\n')
print('wrote candidate; moved items', moved, 'gain', log['gain_total'])
