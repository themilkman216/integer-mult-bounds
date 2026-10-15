#!/usr/bin/env python3
"""Express the candidate as owner moves vs #2322, and regenerate it from
the pinned PR2312 owner map in the style of #2322's generate_owners.py.

Writes CANDIDATE-MOVES.json.gz (delta vs shipped #2322 owners, columns
stage/replica/helper/owner_replica/child/port/offset) and
REGENERATION.json: (i) positive control — shipped OWNERS regenerated from
PR2312 OWNERS + #2322 OWNER-MOVES byte-semantically identical to shipped;
(ii) candidate regenerated from PR2312 OWNERS + merged moves identical to
CANDIDATE-OWNERS.  Needs the pinned PR2312 source root (argv[1], default
/tmp/muse2322/src2312 as materialised in this session; the package's
fetch_suppliers.py produces the same tree from the network).
"""
import gzip, hashlib, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from model2322 import OUT, PKG, rd

SRC = Path(sys.argv[1] if len(sys.argv) > 1 else '/tmp/muse2322/src2312')
DROP = {384, 386, 387, 388}
pkg2312 = SRC / 'research/gmx-t74-borrow43-width-exchange'
assert (pkg2312 / 'OWNERS.json.gz').is_file(), f'PR2312 source not at {SRC}'

shipped = rd(PKG / 'data/OWNERS.json.gz')
cand = rd(OUT / 'CANDIDATE-OWNERS.json.gz')
assert len(shipped) == len(cand)
cols = ['stage', 'replica', 'helper', 'owner_replica', 'child', 'port', 'offset']
delta = []
for s, c in zip(shipped, cand):
    assert (s['stage'], s['replica'], s['helper'], s['time']) == \
           (c['stage'], c['replica'], c['helper'], c['time'])
    if any(s[k] != c[k] for k in ('owner_replica', 'child', 'port', 'offset')):
        delta.append([c[k] for k in cols])
(OUT / 'CANDIDATE-MOVES.json.gz').write_bytes(gzip.compress(
    json.dumps(dict(columns=cols, rows=delta), sort_keys=True,
               separators=(',', ':')).encode(), mtime=0))
print('delta moves vs shipped:', len(delta))

def regenerate(moves_extra):
    plan = rd(pkg2312 / 'new/PLAN.json')
    order = rd(PKG / 'CALL-ORDER.json')
    at = {tuple(x): i for i, x in enumerate(order)}
    patch = rd(PKG / 'OWNER-MOVES.json.gz')
    moves = {tuple(z[:3]): dict(zip(patch['columns'], z)) for z in patch['rows']}
    for z in moves_extra:
        moves[tuple(z[:3])] = dict(zip(cols, z))
    rows = []
    for old in rd(pkg2312 / 'OWNERS.json.gz'):
        h = old['helper']
        if h in DROP:
            continue
        z = dict(old); z['helper'] = h - sum(k < h for k in DROP)
        key = (z['stage'], z['replica'], z['helper'])
        if key in moves:
            for k in ('owner_replica', 'child', 'port', 'offset'):
                z[k] = moves[key][k]
        z['time'] = at[z['stage'], z['replica']]
        r, c, v = z['owner_replica'], z['child'], z['port']
        z['copy'] = r * 112 + v
        z['family'] = r * 896 + (2 * plan['pairs'][str(c)] + plan['sides'][str(c)]) * 112 + v
        rows.append(z)
    rows.sort(key=lambda z: (z['time'], z['helper']))
    return rows

regen_ship = regenerate([])
assert regen_ship == shipped, 'positive control: shipped regeneration mismatch'
regen_cand = regenerate(delta)
cand_sorted = sorted(cand, key=lambda z: (z['time'], z['helper']))
assert regen_cand == cand_sorted, 'candidate regeneration mismatch'
res = dict(status='PASS_REGENERATED_SHIPPED_AND_CANDIDATE_FROM_PR2312',
           delta_moves=len(delta),
           shipped_rows=len(regen_ship), candidate_rows=len(regen_cand),
           source_root=str(SRC),
           pr2312_owners_sha256=hashlib.sha256(
               (pkg2312 / 'OWNERS.json.gz').read_bytes()).hexdigest())
(OUT / 'REGENERATION.json').write_text(json.dumps(res, indent=1) + '\n')
print(res['status'])
