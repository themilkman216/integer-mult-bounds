#!/usr/bin/env python3
"""Alternating-path (ejection-chain) search for improving units.

Direct width-7 moves from cap32 bins into the cap16 [9] rem-7 bins are
window-blocked (see DIAGNOSE.json).  A seven-chain routes the rem-7 hole:
hole bin <- 7-item from bin x1 <- 7-item from x2 <- ... <- 7-item from a
cap32 [7,7,9,9] bin; intermediate bins keep their pattern (send one 7,
receive one 7).  Ten such chains into ten distinct [9] bins, taking both
7s of five cap32 bins, followed by five nine-chains from one cap48
[9,9,9,9,9] bin into those cap32 bins, realise one improving unit
(Delta idle moment = f(48)+5f(5)-10f(7)-f(3) < 0 at a2269, exact).
Every applied chain is validated by the full literal checker
(model.check_rows).  Usage: find_chains.py 43|48 [max_units] [seed]
Writes FILL<which>-CHAINED.json.gz and CHAINS-<which>.json.
"""
import gzip, json, random, sys, time
from collections import defaultdict, deque
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from model import load_base, load_case, width_of, check_rows, repack_offsets, fam, OUT

base = load_base(); win = base['win']

class State:
    def __init__(self, case, rows):
        self.case = case; self.rows = rows
        self.rebuild()
    def rebuild(self):
        self.bins = defaultdict(list)
        for idx, r in enumerate(self.rows):
            self.bins[(r[2], r[3], r[4])].append(idx)
        self.call_fams = defaultdict(set)
        for r in self.rows:
            self.call_fams[r[0]].add(fam(base, r[2], r[3], r[4]))
        self.by_time_width = defaultdict(list)  # (time,width) -> row idx
        for idx, r in enumerate(self.rows):
            self.by_time_width[(r[0], self.w(idx))].append(idx)
    def w(self, idx):
        r = self.rows[idx]; return width_of(base, self.case, r[0], r[1])
    def btype(self, b):
        return win[(b[0], b[1])][0], tuple(sorted((self.w(i) for i in self.bins[b]), reverse=True))
    def bin_of(self, idx):
        r = self.rows[idx]; return (r[2], r[3], r[4])

def find_chain(st, hole, width, goal_pred, rng, max_depth=6, preferred=()):
    """BFS alternating path: hole receives a `width` item; each intermediate
    bin sends one and receives one; final item comes from a bin satisfying
    goal_pred(bin).  Returns list of (row_idx, target_bin) moves or None.
    Edge test: item time in target window; target family free in item's call
    (conservative, w.r.t. pre-chain state, own family allowed)."""
    # BFS over hole bins; parent[b] = (item_idx moved into b's predecessor ...)
    # Represent: came[b] = (prev_hole_bin, item_idx) meaning item_idx (from b) moves into prev_hole_bin.
    came = {hole: None}
    q = deque([hole]); depth = {hole: 0}
    goal_item = None; goal_bin = None
    pref = set(preferred)
    while q and goal_item is None:
        hb = q.popleft()
        if depth[hb] >= max_depth:
            continue
        cap_h, times_h = win[(hb[0], hb[1])]
        fam_h = fam(base, *hb)
        cands = []
        for t in times_h:
            for idx in st.by_time_width[(t, width)]:
                src = st.bin_of(idx)
                if src in came:
                    continue
                own = fam(base, *src)
                if fam_h in st.call_fams[t] and fam_h != own:
                    continue
                cands.append(idx)
        rng.shuffle(cands)
        # goal items first (preferred goals first), then intermediates
        cands.sort(key=lambda idx: (0 if st.bin_of(idx) in pref else 1 if goal_pred(st.bin_of(idx)) else 2))
        for idx in cands:
            src = st.bin_of(idx)
            if goal_pred(src):
                came[src] = (hb, idx); goal_item = idx; goal_bin = src; break
            if src not in came:
                came[src] = (hb, idx); depth[src] = depth[hb] + 1; q.append(src)
    if goal_item is None:
        return None
    moves = []
    b = goal_bin
    while came[b] is not None:
        prev_hole, idx = came[b]
        moves.append((idx, prev_hole))
        b = prev_hole
    return moves

def apply_moves(st, moves):
    newrows = [list(r) for r in st.rows]
    for idx, tb in moves:
        newrows[idx][2], newrows[idx][3], newrows[idx][4] = tb
    newrows = repack_offsets(base, st.case, newrows)
    idle, H = check_rows(base, st.case, newrows)  # raises if illegal
    st.rows = newrows; st.rebuild()
    return idle, H

