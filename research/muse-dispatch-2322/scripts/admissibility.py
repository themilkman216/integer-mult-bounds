#!/usr/bin/env python3
"""Admissibility analysis for 665+1 / 666 dispatches on #2322.

This is a code-level analysis, NOT an executed strict replay of a
candidate data copy.  The priced result (scripts/screen.py) is a
zero gain for every dispatch, so the full #2322 cold_replay of a
665+1 candidate was not run (task step 2 is conditional on a
strict gain).  What is established here, from hash-pinned code:

 (A) The strict replay driver that #2322's delta_replay.py runs
     (a verbatim copy of the pinned #2312 runtime) binds BOTH
     providers unconditionally:
       replay.py: bind  --provider gauge44=... --provider extra=...
       code/bind_providers_portable.py: assert set(dirs)==set(PIDS)
       code/witness.py: PIDS = sorted(set(DISPATCH.values()));
                        assert set(PROVIDERS)==set(PIDS) in strict;
                        partner() asserts len(PIDS)>1.
     Hence a 666 all-extra (single-provider) dispatch fails at the
     bind stage of replay.py, in discovery and in strict mode,
     before assembly_controls' own single-provider branch
     (len(PIDS)==1 drops partner-only controls) is ever reached
     through this driver.  At least one gauge44 call must remain.

 (B) Which one?  Priced: any (H is invariant).  Partner controls
     in pinned code/assembly_controls.py construct mutants with
       wrong_selected_call: c = first call of provider P;
           d = next call != c with provider != P (or single-provider
               case) and (d.stage - c.stage) % 2 == 0
       moved: a = first call of P;
           b = next call with provider != P and same orientation.
     Orientation is forward iff stage is even (asserted per call in
     bind_providers_portable.py).  The first selected call overall
     is extra, stage 0, forward (data/PLAN.json order ==
     shipped invoice selected_calls order, checked in screen.py).
     If the sole retained gauge44 call were odd-stage/backward,
     the P=extra searches above would have no witness (next()
     raises StopIteration instead of producing a rejected mutant).
     Hence a sole retained gauge44 call must additionally be
     even-stage/forward for this checker to run as written:
     142 of the 249 shipped gauge44 calls qualify; the Track-3D
     choice (8,73) -- sorted-last shipped gauge44 key, stage 8,
     forward, time 665 -- is one of them, not a unique choice.

 (C) The pinned assembly_controls itself acknowledges the priced
     facts used by screen.py: stale_profile() has the branch
     "equal partner profiles (e.g. after a frame refit): the
     substitution would be the identity, so use a dishonest
     profile ..." and stale_program() the analogous
     "identical partner programs" branch.

Hash discipline: refs/upr/2312 (6a05b1bb) is a LATER head than the
fb76f799 pin in #2322.  Every #2312 file quoted here is used only
after its sha256 is verified equal to its entry in #2322's
UPSTREAM-2312.json.  Files whose later-head bytes differ from the
pin (audit_mixed.py, invoice_allcold.py, audit_allcold.py,
assemble.py, freeze_spec.py, independent_core.py, emit_allcold.py,
new/SPEC.json; rechecked below) are NOT quoted for pinned claims.

Writes ADMISSIBILITY.json.  Meta Muse (muse-wonder-full-1.0).
"""
import hashlib, json, subprocess, sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent
ROOT = OUT.parents[1]
PKG = ROOT / 'research/t74-joint-owner-hillclimb'
PREFIX = 'research/gmx-t74-borrow43-width-exchange/'
inv = {f['path']: f for f in json.loads((PKG / 'UPSTREAM-2312.json').read_text())['files']}
plan = json.loads((PKG / 'data/PLAN.json').read_text())


def pinned_text(rel):
    path = PREFIX + rel
    raw = subprocess.check_output(['git', 'show', f'refs/upr/2312:{path}'], cwd=ROOT)
    digest = hashlib.sha256(raw).hexdigest()
    ok = digest == inv[path]['sha256']
    return raw.decode('utf-8', 'replace'), digest, ok


QUOTED = ['replay.py', 'code/witness.py', 'code/bind_providers_portable.py',
          'code/assembly_controls.py', 'new/BORROW-PROVIDERS.json']
DIFFERING = ['audit_mixed.py', 'code/invoice_allcold.py', 'code/audit_allcold.py',
             'code/assemble.py', 'freeze_spec.py', 'independent_core.py',
             'code/emit_allcold.py', 'new/SPEC.json']
texts, hashes = {}, {}
for rel in QUOTED:
    texts[rel], hashes[rel], ok = pinned_text(rel)
    assert ok, f'quoted file no longer matches pinned inventory: {rel}'
differing_now = []
for rel in DIFFERING:
    _t, _d, ok = pinned_text(rel)
    if not ok:
        differing_now.append(rel)


def need(rel, needle):
    assert needle in texts[rel], (rel, needle)
    line = next(i + 1 for i, ln in enumerate(texts[rel].splitlines()) if needle in ln)
    return line


lines = {}
lines['replay_bind_both'] = need('replay.py', "'--provider','gauge44='+str(local),'--provider','extra='")
lines['replay_independent_both'] = need('replay.py', "run('independent',P/'audit_mixed.py'")
lines['bind_set_dirs_eq_pids'] = need('code/bind_providers_portable.py', 'assert set(dirs)==set(PIDS)')
lines['bind_orientation_law'] = need('code/bind_providers_portable.py',
                                     "'forward'if c['stage']%2==0 else'backward'")
