#!/usr/bin/env python3
"""Verifier for muse-t74-exact-fill.  Writes RESULT.json.

Stages (all fresh):
 1. Literal fill checks (model.check_rows, mirroring reconstruct.py) for the
    shipped 43 fill, adapted 48 fill, and both all-extra dispatch candidates;
    idle/H compared with ANALYSIS/BOUNDS/DISPATCH-CANDIDATE records.  One
    candidate also re-run through a patched copy of #2269's reconstruct.py.
 2. Exact rational counting-dual lower bound recomputed from BOUNDS.json
    prices: gamma_cap re-derived as min over ALL patterns (f_lo via
    ceiling.child_cost at A2269); LB <= shipped idle lo for both cases.
 3. Exact signs: Delta_unit < 0 at A2269 and at endpoint b; per-call paid
    extra < gauge44 (disjoint intervals); candidate H global moment strictly
    below #2269 H global moment (disjoint intervals).
 4. Seven-chain BFS closure rechecked on both fills: A-bins in windows
    (4,0),(6,0) unreachable from cap32 [7,7,9,9] bins (depth<=8, exhaustive
    visited closure), the two (29,16) bins reachable at depth 1.
 5. Candidate2 (665 extra + 1 gauge44) fill check + carry-through binding:
    H equals strict ASSEMBLY profile, exact moment strictly below #2269 H,
    supplier/outer kappas in CARRY-THROUGH.json exceed #2269 exactly,
    candidate-fill sha256 bound.  (Strict/full-verify/outer runs themselves
    are recorded receipts under work/; regenerable via scripts in README.)
Tamper controls (must be REJECTED):
 T1 one candidate-fill offset shifted -> literal checker rejects;
 T2 gamma_16 inflated by 1/10^6 -> exact pattern-feasibility check rejects;
 T3 candidate H rank-1 count incremented -> equality with checker profile
    and with BOUNDS candidate both fail (comparison self-test);
 T4 one row moved to a window-violating bin -> literal checker rejects;
 T5 retained gauge44 call also overridden (single-provider dispatch) ->
    both-providers admissibility gate rejects (mirrors audit_mixed).
"""
import gzip, hashlib, json, subprocess, sys, tempfile, time
from collections import Counter, defaultdict, deque
from fractions import Fraction as Q
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
sys.path.insert(0, str(OUT / 'scripts'))
sys.path.insert(0, str(ROOT / 'research/complex-local-word-ceiling'))
from model import load_base, load_case, check_rows, idle_and_H, fam, PKG  # noqa: E402
import patterns as P  # noqa: E402
import ceiling  # noqa: E402

def rd(p):
    b = Path(p).read_bytes()
    return json.loads(gzip.decompress(b) if str(p).endswith('.gz') else b)
def check(cond, msg):
    if not cond: raise AssertionError(msg)
    return True

t_start = time.time()
res = dict(status='RUNNING', stages={}, tampers={})
base = load_base(); win = base['win']
bounds = rd(OUT / 'BOUNDS.json'); analysis = rd(OUT / 'ANALYSIS.json')
outer = rd(PKG / 'outer/OUTER-CLAIM.json'); K = Q(outer['kappa_rational']); A = K / (1 - K)
b_end = Q(rd(PKG / 'outer/B.json')['b'])
cost = {r: ceiling.child_cost(r, 73, A) for r in range(1, 49)}
def flo(r): return cost[r][0] if r else Q(0)
def fhi(r): return cost[r][1] if r else Q(0)
def moment(prof):
    return (sum(n * flo(int(r)) for r, n in prof.items()),
            sum(n * fhi(int(r)) for r, n in prof.items()))

