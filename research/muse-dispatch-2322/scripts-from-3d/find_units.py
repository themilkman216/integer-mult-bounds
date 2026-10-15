#!/usr/bin/env python3
"""Search for window/family-realizable improving units in a shipped fill.

Unit (from the integral pattern-LP optimum, minimal improving exchange):
  10x cap16 [9]        (rem 7)  ->  10x cap16 [7,9]     (rem 0)
   5x cap32 [7,7,9,9]  (rem 0)  ->   5x cap32 [9,9,9]   (rem 5)
   1x cap48 [9,9,9,9,9](rem 3)  ->   1x cap48 []        (rem 48)
Moves: ten width-7 items from the five cap32 bins into the ten cap16 bins;
five width-9 items from the cap48 bin into the five cap32 bins.  Idle
moment change at a2269 is exactly Delta = f(48)+5f(5)-10f(7)-f(3) < 0
(certified by ceiling.child_cost intervals in bounds/verify).
Legality of every candidate unit is decided by the full literal checker
(model.check_rows, mirroring reconstruct.py) on the modified fill.
Greedy: apply units sequentially to the working fill, re-searching after
each accepted unit.  Usage: find_units.py 43|48 [max_units] [seed]
Writes FILL<which>-IMPROVED.json.gz (rows only changed if units found),
UNITS-<which>.json with the unit bin lists and checker idle/H after each.
"""
import gzip, json, random, sys
from collections import defaultdict
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from model import load_base, load_case, width_of, check_rows, repack_offsets, fam, OUT

def hopcroft_karp(adj, n_right):
    """adj: dict left -> list of right ids. Returns match_right: right -> left."""
    from collections import deque
    INF = float('inf')
    pair_u, pair_v, dist = {}, {}, {}
    def bfs():
        q = deque()
        for u in adj:
            if u not in pair_u:
                dist[u] = 0; q.append(u)
            else:
                dist[u] = INF
        found = False
        while q:
            u = q.popleft()
            for v in adj[u]:
                w = pair_v.get(v)
                if w is None:
                    found = True
                elif dist.get(w, INF) == INF:
                    dist[w] = dist[u] + 1; q.append(w)
        return found
    def dfs(u):
        for v in adj[u]:
            w = pair_v.get(v)
            if w is None or (dist.get(w, -1) == dist[u] + 1 and dfs(w)):
                pair_u[u] = v; pair_v[v] = u; return True
        dist[u] = float('inf'); return False
    matching = 0
    while bfs():
        for u in list(adj):
            if u not in pair_u and dfs(u):
                matching += 1
    return pair_v

def small_match(items, targets, compat):
    """Backtracking assignment items->targets (both small). compat(i,t)->bool.
    Returns dict item_index->target or None."""
    order = sorted(range(len(items)), key=lambda i: sum(compat(i, t) for t in range(len(targets))))
    assign = {}
    used = set()
    def bt(k):
        if k == len(order):
            return True
        i = order[k]
        for t in range(len(targets)):
            if t not in used and compat(i, t):
                assign[i] = t; used.add(t)
                if bt(k + 1):
                    return True
                del assign[i]; used.discard(t)
        return False
    return assign if bt(0) else None

