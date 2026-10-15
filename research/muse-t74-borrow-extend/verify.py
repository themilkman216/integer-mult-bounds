#!/usr/bin/env python3
"""Verifier for muse-t74-borrow-extend.

Re-runs the cheap decisive stages against the shipped artifacts and checks
the recorded receipts for the expensive ones:
  1. #2269's independent audit_local.py on both 48-alias BORROW-WORDs
     (fresh run; profile/mass/widths compared to AUDIT-48*.json);
  2. #2269's literal owner-fill checker (reconstruct48.py) on FILL48
     (fresh run into a temp dir) and global-profile invariance vs #2269;
  3. exact-interval ceilings (pinned ceiling.py) for the audited 43- and
     48-alias local profiles, and the exact global-profile moment identity;
  4. receipt binding: BUILD48 stages, native STEPS (all exit 0), REBIND
     profile arithmetic.
  Round 2 additions:
  5. fresh audits of both 80-alias words (mass 5264, 64 corrections) and
     census/solve receipts;
  6. fresh literal owner check of FILL80 (reconstruct80.py) and the exact
     interval global moment of its H, compared against #2269's H;
  7. exact rational pattern-LP dual certificate: the floored dual of
     PATTERN-LP.json is checked feasible against ceiling.child_cost lower
     bounds over all 1163 bin patterns, and paid80_lo + dual objective is
     compared against #2269's moment upper bound;
  8. receipts: BUILD-49/80, NATIVE80 steps, REBIND80, LEMMAG80.
Tamper controls (must all be REJECTED): (T1) one gate coefficient in a copy
of the 48-word flipped -> audit_local must fail; (T2) one FILL48 offset
shifted -> owner checker must fail; (T3) claimed local mass off by one ->
this verifier's comparison must fail (self-test of the comparison);
(T4) initial-correction sign flipped in an 80-word copy -> audit must fail;
(T5) one dual variable inflated by 1/1000 -> exact dual feasibility must fail.
Writes RESULT.json (round-1 snapshot preserved as RESULT-R1.json).
No kappa is claimed: see README (round-2 result is a scoped obstruction).
"""
import gzip, hashlib, json, subprocess, sys, tempfile, time
from fractions import Fraction as Q
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
PKG = ROOT / 'research/gmx-t74-borrow43'
B = PKG / 'new/borrow'
sys.path.insert(0, str(ROOT / 'research/complex-local-word-ceiling'))
import ceiling  # noqa: E402

def rd(p):
    b = Path(p).read_bytes()
    return json.loads(gzip.decompress(b) if str(p).endswith('.gz') else b)
def run(cmd, **kw):
    t = time.monotonic()
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    return r, time.monotonic() - t
def check(cond, msg):
    if not cond: raise AssertionError(msg)
    return True

res = dict(status='RUNNING', stages={}, tampers={})
tmp = Path(tempfile.mkdtemp(prefix='muse-t74-verify-'))

# 1. fresh independent audits
for tag, canon in [('base', 'gauge44.canonical.json.gz'), ('extra', 'extra.canonical.json.gz')]:
    word = OUT / 'words' / f'BORROW-WORD-48{tag}.json.gz'
    outp = tmp / f'audit-{tag}.json'
    r, dt = run([sys.executable, '-B', str(B / 'audit_local.py'), '--word', str(word),
                 '--base', str(B / 'inputs' / canon), '--output', str(outp)])
    check(r.returncode == 0, f'audit {tag} rc')
    a, shipped = rd(outp), rd(OUT / f'AUDIT-48{tag}.json')
    for k in ('local_profile', 'local_mass', 'width_inventory', 'removed_helpers', 'status'):
        check(a[k] == shipped[k], f'audit {tag} {k}')
    check(a['local_mass'] == 5360 and a['removed_helpers'] == 48, f'audit {tag} headline')
    res['stages'][f'audit48-{tag}'] = dict(rc=0, seconds=dt, profile=a['local_profile'])

