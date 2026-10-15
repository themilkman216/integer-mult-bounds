#!/usr/bin/env python3
"""Cheap exact dispatch screen for #2322 (Track 3F).

Question: does the Track-3D 665-extra + 1-gauge44 provider dispatch,
which gained on #2269 because extra's paid profile was cheaper,
gain on #2322's priced profile H?

Method (all exact; no floats in any conclusion):
 1. Compare every priced per-provider quantity in #2322 at four
    layers: data/PLAN.json registry, data/SPEC.json providers,
    BASELINE-CONTRACT (#2312 supplier), words/{base,extra} reports.
 2. Independently recount each word's paid profile and width
    inventory from the literal word fields, using #2322's own
    generate_words.paid_profile().
 3. Recompute idle+H under candidate dispatches with #2322's own
    verify.owners_check() (full window/family/width/offset legality,
    289044 rows), mutating only plan['provider_calls'][t]['provider'].
 4. Evaluate the directed-integer moment enclosure
    vendor/fine_moment.moment(73, 66304, H, b) for shipped and
    candidate H at the CLAIM native endpoints and at CLAIM kappa;
    enclosures must be identical Fractions when H is identical.
 5. Retained-call census: orientation == stage parity, first-extra
    compatibility of every shipped gauge44 call (see README).

Writes SCREEN.json next to this package's README. Read-only w.r.t.
every predecessor package. Substantial AI assistance: Meta Muse
(muse-wonder-full-1.0). Apache-2.0.
"""
import copy, gzip, hashlib, importlib.util, json, sys, time
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent                       # research/muse-dispatch-2322
ROOT = OUT.parents[1]                   # workspace root
PKG = ROOT / 'research/t74-joint-owner-hillclimb'   # #2322 package


def read(p):
    p = Path(p)
    return json.loads(gzip.decompress(p.read_bytes()) if p.suffix == '.gz' else p.read_bytes())


def load_mod(name, path):
    sp = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(mod)
    return mod


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


t0 = time.monotonic()
plan = read(PKG / 'data/PLAN.json')
spec = read(PKG / 'data/SPEC.json')
claim = read(PKG / 'CLAIM.json')
contract = read(PKG / 'BASELINE-CONTRACT.json.gz')
rows = read(PKG / 'data/OWNERS.json.gz')
words = {k: read(PKG / f'words/{k}.json.gz') for k in ('base', 'extra')}
res = {'status': 'SCREEN_RUNNING',
       'base_pkg': 'research/t74-joint-owner-hillclimb (#2322, head 002304ef)',
       'kappa_2322_rational': claim['kappa'],
       'inputs_sha256': {n: sha(PKG / n) for n in
                         ('data/PLAN.json', 'data/SPEC.json', 'data/OWNERS.json.gz',
                          'data/DISPATCH.json', 'CLAIM.json',
                          'words/base.json.gz', 'words/extra.json.gz')}}

# --- 1. priced per-provider quantities at four layers -------------
reg = plan['provider_registry']
layers = {}
layers['plan_paid_equal'] = reg['gauge44']['actual_paid_profile'] == reg['extra']['actual_paid_profile']
layers['plan_widths_list_equal'] = reg['gauge44']['widths'] == reg['extra']['widths']
layers['plan_ports_equal'] = reg['gauge44']['ports'] == reg['extra']['ports']
layers['plan_centers_equal'] = reg['gauge44']['centers'] == reg['extra']['centers']
layers['plan_orientation_program_sha_equal'] = (
    reg['gauge44']['orientation_program_sha256'] == reg['extra']['orientation_program_sha256'])
layers['spec_expected_profile_equal'] = (
    spec['providers']['gauge44']['expected_profile'] == spec['providers']['extra']['expected_profile'])
layers['spec_paid_profile_equal'] = (
    spec['providers']['gauge44']['complete_contract']['paid_profile']
    == spec['providers']['extra']['complete_contract']['paid_profile'])
