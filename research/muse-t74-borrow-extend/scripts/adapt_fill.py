#!/usr/bin/env python3
"""Adapt #2269's shipped 437-helper owner fill to the 432-helper words.

Helper indices are register order (224..703) minus removed helpers. The five
newly removed helpers (606,635,637,638,639) lose their hosted roles; the
remaining roles keep (owner_replica, child, port) and are repacked to a
gap-free prefix per bin in old-offset order. Widths are checked register by
register against the native 48-alias widths (from rebind.py output).
Outputs: FILL48.json.gz and BORROW-PROVIDERS48.json in this package.
Verification is by #2269's reconstruct.py (literal checker), run separately.
"""
import gzip, json
from collections import defaultdict
from pathlib import Path

PKG = Path('research/gmx-t74-borrow43')
OUT = Path('research/muse-t74-borrow-extend')
def rd(p):
    b = Path(p).read_bytes()
    return json.loads(gzip.decompress(b) if str(p).endswith('.gz') else b)

wit43 = rd(PKG / 'new/borrow/inputs/witness_43_base.json')
wit48 = rd(OUT / 'witness_48_base.json')
rem43 = sorted(p['register'] for p in wit43['pairs'])
rem48 = sorted(p['register'] for p in wit48['pairs'])
helpers = list(range(224, 704))
idx43 = {r: i for i, r in enumerate(r for r in helpers if r not in rem43)}
idx48 = {r: i for i, r in enumerate(r for r in helpers if r not in rem48)}
new_removed = [r for r in rem48 if r not in rem43]
drop_idx = {idx43[r] for r in new_removed}
print('new removed', new_removed, 'old indices', sorted(drop_idx))

plan48 = rd('/tmp/rebind48/PLAN.json')
prov43 = rd(PKG / 'new/BORROW-PROVIDERS.json')
prov48 = {}
for pid in ('gauge44', 'extra'):
    w48 = plan48['provider_registry'][pid]['widths']
    w43 = prov43[pid]['widths']
    assert len(w48) == 432 and len(w43) == 437
    diffs = [(r, w43[idx43[r]], w48[idx48[r]]) for r in helpers
             if r not in rem48 and w43[idx43[r]] != w48[idx48[r]]]
    print(pid, 'width diffs on surviving helpers:', diffs)
    assert not diffs
    prov48[pid] = dict(widths=w48,
                       actual_paid_profile=plan48['provider_registry'][pid]['actual_paid_profile'])
(OUT / 'BORROW-PROVIDERS48.json').write_text(json.dumps(prov48, indent=1) + '\n')

fill = rd(PKG / 'new/borrow-fill/FILL.json.gz')
rows = []
for time, helper, rep, child, port, offset in fill['rows']:
    if helper in drop_idx: continue
    reg = next(r for r, i in idx43.items() if i == helper)
    rows.append([time, idx48[reg], rep, child, port, offset])
# repack offsets per bin in old-offset order; width depends on dispatch,
# resolved by reconstruct from providers -- widths are provider-specific, so
# repack per (bin) using each row's own provider width via the order/dispatch
plan_in = rd(PKG / 'inputs/PLAN.json'); T = plan_in['T']
order = [[s, r + T * g] for s, r in plan_in['order'] for g in range(2)]
dispatch = {(s, r + T * g): pid for s, r, pid in rd(PKG / 'inputs/DISPATCH.json') for g in range(2)}
for s_, r_, p_ in fill['dispatch_overrides']: dispatch[s_, r_] = p_
bins = defaultdict(list)
for row in rows: bins[(row[2], row[3], row[4])].append(row)
for b, rs in bins.items():
    rs.sort(key=lambda x: x[5])
    off = 0
    for row in rs:
        stage, replica = order[row[0]]
        wdt = prov48[dispatch[stage, replica]]['widths'][row[1]]
        row[5] = off; off += wdt
out = dict(columns=fill['columns'], rows=sorted(rows),
           dispatch_overrides=fill['dispatch_overrides'])
p = OUT / 'FILL48.json.gz'
p.write_bytes(gzip.compress(json.dumps(out, separators=(',', ':')).encode(), mtime=0))
print('wrote', p, 'rows', len(rows), 'expected', len(order) * 432)
assert len(rows) == len(order) * 432