# T1: tampered word (flip one add coefficient) must be rejected
w = rd(OUT / 'words/BORROW-WORD-48base.json.gz')
g = next(g for g in w['B'] if g[0] == 'add'); g[3] = g[3] + 1
tw = tmp / 'tampered-word.json.gz'
tw.write_bytes(gzip.compress(json.dumps(w, separators=(',', ':')).encode()))
r, _ = run([sys.executable, '-B', str(B / 'audit_local.py'), '--word', str(tw),
            '--base', str(B / 'inputs/gauge44.canonical.json.gz'),
            '--output', str(tmp / 'tampered-audit.json')])
res['tampers']['T1_gate_coefficient'] = dict(rejected=r.returncode != 0)
check(r.returncode != 0, 'T1 tampered word was ACCEPTED')

# 2. owner fill literal check + profile invariance
r, dt = run([sys.executable, '-B', str(OUT / 'scripts/reconstruct48.py'),
             '--out', str(tmp / 'owners')], cwd=ROOT)
check(r.returncode == 0 and 'PASS_OWNER_VERIFY' in r.stdout, 'reconstruct48')
new_prof = {str(k): v for k, v in rd(tmp / 'owners/PROFILE.json').items()}
old_prof = rd(PKG / 'PROFILE.json')
check(new_prof == old_prof, 'global profile invariance (expected equal)')
res['stages']['owner-fill48'] = dict(rc=0, seconds=dt, global_profile=new_prof,
                                     invariant_vs_2269=True,
                                     idle=rd(tmp / 'owners/RESULT.json')['idle'])
# T2: shifted offset must be rejected
f = rd(OUT / 'FILL48.json.gz'); f['rows'][0][5] += 1
tf = tmp / 'FILL48-tampered.json.gz'
tf.write_bytes(gzip.compress(json.dumps(f, separators=(',', ':')).encode(), mtime=0))
src = (OUT / 'scripts/reconstruct48.py').read_text().replace(
    "research/muse-t74-borrow-extend/FILL48.json.gz", str(tf))
(tmp / 'reconstruct-tamper.py').write_text(src)
r, _ = run([sys.executable, '-B', str(tmp / 'reconstruct-tamper.py'),
            '--out', str(tmp / 'owners-tamper')], cwd=ROOT)
res['tampers']['T2_fill_offset'] = dict(rejected=r.returncode != 0)
check(r.returncode != 0, 'T2 tampered fill was ACCEPTED')

# 3. exact ceilings for audited local profiles + global moment identity
M, FAM, ST, CEN, GRID = 73, 896, 9, 64, Q(1, 10**12)
P43 = {1: 2351, 2: 501, 3: 414, 4: 129, 5: 42, 8: 8}
P48 = {1: 2351, 2: 501, 3: 414, 4: 129, 5: 37, 8: 8}
ceil = {}
for name, p in [('borrow43-base', P43), ('borrow48-base', P48)]:
    lo, hi = ceiling.ceiling(p, M, FAM, ST, CEN, grid=GRID)
    ceil[name] = dict(a_lo=str(lo), a_hi=str(hi), a_hi_dec=float(hi))
check(Q(ceil['borrow48-base']['a_lo']) > Q(ceil['borrow43-base']['a_hi']),
      'local ceiling must strictly rise (relaxation level)')
# global moment at a2269 for old vs new global profile: identical object
K = Q(16962471390584742, 10**19); A = K / (1 - K)
def gmoment(prof):
    lo = hi = Q(0)
    for r_, n in prof.items():
        c_lo, c_hi = ceiling.child_cost(int(r_), M, A)
        lo += n * c_lo; hi += n * c_hi
    return lo, hi
gm_new, gm_old = gmoment(new_prof), gmoment(old_prof)
check(gm_new == gm_old, 'global moment identity')
res['stages']['exact-prices'] = dict(ceilings=ceil,
    global_moment_at_a2269=[str(gm_new[0]), str(gm_new[1])],
    global_moment_dec=float(gm_new[1]), identical_to_2269=True)