layers['spec_complete_contract_local_equal'] = (
    spec['providers']['gauge44']['complete_contract']['local']
    == spec['providers']['extra']['complete_contract']['local'])
layers['spec_expected_local_equal'] = (
    spec['providers']['gauge44']['expected_local'] == spec['providers']['extra']['expected_local'])
layers['spec_program_hashes_equal'] = (
    spec['providers']['gauge44']['program_hashes'] == spec['providers']['extra']['program_hashes'])
layers['spec_local_adapters_bound_compiler_equal'] = all(
    spec['providers']['gauge44']['complete_contract'][k]
    == spec['providers']['extra']['complete_contract'][k]
    for k in ('local_adapters', 'local_primitive_bound', 'compiler',
              'entering_helpers', 'entrance_rank', 'children'))
layers['contract_2312_paid_equal'] = contract['paid']['gauge44'] == contract['paid']['extra']
layers['contract_widths_list_equal'] = contract['widths']['gauge44'] == contract['widths']['extra']
layers['word_report_profile_equal'] = (
    words['base']['report']['local_profile'] == words['extra']['report']['local_profile'])
# Fifth layer: #2322's own shipped strict invoice receipt.
invoice = read(PKG / 'evidence/full-replay/delta/strict/global/audit/PREFIX-AND-INVOICE.json')
layers['invoice_paid_equal'] = (
    invoice['providers']['gauge44']['paid_profile']
    == invoice['providers']['extra']['paid_profile'])
layers['invoice_local_by_orientation_equal'] = (
    invoice['providers']['gauge44']['local'] == invoice['providers']['extra']['local'])
layers['invoice_selected_order_eq_plan'] = (
    [(c['stage'], c['replica'], c['provider_id']) for c in invoice['selected_calls']]
    == [(c['stage'], c['replica'], c['provider']) for c in plan['provider_calls']])
res['invoice_selected_local_paid_profile'] = invoice['selected_local_paid_profile']
paid_common = {int(k): v for k, v in reg['extra']['actual_paid_profile'].items()}
res['layer_equalities'] = layers
res['paid_common'] = {str(k): v for k, v in sorted(paid_common.items())}
res['contract_2312_paid_common'] = contract['paid']['extra']
assert all(layers.values()), layers

# Per-orientation local totals that enter the finite invoice are
# also provider-invariant (spec complete_contract equality above);
# orientation is fixed by the parent calls, checked in section 5.

# --- 2. literal recount of both changed words --------------------
gen = load_mod('gen2322', PKG / 'generate_words.py')
recount = {}
for kind in ('base', 'extra'):
    prof, widths = gen.paid_profile(words[kind])
    recount[kind] = {'paid_profile': {str(k): v for k, v in prof.items()},
                     'width_inventory': {str(k): v for k, v in widths.items()}}
res['word_recount'] = recount
assert recount['base'] == recount['extra'], recount
assert {int(k): v for k, v in recount['extra']['paid_profile'].items()} == paid_common
# The words are nevertheless distinct circuits (priced equality only).
diffs = {}
for key in words['base']:
    a, b = words['base'][key], words['extra'][key]
    if isinstance(a, list) and isinstance(b, list) and len(a) == len(b):
        n = sum(1 for x, y in zip(a, b) if x != y)
        if n:
            diffs[key] = n
    elif a != b:
        diffs[key] = 'non-list-diff'
res['word_field_diff_counts'] = diffs
print('layers equal; word recounts equal; word diffs', diffs, flush=True)