def main():
    which = sys.argv[1]; max_units = int(sys.argv[2]) if len(sys.argv) > 2 else 15
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else 777
    rng = random.Random(seed)
    case = load_case(base, which)
    st = State(case, [list(r) for r in case['fill']['rows']])
    idle0, H0 = check_rows(base, case, st.rows)
    print(which, 'start idle', dict(sorted(idle0.items())), flush=True)
    log = dict(which=which, seed=seed, idle_before={str(k): v for k, v in sorted(idle0.items())},
               H_before={str(k): v for k, v in sorted(H0.items())}, units=[])
    for uno in range(max_units):
        t0 = time.time()
        Abins = [b for b in st.bins if st.btype(b) == (16, (9,))]
        if len(Abins) < 10:
            print('fewer than 10 rem-7 bins left'); break
        rng.shuffle(Abins)
        hit_B = []          # B bins that lost both 7s, in completion order
        hit_count = defaultdict(int)
        unit_moves = []
        used_A = []
        snapshot = [list(r) for r in st.rows]
        ok = True
        # ten seven-chains
        for ci in range(10):
            def goalB(b, st=st):
                return st.btype(b) in ((32, (9, 9, 7, 7)), (32, (9, 9, 7)))
            pref = [b for b, c in hit_count.items() if c == 1]
            done = False
            for ab in Abins:
                if ab in used_A or st.btype(ab) != (16, (9,)):
                    continue
                moves = find_chain(st, ab, 7, goalB, rng, preferred=pref)
                if moves is None:
                    continue
                srcB = st.bin_of(moves[0][0])
                try:
                    apply_moves(st, moves)
                except AssertionError:
                    continue
                hit_count[srcB] += 1
                if hit_count[srcB] == 2:
                    hit_B.append(srcB)
                used_A.append(ab); unit_moves.append(('7', moves)); done = True
                break
            if not done:
                print(f'unit {uno}: seven-chain {ci} failed'); ok = False; break
        if ok and len(hit_B) != 5:
            print(f'unit {uno}: seven-chains done but hit_B={len(hit_B)} (counts {dict(hit_count)})')
            ok = False
        if ok:
            # choose a single C bin and drain it into the 5 B bins
            Cbins = [b for b in st.bins if st.btype(b) == (48, (9, 9, 9, 9, 9))]
            rng.shuffle(Cbins)
            drained = False
            for cb in Cbins[:400]:
                snap2 = [list(r) for r in st.rows]
                moves9_all = []; good = True
                for bb in hit_B:
                    if st.btype(bb) != (32, (9, 9)):
                        good = False; break
                    def goalC(b, cb=cb):
                        return b == cb
                    moves = find_chain(st, bb, 9, goalC, rng, max_depth=5)
                    if moves is None:
                        good = False; break
                    try:
                        apply_moves(st, moves)
                    except AssertionError:
                        good = False; break
                    moves9_all.append(moves)
                if good and st.btype(cb) == (48, ()):
                    unit_moves.append(('9', moves9_all)); drained = True
                    print(f'unit {uno}: drained C bin {cb}')
                    break
                st.rows = snap2; st.rebuild()
            if not drained:
                print(f'unit {uno}: no C bin could be drained'); ok = False
        if not ok:
            st.rows = snapshot; st.rebuild()
            print(f'unit {uno} rolled back ({time.time()-t0:.1f}s)'); break
        idle, H = check_rows(base, case, st.rows)
        rec = dict(unit=uno, A=[list(b) for b in used_A], B=[list(b) for b in hit_B],
                   idle_after={str(k): v for k, v in sorted(idle.items())},
                   H_after={str(k): v for k, v in sorted(H.items())},
                   chain_lengths=[len(m) for tag, ms in unit_moves if tag == '7' for m in [ms]])
        log['units'].append(rec)
        print(f'unit {uno} ACCEPTED ({time.time()-t0:.1f}s) idle {rec["idle_after"]}', flush=True)
    out_fill = dict(columns=case['fill']['columns'], rows=sorted(st.rows),
                    dispatch_overrides=case['fill']['dispatch_overrides'])
    p = OUT / f'FILL{which}-CHAINED.json.gz'
    p.write_bytes(gzip.compress(json.dumps(out_fill, separators=(',', ':')).encode(), mtime=0))
    (OUT / f'CHAINS-{which}.json').write_text(json.dumps(log, indent=1) + '\n')
    print('units applied:', len(log['units']), '->', p)

if __name__ == '__main__':
    main()
