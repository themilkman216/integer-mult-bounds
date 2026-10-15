#!/usr/bin/env python3
"""End-to-end build for a low-extended witness (round 2), generalising build48.py.

1. Exact free-operator replay (vendored pr2226_replay.py with only the
   pair-count assertion changed to this witness's counts; original untouched).
2. Embed the fresh replay into the witness, build the BORROW-WORD with
   #2269's build_word.py, audit with audit_local.py (independent), and run
   borrow_controls.py negative controls.  Outputs land in this package.

Usage (workspace root):
  python3 -B .../scripts/build_low.py --tag base \
      --witness witness_49_base.json --stem 49base --word BORROW-WORD-49base.json.gz
Receipts: REPLAY<stem>.json, AUDIT-<stem>.json, CONTROLS-<stem>.json,
BUILD-<stem>.json in the package dir; word under words/.
"""
import argparse, json, subprocess, sys, time
from pathlib import Path

ROOT = Path.cwd()
B = ROOT / 'research/gmx-t74-borrow43/new/borrow'
OUT = ROOT / 'research/muse-t74-borrow-extend'
SCR = OUT / 'scripts'
CANON = {'base': ('gauge44.canonical.json.gz', 'eeb6a236'),
         'extra': ('extra.canonical.json.gz', 'cd417b90')}

def run(cmd, **kw):
    t = time.monotonic()
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    return r, time.monotonic() - t

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--tag', required=True, choices=['base', 'extra'])
    ap.add_argument('--witness', required=True)
    ap.add_argument('--stem', required=True, help='e.g. 49base or 80base')
    ap.add_argument('--word', required=True)
    a = ap.parse_args()
    canon, base_name = CANON[a.tag]
    witp = OUT / a.witness
    wit = json.loads(witp.read_text())
    npairs = len(wit['pairs']); nlow = sum(p['low'] for p in wit['pairs'])
    src = (ROOT / 'research/gmx-t74-borrow43/new/code/borrow/vendor/pr2226_replay.py').read_text()
    old = "assert len(pairs)==80 and sum(x['low'] for x in pairs)==32"
    assert old in src
    (SCR / 'replay_low.py').write_text(
        src.replace(old, f'assert len(pairs)=={npairs} and sum(x[\'low\'] for x in pairs)=={nlow}'))
    res = dict(tag=a.tag, witness=a.witness, pairs=npairs, low=nlow)
    rep = OUT / f'REPLAY{a.stem}.json'
    r, dt = run([sys.executable, '-B', str(SCR / 'replay_low.py'),
                 '--word', str(B / 'inputs' / canon), '--blocks', str(B / 'inputs/blocks.json'),
                 '--inventory', str(witp), '--recover-cold', '--output', str(rep)])
    print(f'replay rc={r.returncode} {dt:.1f}s\n{(r.stdout + r.stderr)[-1500:]}')
    res.update(replay_rc=r.returncode, replay_seconds=dt)
    if r.returncode:
        (OUT / f'BUILD-{a.stem}.json').write_text(json.dumps(res, indent=1) + '\n')
        return 1
    wit['replay'] = json.loads(rep.read_text())
    witp.write_text(json.dumps(wit, indent=1) + '\n')
    wordp = OUT / 'words' / a.word
    code = (f"import sys; sys.path.insert(0, r'{B}'); import build_word; "
            f"build_word.main(r'{B}/inputs/{canon}', r'{B}/inputs/blocks.json', r'{witp}', r'{wordp}', '{base_name}')")
    r, dt = run([sys.executable, '-B', '-c', code], cwd=B)
    print(f'build_word rc={r.returncode} {dt:.1f}s\n{(r.stdout + r.stderr)[-1500:]}')
    res.update(build_rc=r.returncode, build_seconds=dt)
    if r.returncode:
        (OUT / f'BUILD-{a.stem}.json').write_text(json.dumps(res, indent=1) + '\n')
        return 1
    aud = OUT / f'AUDIT-{a.stem}.json'
    r, dt = run([sys.executable, '-B', str(B / 'audit_local.py'), '--word', str(wordp),
                 '--base', str(B / 'inputs' / canon), '--output', str(aud)])
    print(f'audit rc={r.returncode} {dt:.1f}s\n{(r.stdout + r.stderr)[-1200:]}')
    res.update(audit_rc=r.returncode, audit_seconds=dt)
    if aud.exists():
        aj = json.loads(aud.read_text())
        res.update(audit_profile=aj.get('local_profile'), audit_mass=aj.get('local_mass'),
                   audit_widths=aj.get('width_inventory'), audit_status=aj.get('status'),
                   corrections=aj.get('corrections'), restored_cold=aj.get('restored_cold'))
    ctl = OUT / f'CONTROLS-{a.stem}.json'
    r, dt = run([sys.executable, '-B', str(B / 'borrow_controls.py'), str(wordp),
                 str(B / 'inputs' / canon), str(ctl)])
    print(f'controls rc={r.returncode} {dt:.1f}s\n{(r.stdout + r.stderr)[-1200:]}')
    res.update(controls_rc=r.returncode, controls_seconds=dt)
    (OUT / f'BUILD-{a.stem}.json').write_text(json.dumps(res, indent=1) + '\n')
    ok = res.get('audit_rc') == 0 and res.get('controls_rc') == 0
    print('PASS_BUILD_LOW' if ok else 'FAIL_BUILD_LOW')
    return 0 if ok else 1

if __name__ == '__main__': sys.exit(main())
