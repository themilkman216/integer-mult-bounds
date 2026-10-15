#!/usr/bin/env python3
"""Structural analysis of the 43- and 48-alias fills: window/bin inventory,
bin patterns (cap, remainder, width multiset), family/window coupling stats,
and the extra active-pair exclusion checked by independent_core.py.
Writes ANALYSIS.json. Read-only w.r.t. predecessor packages."""
import json, sys
from collections import Counter, defaultdict
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from model import load_base, load_case, width_of, check_rows, fam, OUT

base = load_base()
plan, order, win = base['plan'], base['order'], base['win']
out = {}

# window inventory
capcount = Counter(cap for cap, _ in win.values())
out['windows'] = dict(count=len(win), caps={str(k): v for k, v in sorted(capcount.items())},
                      bins_total=len(win) * 112,
                      bins_by_cap={str(k): v * 112 for k, v in sorted(capcount.items())},
                      allowed_size_hist={str(k): v for k, v in sorted(Counter(len(t) for _, t in win.values()).items())},
                      children=sorted({c for _, c in win}), reps=[min(r for r, _ in win), max(r for r, _ in win)],
                      pairs={str(k): v for k, v in sorted(base['pairs'].items())},
                      sides={str(k): v for k, v in sorted(base['sides'].items())})
# child -> (cap set, pair, side)
childinfo = {}
for (rep, child), (cap, _t) in win.items():
    childinfo.setdefault(child, set()).add(cap)
out['child_caps'] = {str(c): sorted(s) for c, s in sorted(childinfo.items())}
# families per (rep,port): children sharing (pair,side) collide
grp = defaultdict(list)
for c in base['pairs']:
    grp[(base['pairs'][c], base['sides'][c])].append(c)
out['family_groups'] = {str(k): v for k, v in sorted(grp.items())}
out['calls'] = len(order)
out['stage_pairs_from_plan'] = 'see parent recipe; not in PLAN.json'

# Is the independent_core active-pair exclusion implied by windows?
# exclusion: NOT (rep == call_replica AND pairs[child] == stage_pair[stage]).
# stage_pair comes from parent recipe; reconstruct it from GLOBAL-TEMPLATE.
import gzip
parent = json.loads(gzip.decompress((Path(__file__).resolve().parents[3] / 'research/gmx-t74-borrow43/inputs/GLOBAL-TEMPLATE.json.gz').read_bytes()))
stage_pair = {e['stage']: e['pair'] for e in parent['recipe'] if e['kind'] == 'local'}
out['stage_pair'] = {str(k): v for k, v in sorted(stage_pair.items())}
viol_allowed = 0; total_allowed = 0
for time, (stage, replica) in enumerate(order):
    for (rep, child), (cap, times) in win.items():
        if time in times:
            total_allowed += 1
            if rep == replica and base['pairs'][child] == stage_pair[stage]:
                viol_allowed += 1
out['active_pair_exclusion'] = dict(allowed_time_windows=total_allowed,
                                    allowed_but_excluded=viol_allowed,
                                    implied_by_windows=(viol_allowed == 0))

for which in ('43', '48'):
    case = load_case(base, which)
    rows = case['fill']['rows']
    idle, H = check_rows(base, case, rows)
    # bin patterns
    bins = defaultdict(list)
    for r in rows:
        bins[(r[2], r[3], r[4])].append(width_of(base, case, r[0], r[1]))
    pat = Counter()
    rem_by_cap = defaultdict(Counter)
    for (rep, child), (cap, _t) in win.items():
        for port in range(112):
            ws = tuple(sorted(bins.get((rep, child, port), []), reverse=True))
            rem = cap - sum(ws)
            pat[(cap, rem, ws)] += 1
            rem_by_cap[cap][rem] += 1
    wcounts = Counter(case['widths']['gauge44'])
    out[f'case{which}'] = dict(
        R=case['R'], rows=len(rows),
        widths_per_call={str(k): v for k, v in sorted(wcounts.items())},
        width_mass_per_call=sum(k * v for k, v in wcounts.items()),
        idle={str(k): v for k, v in sorted(idle.items())},
        H={str(k): v for k, v in sorted(H.items())},
        idle_mass=sum(k * v for k, v in idle.items()),
        rem_by_cap={str(c): {str(k): v for k, v in sorted(d.items())} for c, d in sorted(rem_by_cap.items())},
        top_patterns=[dict(cap=c, rem=r, widths=list(ws), count=n)
                      for (c, r, ws), n in pat.most_common(40)],
        n_patterns=len(pat),
        dispatch_counts={str(k): v for k, v in Counter(case['dispatch'].values()).items()},
        paid=case['paid'])
    # shipped-fill violations of active-pair exclusion?
    bad = sum(1 for t, h, rep, child, port, off in rows
              if rep == order[t][1] and base['pairs'][child] == stage_pair[order[t][0]])
    out[f'case{which}']['active_pair_violations_in_fill'] = bad

(OUT / 'ANALYSIS.json').write_text(json.dumps(out, indent=1) + '\n')
print(json.dumps({k: out[k] for k in ('windows', 'child_caps', 'family_groups', 'stage_pair', 'active_pair_exclusion')}, indent=1))
for which in ('43', '48'):
    c = out[f'case{which}']
    print(which, 'idle', c['idle'], 'H', c['H'], 'idle_mass', c['idle_mass'],
          'viol', c['active_pair_violations_in_fill'], 'npat', c['n_patterns'])
    print(' rem_by_cap', c['rem_by_cap'])
