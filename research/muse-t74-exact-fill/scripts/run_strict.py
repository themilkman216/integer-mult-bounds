#!/usr/bin/env python3
"""Run #2269's strict T74 replay (replay.py) on the candidate package copy,
mirroring verify.py lines 50-56 (layout extraction) and 118-126 (runtime
assembly).  Usage: run_strict.py discover|strict WORKNAME
Layout is extracted once to work/parent/layout from the shipped
upstream-layout.tar.gz (hash-pinned by the retained manifest; parent
admission itself is NOT rerun here -- see README)."""
import os, shutil, subprocess, sys, tarfile
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent
ROOT = OUT.parents[1]
W = OUT / 'work'; pkg = W / 'pkg'
mode, wname = sys.argv[1], sys.argv[2]
lay = W / 'parent' / 'layout'
if not lay.exists():
    lay.mkdir(parents=True)
    with tarfile.open(pkg / 'vendor/pr1297/upstream-layout.tar.gz') as t:
        for m in t.getmembers():
            assert m.isfile() and not Path(m.name).is_absolute() and '..' not in Path(m.name).parts
        t.extractall(lay, filter='data')
    print('layout extracted')
runtime = lay / 'packing74'
if runtime.exists():
    shutil.rmtree(runtime)
runtime.mkdir()
data = runtime / 'candidate'; data.mkdir()
for n in ('replay.py', 'freeze_spec.py', 'audit_mixed.py', 'independent_core.py', 'geometry_controls.py', 'audit_fast.py'):
    shutil.copy2(pkg / n, runtime / n)
for n in ('code', 'construction'):
    shutil.copytree(pkg / n, runtime / n)
(runtime / 'inputs').mkdir()
shutil.copy2(pkg / 'inputs/PR589-EXPECTED.json', runtime / 'inputs/PR589-EXPECTED.json')
for n in ('PLAN.json', 'SPEC.json', 'PROFILE.json', 'OWNERS.json.gz', 'DISPATCH.json', 'CONSTRUCTION.json', 'GLOBAL-TEMPLATE.json.gz'):
    shutil.copy2((pkg / 'new' if n in ('PLAN.json', 'SPEC.json', 'PROFILE.json') else pkg) / n, data / n)
shutil.copytree(W / 'native-extra', runtime / 'native-extra')
work = W / wname
assert not work.exists()
env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1', PYTHONINTMAXSTRDIGITS='0',
           AUDIT_FAST_SHARDS='4', FINE_ENGINE_CACHE=str(W / 'fine-cache'), TMPDIR=str(W))
for k in ('PYTHONOPTIMIZE', 'WITNESS_DISCOVER', 'WITNESS_RECORD', 'WITNESS_SPEC'):
    env.pop(k, None)
cmd = [sys.executable, '-B', str(runtime / 'replay.py'), '--data', str(data), '--work', str(work),
       '--local', str(W / 'native-base/local')]
if mode == 'discover':
    cmd.append('--discover')
print('running', ' '.join(cmd), flush=True)
r = subprocess.run(cmd, env=env)
print('replay rc', r.returncode)
sys.exit(r.returncode)