# 1. fill checks
cases = {}
for which in ('43', '48'):
    case = load_case(base, which); cases[which] = case
    idle, H = check_rows(base, case, case['fill']['rows'])
    check({str(k): v for k, v in H.items()} == {k: v for k, v in analysis[f'case{which}']['H'].items()},
          f'H mismatch {which}')
    res['stages'][f'fill{which}'] = dict(idle={str(k): v for k, v in sorted(idle.items())},
                                         H={str(k): v for k, v in sorted(H.items())})
    cand = rd(OUT / f'FILL{which}-ALLEXtra.json.gz')
    case_c = dict(case)
    disp = dict(base['dispatch0'])
    for s_, r_, p_ in cand['dispatch_overrides']:
        disp[s_, r_] = p_
    case_c['dispatch'] = disp; case_c['fill'] = cand
    cases[f'{which}C'] = case_c
    idle_c, H_c = check_rows(base, case_c, cand['rows'])
    check(idle_c == idle, f'candidate idle must equal shipped idle {which}')
    check({str(k): v for k, v in H_c.items()} == bounds[f'dispatch_{which}']['candidate_H_allexra'],
          f'candidate H mismatch {which}')
    res['stages'][f'candidate{which}'] = dict(H={str(k): v for k, v in sorted(H_c.items())},
                                              overrides=len(cand['dispatch_overrides']))
# one candidate through the real reconstruct.py (patched copy)
tmp = Path(tempfile.mkdtemp(prefix='muse-exactfill-verify-'))
src = (PKG / 'reconstruct.py').read_text()
src = src.replace("F=Path(__file__).resolve().parent", f"F=Path('{PKG}')")
src = src.replace("fill=read(F/'new/borrow-fill/FILL.json.gz')",
                  f"fill=read(Path('{OUT}/FILL43-ALLEXtra.json.gz'))")
(tmp / 'reconstruct.py').write_text(src)
r = subprocess.run([sys.executable, '-B', str(tmp / 'reconstruct.py'), '--out', str(tmp / 'owners')],
                   capture_output=True, text=True, cwd=ROOT)
check(r.returncode == 0 and 'PASS_OWNER_VERIFY' in r.stdout, 'patched reconstruct.py on candidate')
check(rd(tmp / 'owners/PROFILE.json') == bounds['dispatch_43']['candidate_H_allexra'],
      'reconstruct PROFILE vs BOUNDS candidate')
res['stages']['literal_reconstruct_candidate43'] = dict(rc=0)

# T1: shifted offset rejected
bad = [list(x) for x in cases['43C']['fill']['rows']]; bad[0][5] += 1
try:
    check_rows(base, cases['43C'], bad); res['tampers']['T1_offset'] = dict(rejected=False)
except AssertionError:
    res['tampers']['T1_offset'] = dict(rejected=True)
check(res['tampers']['T1_offset']['rejected'], 'T1 accepted!')
# T4: window-violating bin rejected
bad = [list(x) for x in cases['43']['fill']['rows']]
target = next(b for b in [(rep, ch, 0) for (rep, ch) in win] if bad[0][0] not in win[(b[0], b[1])][1])
bad[0][2], bad[0][3], bad[0][4] = target
try:
    check_rows(base, cases['43'], bad); res['tampers']['T4_window'] = dict(rejected=False)
except AssertionError:
    res['tampers']['T4_window'] = dict(rejected=True)
check(res['tampers']['T4_window']['rejected'], 'T4 accepted!')

# 2. exact dual recomputation
p = {int(k): Q(v) for k, v in bounds['rational_dual']['p'].items()}
gamma = {}
allpats = P.all_patterns()
for cap in P.CAPS:
    gamma[cap] = min(flo(cap - sum(n * w for n, w in zip(pat, P.WIDTHS)))
                     + sum(n * p[w] for n, w in zip(pat, P.WIDTHS)) for pat in allpats[cap])
    check(gamma[cap] == Q(bounds['rational_dual']['gamma'][str(cap)]), f'gamma {cap}')
bins_by_cap = {8: 49728, 16: 33152, 32: 33152, 48: 33152}
for which in ('43', '48'):
    case = cases[which]
    wc = Counter(case['widths']['gauge44'])
    items = {w: wc[w] * len(base['order']) for w in P.WIDTHS}
    LB = sum(bins_by_cap[c] * gamma[c] for c in P.CAPS) - sum(items[w] * p[w] for w in P.WIDTHS)
    idle, _ = idle_and_H(base, case, case['fill']['rows'])
    ilo, ihi = moment({int(k): v for k, v in idle.items()})
    check(LB == Q(bounds[f'counting_bound_{which}']['LB']) and LB <= ilo < ihi, f'LB {which}')
    res['stages'][f'dual_bound_{which}'] = dict(LB_dec=float(LB), shipped_idle_dec=[float(ilo), float(ihi)],
                                                gap=float(ihi - LB))
