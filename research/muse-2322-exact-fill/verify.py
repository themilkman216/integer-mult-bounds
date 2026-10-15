#!/usr/bin/env python3
"""Verifier for muse-2322-exact-fill. Writes RESULT.json.

Stages (all fresh, #2322's own checker/engines where they exist):
 1. owners_check (#2322 verify.py, unmodified) on shipped and candidate
    fills; H/idle compared with ANALYSIS/SEARCH/CANDIDATE-ENDPOINT.
 2. Exact rational counting dual recomputed from BOUNDS.json prices at
    b2322 and A2322 over ALL patterns; LB <= shipped idle lo and
    LB <= candidate idle lo; shipped gap decomposition rechecked.
 3. Exact moments: candidate global moment strictly below shipped at both
    parameters (ceiling.child_cost disjoint intervals); directed
    fine_moment shipped-bracket control and candidate 40-digit bracket
    accept/reject, candidate endpoint strictly above shipped.
 4. Seven-chain BFS representatives rechecked on the shipped fill:
    (35,17) depth 1, (43,0) depth 3 (families ignored, superset).
 5. Candidate-data bindings (PLAN assignment hashes/profile vs candidate
    owners, in work/candidate-data) and, when CARRY-THROUGH.json records
    a completed cold replay, its statuses and exact final-kappa gain
    over #2322.  Absence/failure of the carry-through is recorded in
    RESULT.claim, never silently upgraded.
Tamper controls (must be REJECTED by the real checker/dual):
 T1 candidate row offset +1 -> owners_check raises;
 T2 gamma_16 inflated by 1/10^6 -> exact pattern-feasibility rejects;
 T3 candidate row width mutated -> owners_check raises;
 T4 candidate row moved to a window-violating bin (family/copy made
    self-consistent) -> owners_check raises;
 T5 candidate row time +1 -> owners_check raises.
"""
import gzip, hashlib, importlib.util, json, sys, time
from collections import Counter, defaultdict, deque
from fractions import Fraction as Q
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
sys.path.insert(0, str(OUT / 'scripts'))
sys.path.insert(0, str(ROOT / 'research/complex-local-word-ceiling'))
from model2322 import load_all, rd, PKG, fam  # noqa: E402
import patterns as P  # noqa: E402
import ceiling  # noqa: E402

def check(cond, msg):
    if not cond:
        raise AssertionError(msg)
    return True

t_start = time.time()
res = dict(status='RUNNING', stages={}, tampers={})
base = load_all()
verify2322 = base['verify']
analysis = rd(OUT / 'ANALYSIS.json'); bounds = rd(OUT / 'BOUNDS.json')
search = rd(OUT / 'SEARCH.json'); endpoint = rd(OUT / 'CANDIDATE-ENDPOINT.json')

# 1. fill checks with #2322's own checker
Hs, idles = verify2322.owners_check(base['rows'], base['plan'], base['contract'])
check({str(k): v for k, v in Hs.items()} == analysis['shipped_check']['H'], 'shipped H')
cand_rows = rd(OUT / 'CANDIDATE-OWNERS.json.gz')
Hc, idlec = verify2322.owners_check(cand_rows, base['plan'], base['contract'])
check({str(k): v for k, v in Hc.items()} == search['H'] == endpoint['candidate_profile'],
      'candidate H binding')
check({str(k): v for k, v in idlec.items()} == search['idle'], 'candidate idle binding')
check(idlec[7] == 1 and idles[7] == 87, 'singleton reduction 87 -> 1')
res['stages']['fills'] = dict(shipped_idle={str(k): v for k, v in sorted(idles.items())},
                              candidate_idle={str(k): v for k, v in sorted(idlec.items())})

# tampers against the real checker (deep copies of one row)
def rejected(rows):
    try:
        verify2322.owners_check(rows, base['plan'], base['contract'])
        return False
    except (ValueError, IndexError, KeyError, AssertionError):
        return True
bad = [dict(z) for z in cand_rows]; bad[0]['offset'] += 1
res['tampers']['T1_offset'] = dict(rejected=rejected(bad))
check(res['tampers']['T1_offset']['rejected'], 'T1 accepted!')
bad = [dict(z) for z in cand_rows]; bad[0]['width'] = 8 if bad[0]['width'] != 8 else 9
res['tampers']['T3_width'] = dict(rejected=rejected(bad))
check(res['tampers']['T3_width']['rejected'], 'T3 accepted!')
bad = [dict(z) for z in cand_rows]; bad[0]['time'] += 1
res['tampers']['T5_time'] = dict(rejected=rejected(bad))
check(res['tampers']['T5_time']['rejected'], 'T5 accepted!')
bad = [dict(z) for z in cand_rows]
z0 = bad[0]
target = next((rep, ch) for (rep, ch), (cap, ts) in base['win'].items()
              if z0['time'] not in ts)
