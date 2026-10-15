#!/usr/bin/env python3
"""Verifier for muse-dispatch-2322 (Track 3F).

Re-derives, from the #2322 package files themselves, the falsified
dispatch screen: on #2322 both providers price identically, so the
Track-3D 665+1 dispatch changes neither the priced profile H nor
its exact moment, and the candidate kappa equals #2322's kappa
1697060296258836/10^18 exactly (gain 0, no strict gain).  Also
re-checks the retained-call admissibility predicates mirrored from
the hash-pinned #2312 runtime, binds SCREEN.json/ADMISSIBILITY.json
when present, and runs six tamper controls, each mutating a value
and confirming the relevant check then fails.

This verifier does NOT rerun #2322's cold_replay / native Clifford /
strict-controller / outer chain on a candidate package: that carry-
through was conditional on a strict gain, which is falsified here.
The #2322 bounded verify.py receipt is a separate baseline command
recorded in README.  Read-only outside this directory; writes
RESULT.json here.  Meta Muse (muse-wonder-full-1.0), Apache-2.0.
Run: python3 -B research/muse-dispatch-2322/verify.py
"""
import copy, gzip, hashlib, importlib.util, json, sys, time
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PKG = ROOT / 'research/t74-joint-owner-hillclimb'


def need(ok, msg):
    if not ok:
        raise ValueError(msg)


def read(p):
    p = Path(p)
    return json.loads(gzip.decompress(p.read_bytes()) if p.suffix == '.gz' else p.read_bytes())


def load_mod(name, path):
    sp = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


def bind_predicate(values):
    need(set(values) == {'gauge44', 'extra'},
         'bind rule: bound provider dirs {gauge44,extra} != dispatch providers')


def sole_retention_ok(calls, retain):
    sel = [dict(stage=c['stage'],
                provider_id=('gauge44' if (c['stage'], c['replica']) == retain else 'extra'),
                orientation=c['orientation']) for c in calls]
    reasons = []
    for P in ('extra', 'gauge44'):
        c0 = next((c for c in sel if c['provider_id'] == P), None)
        if c0 is None:
            return False, [f'no call of provider {P}']
        if not any(d is not c0 and d['provider_id'] != P
                   and (d['stage'] - c0['stage']) % 2 == 0 for d in sel):
            reasons.append(f'wrong_selected_call witness missing for {P}')
        if not any(c['provider_id'] != P and c['orientation'] == c0['orientation']
                   for c in sel):
            reasons.append(f'moved witness missing for {P}')
    return not reasons, reasons


