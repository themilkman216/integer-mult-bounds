#!/usr/bin/env python3
"""Build the 665-extra + 1-gauge44 dispatch candidate and a candidate package
copy for strict replay.  All-extra (666) is inadmissible under the shipped
checkers: audit_mixed.py requires set(dispatch.values()) == set(bound
provider dirs) = {gauge44, extra}, and audit_allcold.py calls witness.partner()
which asserts >=2 providers in dispatch.  Keeping exactly one gauge44 call
retains both providers in dispatch while realising 248/249 of the exact paid
gain.  Steps: candidate fill -> literal reconstruct -> lift_parent -> package
copy overwrite -> rebind (with fresh natives in work/).  Writes
FILL43-EXTRAm1.json.gz, DISPATCH-CANDIDATE2.json; package copy at work/pkg,
rebound data at work/data-rebound.  Originals are never edited."""
import gzip, json, shutil, subprocess, sys
from collections import Counter
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from model import load_base, load_case, check_rows, OUT, PKG, ROOT

base = load_base(); case = load_case(base, '43')
W = OUT / 'work'; W.mkdir(exist_ok=True)
gauge_keys = sorted(k for k, pid in base['dispatch0'].items() if pid == 'gauge44')
retain = gauge_keys[-1]
overrides = [[s, r, 'extra'] for (s, r) in gauge_keys if (s, r) != retain]
cand_fill = dict(columns=case['fill']['columns'], rows=case['fill']['rows'],
                 dispatch_overrides=overrides)
p = OUT / 'FILL43-EXTRAm1.json.gz'
p.write_bytes(gzip.compress(json.dumps(cand_fill, separators=(',', ':')).encode(), mtime=0))
print('retain gauge call', retain, 'overrides', len(overrides))
# literal check via model
case_c = dict(case); disp = dict(base['dispatch0'])
for s_, r_, p_ in overrides: disp[s_, r_] = p_
case_c['dispatch'] = disp
idle, H = check_rows(base, case_c, cand_fill['rows'])
print('candidate H', dict(sorted(H.items())), 'dispatch', Counter(disp.values()))
# patched reconstruct + lift
tmp = W / 'build-tmp'; shutil.rmtree(tmp, ignore_errors=True); tmp.mkdir(parents=True)
src = (PKG / 'reconstruct.py').read_text()
src = src.replace("F=Path(__file__).resolve().parent", f"F=Path('{PKG}')")
src = src.replace("fill=read(F/'new/borrow-fill/FILL.json.gz')", f"fill=read(Path('{p}'))")
(tmp / 'reconstruct.py').write_text(src)
owners = W / 'cand-owners'; shutil.rmtree(owners, ignore_errors=True)
r = subprocess.run([sys.executable, '-B', str(tmp / 'reconstruct.py'), '--out', str(owners)],
                   capture_output=True, text=True, cwd=ROOT)
assert r.returncode == 0 and 'PASS_OWNER_VERIFY' in r.stdout, r.stdout + r.stderr
print('reconstruct PASS')
parent_out = W / 'cand-parent'; shutil.rmtree(parent_out, ignore_errors=True)
r = subprocess.run([sys.executable, '-B', str(PKG / 'lift_parent.py'), '--owners', str(owners),
                    '--out', str(parent_out)], capture_output=True, text=True, cwd=ROOT)
assert r.returncode == 0, r.stdout + r.stderr
print('lift PASS', r.stdout.strip()[-200:])
# package copy
pkg = W / 'pkg'; shutil.rmtree(pkg, ignore_errors=True)
shutil.copytree(PKG, pkg, ignore=shutil.ignore_patterns('__pycache__'))
shutil.copy2(p, pkg / 'new/borrow-fill/FILL.json.gz')
for n in ('OWNERS.json.gz', 'ORDER.json', 'DISPATCH.json', 'PROFILE.json'):
    shutil.copy2(owners / n, pkg / n)
for n in ('GLOBAL-TEMPLATE.json.gz', 'PLAN.json', 'CONSTRUCTION.json'):
    shutil.copy2(parent_out / n, pkg / n)
# candidate dispatch into new/SPEC base (rebind reads it; discovery will refreeze expected)
def rd(q):
    b = Path(q).read_bytes(); return json.loads(gzip.decompress(b) if str(q).endswith('.gz') else b)
spec = rd(pkg / 'new/SPEC.json')
spec['dispatch'] = rd(owners / 'DISPATCH.json')
spec['call_order'] = rd(owners / 'ORDER.json')
(pkg / 'new/SPEC.json').write_text(json.dumps(spec, indent=2) + '\n')
print('pkg copy ready; spec dispatch counts', Counter(x[2] for x in spec['dispatch']))
# rebind with fresh natives
reb = W / 'data-rebound'; shutil.rmtree(reb, ignore_errors=True)
r = subprocess.run([sys.executable, '-B', str(pkg / 'new/rebind.py'), str(pkg),
                    str(W / 'native-base/local'), str(W / 'native-extra/local'), str(reb)],
                   capture_output=True, text=True, cwd=ROOT)
print('rebind rc', r.returncode, (r.stdout + r.stderr)[-800:])
assert r.returncode == 0
shutil.copy2(reb / 'PLAN.json', pkg / 'new/PLAN.json')
shutil.copy2(reb / 'PROFILE.json', pkg / 'new/PROFILE.json')
shutil.copy2(reb / 'SPEC.json', pkg / 'new/SPEC.json')
plan = rd(pkg / 'new/PLAN.json')
print('rebound provider counts', Counter(c['provider'] for c in plan['provider_calls']),
      'profile', plan['profile'])
rep = dict(retain_gauge_call=list(retain), overrides=len(overrides),
           H={str(k): v for k, v in sorted(H.items())},
           idle={str(k): v for k, v in sorted(idle.items())},
           checker='PASS_OWNER_VERIFY + lift PASS + rebind PASS')
(OUT / 'DISPATCH-CANDIDATE2.json').write_text(json.dumps(rep, indent=1) + '\n')
print('done')
