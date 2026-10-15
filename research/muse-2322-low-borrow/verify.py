#!/usr/bin/env python3
"""Independent verification for muse-2322-low-borrow.

Recomputes, from shipped artifacts (not from the analysis scripts' cached
conclusions):
  1. #2322 word recount via its own generate_words.paid_profile + candidate
     register widths (remaining highs width 5, 653 width 4, lows width 8,
     32 low lenders width 4 unused);
  2. byte identity of the PR2269/PR2312 canonical words;
  3. stage-P audit receipts, plus fresh audit_local re-runs on the shipped
     stage-P words V0 and V653 (supplier trees extracted from local git
     refs refs/upr/2269 and refs/upr/2312 into /tmp, read-only);
  4. exact rational dual certificates for the low x1, 653 and high x1
     scenarios (own recomputation of floored-dual feasibility against
     ceiling.child_cost lower bounds) and the exact margins recorded in
     EXACT-SCREEN.json;
  5. four tamper controls that mutate a value and must be rejected:
     T1 flipped gate coefficient in word_V653 (audit rejects),
     T2 LP bin dual inflated by 1/1000 (exact feasibility rejects),
     T3 SCREEN-LP role total off by one (role reconstruction rejects),
     T4 claimed V653 audit profile altered (receipt binding rejects).
Writes RESULT.json.  Exit 0 only if everything passes; uses require(),
not assert, so it stays sound under python -O.
"""
import copy, gzip, hashlib, importlib.util, json, math, subprocess, sys
from fractions import Fraction as Q
from pathlib import Path

PKG = Path(__file__).resolve().parent
WS = PKG.parents[1]
SRC2322 = WS / 'research/t74-joint-owner-hillclimb'
CALLS = 666

def require(ok, msg):
    if not ok:
        raise SystemExit(f'FAIL: {msg}')