# T3: off-by-one claimed mass must fail comparison (self-test)
try:
    check(rd(OUT / 'AUDIT-48base.json')['local_mass'] == 5361, 'x')
    res['tampers']['T3_mass_off_by_one'] = dict(rejected=False)
except AssertionError:
    res['tampers']['T3_mass_off_by_one'] = dict(rejected=True)
check(res['tampers']['T3_mass_off_by_one']['rejected'], 'T3 self-test')

# 4. receipts
b48 = rd(OUT / 'BUILD48.json')
for tag in ('base', 'extra'):
    for k in ('joint_rc', 'build_rc', 'audit_rc', 'controls_rc'):
        check(b48[tag][k] == 0, f'BUILD48 {tag} {k}')
    steps = rd(OUT / f'NATIVE48-{tag}-STEPS.json')
    check([s['step'] for s in steps] == ['native', 'ledgers', 'local-replay', 'wrappers', 'phases']
          and all(s['exit_code'] == 0 for s in steps), f'native steps {tag}')
    res['stages'][f'native48-{tag} (receipt)'] = dict(
        seconds=sum(s['seconds'] for s in steps))
rb = rd(OUT / 'REBIND.json')
check(rb['new_profile']['5'] == rb['old_profile']['5'] - 5 * 666, 'rebind rank-5 arithmetic')
res['stages']['rebind48 (receipt)'] = dict(new_profile=rb['new_profile'])

# 5. round 2: 80-alias words fresh audits + correction tamper (T4)
import math  # noqa: E402
for tag, canon in [('base', 'gauge44.canonical.json.gz'), ('extra', 'extra.canonical.json.gz')]:
    word = OUT / 'words' / f'BORROW-WORD-80{tag}.json.gz'
    outp = tmp / f'audit80-{tag}.json'
    r, dt = run([sys.executable, '-B', str(B / 'audit_local.py'), '--word', str(word),
                 '--base', str(B / 'inputs' / canon), '--output', str(outp)])
    check(r.returncode == 0, f'audit80 {tag} rc')
    a, shipped = rd(outp), rd(OUT / f'AUDIT-80{tag}.json')
    for k in ('local_profile', 'local_mass', 'width_inventory', 'removed_helpers', 'corrections', 'status'):
        check(a[k] == shipped[k], f'audit80 {tag} {k}')
    check(a['local_mass'] == 5264 and a['removed_helpers'] == 80 and a['corrections'] == 64,
          f'audit80 {tag} headline')
    res['stages'][f'audit80-{tag}'] = dict(rc=0, seconds=dt, profile=a['local_profile'])
w80 = rd(OUT / 'words/BORROW-WORD-80base.json.gz')
w80['initial_corrections'][0]['coefficient'] = str(-Q(w80['initial_corrections'][0]['coefficient']))
tw = tmp / 'tampered80-word.json.gz'
tw.write_bytes(gzip.compress(json.dumps(w80, separators=(',', ':')).encode()))
r, _ = run([sys.executable, '-B', str(B / 'audit_local.py'), '--word', str(tw),
            '--base', str(B / 'inputs/gauge44.canonical.json.gz'),
            '--output', str(tmp / 'tampered80-audit.json')])
res['tampers']['T4_correction_sign'] = dict(rejected=r.returncode != 0)
check(r.returncode != 0, 'T4 tampered correction was ACCEPTED')
# census + solve receipts
cens = rd(OUT / 'LOW-CENSUS.json')
for canon, cen in cens.items():
    check(cen['n_low'] == 48 and len(cen['candidate_low_lenders']) == 32
          and cen['candidate_overlap_with_48_lenders'] == [], f'census {canon}')
    check(all(d['net_temp_zero'] and not d['other_indices'] and not d['mid_non_deferred_indices']
              and all(d['temp_source_unchanged'].values()) for d in cen['lows'].values()),
          f'census lows {canon}')
