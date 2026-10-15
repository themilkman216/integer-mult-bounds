#!/usr/bin/env python3
"""Per-low-helper paid-profile screen (base word, one alias at a time).

For each of the 48 low helpers, builds witness_49 = witness_48 + that helper
lent by register 298 (a fixed lender, isolating the helper effect) via
low_solve.py, then replays with the vendored exact replay (49/1 counts) and
records the local paid profile delta vs the 48-alias profile and the paid
moment saving per call at a2269.  Joint/multi-alias interactions are NOT
captured; this is a screen for allocation choice only.
Output: LOW-SINGLES.json.  Scratch witnesses/replays go to /tmp.
"""
import json, subprocess, sys
from pathlib import Path

ROOT = Path.cwd()
B = ROOT / 'research/gmx-t74-borrow43/new/borrow'
OUT = ROOT / 'research/muse-t74-borrow-extend'
SCR = OUT / 'scripts'
K = 0.0016962471390584742; A = K / (1 - K)
def fmom(p): return sum(n * (int(r) / 73) ** (1 - A) for r, n in p.items())

src = (ROOT / 'research/gmx-t74-borrow43/new/code/borrow/vendor/pr2226_replay.py').read_text()
old = "assert len(pairs)==80 and sum(x['low'] for x in pairs)==32"
assert old in src
(SCR / 'replay49.py').write_text(src.replace(old, "assert len(pairs)==49 and sum(x['low'] for x in pairs)==1"))

census = json.loads((OUT / 'LOW-CENSUS.json').read_text())['gauge44.canonical.json.gz']['lows']
P48 = {'1': 2351, '2': 501, '3': 414, '4': 129, '5': 37, '8': 8}
m48 = fmom(P48)
rows = []
for h in sorted(map(int, census)):
    wit = Path(f'/tmp/wit_single_{h}.json'); rep = Path(f'/tmp/rep_single_{h}.json')
    r1 = subprocess.run([sys.executable, '-B', str(SCR / 'low_solve.py'), '--tag', 'base',
                         '--pairs', f'{h}:298', '--out', str(wit), '--report', f'/tmp/solve_single_{h}.json'],
                        capture_output=True, text=True)
    assert r1.returncode == 0, (h, r1.stdout[-500:], r1.stderr[-500:])
    r2 = subprocess.run([sys.executable, '-B', str(SCR / 'replay49.py'),
                         '--word', str(B / 'inputs/gauge44.canonical.json.gz'),
                         '--blocks', str(B / 'inputs/blocks.json'),
                         '--inventory', str(wit), '--recover-cold', '--output', str(rep)],
                        capture_output=True, text=True)
    assert r2.returncode == 0, (h, r2.stdout[-500:], r2.stderr[-500:])
    prof = {str(k): v for k, v in json.loads(rep.read_text())['local_profile'].items()}
    delta = {k: prof.get(k, 0) - P48.get(k, 0) for k in sorted(set(prof) | set(P48))}
    row = dict(helper=h, base=census[str(h)]['base'], profile=prof, delta={k: v for k, v in delta.items() if v},
               mass_delta=sum(int(k) * v for k, v in delta.items()),
               paid_moment_saving_per_call=m48 - fmom(prof))
    rows.append(row)
    print(h, 'base', row['base'], 'delta', row['delta'], 'mass', row['mass_delta'],
          f"saving {row['paid_moment_saving_per_call']:.6f}", flush=True)
rows.sort(key=lambda x: -x['paid_moment_saving_per_call'])
(OUT / 'LOW-SINGLES.json').write_text(json.dumps(
    dict(lender=298, word='base', p48=P48, m48=m48,
         idle_floor_cost_per_mass_unit=(48 / 73) ** (1 - A) / 48, rows=rows), indent=1) + '\n')
print('wrote LOW-SINGLES.json')
