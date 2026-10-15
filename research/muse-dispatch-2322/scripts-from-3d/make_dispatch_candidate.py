#!/usr/bin/env python3
"""Build all-extra dispatch candidate fills (rows unchanged from shipped/adapted
fills; only dispatch_overrides set every call to provider 'extra') and verify
each with the LITERAL reconstruct checker (patched copy of #2269's
reconstruct.py / round-3C reconstruct48.py pointing at the candidate fill).
Widths are identical across providers, so bin packing is unchanged; only the
aggregate paid profile (hence H) changes.  Writes
FILL43-ALLEXtra.json.gz, FILL48-ALLEXtra.json.gz, DISPATCH-CANDIDATE.json.
Strict-assembly admissibility of all-extra dispatch is NOT checked here."""
import gzip, json, subprocess, sys, tempfile
from collections import Counter
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from model import load_base, load_case, check_rows, OUT, PKG, ROOT

base = load_base()
res = {}
tmp = Path(tempfile.mkdtemp(prefix='muse-dispatch-'))
for which in ('43', '48'):
    case = load_case(base, which)
    overrides = [[s, r, 'extra'] for (s, r), pid in sorted(base['dispatch0'].items()) if pid != 'extra']
    cand_fill = dict(columns=case['fill']['columns'], rows=case['fill']['rows'],
                     dispatch_overrides=overrides)
    p = OUT / f'FILL{which}-ALLEXtra.json.gz'
    p.write_bytes(gzip.compress(json.dumps(cand_fill, separators=(',', ':')).encode(), mtime=0))
    # literal checker via patched reconstruct copy
    if which == '43':
        src = (PKG / 'reconstruct.py').read_text()
        src = src.replace("F=Path(__file__).resolve().parent", f"F=Path('{PKG}')")
        src = src.replace("fill=read(F/'new/borrow-fill/FILL.json.gz')",
                          f"fill=read(Path('{p}'))")
    else:
        src = (ROOT / 'research/muse-t74-borrow-extend/scripts/reconstruct48.py').read_text()
        src = src.replace("research/muse-t74-borrow-extend/FILL48.json.gz", str(p))
    script = tmp / f'reconstruct-{which}.py'
    script.write_text(src)
    outdir = tmp / f'owners-{which}'
    r = subprocess.run([sys.executable, '-B', str(script), '--out', str(outdir)],
                       capture_output=True, text=True, cwd=ROOT)
    ok = r.returncode == 0 and 'PASS_OWNER_VERIFY' in r.stdout
    prof = json.loads((outdir / 'PROFILE.json').read_text()) if ok else None
    print(which, 'overrides', len(overrides), 'literal checker', 'PASS' if ok else 'FAIL',
          (r.stdout + r.stderr)[-500:] if not ok else prof)
    assert ok
    res[which] = dict(overrides=len(overrides), checker='PASS_OWNER_VERIFY',
                      profile={str(k): v for k, v in prof.items()},
                      idle=json.loads((outdir / 'RESULT.json').read_text())['idle'])
(OUT / 'DISPATCH-CANDIDATE.json').write_text(json.dumps(res, indent=1) + '\n')
print('wrote candidates')