for stem, ncorr in [('49base', 2), ('80base', 64), ('80extra', 64)]:
    s = rd(OUT / f'LOW-SOLVE-{stem}.json')
    check(s['solved'] and s['handoff_all_exact'] and len(s['corrections']) == ncorr
          and not s['unhandled_terms'] and not s['y_error_targets_after'], f'low-solve {stem}')
singles = rd(OUT / 'LOW-SINGLES.json')['rows']
check(len(singles) == 48 and all(rw['mass_delta'] == -3 for rw in singles), 'low singles screen')
# 6. round 2: owner fill80 fresh check + exact global moment (loses to 2269)
r, dt = run([sys.executable, '-B', str(OUT / 'scripts/reconstruct80.py'),
             '--out', str(tmp / 'owners80')], cwd=ROOT)
check(r.returncode == 0 and 'PASS_OWNER_VERIFY' in r.stdout, 'reconstruct80')
H80 = {str(k): v for k, v in rd(tmp / 'owners80/PROFILE.json').items()}
gm80 = gmoment(H80)
check(gm80[0] > gm_old[1], 'expected exact result: actual FILL80 moment strictly ABOVE #2269')
res['stages']['owner-fill80'] = dict(
    rc=0, seconds=dt, global_profile=H80,
    idle=rd(tmp / 'owners80/RESULT.json')['idle'],
    global_moment_at_a2269=[str(gm80[0]), str(gm80[1])], global_moment_dec=float(gm80[1]),
    beats_2269=False, margin_above_2269_dec=float(gm80[0] - gm_old[1]))