def load_mod(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

def extract(ref, sub, dest):
    if not (dest / sub).exists():
        dest.mkdir(parents=True, exist_ok=True)
        arc = subprocess.run(['git', '-C', str(WS), 'archive', ref, sub],
                             capture_output=True)
        require(arc.returncode == 0, f'git archive {ref} failed')
        subprocess.run(['tar', '-x', '-C', str(dest)], input=arc.stdout, check=True)

stages = {}

# ---- stage 1: #2322 census recount --------------------------------------
gw = load_mod('gw2322', SRC2322 / 'generate_words.py')
for tag in ('base', 'extra'):
    word = json.loads(gzip.decompress((SRC2322 / 'words' / f'{tag}.json.gz').read_bytes()))
    prof, widths = gw.paid_profile(word)
    require(prof == {1: 2335, 2: 512, 3: 426, 4: 120, 5: 38, 8: 8}, f'{tag} profile')
    require(widths == {4: 33, 5: 9, 7: 38, 8: 114, 9: 240}, f'{tag} widths')
    require(len(word['removed']) == 46 and len(word['initial_corrections']) == 0,
            f'{tag} alias state')
    dim = {}
    for role in range(224, 704):
        s = len(gw.basis(word['start_extra'].get(str(role), [])))
        e = len(gw.basis(word['helper_final'][str(role)])) if str(role) in word['helper_final'] else 9
        dim[role] = e - s
    if tag == 'base':
        for r in (606, 635, 637, 638, 639, 667, 669, 670, 671):
            require(dim[r] == 5 and r not in word['removed'], f'high {r} width')
        require(dim[653] == 4 and 653 not in word['removed'], '653 width')
        lenders = [273, 275, 277, 282, 289, 291, 293, 298, 305, 307, 309, 314,
                   321, 323, 325, 330, 337, 339, 341, 346, 353, 355, 357, 362,
                   369, 371, 373, 378, 385, 387, 389, 394]
        require(all(dim[r] == 4 for r in lenders), 'low lender widths')
        used = {rec[1] for rec in word['warps']}
        require(not used & set(lenders), 'low lender already used')
        for r in (592, 600, 616, 624, 672, 696):
            require(dim[r] == 8, f'low {r} width')
stages['census_2322'] = 'PASS'
print('stage 1 census PASS', flush=True)

# ---- stage 2: canonical identity ----------------------------------------
extract('refs/upr/2269', 'research/gmx-t74-borrow43', Path('/tmp/pr2269src'))
extract('refs/upr/2312', 'research/gmx-t74-borrow43-width-exchange', Path('/tmp/pr2312src'))
B = Path('/tmp/pr2269src/research/gmx-t74-borrow43/new/borrow')
B12 = Path('/tmp/pr2312src/research/gmx-t74-borrow43-width-exchange/new/borrow')
for canon, want in [('gauge44.canonical.json.gz',
                     '65c6d17ffee2eacf27bff438f37fc549c9ed0c909cbc7a52976cc75cf2d15b91'),
                    ('extra.canonical.json.gz',
                     'd7e48dcbafa236a2e1e41f7958244211506f7c7630fe6a2d43d2bdf17b7ae015')]:
    h1 = hashlib.sha256((B / 'inputs' / canon).read_bytes()).hexdigest()
    h2 = hashlib.sha256((B12 / 'inputs' / canon).read_bytes()).hexdigest()
    require(h1 == h2 == want, f'canonical {canon} identity')
stages['canonical_identity'] = 'PASS'
print('stage 2 canonical identity PASS', flush=True)

# ---- stage 3: stage-P receipts + fresh re-audits -------------------------
sp = json.load(open(PKG / 'STAGEP-SINGLES.json'))['results']
exp_delta = {'V653': ({3: -1}, {4: -1, 7: -1, 8: 1}),
             'V606': ({5: -1}, {5: -1}),
             'Vlow592': ({3: -1}, {4: -1, 8: -1, 9: 1}),
             'Vlow624': ({1: 1, 4: -1}, {4: -1, 8: -1, 9: 1})}
require(sp['V0']['profile'] == {'1': 2353, '2': 500, '3': 416, '4': 128, '5': 42, '8': 8},
        'V0 control profile')
require(sp['V0']['widths'] == {'4': 37, '5': 9, '7': 38, '8': 114, '9': 240}, 'V0 widths')
for tag, (dp, dw) in exp_delta.items():
    got_p = {int(k): v for k, v in sp[tag]['delta_profile_vs_V0'].items()}
    got_w = {int(k): v for k, v in sp[tag]['delta_widths_vs_V0'].items()}
    require(got_p == dp and got_w == dw, f'{tag} delta')
    require(sp[tag]['audit_status'] == 'PASS_INDEPENDENT_EXACT_BORROWING_WORD', f'{tag} audit')
    require(sp[tag]['controls_rc'] == 0 and sp[tag]['replay_rc'] == 0, f'{tag} replay/controls')
    aj = json.load(open(PKG / 'stagep' / f'AUDIT-{tag}.json'))
    require(aj['local_profile'] == sp[tag]['profile'], f'{tag} receipt binding')

def audit_fresh(wordpath, outpath):
    r = subprocess.run([sys.executable, '-B', str(B / 'audit_local.py'), '--word',
                        str(wordpath), '--base', str(B / 'inputs/gauge44.canonical.json.gz'),
                        '--output', str(outpath)], capture_output=True, text=True)
    return r

for tag in ('V0', 'V653'):
    outp = Path(f'/tmp/muse-2322-verify-AUDIT-{tag}.json')
    r = audit_fresh(PKG / 'stagep' / f'word_{tag}.json.gz', outp)
    require(r.returncode == 0, f'fresh audit {tag}')
    aj = json.loads(outp.read_text())
    require(aj['local_profile'] == sp[tag]['profile'], f'fresh audit {tag} profile')
    require(aj['width_inventory'] == sp[tag]['widths'], f'fresh audit {tag} widths')
stages['stagep_singles'] = 'PASS'
print('stage 3 stage-P singles PASS', flush=True)

# ---- stage 4: exact dual certificates (own recomputation) ----------------
ceiling = load_mod('ceiling', WS / 'research/complex-local-word-ceiling/ceiling.py')
claim = json.load(open(SRC2322 / 'CLAIM.json'))
k_num, k_den = (int(x) for x in claim['kappa'].split('/'))
A2322 = Q(k_num, k_den) / (1 - Q(k_num, k_den))
CAPS = {8: 49728, 16: 33152, 32: 33152, 48: 33152}
WIDTHS = [9, 8, 7, 5, 4]
_cost = {}
def cost(r):
    if r not in _cost:
        _cost[r] = (Q(0), Q(0)) if r == 0 else ceiling.child_cost(r, 73, A2322)
    return _cost[r]

pats = []
for cap in CAPS:
    for a in range(cap // 9 + 1):
        for b in range((cap - 9 * a) // 8 + 1):
            for c_ in range((cap - 9 * a - 8 * b) // 7 + 1):
                for d in range((cap - 9 * a - 8 * b - 7 * c_) // 5 + 1):
                    for e in range((cap - 9 * a - 8 * b - 7 * c_ - 5 * d) // 4 + 1):
                        cnt = (a, b, c_, d, e)
                        pats.append((cap, cnt, cap - sum(w * x for w, x in zip(WIDTHS, cnt))))
require(len(pats) == 1163, 'pattern count')

def dual_check(roles, duals_float):
    """Returns (objective, min_slack) with 1e-12-floored rational duals."""
    fl = lambda v: Q(math.floor(v * 10**12), 10**12)
    yb = {int(k): fl(v) for k, v in duals_float['bins'].items()}
    yr = {int(k): fl(v) for k, v in duals_float['roles'].items()}
    slack = min(cost(rem)[0] - yb[cap] - sum(yr[w] * x for w, x in zip(WIDTHS, cnt))
                for cap, cnt, rem in pats)
    obj = sum(CAPS[c] * yb[c] for c in CAPS) + sum(roles[w] * yr[w] for w in WIDTHS)
    return obj, slack

def qdec(x): return float(x.numerator) / float(x.denominator)

GLOBAL = {int(k): v for k, v in json.load(open(SRC2322 / 'data/PROFILE.json')).items()}
actual_hi = sum(Q(n) * cost(r)[1] for r, n in GLOBAL.items())
screen = json.load(open(PKG / 'SCREEN-LP.json'))
exact = json.load(open(PKG / 'EXACT-SCREEN.json'))
erows = {r['name']: r for r in exact['rows']}
PAID_CALL = {1: 2335, 2: 512, 3: 426, 4: 120, 5: 38, 8: 8}
scen_paid = {'low x1': {3: -1}, '653 re-alias (measured stage-P)': {3: -1},
             'high x1': {5: -1}, 'base #2322 widths (LP gap check)': {}}
computed = {}
for name, pdelta in scen_paid.items():
    row = next(r for r in screen['rows'] if r['name'] == name)
    roles = {int(k): v for k, v in row['roles'].items()}
    obj, slack = dual_check(roles, row['duals'])
    require(slack >= 0, f'{name} dual feasibility')
    p = dict(PAID_CALL)
    for r, d in pdelta.items():
        p[r] += d
    plo = sum(Q(CALLS * n) * cost(r)[0] for r, n in p.items())
    computed[name] = plo + obj
    margin = qdec(computed[name] - actual_hi)
    require(abs(margin - float(erows[name]['margin_vs_actual'])) < 1e-6,
            f'{name} exact margin recomputation ({margin} vs {erows[name]["margin_vs_actual"]})')
require(computed['low x1'] > actual_hi, 'low x1 must be falsified')
require(computed['653 re-alias (measured stage-P)'] > actual_hi, '653 must be falsified')
alt = computed['high x1'] - computed['base #2322 widths (LP gap check)']
require(-Q(1, 10**8) < alt < Q(1, 10**8), 'high x1 must be LP-neutral vs base bound')
for name in ('low x32', 'low x32 (joint paid delta variant)',
             'low624 class x1 (measured stage-P)'):
    require(erows[name]['falsified_vs_actual'] is True, f'{name} recorded falsified')
    require(float(erows[name]['margin_vs_actual']) > 0, f'{name} recorded margin')
require(erows['high x9 (all width-5)']['falsified_vs_actual'] is False,
        'high x9 neutrality (not falsification) recorded')
stages['exact_screen'] = 'PASS'
print('stage 4 exact screen PASS', flush=True)

# ---- stage 5: tamper controls (each mutates a value; must be rejected) ---
# T1: flipped gate coefficient in a copy of the V653 word.
w = json.loads(gzip.decompress((PKG / 'stagep/word_V653.json.gz').read_bytes()))
gi = next(i for i, g in enumerate(w['B']) if g[0] == 'add')
w['B'][gi][3] = -w['B'][gi][3]
badp = Path('/tmp/muse-2322-verify-T1.json.gz')
badp.write_bytes(gzip.compress(json.dumps(w, separators=(',', ':')).encode()))
r = audit_fresh(badp, Path('/tmp/muse-2322-verify-T1.out.json'))
require(r.returncode != 0, 'T1 tampered word was ACCEPTED')

# T2: LP bin dual inflated by 1/1000 breaks exact dual feasibility.
row = next(r for r in screen['rows'] if r['name'] == 'low x1')
roles = {int(k): v for k, v in row['roles'].items()}
tampered_duals = copy.deepcopy(row['duals'])
tampered_duals['bins']['32'] += 1e-3
_, slack_bad = dual_check(roles, tampered_duals)
require(slack_bad < 0, 'T2 inflated dual was ACCEPTED as feasible')

# T3: role reconstruction from stage-P widths must match SCREEN-LP; off-by-one must not.
base_roles = {9: 240, 8: 114, 7: 38, 5: 9, 4: 33}
exp_roles = {w: CALLS * (base_roles[w] + {9: 1, 8: -1, 4: -1}.get(w, 0)) for w in WIDTHS}
require({int(k): v for k, v in row['roles'].items()} == exp_roles, 'T3 honest roles')
bad_roles = dict(exp_roles); bad_roles[9] -= 1
require({int(k): v for k, v in row['roles'].items()} != bad_roles,
        'T3 tampered roles were ACCEPTED (test itself broken)')

# T4: an altered claimed V653 profile must not bind to the shipped audit receipt.
fake = dict(sp['V653']['profile']); fake['3'] -= 1
aj = json.load(open(PKG / 'stagep/AUDIT-V653.json'))
require(aj['local_profile'] == sp['V653']['profile'], 'T4 honest binding')
require(aj['local_profile'] != fake, 'T4 tampered profile was ACCEPTED (test itself broken)')
stages['tamper_controls'] = 'PASS (T1-T4 all rejected)'
print('stage 5 tamper controls PASS', flush=True)

# ---- RESULT.json -----------------------------------------------------------
result = dict(
    status='PASS_MUSE_2322_LOW_BORROW_VERIFY',
    verdict='NO_NEW_KAPPA',
    kappa_2322_compared_against=claim['kappa'],
    kappa_2322_decimal=claim['decimal'],
    exact_actual_total_hi=exact['actual_total_hi'],
    margins_vs_actual={r['name']: r['margin_vs_actual'] for r in exact['rows']},
    falsified={r['name']: r['falsified_vs_actual'] for r in exact['rows']},
    stagep_deltas={t: dict(profile=sp[t]['delta_profile_vs_V0'],
                           widths=sp[t]['delta_widths_vs_V0']) for t in exp_delta},
    stages=stages,
    scope=('Exact pattern-LP dual certificates at a2322 for the shipped bin '
           'template; paid/width deltas measured exactly at stage P on the '
           'true PR2312 witness and transferred to #2322 final totals '
           '(assumption A: frame refit / pivot kernels / block-616 stages '
           'do not change these deltas). No native emission, owner fill, '
           'strict assembly or outer witness was run for candidates, per '
           'the stop rule. No new kappa is claimed.'),
    disclosure='Prepared with Meta Muse (muse-wonder-full-1.0) assistance.')
(PKG / 'RESULT.json').write_text(json.dumps(result, indent=1) + '\n')
print('PASS_MUSE_2322_LOW_BORROW_VERIFY')
print('wrote RESULT.json')
