#!/usr/bin/env python3
"""Decisive test + build for the 48-alias extension.

1. Adapted exact free-operator replay (copy of the vendored pr2226_replay.py
   with only the pair-count assertion changed 80/32 -> 48/0; original kept
   untouched in research/gmx-t74-borrow43). If the joint 48 replay fails,
   fall back to one-new-pair-at-a-time replays to localise the obstruction.
2. On success: embed fresh replay into witness_48_*.json, build BORROW-WORDs
   with #2269's build_word.py, audit with its audit_local.py and negative
   controls (borrow_controls.py). All outputs land in this package.
"""
import json, subprocess, sys, time
from pathlib import Path

ROOT = Path.cwd()
B = ROOT / 'research/gmx-t74-borrow43/new/borrow'
OUT = ROOT / 'research/muse-t74-borrow-extend'
SCR = OUT / 'scripts'

src = (ROOT / 'research/gmx-t74-borrow43/new/code/borrow/vendor/pr2226_replay.py').read_text()
old = 'assert len(pairs)==80 and sum(x[\'low\'] for x in pairs)==32'
assert old in src
(SCR / 'replay48.py').write_text(src.replace(old, 'assert len(pairs)==48 and sum(x[\'low\'] for x in pairs)==0'))

def run(cmd, **kw):
    t = time.monotonic()
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    return r, time.monotonic() - t

def replay(canon, wit_path, out_path):
    return run([sys.executable, '-B', str(SCR / 'replay48.py'),
                '--word', str(B / 'inputs' / canon), '--blocks', str(B / 'inputs/blocks.json'),
                '--inventory', str(wit_path), '--recover-cold', '--output', str(out_path)])

results = {}
for canon, tag, base_name in [('gauge44.canonical.json.gz', 'base', 'eeb6a236'),
                              ('extra.canonical.json.gz', 'extra', 'cd417b90')]:
    witp = OUT / f'witness_48_{tag}.json'
    rep = OUT / f'REPLAY48-{tag}.json'
    r, dt = replay(canon, witp, rep)
    print(f'[{tag}] joint-48 replay rc={r.returncode} in {dt:.1f}s')
    print((r.stdout + r.stderr)[-1200:])
    results[tag] = dict(joint_rc=r.returncode, joint_seconds=dt)
    if r.returncode != 0:
        # localise: one new pair at a time on top of witness_43
        wit43 = json.loads((B / 'inputs' / f'witness_43_{tag}.json').read_text())
        wit48 = json.loads(witp.read_text())
        singles = {}
        for p in wit48['pairs'][43:]:
            w1 = json.loads(json.dumps(wit43)); w1['pairs'] = wit43['pairs'] + [p]
            # replay48 asserts 48 pairs; make a 44-variant on the fly
            (SCR / 'replay44.py').write_text(src.replace(old, 'assert len(pairs)==44 and sum(x[\'low\'] for x in pairs)==0'))
            tmp = OUT / f'witness_44_{tag}_{p["register"]}.json'
            tmp.write_text(json.dumps(w1))
            r1, dt1 = run([sys.executable, '-B', str(SCR / 'replay44.py'),
                           '--word', str(B / 'inputs' / canon), '--blocks', str(B / 'inputs/blocks.json'),
                           '--inventory', str(tmp), '--recover-cold',
                           '--output', str(OUT / f'REPLAY44-{tag}-{p["register"]}.json')])
            tail = (r1.stdout + r1.stderr).strip().splitlines()
            singles[p['register']] = dict(rc=r1.returncode, seconds=dt1,
                                          last=tail[-1][-300:] if tail else '')
            print(f'  single {p["register"]}<-{p["borrow_from"]} rc={r1.returncode} {singles[p["register"]]["last"]}')
        results[tag]['singles'] = singles
        continue
    # embed fresh replay and build the word
    wit = json.loads(witp.read_text()); wit['replay'] = json.loads(rep.read_text())
    witp.write_text(json.dumps(wit, indent=1) + '\n')
    (OUT / 'words').mkdir(exist_ok=True)
    wordp = OUT / 'words' / f'BORROW-WORD-48{tag}.json.gz'
    code = (f"import sys; sys.path.insert(0, r'{B}'); import build_word; "
            f"build_word.main(r'{B}/inputs/{canon}', r'{B}/inputs/blocks.json', r'{witp}', r'{wordp}', '{base_name}')")
    r2, dt2 = run([sys.executable, '-B', '-c', code], cwd=B)
    print(f'[{tag}] build_word rc={r2.returncode} in {dt2:.1f}s\n{(r2.stdout + r2.stderr)[-800:]}')
    results[tag]['build_rc'] = r2.returncode; results[tag]['build_seconds'] = dt2
    if r2.returncode: continue
    aud = OUT / f'AUDIT-48{tag}.json'
    r3, dt3 = run([sys.executable, '-B', str(B / 'audit_local.py'), '--word', str(wordp),
                   '--base', str(B / 'inputs' / canon), '--output', str(aud)])
    print(f'[{tag}] audit rc={r3.returncode} in {dt3:.1f}s\n{(r3.stdout + r3.stderr)[-800:]}')
    results[tag]['audit_rc'] = r3.returncode; results[tag]['audit_seconds'] = dt3
    ctl = OUT / f'CONTROLS-48{tag}.json'
    r4, dt4 = run([sys.executable, '-B', str(B / 'borrow_controls.py'), str(wordp),
                   str(B / 'inputs' / canon), str(ctl)])
    print(f'[{tag}] controls rc={r4.returncode} in {dt4:.1f}s\n{(r4.stdout + r4.stderr)[-800:]}')
    results[tag]['controls_rc'] = r4.returncode; results[tag]['controls_seconds'] = dt4
    if aud.exists():
        a = json.loads(aud.read_text())
        results[tag]['audit_profile'] = a.get('local_profile')
        results[tag]['audit_mass'] = a.get('local_mass')
        results[tag]['audit_status'] = a.get('status')

(OUT / 'BUILD48.json').write_text(json.dumps(results, indent=1) + '\n')
ok = all(v.get('audit_rc') == 0 and v.get('controls_rc') == 0 for v in results.values())
print('PASS_BUILD48' if ok else 'FAIL_OR_PARTIAL_BUILD48')