lines['witness_pids'] = need('code/witness.py', 'PIDS=tuple(sorted(set(DISPATCH.values())))')
lines['witness_providers_eq_pids'] = need('code/witness.py',
                                          "assert DISCOVER or set(PROVIDERS)==set(PIDS)")
lines['witness_partner'] = need('code/witness.py', 'assert len(PIDS)>1')
lines['ac_single_provider_branch'] = need('code/assembly_controls.py', 'if len(PIDS)==1:')
lines['ac_equal_partner_profiles'] = need('code/assembly_controls.py',
                                          'equal partner profiles (e.g. after a frame refit)')
lines['ac_identical_partner_programs'] = need('code/assembly_controls.py',
                                              'identical partner programs')
lines['ac_wrong_selected_call'] = need('code/assembly_controls.py',
                                       "(d['stage'] - c['stage']) % 2 == 0")
lines['ac_moved'] = need('code/assembly_controls.py',
                         "c['provider_id'] != P and c['orientation'] == a['orientation']")

# #2322 delta_replay: verbatim PR2312 runtime copy (local workspace file).
delta = (PKG / 'delta_replay.py').read_text()
assert 'Use the exact PR2312 verifier runtime' in delta
assert "run('discovery',runtime/'replay.py'" in delta
assert "run('strict',runtime/'replay.py'" in delta

# Partner-control witness existence for every sole-retention candidate.
calls = plan['provider_calls']
assert [c['time'] for c in calls] == list(range(666))
first_extra = next(c for c in calls if c['provider'] == 'extra')

def sole_retention_ok(retain):
    """Mirror assembly_controls next() searches for dispatch with
    `retain` as the only gauge44 call (selected order := plan order,
    which screen.py checks equals the shipped invoice order)."""
    sel = [dict(stage=c['stage'], replica=c['replica'],
                provider_id=('gauge44' if (c['stage'], c['replica']) == retain else 'extra'),
                orientation=c['orientation']) for c in calls]
    reasons = []
    for P in ('extra', 'gauge44'):
        c0 = next((c for c in sel if c['provider_id'] == P), None)
        if c0 is None:
            return False, [f'no call of provider {P}']
        if not any(d is not c0 and d['provider_id'] != P
                   and (d['stage'] - c0['stage']) % 2 == 0 for d in sel):
            reasons.append(f'wrong_selected_call: no partner-stage-parity witness for P={P}')
        if not any(c['provider_id'] != P and c['orientation'] == c0['orientation']
                   for c in sel):
            reasons.append(f'moved: no same-orientation partner witness for P={P}')
    return not reasons, reasons


def bind_predicate(dispatch_values, bound_dirs=('extra', 'gauge44')):
    """Mirror bind_providers_portable: set(bound dirs) == set(PIDS)."""
    return set(dispatch_values) == set(bound_dirs)


gauge = [(c['stage'], c['replica']) for c in calls if c['provider'] == 'gauge44']
ok_keys, bad_keys = [], []
for k in gauge:
    ok, _r = sole_retention_ok(k)
    (ok_keys if ok else bad_keys).append(k)
assert bind_predicate(['extra'] * 666) is False          # 666 all-extra
assert bind_predicate(['extra'] * 665 + ['gauge44']) is True   # 665+1
assert bind_predicate([c['provider'] for c in calls]) is True  # shipped
ok873, r873 = sole_retention_ok((8, 73))
ok365, r365 = sole_retention_ok((3, 65))
assert ok873 and not ok365, (r873, r365)
assert all(k[0] % 2 == 0 for k in ok_keys) and all(k[0] % 2 == 1 for k in bad_keys)

res = {'status': 'PASS_ADMISSIBILITY_CODE_ANALYSIS_2322',
       'scope': ('Code-level analysis of hash-pinned #2312 runtime as used verbatim '
                 'by #2322 delta_replay.py. Not an executed strict replay of a '
                 'candidate package (screen is zero-gain; task step 2 conditional).'),
       'pinned_quoted_files_sha256_verified': hashes,
       'later_head_files_differing_from_pin_not_quoted': differing_now,
       'line_numbers_in_pinned_files': lines,
       'bind_predicate': {'shipped_417_249': True, 'extra665_gauge1': True,
                           'all_extra_666': False,
                           'rule': 'bind_providers_portable assert set(dirs)==set(PIDS), '
                                   'dirs hardcoded {gauge44,extra} by replay.py bind stage'},
       'sole_retention_partner_control_census': {
           'gauge_calls': len(gauge), 'even_stage_forward_ok': len(ok_keys),
           'odd_stage_backward_not_ok': len(bad_keys),
           'first_extra_call': {k: first_extra[k] for k in
                                ('stage', 'replica', 'time', 'orientation')},
           'retain_8_73_ok': ok873, 'retain_3_65_reasons': r365,
           'retain_8_73_is_unique': False},
       'verdict': ('665+1 with retained (8,73) satisfies the both-providers '
                   'bind/witness rules and the partner-control witness-existence '
                   'conditions mirrored here; 666 all-extra fails the bind rule in '
                   'the replay driver as written. Any admissibility beyond these '
                   'mirrored predicates (full discovery->freeze->strict->outer) '
                   'was not executed, because the dispatch is priced-identical: '
                   'its kappa would be exactly #2322 kappa.'),
       'python': sys.version.split()[0]}
(OUT / 'ADMISSIBILITY.json').write_text(json.dumps(res, indent=1) + '\n')
print(res['status'], 'ok sole retentions', len(ok_keys), 'of', len(gauge), flush=True)