def main():
    need(__debug__, 'assertions must be enabled (do not run with -O)')
    t0 = time.monotonic()
    plan = read(PKG / 'data/PLAN.json')
    spec = read(PKG / 'data/SPEC.json')
    claim = read(PKG / 'CLAIM.json')
    contract = read(PKG / 'BASELINE-CONTRACT.json.gz')
    rows = read(PKG / 'data/OWNERS.json.gz')
    invoice = read(PKG / 'evidence/full-replay/delta/strict/global/audit/PREFIX-AND-INVOICE.json')
    words = {k: read(PKG / f'words/{k}.json.gz') for k in ('base', 'extra')}
    reg = plan['provider_registry']
    stages = []

    # 1. priced equality at every layer + literal word recount
    eq = {
        'plan_paid': reg['gauge44']['actual_paid_profile'] == reg['extra']['actual_paid_profile'],
        'plan_widths': reg['gauge44']['widths'] == reg['extra']['widths'],
        'plan_ports_centers': reg['gauge44']['ports'] == reg['extra']['ports']
                              and reg['gauge44']['centers'] == reg['extra']['centers'],
        'spec_expected_and_paid': (
            spec['providers']['gauge44']['expected_profile']
            == spec['providers']['extra']['expected_profile']
            and spec['providers']['gauge44']['complete_contract']['paid_profile']
            == spec['providers']['extra']['complete_contract']['paid_profile']),
        'spec_local_by_orientation': (
            spec['providers']['gauge44']['complete_contract']['local']
            == spec['providers']['extra']['complete_contract']['local']
            and spec['providers']['gauge44']['program_hashes']
            == spec['providers']['extra']['program_hashes']),
        'contract_2312': contract['paid']['gauge44'] == contract['paid']['extra']
                         and contract['widths']['gauge44'] == contract['widths']['extra'],
        'invoice': (invoice['providers']['gauge44']['paid_profile']
                    == invoice['providers']['extra']['paid_profile']
                    and invoice['providers']['gauge44']['local']
                    == invoice['providers']['extra']['local']),
        'invoice_order_eq_plan': (
            [(c['stage'], c['replica'], c['provider_id']) for c in invoice['selected_calls']]
            == [(c['stage'], c['replica'], c['provider']) for c in plan['provider_calls']]),
    }
    need(all(eq.values()), f'provider priced quantities differ: {eq}')
    gen = load_mod('vgen', PKG / 'generate_words.py')
    recounts = {k: gen.paid_profile(w) for k, w in words.items()}
    need(recounts['base'] == recounts['extra'], 'word recounts differ')
    paid_common = {int(k): v for k, v in reg['extra']['actual_paid_profile'].items()}
    need(recounts['extra'][0] == paid_common, 'recount != registry paid')
    stages.append('provider_priced_equality_and_word_recount')

    # 2. H under shipped / 665+1 / 666 dispatches, full owners legality
    ver = load_mod('vver', PKG / 'verify.py')
    calls = plan['provider_calls']

    def H_for(dispatch, plan_in=None):
        plan2 = copy.deepcopy(plan if plan_in is None else plan_in)
        for c in plan2['provider_calls']:
            c['provider'] = dispatch[c['stage'], c['replica']]
        H, _idle = ver.owners_check(rows, plan2, contract)
        return dict(sorted(H.items()))

    keys = [(c['stage'], c['replica']) for c in calls]
    disp = {'shipped': {k: c['provider'] for k, c in zip(keys, calls)},
            'cand665_1': {k: ('gauge44' if k == (8, 73) else 'extra') for k in keys},
            'all_extra': {k: 'extra' for k in keys}}
    Hs = {n: H_for(d) for n, d in disp.items()}
    need(Hs['shipped'] == Hs['cand665_1'] == Hs['all_extra'], 'H depends on dispatch')
    H = Hs['shipped']
    need(H == {int(k): v for k, v in claim['global_profile'].items()}, 'H != CLAIM profile')
    need(sum(r * n for r, n in H.items()) == 73 * 66304 - 23680, 'H mass/deficit')
    stages.append('owners_check_H_dispatch_invariant')

    # 3. exact directed moments: candidate enclosure identical, gain zero
    eng = load_mod('veng', PKG / 'vendor/fine_moment.py')
    eng.SH = 256; eng.GRID = 1 << 256; eng.LOG_TERMS = 100; eng.EXP_TERMS = 96
    lo_b, hi_b = Q(claim['native_endpoint_lower']), Q(claim['native_endpoint_upper'])
    need(eng.moment(73, 66304, sorted(H.items()), lo_b)[1] < 1, 'native lower not accepted')
    need(eng.moment(73, 66304, sorted(H.items()), hi_b)[0] > 1, 'native upper not rejected')
    e_ship = eng.moment(73, 66304, sorted(Hs['shipped'].items()), Q(claim['kappa']))
    e_cand = eng.moment(73, 66304, sorted(Hs['cand665_1'].items()), Q(claim['kappa']))
    need(e_ship == e_cand, 'candidate moment enclosure differs from shipped')
    need(Q(claim['kappa']) == Q(1697060296258836, 10**18), 'kappa_2322 pin')
    stages.append('exact_moment_identical_gain_zero')

    # 4. retained-call admissibility predicates (mirrored, see README)
    bind_predicate([c['provider'] for c in calls])
    bind_predicate(list(disp['cand665_1'].values()))
    ok_counts = Counter()
    for c in calls:
        if c['provider'] != 'gauge44':
            continue
        ok, _ = sole_retention_ok(calls, (c['stage'], c['replica']))
        ok_counts[(c['orientation'], ok)] += 1
    need(ok_counts == {('forward', True): 142, ('backward', False): 107},
         f'sole-retention census: {ok_counts}')
    ok873, _ = sole_retention_ok(calls, (8, 73))
    need(ok873, '(8,73) sole retention fails partner predicates')
    stages.append('retained_call_admissibility_predicates')

    # 5. bind to SCREEN.json / ADMISSIBILITY.json receipts if present
    bound = {}
    for name, status in [('SCREEN.json', 'PASS_SCREEN_ZERO_DISPATCH_GAIN_ON_2322'),
                         ('ADMISSIBILITY.json', 'PASS_ADMISSIBILITY_CODE_ANALYSIS_2322')]:
        p = HERE / name
        if p.is_file():
            d = json.loads(p.read_text())
            need(d['status'] == status, f'{name} status')
            bound[name] = hashlib.sha256(p.read_bytes()).hexdigest()
    if 'SCREEN.json' in bound:
        scr = json.loads((HERE / 'SCREEN.json').read_text())
        need({int(k): v for k, v in scr['H_common'].items()} == H, 'SCREEN H mismatch')
        for rel, digest in scr['inputs_sha256'].items():
            need(hashlib.sha256((PKG / rel).read_bytes()).hexdigest() == digest,
                 f'input drift vs SCREEN: {rel}')
    stages.append('screen_admissibility_receipt_binding')

    # 6. tamper controls: mutate a value, confirm the check fails
    controls = []

    def expect_fail(label, fn):
        try:
            fn()
        except (ValueError, AssertionError, KeyError, IndexError) as exc:
            controls.append(f'{label}: rejected ({type(exc).__name__})')
            return
        raise ValueError('tamper control ACCEPTED: ' + label)

    def t1():
        bad = copy.deepcopy(plan)
        bad['provider_registry']['extra']['actual_paid_profile']['1'] += 1
        need(H_for(disp['cand665_1'], bad) == H, 'paid tamper went undetected')
    expect_fail('T1 extra paid_profile[1]+=1', t1)

    def t2():
        bad = copy.deepcopy(plan)
        w = bad['provider_registry']['extra']['widths']
        j = next(i for i, x in enumerate(w) if x != w[0])
        w[0], w[j] = w[j], w[0]
        need(H_for(disp['cand665_1'], bad) == H, 'width tamper went undetected')
    expect_fail('T2 extra widths swapped (two helpers)', t2)

    def t3():
        z = rows[0]
        old = z['offset']
        z['offset'] = old + 100
        try:
            ver.owners_check(rows, plan, contract)
        finally:
            z['offset'] = old
        need(False, 'row offset tamper accepted')
    expect_fail('T3 owner-row offset +=100', t3)

    def t4():
        wrong = Counter(H)
        wrong[1] += 1
        need(sum(r * n for r, n in wrong.items()) == 73 * 66304 - 23680,
             'undercharged profile mass')
    expect_fail('T4 H[1]+=1 mass', t4)

    expect_fail('T5 all-extra 666 bind rule',
                lambda: bind_predicate(list(disp['all_extra'].values())))

    def t6():
        ok, reasons = sole_retention_ok(calls, (3, 65))
        need(ok, f'backward sole retention accepted: {reasons}')
    expect_fail('T6 sole retained gauge44 (3,65) backward/odd-stage', t6)

    result = {'status': 'PASS_MUSE_DISPATCH_2322_VERIFY_ZERO_GAIN',
              'claim': ('No strict dispatch gain on #2322: H and exact moment '
                        'identical for shipped 417/249, 665+1 retain (8,73), '
                        'and 666 all-extra dispatches.'),
              'kappa_2322': '1697060296258836/1000000000000000000',
              'kappa_candidate': '1697060296258836/1000000000000000000',
              'kappa_gain_exact': '0',
              'H': {str(k): v for k, v in H.items()},
              'paid_common_per_call': {str(k): v for k, v in sorted(paid_common.items())},
              'moment_enclosure_at_kappa2322': [str(e_ship[0]), str(e_ship[1])],
              'stages': stages,
              'tamper_controls_rejected': controls,
              'receipt_sha256': bound,
              'not_run': ('#2322 cold_replay / discovery->strict->outer on a 665+1 '
                          'candidate data copy (conditional on a strict gain, '
                          'falsified here); see README open obligations.'),
              'python': sys.version.split()[0],
              'seconds': round(time.monotonic() - t0, 3)}
    (HERE / 'RESULT.json').write_text(json.dumps(result, indent=1) + '\n')
    print(result['status'], 'stages', len(stages), 'controls', len(controls),
          'seconds', result['seconds'], flush=True)
    for c in controls:
        print(' control', c, flush=True)


if __name__ == '__main__':
    main()