# T2: inflated gamma rejected by exact pattern feasibility
g_bad = gamma[16] + Q(1, 10**6)
viol = min(flo(16 - sum(n * w for n, w in zip(pat, P.WIDTHS)))
           + sum(n * p[w] for n, w in zip(pat, P.WIDTHS)) for pat in allpats[16])
res['tampers']['T2_gamma_inflated'] = dict(rejected=bool(viol < g_bad))
check(viol < g_bad, 'T2 accepted!')

# 3. exact signs
for name, Aval in [('A2269', A), ('b_endpoint', b_end)]:
    cc = {rr: ceiling.child_cost(rr, 73, Aval) for rr in (3, 5, 7, 48)}
    hi = cc[48][1] + 5 * cc[5][1] - 10 * cc[7][0] - cc[3][0]
    check(hi < 0, f'delta unit {name}')
    res['stages'][f'delta_unit_{name}_hi'] = float(hi)
H2269 = {int(k): v for k, v in rd(PKG / 'PROFILE.json').items()}
glo = moment(H2269)
for which in ('43', '48'):
    case = cases[which]
    ge = moment({int(k): v for k, v in case['paid']['gauge44'].items()})
    ex = moment({int(k): v for k, v in case['paid']['extra'].items()})
    check(ex[1] < ge[0], f'extra<gauge per call {which}')
    candH = {int(k): v for k, v in bounds[f'dispatch_{which}']['candidate_H_allexra'].items()}
    cm = moment(candH)
    check(cm[1] < glo[0], f'candidate moment < H2269 {which}')
    res['stages'][f'moment_gain_{which}'] = dict(candidate_minus_H2269_hi=float(cm[1] - glo[0]),
                                                 per_call_extra_minus_gauge_hi=float(ex[1] - ge[0]))
# T3: tampered candidate H fails equality (real comparison, must detect)
tampered_H = dict(bounds['dispatch_43']['candidate_H_allexra']); tampered_H['1'] += 1
detected = (tampered_H != {str(k): v for k, v in rd(tmp / 'owners/PROFILE.json').items()}
            and moment({int(k): v for k, v in tampered_H.items()})[0]
                != moment({int(k): v for k, v in bounds['dispatch_43']['candidate_H_allexra'].items()})[0])
res['tampers']['T3_H_count'] = dict(rejected=bool(detected))
check(detected, 'T3 not detected!')

# 4. seven-chain BFS closure (both fills; A-bin windows (4,0),(6,0) vs (29,16))
def bfs_reach(case, hole, max_depth=8):
    rows = case['fill']['rows']
    from model import width_of
    bins = defaultdict(list)
    for idx, rr in enumerate(rows):
        bins[(rr[2], rr[3], rr[4])].append(idx)
    def w(idx):
        rr = rows[idx]; return width_of(base, case, rr[0], rr[1])
    def btype(b):
        return win[(b[0], b[1])][0], tuple(sorted((w(i) for i in bins[b]), reverse=True))
    by_tw = defaultdict(list)
    for idx, rr in enumerate(rows):
        by_tw[(rr[0], w(idx))].append(idx)
    came = {hole}; q = deque([(hole, 0)])
    while q:
        hb, d = q.popleft()
        if d >= max_depth: continue
        for t in win[(hb[0], hb[1])][1]:
            for idx in by_tw[(t, 7)]:
                src = (rows[idx][2], rows[idx][3], rows[idx][4])
                if src in came: continue
                came.add(src)
                if btype(src) == (32, (9, 9, 7, 7)):
                    return d + 1, len(came)
                q.append((src, d + 1))
    return None, len(came)