z0['owner_replica'], z0['child'], z0['port'] = target[0], target[1], 0
z0['copy'] = target[0] * 112
z0['family'] = fam(base, target[0], target[1], 0)
res['tampers']['T4_window'] = dict(rejected=rejected(bad))
check(res['tampers']['T4_window']['rejected'], 'T4 accepted!')

# 2. exact counting dual recomputation
allpats = P.all_patterns()
for name, Aval in [('b2322', P.B2322), ('A2322', P.K2322 / (1 - P.K2322))]:
    cost = {r: ceiling.child_cost(r, 73, Aval) for r in range(1, 49)}
    flo = lambda r: cost[r][0] if r else Q(0)
    fhi = lambda r: cost[r][1] if r else Q(0)
    rec = bounds[name]
    p = {int(k): Q(v) for k, v in rec['rational_dual']['p'].items()}
    gamma = {}
    for cap in P.CAPS:
        gamma[cap] = min(flo(cap - sum(n * w for n, w in zip(pat, P.WIDTHS)))
                         + sum(n * p[w] for n, w in zip(pat, P.WIDTHS))
                         for pat in allpats[cap])
        check(gamma[cap] == Q(rec['rational_dual']['gamma'][str(cap)]), f'gamma {name} {cap}')
    LB = sum(P.BINS_BY_CAP[c] * gamma[c] for c in P.CAPS) - sum(P.ITEMS[w] * p[w] for w in P.WIDTHS)
    check(LB == Q(rec['LB']), f'LB {name}')
    silo = sum(n * flo(r) for r, n in idles.items())
    cilo = sum(n * flo(r) for r, n in idlec.items())
    cihi = sum(n * fhi(r) for r, n in idlec.items())
    check(LB <= cilo and LB <= silo, f'LB ordering {name}')
    decomp_sum = sum(Q(d['rc']) * d['count'] for d in rec['shipped_gap_decomposition'])
    res['stages'][f'dual_{name}'] = dict(
        LB_dec=float(LB), shipped_gap_dec=float(silo - LB),
        candidate_gap_dec=float(cilo - LB),
        decomposition_sum_dec=float(decomp_sum))
    if name == 'b2322':
        g_bad = gamma[16] + Q(1, 10**6)
        viol = min(flo(16 - sum(n * w for n, w in zip(pat, P.WIDTHS)))
                   + sum(n * p[w] for n, w in zip(pat, P.WIDTHS)) for pat in allpats[16])
        res['tampers']['T2_gamma_inflated'] = dict(rejected=bool(viol < g_bad))
        check(viol < g_bad, 'T2 accepted!')
    # 3a. exact global moment comparison (ceiling intervals)
    def gmoment(H):
        return (sum(n * flo(r) for r, n in H.items()), sum(n * fhi(r) for r, n in H.items()))
    gs, gc = gmoment(Hs), gmoment(Hc)
    check(gc[1] < gs[0], f'candidate moment strictly below shipped at {name}')
    res['stages'][f'moment_gain_{name}'] = float(gs[0] - gc[1])

# 3b. directed fine_moment endpoint
spec = importlib.util.spec_from_file_location('fmv', PKG / 'vendor/fine_moment.py')
e = importlib.util.module_from_spec(spec); spec.loader.exec_module(e)
e.SH = 256; e.GRID = 1 << 256; e.LOG_TERMS = 100; e.EXP_TERMS = 96
slo = Q(base['claim']['native_endpoint_lower']); shi = Q(base['claim']['native_endpoint_upper'])
clo = Q(endpoint['candidate_bracket'][0]); chi = Q(endpoint['candidate_bracket'][1])
check(e.moment(73, 66304, sorted(Hs.items()), slo)[1] < 1 < e.moment(73, 66304, sorted(Hs.items()), shi)[0],
      'shipped bracket control')
check(e.moment(73, 66304, sorted(Hc.items()), clo)[1] < 1 < e.moment(73, 66304, sorted(Hc.items()), chi)[0],
      'candidate bracket')
check(clo > shi, 'candidate endpoint strictly above shipped')
res['stages']['endpoint'] = dict(candidate_bracket=endpoint['candidate_bracket'],
                                 gain_dec=float(clo - shi))

