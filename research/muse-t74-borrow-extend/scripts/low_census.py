#!/usr/bin/env python3
"""Round-2 census: low helpers, their early B prefix gates, and low lenders.

For each T74 canonical word (gauge44/extra) and each of the 48 low helpers
(block helpers not in the block's `high` list), classify every B gate
incident to the helper before its block's first_correction as
  * echo:  add Y, helper, c          (Y in [v,2v))
  * temp:  add helper, source, t     (external temporary addition)
  * other: anything else (must not occur)
and verify that (a) the net temp coefficient per source is zero at the end
of the prefix, (b) no non-deferred B gate touches the helper between the
prefix and its block deadline, and (c) temp sources are never a destination
before the last echo they feed (so a direct rewrite gate Y += c*t*source
reads the same row the temp gate read).  Derives, per helper,
deleted_echo_indices / deleted_prefix_indices / early_prefix_rewrites in
#2226's field format.

Also censuses candidate low lenders: registers with start frame zero and
final dimension 4 (paid-rank-0 handoff into a 4/5-dim common frame), and
records which of them witness_48's early_tail_events touch.

Output: LOW-CENSUS.json in this package.  Run from the workspace root.
"""
import gzip, json
from fractions import Fraction as Q
from pathlib import Path

B = Path('research/gmx-t74-borrow43/new/borrow')
OUT = Path('research/muse-t74-borrow-extend')

def incident(e): return e[1:3] if e[0] == 'add' else e[1:2]

def derive_prefix(w, blk, h):
    v = w['v']
    prefix = [i for i, e in enumerate(w['B'])
              if i < blk['first_correction'] and h in incident(e)]
    echoes, temps, others, rewrites = [], [], [], {}
    cum = {}   # source -> cumulative temp coeff (Fraction)
    for i in prefix:
        e = w['B'][i]
        assert e[0] == 'add', (h, i, e)
        if v <= e[1] < 2 * v and e[2] == h:
            echoes.append(i)
            c = Q(e[3], e[4])
            gates = []
            for s, t in sorted(cum.items()):
                if t:
                    rc = c * t
                    gates.append(['add', e[1], s, rc.numerator, rc.denominator, e[-1]])
            rewrites[str(i)] = gates
        elif e[1] == h:
            temps.append(i)
            cum[e[2]] = cum.get(e[2], Q(0)) + Q(e[3], e[4])
        else:
            others.append(i)
    net_zero = all(t == 0 for t in cum.values())
    # (b) gates between first_correction and first_input touching h must be
    # helper-only for this block (they are deferred to first_input in replay)
    ss = set(blk['helpers'])
    mid_bad = [i for i in range(blk['first_correction'], blk['first_input'])
               if h in incident(w['B'][i]) and not set(incident(w['B'][i])) <= ss]
    # (c) temp sources never a B destination at/before the echo block end
    src_ok = {}
    for s in {w['B'][i][2] for i in temps}:
        last_echo = max(echoes) if echoes else -1
        dest_before = [i for i, e in enumerate(w['B'][:last_echo + 1])
                       if e[0] in ('add', 'scale') and e[1] == s]
        src_ok[s] = not dest_before
    return dict(
        register=h, base=blk['base'], deadline=blk['first_input'],
        first_correction=blk['first_correction'],
        prefix_indices=prefix, echo_indices=echoes, temp_indices=temps,
        other_indices=others, net_temp_zero=bool(net_zero),
        temp_sources=sorted({w['B'][i][2] for i in temps}),
        temp_source_unchanged={str(k): v for k, v in sorted(src_ok.items())},
        mid_non_deferred_indices=mid_bad,
        deleted_echo_indices=echoes, deleted_prefix_indices=prefix,
        early_prefix_rewrites=rewrites,
        echo_gates=[w['B'][i] for i in echoes],
        temp_gates=[w['B'][i] for i in temps])

def census_word(canon, witname):
    w = json.loads(gzip.decompress((B / 'inputs' / canon).read_bytes()))
    blocks = json.loads((B / 'inputs/blocks.json').read_text())['sources'][0]['blocks']
    wit = json.loads((OUT / witname).read_text())
    v, n = w['v'], 2 * w['v'] + w['R']
    lows = {}
    for blk in blocks:
        for h in blk['helpers']:
            if h not in blk['high']:
                lows[h] = derive_prefix(w, blk, h)
    # candidate low lenders
    cand = [r for r in range(n)
            if len(w['frames'][w['start'][r]]) == 0
            and len(w['frames'][w['final'][r]]) == 4]
    tail_targets = sorted({e['gate'][1] for e in wit['early_tail_events']})
    lent48 = sorted(p['borrow_from'] for p in wit['pairs'])
    return dict(
        canon=canon, n_low=len(lows),
        lows={str(k): v_ for k, v_ in sorted(lows.items())},
        candidate_low_lenders=cand,
        early_tail_targets=tail_targets,
        candidate_lenders_all_tail_restored=sorted(set(cand) & set(tail_targets)),
        lenders_used_by_48=lent48,
        candidate_overlap_with_48_lenders=sorted(set(cand) & set(lent48)))

res = {}
for canon, witn in [('gauge44.canonical.json.gz', 'witness_48_base.json'),
                    ('extra.canonical.json.gz', 'witness_48_extra.json')]:
    r = census_word(canon, witn)
    res[canon] = r
    bad = [h for h, d in r['lows'].items()
           if d['other_indices'] or not d['net_temp_zero']
           or d['mid_non_deferred_indices']
           or not all(d['temp_source_unchanged'].values())]
    special = {h: d['temp_sources'] for h, d in r['lows'].items() if d['temp_indices']}
    print(canon, 'lows', r['n_low'], 'bad', bad, 'special(temp)', special)
    print('  lenders cand', len(r['candidate_low_lenders']),
          'tail-restored', len(r['candidate_lenders_all_tail_restored']),
          'overlap48', r['candidate_overlap_with_48_lenders'])
    assert not bad
(Path(OUT / 'LOW-CENSUS.json')).write_text(json.dumps(res, indent=1) + '\n')
print('wrote LOW-CENSUS.json')
