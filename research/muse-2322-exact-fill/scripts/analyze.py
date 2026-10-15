#!/usr/bin/env python3
"""Structural analysis of #2322's shipped owner fill. Writes ANALYSIS.json.

Exact integer counting throughout. Includes: window inventory and interval
contiguity; provider width/paid identity (3F recheck); bin patterns and the
locations of every non-tight pattern; same-family-group window disjointness
(the condition that collapses per-call family distinctness to per-bin
distinct calls); prefix/suffix tight-cut scan for cap-16 [9] bins.
"""
import json, sys
from collections import Counter, defaultdict
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from model2322 import load_all, PER_CALL, OUT

base = load_all()
plan, win, rows = base['plan'], base['win'], base['rows']
out = {}

capcount = Counter(cap for cap, _ in win.values())
contig = all(list(ts) == list(range(min(ts), max(ts) + 1)) for _, ts in win.values())
out['windows'] = dict(count=len(win), caps={str(k): v for k, v in sorted(capcount.items())},
                      bins_total=len(win) * 112,
                      bins_by_cap={str(k): v * 112 for k, v in sorted(capcount.items())},
                      all_allowed_contiguous_intervals=bool(contig),
                      interval={f'{r},{c}': [min(ts), max(ts)] for (r, c), (_, ts) in list(win.items())[:0]})
reg = plan['provider_registry']
out['providers_identical'] = dict(
    widths_equal=reg['gauge44']['widths'] == reg['extra']['widths'],
    paid_equal=reg['gauge44']['actual_paid_profile'] == reg['extra']['actual_paid_profile'],
    widths_per_call={str(k): v for k, v in sorted(Counter(reg['gauge44']['widths']).items())},
    paid_per_call=reg['gauge44']['actual_paid_profile'],
    dispatch_counts=dict(Counter(c['provider'] for c in plan['provider_calls'])))

# family groups: G = rep*8 + Q(child), Q = 2*pairs+sides. Windows sharing (rep,Q)
groups = defaultdict(list)
for (rep, child), (cap, ts) in win.items():
    q = 2 * base['pairs'][child] + base['sides'][child]
    groups[(rep, q)].append((child, min(ts), max(ts)))
overlap = 0; ngroups_multi = 0
for g, lst in groups.items():
    if len(lst) > 1:
        ngroups_multi += 1
        for i in range(len(lst)):
            for j in range(i + 1, len(lst)):
                if lst[i][1] <= lst[j][2] and lst[j][1] <= lst[i][2]:
                    overlap += 1
out['family_groups'] = dict(n_groups=len(groups), multi_window_groups=ngroups_multi,
                            pairwise_overlapping_same_group_pairs=overlap,
                            collapse_to_per_bin_distinct_calls=bool(overlap == 0))

# shipped fill checked by #2322's own checker
H, idle = base['verify'].owners_check(rows, plan, base['contract'])
out['shipped_check'] = dict(H={str(k): v for k, v in sorted(H.items())},
                            idle={str(k): v for k, v in sorted(idle.items())},
                            matches_claim=dict(H) == {int(k): v for k, v in base['claim']['global_profile'].items()})

bins = defaultdict(list)
for z in rows:
    bins[(z['owner_replica'], z['child'], z['port'])].append(z['width'])
pat = Counter(); rem_by_cap = defaultdict(Counter)
for (rep, child), (cap, _t) in win.items():
    for port in range(112):
        ws = tuple(sorted(bins.get((rep, child, port), []), reverse=True))
        pat[(cap, cap - sum(ws), ws)] += 1
        rem_by_cap[cap][cap - sum(ws)] += 1
out['patterns'] = [dict(cap=c, rem=r, widths=list(ws), count=n)
                   for (c, r, ws), n in pat.most_common()]
out['rem_by_cap'] = {str(c): {str(k): v for k, v in sorted(d.items())}
                     for c, d in sorted(rem_by_cap.items())}

def locations(cap_target, ws_target):
    loc = Counter()
    for (rep, child), (cap, _t) in win.items():
        if cap != cap_target:
            continue
        for port in range(112):
            if sorted(bins.get((rep, child, port), [])) == sorted(ws_target):
                loc[f'{rep},{child}'] += 1
    return dict(loc.most_common())
out['nontight_locations'] = {
    'cap16_[9]': locations(16, [9]),
    'cap48_[9,9,9,9,8,4]': locations(48, [9, 9, 9, 9, 8, 4]),
    'cap48_[9,9,9,9,8]': locations(48, [9, 9, 9, 9, 8]),
    'cap48_[9,9,9]': locations(48, [9, 9, 9]),
    'cap48_[9,9,9,9]': locations(48, [9, 9, 9, 9]),
}
for key in [(43, 0), (35, 17), (56, 10), (53, 12)]:
    cap, ts = win[key]
    out.setdefault('key_windows', {})[f'{key[0]},{key[1]}'] = dict(
        cap=cap, lo=min(ts), hi=max(ts), size=len(ts))

# prefix / suffix tight cut scan: k_lb = B16 - supply7 - (supply8 - B8)//2
def scan(mode):
    best = []
    for T in range(666):
        if mode == 'prefix':
            S = [k for k, (cap, ts) in win.items() if max(ts) <= T]
            nc = T + 1
        else:
            S = [k for k, (cap, ts) in win.items() if min(ts) >= T]
            nc = 666 - T
        if not S:
            continue
        bc = Counter(win[k][0] for k in S)
        klb = bc[16] * 112 - nc * PER_CALL[7] - (nc * PER_CALL[8] - bc[8] * 112) // 2
        best.append((klb, T))
    return max(best)
out['tight_prefix_cut'] = dict(max_k_lower_bound=scan('prefix')[0], at_T=scan('prefix')[1])
out['tight_suffix_cut'] = dict(max_k_lower_bound=scan('suffix')[0], at_T=scan('suffix')[1])

(OUT / 'ANALYSIS.json').write_text(json.dumps(out, indent=1) + '\n')
print('providers identical:', out['providers_identical'])
print('family collapse:', out['family_groups'])
print('shipped H ok:', out['shipped_check']['matches_claim'], 'idle', out['shipped_check']['idle'])
print('patterns:', len(out['patterns']))
for p in out['patterns']:
    print(' ', p)
print('nontight locations:', out['nontight_locations'])
print('tight cuts:', out['tight_prefix_cut'], out['tight_suffix_cut'])
print('intervals contiguous:', out['windows']['all_allowed_contiguous_intervals'])