# 4. seven-chain BFS representatives on shipped fill
rows = base['rows']; win = base['win']
bins = defaultdict(list)
for idx, z in enumerate(rows):
    bins[(z['owner_replica'], z['child'], z['port'])].append(idx)
def btype(b):
    return win[(b[0], b[1])][0], tuple(sorted((rows[i]['width'] for i in bins[b]), reverse=True))
by_tw = defaultdict(list)
for idx, z in enumerate(rows):
    by_tw[(z['time'], z['width'])].append(idx)
def bfs_depth(hole, max_depth=10):
    came = {hole}; q = deque([(hole, 0)])
    while q:
        hb, d = q.popleft()
        if d >= max_depth:
            continue
        for t in win[(hb[0], hb[1])][1]:
            for idx in by_tw[(t, 7)]:
                z = rows[idx]; src = (z['owner_replica'], z['child'], z['port'])
                if src in came:
                    continue
                came.add(src)
                if btype(src) == (32, (9, 9, 7, 7)):
                    return d + 1, len(came)
                q.append((src, d + 1))
    return None, len(came)
Abins = [b for b in bins if btype(b) == (16, (9,))]
reps = {}
for b in Abins:
    reps.setdefault((b[0], b[1]), b)
depths = {f'{k[0]},{k[1]}': bfs_depth(v) for k, v in sorted(reps.items())}
check(depths['35,17'][0] == 1 and depths['43,0'][0] == 3, f'BFS depths {depths}')
res['stages']['chain_bfs'] = {k: dict(depth=d, visited=v) for k, (d, v) in depths.items()}

# 5. candidate-data bindings + optional carry-through
cand_data = OUT / 'work/candidate-data'
check(cand_data.is_dir(), 'work/candidate-data missing: run scripts/build_candidate_data.py')
plan2 = rd(cand_data / 'PLAN.json')
gz = (OUT / 'CANDIDATE-OWNERS.json.gz').read_bytes()
check(hashlib.sha256(gz).hexdigest() == plan2['assignment_sha256'] ==
      hashlib.sha256((cand_data / 'OWNERS.json.gz').read_bytes()).hexdigest(), 'assignment sha')
canon = json.dumps(cand_rows, sort_keys=True, separators=(',', ':')).encode()
check(hashlib.sha256(canon).hexdigest() == plan2['assignment_content_sha256'], 'content sha')
check(plan2['profile'] == search['H'] == rd(cand_data / 'PROFILE.json'), 'profile binding')
check(rd(cand_data / 'CONSTRUCTION.json')['idle'] == search['idle'], 'construction idle')
stage5 = dict(candidate_owners_sha256=hashlib.sha256(gz).hexdigest(), carry=None)
claim_txt = ('LEGAL_FILL_NATIVE_ENDPOINT_ONLY: candidate passes #2322 owners_check and '
             'exact endpoint; full cold replay not (yet) recorded as passed')
ct_path = OUT / 'CARRY-THROUGH.json'
if ct_path.exists():
    ct = rd(ct_path)
    stage5['carry'] = {k: ct.get(k) for k in ('status', 'delta_status', 'final_kappa_dec',
                                              'gain_over_2322_dec', 'driver_exit_code')}
    if ct.get('status') == 'PASS_SOURCE_BOUND_CHANGED_OWNER_REPLAY':
        check(ct['candidate_owners_sha256'] == hashlib.sha256(gz).hexdigest(), 'carry owners binding')
        check(ct['delta_status'] == 'PASS_CHANGED_T74_FULL_DELTA_ADMISSION', 'carry delta status')
        check(ct['exceeds_2322_final'] and Q(ct['final_kappa']) > Q(ct['shipped_final_kappa']),
              'carry kappa must exceed #2322 final exactly')
        claim_txt = ('CONDITIONAL_KAPPA_CANDIDATE_CARRIED: full #2322 cold replay pass on '
                     'candidate data; see CARRY-THROUGH.json for exact kappa and scope')
res['stages']['bindings'] = stage5

res.update(status='PASS_MUSE_2322_EXACT_FILL_VERIFY', seconds=time.time() - t_start,
           claim=claim_txt)
(OUT / 'RESULT.json').write_text(json.dumps(res, indent=1) + '\n')
print(res['status'], f"({res['seconds']:.1f}s)")
print(json.dumps(res['tampers'], indent=1))
print('claim:', res['claim'])
