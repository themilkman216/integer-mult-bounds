#!/usr/bin/env python3
"""Exact stage-P single-alias measurements on the PR2312/#2322 lineage.

Stage P = build_word(canonical, blocks, witness) audited by audit_local.py
against the canonical word: the last pipeline stage that composes with a
changed witness (the later frame-refit patch is index-based and the
pivot-kernel patch replaces whole sections; neither re-derivation is
shipped).  Canonical words are byte-identical between PR2269 and PR2312
(sha256 checked in verify.py), so the vendored #2226 replay / builder /
auditor from the PR2269 tree (local ref refs/upr/2269) applies verbatim.

Variants (base word gauge44; witness = PR2312's shipped 42-pair witness):
  V0       control: witness unchanged; must reproduce PR2312's pinned audit
           (profile {1:2353,2:500,3:416,4:128,5:42,8:8}, widths
           {4:37,5:9,7:38,8:114,9:240}, restored_cold 78).
  V653     + helper 653 <- lender 73 (pair record from the prior round's
           witness_48_base; the alias PR2312 dropped).
  V606     + helper 606 <- lender 1 (width-5 high control, prior round 1).
  Vlow592  + low helper 592 <- lender 298 (prior round 2 record + its two
           initial corrections, operator words remapped 49 -> 43).
  Vlow624  + low helper 624 <- lender 378 (the rank-4/rank-1 singles class).

Each variant: adapted exact free-operator replay (only the pair-count
assertion changed, as in the prior round), build_word, independent
audit_local, borrow_controls.  G_columns for appended pairs are computed
with bw_gauss.change and cross-checked against the prior witnesses.
Supplier trees are extracted from local git refs into /tmp (read-only use;
nothing in the workspace outside this package is written).
Output: STAGEP-SINGLES.json + per-variant audit receipts under stagep/.
"""
import copy, json, subprocess, sys, time
from pathlib import Path

PKG = Path(__file__).resolve().parent.parent
WS = Path(__file__).resolve().parents[3]
WORK = Path('/tmp/muse-2322-stagep')
PRIOR = WS / 'research/prior-muse-t74-borrow-extend'

def extract(ref, sub, dest):
    if (dest / sub).exists():
        return
    dest.mkdir(parents=True, exist_ok=True)
    arc = subprocess.run(['git', '-C', str(WS), 'archive', ref, sub],
                         capture_output=True)
    assert arc.returncode == 0, arc.stderr.decode()[-500:]
    tar = subprocess.run(['tar', '-x', '-C', str(dest)], input=arc.stdout)
    assert tar.returncode == 0

extract('refs/upr/2269', 'research/gmx-t74-borrow43', Path('/tmp/pr2269src'))
extract('refs/upr/2312', 'research/gmx-t74-borrow43-width-exchange', Path('/tmp/pr2312src'))
B = Path('/tmp/pr2269src/research/gmx-t74-borrow43/new/borrow')
CODE = Path('/tmp/pr2269src/research/gmx-t74-borrow43/new/code/borrow')
W2312 = Path('/tmp/pr2312src/research/gmx-t74-borrow43-width-exchange/new/borrow/inputs/witness_43_base.json')
CANON = B / 'inputs/gauge44.canonical.json.gz'
sys.path.insert(0, str(CODE))
import bw_gauss  # noqa: E402

WORK.mkdir(parents=True, exist_ok=True)
(PKG / 'stagep').mkdir(exist_ok=True)

base_wit = json.loads(W2312.read_text())
w48 = json.loads((PRIOR / 'witness_48_base.json').read_text())
w80 = json.loads((PRIOR / 'witness_80_base.json').read_text())

def pair_of(w, reg):
    return next(p for p in w['pairs'] if p['register'] == reg)

def gauss_of(w, reg):
    op = next(i + 1 for i, p in enumerate(w['pairs']) if p['register'] == reg)
    return next(r for r in w['gaussian']['records'] if r['operator'] == op)