# --- 2b. recount the PINNED #2312 source words (via local git ref) --
# refs/upr/2312 (6a05b1bb) is a later head than the fb76f799 pin, so
# each blob is used only after its sha256 matches both generate_words
# SOURCE_WORDS and UPSTREAM-2312.json. Absence is recorded, not fatal.
import subprocess
src_recount = {'available': False}
try:
    inv2312 = {f['path']: f for f in read(PKG / 'UPSTREAM-2312.json')['files']}
    got = {}
    for kind in ('base', 'extra'):
        rel = f'new/borrow/words/BORROW-WORD-43{kind}.json.gz'
        path = 'research/gmx-t74-borrow43-width-exchange/' + rel
        raw = subprocess.check_output(['git', 'show', f'refs/upr/2312:{path}'],
                                      cwd=ROOT, stderr=subprocess.STDOUT)
        digest = hashlib.sha256(raw).hexdigest()
        assert digest == gen.SOURCE_WORDS[kind] == inv2312[path]['sha256'], kind
        prof, widths = gen.paid_profile(json.loads(gzip.decompress(raw)))
        got[kind] = {'paid_profile': {str(k): v for k, v in prof.items()},
                     'width_inventory': {str(k): v for k, v in widths.items()},
                     'sha256': digest}
    src_recount = {'available': True, 'words': got,
                   'both_equal': ({k: v for k, v in got['base'].items() if k != 'sha256'}
                                  == {k: v for k, v in got['extra'].items() if k != 'sha256'}),
                   'pin': 'sha256 matches generate_words.SOURCE_WORDS and UPSTREAM-2312.json'}
    assert src_recount['both_equal']
    assert got['base']['paid_profile'] == {str(k): v for k, v in contract['paid']['extra'].items()}
except Exception as exc:  # local ref or pin unavailable: record honestly
    src_recount = {'available': False, 'error': type(exc).__name__ + ': ' + str(exc)[:300]}
res['pr2312_source_word_recount'] = src_recount
print('2312 source recount', src_recount.get('available'), flush=True)

# --- 3. H under candidate dispatches (full owners_check) ---------
ver = load_mod('ver2322', PKG / 'verify.py')
calls = plan['provider_calls']
key_of = [(c['stage'], c['replica']) for c in calls]
gauge_keys = sorted(k for k, c in zip(key_of, calls) if c['provider'] == 'gauge44')
res['shipped_counts'] = dict(Counter(c['provider'] for c in calls))
assert res['shipped_counts'] == {'extra': 417, 'gauge44': 249}

def H_for(dispatch):
    """dispatch: dict (stage,replica)->provider. Full legality recount."""
    plan2 = copy.deepcopy(plan)
    for c in plan2['provider_calls']:
        c['provider'] = dispatch[c['stage'], c['replica']]
    H, idle = ver.owners_check(rows, plan2, contract)
    return dict(sorted(H.items())), dict(sorted(idle.items()))

shipped_disp = {k: c['provider'] for k, c in zip(key_of, calls)}
cands = {'shipped_417_249': shipped_disp,
         'all_extra_666': {k: 'extra' for k in key_of},
         'all_gauge_666': {k: 'gauge44' for k in key_of}}
RETAIN = (8, 73)   # Track-3D retained call; already gauge44 here
cands['extra665_retain_8_73'] = {k: ('gauge44' if k == RETAIN else 'extra') for k in key_of}
cands['extra665_retain_3_65_backward'] = {
    k: ('gauge44' if k == (3, 65) else 'extra') for k in key_of}
cands['extra665_retain_first_gauge_2_33'] = {
    k: ('gauge44' if k == gauge_keys[0] else 'extra') for k in key_of}
# Deterministic mixed pattern: provider by (time % 3 == 0).
cands['mod3_mixed'] = {key_of[t]: ('gauge44' if t % 3 == 0 else 'extra')
                       for t in range(len(calls))}

profiles = {}
for name, disp in cands.items():
    t = time.monotonic()
    H, idle = H_for(disp)
    profiles[name] = {'counts': dict(Counter(disp.values())),
                      'H': {str(k): v for k, v in H.items()},
                      'idle': {str(k): v for k, v in idle.items()},
                      'owners_check_seconds': round(time.monotonic() - t, 3)}
    print(name, profiles[name]['counts'], 'mass', sum(k * v for k, v in H.items()),
          flush=True)