def main():
    which = sys.argv[1]; max_units = int(sys.argv[2]) if len(sys.argv) > 2 else 15
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else 12345
    rng = random.Random(seed)
    base = load_base(); case = load_case(base, which)
    win = base['win']
    rows = [list(r) for r in case['fill']['rows']]
    idle0, H0 = check_rows(base, case, rows)
    print(which, 'start idle', dict(sorted(idle0.items())), flush=True)
    units = []
    for unit_no in range(max_units):
        # rebuild bin/item structures from current rows
        bins = defaultdict(list)   # bin -> list of row indices
        for idx, r in enumerate(rows):
            bins[(r[2], r[3], r[4])].append(idx)
        def w_of(idx):
            r = rows[idx]; return width_of(base, case, r[0], r[1])
        def btype(b):
            cap = win[(b[0], b[1])][0]
            return cap, tuple(sorted((w_of(i) for i in bins[b]), reverse=True))
        call_fams = defaultdict(set)
        for r in rows:
            call_fams[r[0]].add(fam(base, r[2], r[3], r[4]))
        Abins = [b for b in bins if btype(b) == (16, (9,))]
        Bbins = [b for b in bins if btype(b) == (32, (9, 9, 7, 7))]
        Cbins = [b for b in bins if btype(b) == (48, (9, 9, 9, 9, 9))]
        rng.shuffle(Abins); rng.shuffle(Bbins); rng.shuffle(Cbins)
        if len(Abins) < 10 or len(Bbins) < 5 or not Cbins:
            print('pool exhausted', len(Abins), len(Bbins), len(Cbins)); break
        A_id = {b: i for i, b in enumerate(Abins)}
        # 7-items in B bins, keyed (bin, slot)
        seven_items = []  # (row_idx, bin)
        for b in Bbins:
            for idx in bins[b]:
                if w_of(idx) == 7:
                    seven_items.append((idx, b))
        adj = {}
        for si, (idx, b) in enumerate(seven_items):
            r = rows[idx]; t = r[0]; own_fam = fam(base, r[2], r[3], r[4])
            lst = []
            for ab in Abins:
                if t not in win[(ab[0], ab[1])][1]:
                    continue
                fa = fam(base, *ab)
                if fa in call_fams[t] and fa != own_fam:
                    continue
                lst.append(A_id[ab])
            adj[si] = lst
        match_v = hopcroft_karp(adj, len(Abins))
        # B bins with both 7s matched
        by_bin = defaultdict(list)
        for v, si in match_v.items():
            by_bin[seven_items[si][1]].append((si, Abins[v]))
        full_B = [b for b, ms in by_bin.items() if len(ms) == 2]
        print(f'unit {unit_no}: A={len(Abins)} B={len(Bbins)} C={len(Cbins)} '
              f'matched7={len(match_v)} fullB={len(full_B)}', flush=True)
        if len(full_B) < 5:
            print('no 5 fully-matched B bins'); break
        # try groups of 5 full-B bins (in shuffled order, chunks then random combos)
        rng.shuffle(full_B)
        found = None
        groups = [full_B[i:i + 5] for i in range(0, len(full_B) - 4, 5)]
        for _ in range(200):
            groups.append(rng.sample(full_B, 5))
        tried_c = 0
        for grp in groups:
            if found: break
            # candidate moves for 7s
            moves7 = []  # (row_idx, target_Abin)
            usedA = set()
            ok = True
            for b in grp:
                for si, ab in by_bin[b]:
                    if ab in usedA: ok = False; break
                    usedA.add(ab); moves7.append((seven_items[si][0], ab))
                if not ok: break
            if not ok or len(moves7) != 10:
                continue
            for cb in Cbins:
                tried_c += 1
                nines = [idx for idx in bins[cb] if w_of(idx) == 9]
                def compat9(i, tj, nines=nines, grp=grp):
                    r = rows[nines[i]]; t = r[0]; bb = grp[tj]
                    if t not in win[(bb[0], bb[1])][1]:
                        return False
                    fb = fam(base, *bb); own = fam(base, r[2], r[3], r[4])
                    return fb not in call_fams[t] or fb == own
                asg = small_match(nines, grp, compat9)
                if asg is None:
                    continue
                moves9 = [(nines[i], grp[tj]) for i, tj in asg.items()]
                # apply to a copy and run the full literal checker
                newrows = [list(r) for r in rows]
                for idx, tb in moves7 + moves9:
                    newrows[idx][2], newrows[idx][3], newrows[idx][4] = tb
                newrows = repack_offsets(base, case, newrows)
                try:
                    idle1, H1 = check_rows(base, case, newrows)
                except AssertionError as e:
                    continue
                found = dict(A=[list(b) for b in usedA], B=[list(b) for b in grp],
                             C=list(cb),
                             moves7=[[int(rows[i][0]), int(rows[i][1]), list(tb)] for i, tb in moves7],
                             moves9=[[int(rows[i][0]), int(rows[i][1]), list(tb)] for i, tb in moves9],
                             idle_after={str(k): v for k, v in sorted(idle1.items())},
                             H_after={str(k): v for k, v in sorted(H1.items())})
                rows = newrows
                print(f'  ACCEPTED unit {unit_no} (tried C bins {tried_c}); idle {found["idle_after"]}', flush=True)
                break
        if not found:
            print('no realizable unit found this round'); break
        units.append(found)
    out_fill = dict(columns=case['fill']['columns'], rows=sorted(rows),
                    dispatch_overrides=case['fill']['dispatch_overrides'])
    p = OUT / f'FILL{which}-IMPROVED.json.gz'
    p.write_bytes(gzip.compress(json.dumps(out_fill, separators=(',', ':')).encode(), mtime=0))
    rep = dict(which=which, seed=seed, units_applied=len(units),
               idle_before={str(k): v for k, v in sorted(idle0.items())},
               H_before={str(k): v for k, v in sorted(H0.items())}, units=units)
    (OUT / f'UNITS-{which}.json').write_text(json.dumps(rep, indent=1) + '\n')
    print('applied', len(units), 'units; wrote', p)

if __name__ == '__main__':
    main()