# 7. round 2: exact pattern-LP dual obstruction for the 80 providers
flo = {r_: (ceiling.child_cost(r_, M, A)[0] if r_ else Q(0)) for r_ in range(49)}
lpj = rd(OUT / 'PATTERN-LP.json')
CAPS_ = {8: 49728, 16: 33152, 32: 33152, 48: 33152}
ROLES_ = {9: 181152, 8: 55944, 7: 23976, 5: 2664, 4: 2664}
WS_ = [9, 8, 7, 5, 4]
PATS_ = []
for cap_ in CAPS_:
    for aa in range(cap_ // 9 + 1):
        for bb in range((cap_ - 9 * aa) // 8 + 1):
            for cc in range((cap_ - 9 * aa - 8 * bb) // 7 + 1):
                for dd in range((cap_ - 9 * aa - 8 * bb - 7 * cc) // 5 + 1):
                    for ee in range((cap_ - 9 * aa - 8 * bb - 7 * cc - 5 * dd) // 4 + 1):
                        PATS_.append((cap_, (aa, bb, cc, dd, ee)))
check(len(PATS_) == lpj['patterns'] == 1163, 'pattern enumeration count')
def dual_min_slack(ybins, yroles):
    worst = None
    for cap_, cnt in PATS_:
        rem_ = cap_ - sum(w_ * x for w_, x in zip(WS_, cnt))
        s = flo[rem_] - ybins[cap_] - sum(yroles[w_] * x for w_, x in zip(WS_, cnt))
        if worst is None or s < worst: worst = s
    return worst
ybin = {int(c): Q(math.floor(v * 10**12), 10**12) for c, v in lpj['dual_variables']['bins'].items()}
yrole = {int(w_): Q(math.floor(v * 10**12), 10**12) for w_, v in lpj['dual_variables']['roles'].items()}
minslack = dual_min_slack(ybin, yrole)
check(minslack >= 0, 'floored rational dual must be feasible vs exact lower child costs')
dual_obj = (sum(ybin[c] * n for c, n in CAPS_.items())
            + sum(yrole[w_] * n for w_, n in ROLES_.items()))
prov80 = rd(OUT / 'BORROW-PROVIDERS80.json')
dis80 = rd(tmp / 'owners80/RESULT.json')['dispatch']
paid80 = {}
for pid, key in [('gauge44', 'gauge44'), ('extra', 'extra')]:
    for r_, n in prov80[pid]['actual_paid_profile'].items():
        paid80[r_] = paid80.get(r_, 0) + dis80[key] * n
paid80_lo = gmoment(paid80)[0]
total_lo = paid80_lo + dual_obj
check(total_lo > gm_old[1], 'expected exact obstruction: every legal 80-fill H moment exceeds #2269')
res['stages']['pattern-lp-dual'] = dict(
    patterns=len(PATS_), min_slack=str(minslack), min_slack_dec=float(minslack),
    idle_lower_bound=str(dual_obj), idle_lower_bound_dec=float(dual_obj),
    paid80_aggregate=paid80, total_lower_bound_dec=float(total_lo),
    margin_above_2269_dec=float(total_lo - gm_old[1]),
    scope='fractional pattern counts / windows+families relaxed; shipped dispatch counts; widths identical per provider index')
# T5: inflating one dual variable must break exact dual feasibility
yrole_bad = dict(yrole); yrole_bad[9] += Q(1, 1000)
res['tampers']['T5_dual_inflated'] = dict(rejected=dual_min_slack(ybin, yrole_bad) < 0)
check(res['tampers']['T5_dual_inflated']['rejected'], 'T5 inflated dual was ACCEPTED')
# 8. round 2 receipts
for stem in ('49base', '80base', '80extra'):
    bd = rd(OUT / f'BUILD-{stem}.json')
    for k in ('replay_rc', 'build_rc', 'audit_rc', 'controls_rc'):
        check(bd[k] == 0, f'BUILD-{stem} {k}')
for tag in ('base', 'extra'):
    steps = rd(OUT / f'NATIVE80-{tag}-STEPS.json')
    check([s['step'] for s in steps] == ['native', 'ledgers', 'local-replay', 'wrappers', 'phases']
          and all(s['exit_code'] == 0 for s in steps), f'native80 steps {tag}')
    res['stages'][f'native80-{tag} (receipt)'] = dict(seconds=sum(s['seconds'] for s in steps))
rb80 = rd(OUT / 'REBIND80.json')
check(rb80['new_paid']['gauge44'] == prov80['gauge44']['actual_paid_profile']
      and rb80['new_paid']['extra'] == prov80['extra']['actual_paid_profile'], 'rebind80 paid profiles')
res['stages']['rebind80 (receipt)'] = dict(new_paid=rb80['new_paid'])
lem = rd(OUT / 'LEMMAG80.json')
check(len(lem) == 2 and all(all(v == 0 for v in row['honest'][o].values())
      for row in lem.values() for o in ('forward', 'backward'))
      and all(all(row['borrow_mutants'].values()) for row in lem.values()), 'LEMMAG80 receipt')

res.update(status='PASS_MUSE_T74_BORROW_EXTEND_R2_VERIFY',
           engine_sha256=hashlib.sha256(
               (ROOT / 'research/complex-local-word-ceiling/ceiling.py').read_bytes()).hexdigest(),
           word_sha256={t: hashlib.sha256((OUT / 'words' / f'BORROW-WORD-48{t}.json.gz').read_bytes()).hexdigest()
                        for t in ('base', 'extra')},
           word80_sha256={t: hashlib.sha256((OUT / 'words' / f'BORROW-WORD-80{t}.json.gz').read_bytes()).hexdigest()
                          for t in ('base', 'extra')},
           claim='NO_KAPPA_R2: 80-alias words/natives verified; exact pattern-LP dual shows no legal 80-fill beats #2269 H moment (scoped, see README)')
(OUT / 'RESULT.json').write_text(json.dumps(res, indent=1) + '\n')
print(res['status'])
print(json.dumps(res['stages']['exact-prices'], indent=1))