Hs = [p['H'] for p in profiles.values()]
assert all(h == Hs[0] for h in Hs), 'dispatch changed H'
H = {int(k): v for k, v in Hs[0].items()}
assert H == {int(k): v for k, v in claim['global_profile'].items()}
res['candidate_profiles'] = profiles
res['H_common'] = Hs[0]
res['H_rank_mass'] = sum(k * v for k, v in H.items())
res['H_deficit_check'] = 73 * 66304 - res['H_rank_mass']

# Algebraic form over ALL 2^666 dispatches, from layers 1-2:
# width_of(row) reads provider widths (identical lists), so idle
# is dispatch-free; paid enters H only as a per-call sum of the
# identical paid profiles, i.e. exactly 666*paid_common.
idle0 = {int(k): v for k, v in profiles['shipped_417_249']['idle'].items()}
alg = Counter(idle0)
alg.update({r: 666 * n for r, n in paid_common.items()})
assert dict(sorted(alg.items())) == H, (dict(alg), H)
res['algebraic_H_eq_idle_plus_666_paid_common'] = True
# Each of the 249 single-retention 665+1 dispatches, formula level:
retained_variants = []
for k in gauge_keys:
    var = Counter(idle0)
    var.update({r: (665 * paid_common[r] + paid_common[r]) for r in paid_common})
    retained_variants.append(dict(sorted(var.items())) == H)
res['all_249_single_retentions_same_H_by_formula'] = all(retained_variants)
assert res['all_249_single_retentions_same_H_by_formula']
print('H invariant under all spot-checked dispatches and by formula', flush=True)

# --- 4. exact directed moment enclosures -------------------------
eng = load_mod('fm2322', PKG / 'vendor/fine_moment.py')
eng.SH = 256; eng.GRID = 1 << 256; eng.LOG_TERMS = 100; eng.EXP_TERMS = 96
entries = sorted(H.items())
moments = {}
from decimal import Decimal, localcontext
def dec30(q):
    with localcontext() as ctx:
        ctx.prec = 30
        return str(Decimal(q.numerator) / Decimal(q.denominator))
for label, bstr in [('at_native_endpoint_lower', claim['native_endpoint_lower']),
                    ('at_native_endpoint_upper', claim['native_endpoint_upper']),
                    ('at_claim_kappa', claim['kappa'])]:
    lo, hi = eng.moment(73, 66304, entries, Q(bstr))
    moments[label] = {'b': bstr, 'enclosure': [str(lo), str(hi)],
                      'enclosure_minus_one_dec30': [dec30(lo - 1), dec30(hi - 1)],
                      'below_one': bool(hi < 1), 'above_one': bool(lo > 1)}
    print(label, moments[label]['enclosure_minus_one_dec30'], flush=True)
assert moments['at_native_endpoint_lower']['below_one']
assert moments['at_native_endpoint_upper']['above_one']
# Candidate dispatch has the same H dict, hence the engine receives
# byte-identical inputs; evaluate it as a separate call anyway.
Hc = {int(k): v for k, v in profiles['extra665_retain_8_73']['H'].items()}
lo2, hi2 = eng.moment(73, 66304, sorted(Hc.items()), Q(claim['kappa']))
lo1, hi1 = eng.moment(73, 66304, entries, Q(claim['kappa']))
assert (lo1, hi1) == (lo2, hi2), 'candidate moment enclosure differs'
res['exact_moments'] = moments
res['candidate_665_1_moment_enclosure_at_kappa2322_identical'] = True
res['moment_gain'] = '0 (identical enclosures; interval difference is [0,0])'
res['kappa_gain_over_2322'] = '0'
res['kappa_candidate_by_exact_rational_comparison'] = (
    'equal to 1697060296258836/1000000000000000000; no strict gain')