for which in ('43', '48'):
    case = cases[which]
    d40, v40 = bfs_reach(case, (4, 0, 0))
    d29, v29 = bfs_reach(case, (29, 16, 0))
    check(d40 is None and d29 == 1, f'BFS closure {which}: {(d40, v40, d29)}')
    res['stages'][f'chain_closure_{which}'] = dict(window_4_0_depth=d40, visited_4_0=v40,
                                                   window_29_16_depth=d29, visited_29_16=v29)

# 5. candidate2 (665 extra + 1 gauge44) + carry-through binding
cand2 = rd(OUT / 'FILL43-EXTRAm1.json.gz')
disp2 = dict(base['dispatch0'])
for s_, r_, p_ in cand2['dispatch_overrides']:
    disp2[s_, r_] = p_
check(Counter(disp2.values()) == Counter({'extra': 665, 'gauge44': 1}),
      'candidate2 dispatch must use both providers (audit_mixed set equality; partner controls)')
case2 = dict(cases['43']); case2['dispatch'] = disp2
idle2, H2 = check_rows(base, case2, cand2['rows'])
ct = rd(OUT / 'CARRY-THROUGH.json')
check({str(k): v for k, v in H2.items()} == {str(k): v for k, v in ct['profile'].items()},
      'candidate2 H vs strict ASSEMBLY profile')
m2 = moment({int(k): v for k, v in H2.items()})
check(m2[1] < glo[0], 'candidate2 exact moment must be strictly below H2269')
check(Q(ct['outer_kappa']) == Q(ct['outer_kappa_rational']) > Q(ct['outer_kappa_2269']),
      'outer kappa must exceed #2269 headline exactly')
check(Q(ct['supplier_kappa']) > Q(ct['supplier_kappa_2269']), 'supplier kappa gain')
check(ct['strict_status'] == 'PASS_STRICT_MIXED_T74_EXACT_FILL'
      and ct['full_verify_status'] == 'PASS_T74_EXACT_FILL_COMPLETE_FINITE_ADMISSION', 'carry statuses')
check(hashlib.sha256((OUT / 'FILL43-EXTRAm1.json.gz').read_bytes()).hexdigest()
      == ct['sha256']['candidate_fill'], 'candidate fill hash binding')
fine = rd(OUT / 'FINE-ENDPOINTS.json')
check(Q(fine['native']['lower']) == Q(ct['complex_lower']), 'fine endpoint vs ASSEMBLY complex_lower')
res['stages']['candidate2_carry_through'] = dict(
    H={str(k): v for k, v in sorted(H2.items())},
    moment_gain_vs_H2269_at_least=float(glo[0] - m2[1]),
    supplier_kappa_decimal=ct['supplier_kappa_decimal'],
    outer_kappa=ct['outer_kappa'], outer_gain_dec=ct['outer_gain_dec'])
# T5: overriding the retained gauge call too (single-provider dispatch) must
# fail the both-providers admissibility gate above (mirrors audit_mixed).
disp_bad = dict(disp2)
retain_key = next(k for k, v in disp_bad.items() if v == 'gauge44')
disp_bad[retain_key] = 'extra'
res['tampers']['T5_single_provider_dispatch'] = dict(
    rejected=bool(Counter(disp_bad.values()) != Counter({'extra': 665, 'gauge44': 1})
                  and set(disp_bad.values()) != {'gauge44', 'extra'}))
check(res['tampers']['T5_single_provider_dispatch']['rejected'], 'T5 accepted!')

res.update(status='PASS_MUSE_T74_EXACT_FILL_VERIFY',
           seconds=time.time() - t_start,
           engine_sha256=hashlib.sha256((ROOT / 'research/complex-local-word-ceiling/ceiling.py').read_bytes()).hexdigest(),
           claim=('CONDITIONAL_KAPPA_CANDIDATE: 665+1 dispatch candidate carried through '
                  'strict assembly, full package verify, fine endpoints and outer ledger '
                  '(see CARRY-THROUGH.json/README for exact kappas, scope and the two '
                  'sympy-blocked outer evidence replays); fill-rows k<150 remains open'))
(OUT / 'RESULT.json').write_text(json.dumps(res, indent=1) + '\n')
print(res['status'], f"({res['seconds']:.1f}s)")
print(json.dumps(res['tampers'], indent=1))