def extend(wit, pair, corrections=()):
    ext = copy.deepcopy(wit)
    op = len(ext['pairs']) + 1
    ext['pairs'] = ext['pairs'] + [copy.deepcopy(pair)]
    gcols = bw_gauss.change(pair['retirement_basis'], pair['handoff_basis'], 9)
    ext['gaussian']['records'] = ext['gaussian']['records'] + [dict(
        operator=op, G_columns=gcols,
        handoff_exact_monomial_sha256=None, full_exit_exact_monomial_sha256=None)]
    ext['gaussian']['operators'] = len(ext['gaussian']['records'])
    ext['initial_corrections'] = ext['initial_corrections'] + list(corrections)
    return ext, op, gcols

variants = {}
variants['V0'] = (copy.deepcopy(base_wit), 'PR2312 shipped 42-pair witness (control)')

p653 = pair_of(w48, 653)
v, op, g = extend(base_wit, p653)
assert g == gauss_of(w48, 653)['G_columns'], '653 G_columns cross-check failed'
v['variant'] = 'pr2312_plus_653'
variants['V653'] = (v, 'PR2312 + 653<-73')

p606 = pair_of(w48, 606)
v, op, g = extend(base_wit, p606)
assert g == gauss_of(w48, 606)['G_columns'], '606 G_columns cross-check failed'
v['variant'] = 'pr2312_plus_606'
variants['V606'] = (v, 'PR2312 + 606<-1 (width-5 high)')

for tag, reg, lender in [('Vlow592', 592, 298), ('Vlow624', 624, 378)]:
    p = pair_of(w80, reg)
    old_op = next(i + 1 for i, x in enumerate(w80['pairs']) if x['register'] == reg)
    corrs = []
    for c in w80['initial_corrections']:
        if c['source'] == lender:
            c2 = copy.deepcopy(c)
            assert c2['operator_word'] == [old_op], (tag, c2)
            corrs.append(c2)
    v, op, g = extend(base_wit, p, corrs)
    for c2 in v['initial_corrections']:
        if c2['source'] == lender:
            c2['operator_word'] = [op]
    assert g == gauss_of(w80, reg)['G_columns'], f'{tag} G_columns cross-check failed'
    assert len(corrs) == 2, (tag, corrs)
    v['variant'] = f'pr2312_plus_low{reg}'
    variants[tag] = (v, f'PR2312 + low {reg}<-{lender}')

replay_src = (CODE / 'vendor/pr2226_replay.py').read_text()
OLD_ASSERT = "assert len(pairs)==80 and sum(x['low'] for x in pairs)==32"
assert OLD_ASSERT in replay_src

def run(cmd, **kw):
    t = time.monotonic()
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    return r, time.monotonic() - t

