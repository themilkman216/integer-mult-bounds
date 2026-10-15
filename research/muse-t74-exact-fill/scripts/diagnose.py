#!/usr/bin/env python3
"""Diagnose why width-7 items cannot move into cap16 [9] (rem-7) bins:
window membership vs family distinctness, and the window structure of the
bin classes involved in the pattern-LP recombination."""
import json, sys
from collections import Counter, defaultdict
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from model import load_base, load_case, width_of, fam, OUT

base = load_base(); win = base['win']; order = base['order']
out = {}
for which in ('43',):
    case = load_case(base, which); rows = case['fill']['rows']
    bins = defaultdict(list)
    for idx, r in enumerate(rows):
        bins[(r[2], r[3], r[4])].append(idx)
    def w_of(i): return width_of(base, case, rows[i][0], rows[i][1])
    def btype(b): return win[(b[0], b[1])][0], tuple(sorted((w_of(i) for i in bins[b]), reverse=True))
    bytype = defaultdict(list)
    for b in bins: bytype[btype(b)].append(b)
    # also empty bins
    call_fams = defaultdict(set)
    for r in rows: call_fams[r[0]].add(fam(base, r[2], r[3], r[4]))
    A = bytype[(16, (9,))]
    info = {}
    info['A_windows'] = {str(k): v for k, v in Counter((b[0], b[1]) for b in A).most_common()}
    info['A_window_sizes'] = {str(k): v for k, v in Counter(len(win[(b[0], b[1])][1]) for b in A).items()}
    info['A_resident_times'] = sorted(rows[bins[b][0]][0] for b in A)[:20]
    # for each 7-item source class, count window-ok and window+family-ok targets among A
    for src_type, label in [((32, (9, 9, 7, 7)), 'B7799'), ((32, (9, 8, 8, 7)), 'B7889'),
                            ((16, (9, 7)), 'C79')]:
        items = [i for b in bytype[src_type] for i in bins[b] if w_of(i) == 7]
        wok = fok = 0; per_item_w = []
        for i in items:
            r = rows[i]; t = r[0]; own = fam(base, r[2], r[3], r[4]); c = 0
            for ab in A:
                if t in win[(ab[0], ab[1])][1]:
                    c += 1
                    fa = fam(base, *ab)
                    if fa not in call_fams[t] or fa == own:
                        fok += 1
            per_item_w.append(c)
            wok += c
        info[label] = dict(items=len(items), window_ok_pairs=wok, window_family_ok_pairs=fok,
                           items_with_any_window_ok=sum(1 for c in per_item_w if c),
                           max_window_ok=max(per_item_w) if per_item_w else 0)
    # A-bin window allowed times: what stages/replicas? and B-bin 7-item times
    awin_times = Counter()
    for b in A:
        for t in win[(b[0], b[1])][1]:
            awin_times[t] += 1
    info['A_allowed_time_stage_hist'] = {str(k): v for k, v in Counter(order[t][0] for b in A for t in win[(b[0], b[1])][1]).items()}
    b7_times = [rows[i][0] for b in bytype[(32, (9, 9, 7, 7))] for i in bins[b] if w_of(i) == 7]
    info['B7799_seven_stage_hist'] = {str(k): v for k, v in Counter(order[t][0] for t in b7_times).items()}
    a9_times = [rows[bins[b][0]][0] for b in A]
    info['A_resident_stage_hist'] = {str(k): v for k, v in Counter(order[t][0] for t in a9_times).items()}
    # window overlap structure: for A windows, which children/reps
    info['A_children'] = {str(k): v for k, v in Counter(b[1] for b in A).items()}
    info['A_reps'] = {str(k): v for k, v in Counter(b[0] for b in A).items()}
    info['B7799_children'] = {str(k): v for k, v in Counter(b[1] for b in bytype[(32, (9, 9, 7, 7))]).items()}
    info['B7889_children'] = {str(k): v for k, v in Counter(b[1] for b in bytype[(32, (9, 8, 8, 7))]).items()}
    out[which] = info
    print(json.dumps(info, indent=1))
(OUT / 'DIAGNOSE.json').write_text(json.dumps(out, indent=1) + '\n')
