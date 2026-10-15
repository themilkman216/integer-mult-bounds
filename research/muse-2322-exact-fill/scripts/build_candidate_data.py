#!/usr/bin/env python3
"""Build candidate data/ for #2322's delta/cold replay from CANDIDATE-OWNERS.

Copies #2322's data directory, substitutes the candidate owner map, and
updates exactly the fields that bind it: PLAN.profile,
PLAN.assignment_sha256 (gz bytes), PLAN.assignment_content_sha256
(canonical sorted-rows JSON), PROFILE.json and CONSTRUCTION.idle.
Serialization matches the shipped files (json indent=2 + newline).
SPEC.json is copied unchanged: delta_replay strips and re-freezes it.
Writes OUT/work/candidate-data/ and validates it with #2322's
owners_check in-process first.
"""
import gzip, hashlib, json, shutil, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from model2322 import load_all, OUT, PKG, rd

base = load_all()
cand_rows = rd(OUT / 'CANDIDATE-OWNERS.json.gz')
# #2322's own checker on the candidate rows against the *candidate* plan below;
# windows/order/providers are unchanged, so check against shipped plan here.
H, idle = base['verify'].owners_check(cand_rows, base['plan'], base['contract'])

out = OUT / 'work/candidate-data'
if out.exists():
    shutil.rmtree(out)
shutil.copytree(PKG / 'data', out)
cand_gz = (OUT / 'CANDIDATE-OWNERS.json.gz').read_bytes()
(out / 'OWNERS.json.gz').write_bytes(cand_gz)

def wjson(path, obj):
    path.write_text(json.dumps(obj, indent=2) + '\n')

plan = rd(out / 'PLAN.json')
plan['profile'] = {str(k): v for k, v in sorted(H.items())}
plan['assignment_sha256'] = hashlib.sha256(cand_gz).hexdigest()
canon = json.dumps(cand_rows, sort_keys=True, separators=(',', ':')).encode()
plan['assignment_content_sha256'] = hashlib.sha256(canon).hexdigest()
wjson(out / 'PLAN.json', plan)
wjson(out / 'PROFILE.json', {str(k): v for k, v in sorted(H.items())})
cons = rd(out / 'CONSTRUCTION.json')
cons['idle'] = {str(k): v for k, v in sorted(idle.items())}
wjson(out / 'CONSTRUCTION.json', cons)

# recheck against the candidate plan bytes
plan2 = rd(out / 'PLAN.json')
assert plan2['windows'] == base['plan']['windows'] and plan2['order'] == base['plan']['order']
H2, idle2 = base['verify'].owners_check(cand_rows, plan2, base['contract'])
assert dict(H2) == dict(H) and dict(idle2) == dict(idle)
print('candidate data written to', out)
print('H', dict(sorted(H.items())))
print('idle', dict(sorted(idle.items())))
print('owners gz sha256', plan['assignment_sha256'])