results = {}
for tag, (wit, desc) in variants.items():
    npairs = len(wit['pairs']); nlow = sum(p['low'] for p in wit['pairs'])
    witp = WORK / f'witness_{tag}.json'
    witp.write_text(json.dumps(wit, indent=1) + '\n')
    rep_py = WORK / f'replay_{tag}.py'
    rep_py.write_text(replay_src.replace(
        OLD_ASSERT, f'assert len(pairs)=={npairs} and sum(x[\'low\'] for x in pairs)=={nlow}'))
    rep = WORK / f'replay_{tag}.json'
    r, dt = run([sys.executable, '-B', str(rep_py), '--word', str(CANON),
                 '--blocks', str(B / 'inputs/blocks.json'), '--inventory', str(witp),
                 '--recover-cold', '--output', str(rep)])
    res = dict(description=desc, pairs=npairs, low=nlow, replay_rc=r.returncode,
               replay_seconds=round(dt, 2), replay_tail=(r.stdout + r.stderr)[-400:])
    print(f'[{tag}] replay rc={r.returncode} {dt:.1f}s', flush=True)
    if r.returncode == 0:
        wit['replay'] = json.loads(rep.read_text())
        witp.write_text(json.dumps(wit, indent=1) + '\n')
        wordp = WORK / f'word_{tag}.json.gz'
        code = (f"import sys; sys.path.insert(0, r'{B}'); import build_word; "
                f"build_word.main(r'{CANON}', r'{B}/inputs/blocks.json', r'{witp}', r'{wordp}', 'eeb6a236')")
        r, dt = run([sys.executable, '-B', '-c', code], cwd=B)
        res.update(build_rc=r.returncode, build_seconds=round(dt, 2),
                   build_tail=(r.stdout + r.stderr)[-400:])
        print(f'[{tag}] build rc={r.returncode} {dt:.1f}s', flush=True)
    if res.get('build_rc') == 0:
        aud = PKG / 'stagep' / f'AUDIT-{tag}.json'
        r, dt = run([sys.executable, '-B', str(B / 'audit_local.py'), '--word',
                     str(WORK / f'word_{tag}.json.gz'), '--base', str(CANON),
                     '--output', str(aud)])
        res.update(audit_rc=r.returncode, audit_seconds=round(dt, 2),
                   audit_tail=(r.stdout + r.stderr)[-300:])
        if aud.exists():
            aj = json.loads(aud.read_text())
            res.update(audit_status=aj.get('status'), profile=aj.get('local_profile'),
                       mass=aj.get('local_mass'), widths=aj.get('width_inventory'),
                       removed=aj.get('removed_helpers'), warps=aj.get('warps'),
                       corrections=aj.get('corrections'),
                       restored_cold=aj.get('restored_cold'),
                       zero_buffers=aj.get('zero_buffers'))
        print(f'[{tag}] audit rc={r.returncode} profile={res.get("profile")} '
              f'widths={res.get("widths")}', flush=True)
        ctl = PKG / 'stagep' / f'CONTROLS-{tag}.json'
        r, dt = run([sys.executable, '-B', str(B / 'borrow_controls.py'),
                     str(WORK / f'word_{tag}.json.gz'), str(CANON), str(ctl)])
        res.update(controls_rc=r.returncode, controls_seconds=round(dt, 2),
                   controls_tail=(r.stdout + r.stderr)[-300:])
        print(f'[{tag}] controls rc={r.returncode} {dt:.1f}s', flush=True)
    results[tag] = res

def delta(a, b):
    keys = set(a) | set(b)
    return {k: a.get(k, 0) - b.get(k, 0) for k in sorted(keys, key=int)
            if a.get(k, 0) - b.get(k, 0)}

if 'V0' in results and results['V0'].get('profile'):
    for tag in results:
        if tag != 'V0' and results[tag].get('profile'):
            results[tag]['delta_profile_vs_V0'] = delta(
                {int(k): v for k, v in results[tag]['profile'].items()},
                {int(k): v for k, v in results['V0']['profile'].items()})
            results[tag]['delta_widths_vs_V0'] = delta(
                {int(k): v for k, v in results[tag]['widths'].items()},
                {int(k): v for k, v in results['V0']['widths'].items()})
            print(f'[{tag}] dProfile {results[tag]["delta_profile_vs_V0"]} '
                  f'dWidths {results[tag]["delta_widths_vs_V0"]} '
                  f'dMass {results[tag]["mass"] - results["V0"]["mass"]}')

out = dict(canonical='gauge44.canonical.json.gz (byte-identical PR2269/PR2312 inputs)',
           base_witness='PR2312 new/borrow/inputs/witness_43_base.json (42 pairs)',
           stage='P: adapted pr2226 replay + build_word + audit_local --base canonical + borrow_controls',
           results=results)
(PKG / 'STAGEP-SINGLES.json').write_text(json.dumps(out, indent=1) + '\n')
print('wrote STAGEP-SINGLES.json')