K2322 = Q(claim['kappa'])
assert K2322 == Q(1697060296258836, 10**18)
res['kappa_2322_reduced'] = str(K2322)

# --- 5. retained-call census (admissibility, priced view) --------
assert all(c['orientation'] == ('forward' if c['stage'] % 2 == 0 else 'backward')
           for c in calls), 'orientation is not stage parity'
first_extra = next(c for c in calls if c['provider'] == 'extra')
compat, incompat = [], []
for c in calls:
    if c['provider'] != 'gauge44':
        continue
    ok = (c['orientation'] == first_extra['orientation']
          and (c['stage'] - first_extra['stage']) % 2 == 0)
    (compat if ok else incompat).append([c['stage'], c['replica'], c['time'],
                                          c['orientation']])
retain_call = next(c for c in calls if (c['stage'], c['replica']) == RETAIN)
res['retained_call_census'] = {
    'orientation_law': 'forward iff stage even (all 666 calls)',
    'first_extra_call': {k: first_extra[k] for k in ('stage', 'replica', 'time', 'orientation')},
    'gauge_calls_total': len(compat) + len(incompat),
    'even_stage_forward_gauge_calls': len(compat),
    'odd_stage_backward_gauge_calls': len(incompat),
    'retain_8_73': {k: retain_call[k] for k in ('stage', 'replica', 'time', 'orientation', 'provider')},
    'retain_8_73_sorted_last_gauge_key': gauge_keys[-1] == RETAIN,
    'note': ('Priced view: every single retention gives the same H. '
             'Partner-control view (README): only even-stage/forward '
             'retentions keep assembly_controls next() searches for '
             'P=extra satisfiable if it is the sole gauge44 call.')}
print('retained census', res['retained_call_census'], flush=True)

# --- 6. the #2269 lever that is absent here (quoted constants) ---
# #2269 BORROW-PROVIDERS.json at refs/upr/2269 b479fc55 (read this
# session via `git show`); #2312 providers at refs/upr/2312.
g2269 = {1: 2351, 2: 501, 3: 414, 4: 129, 5: 42, 8: 8}
e2269 = {1: 2339, 2: 509, 3: 418, 4: 125, 5: 42, 8: 8}
delta2269 = {r: g2269[r] - e2269[r] for r in g2269}
assert delta2269 == {1: 12, 2: -8, 3: -4, 4: 4, 5: 0, 8: 0}
assert sum(r * n for r, n in delta2269.items()) == 0
res['contrast_2269'] = {'gauge44_paid': g2269, 'extra_paid': e2269,
                        'gauge_minus_extra_per_call': delta2269,
                        'pr2312_paid_common_438': contract['paid']['extra'],
                        'pr2322_paid_common_434': res['paid_common'],
                        'explanation': ('#2312 exact frame refit (42 gauge44 '
                                        'frames, 30 extra frames) + pivot-518/506 '
                                        'kernels on both words -> common profile '
                                        '{2343,504,422,124,42,8}; #2322 four-handoff '
                                        'delta {-8,+8,+4,-4,-4} applied to both -> '
                                        '{2335,512,426,120,38,8}.')}
# Check the #2322 delta arithmetic on the common profiles.
c2312 = {int(k): v for k, v in contract['paid']['extra'].items()}
delta2322 = {1: -8, 2: 8, 3: 4, 4: -4, 5: -4, 8: 0}
assert {r: c2312[r] + delta2322[r] for r in c2312} == paid_common

res['status'] = 'PASS_SCREEN_ZERO_DISPATCH_GAIN_ON_2322'
res['seconds_total'] = round(time.monotonic() - t0, 3)
res['python'] = sys.version.split()[0]
(OUT / 'SCREEN.json').write_text(json.dumps(res, indent=1) + '\n')
print(res['status'], 'seconds', res['seconds_total'], flush=True)
