#!/usr/bin/env python3
"""Round-2 low-alias derivation: pair records + exact initial-compensation solve.

Starting from witness_48_{tag}.json (round 1), appends candidate low pairs
(helper:lender) in the order given, deriving per pair:
  * deleted_echo_indices / deleted_prefix_indices / early_prefix_rewrites
    from LOW-CENSUS.json (scripts/low_census.py must run first);
  * retirement_basis/frame/dimension and handoff_basis from a frame-only
    simulation in pr2226_replay order (same method as round-1 nominate.py,
    generalised to low pairs and their rewrites/deletions);
  * G_columns via bw_gauss.change(retirement_basis, handoff_basis, 9).

Then solves for the frame-zero initial compensation terms exactly: a
diagnostic free-operator replay (same gate order as pr2226_replay.py, but
recording instead of asserting) is run with no corrections; the final Y
error per target must consist solely of terms (lender, (op,)) with dyadic
coefficients, for op the candidate pair that lent `lender`.  The correction
for each such term is its negation.  The diagnostic is re-run with the
derived corrections and must give Y == Y + X exactly, and every low lender
must be exactly its own initial input at its handoff.  Any other error term
shape falsifies the candidate set and is reported, not patched.

This is a solver/builder, not an independent checker: the emitted witness
is only claimed after the vendored exact replay, build_word, audit_local
and borrow_controls pass on it (scripts/build_low.py).
"""
import argparse, gzip, json, sys, time
from fractions import Fraction as Q
from pathlib import Path

B = Path('research/gmx-t74-borrow43/new/borrow')
OUT = Path('research/muse-t74-borrow-extend')
sys.path.insert(0, 'research/gmx-t74-borrow43/new/code/borrow')
import bw_gauss  # noqa: E402

def span(basis):
    s = {0}
    for x in basis: s |= {t ^ x for t in list(s)}
    return frozenset(s)
def dim(s): return len(s).bit_length() - 1
def incident(e): return e[1:3] if e[0] == 'add' else e[1:2]
def frame_basis(F):
    b = {}
    for x in F:
        while x:
            j = x.bit_length()
            if j not in b: b[j] = x; break
            x ^= b[j]
    return [b[j] for j in sorted(b, reverse=True)]
def add(dst, src, c):
    for k, val in list(src.items()):
        z = dst.get(k, Q(0)) + c * val
        if z: dst[k] = z
        elif k in dst: del dst[k]
def warp(row, op):
    return {(var, word[1:] if word and word[0] == -op else (op,) + word): val
            for (var, word), val in row.items()}

CANON = {'base': 'gauge44.canonical.json.gz', 'extra': 'extra.canonical.json.gz'}

def load(tag):
    w = json.loads(gzip.decompress((B / 'inputs' / CANON[tag]).read_bytes()))
    blocks = json.loads((B / 'inputs/blocks.json').read_text())['sources'][0]['blocks']
    wit = json.loads((OUT / f'witness_48_{tag}.json').read_text())
    census = json.loads((OUT / 'LOW-CENSUS.json').read_text())[CANON[tag]]['lows']
    return w, blocks, wit, census

def deferred_map(w, blocks):
    deferred, skip = {}, set()
    for b in blocks:
        ss, part = set(b['helpers']), []
        for i in range(b['first_correction'], b['first_input']):
            e = w['B'][i]
            if set(incident(e)) <= ss: part.append(e); skip.add(i)
        deferred[b['first_input']] = part
    return deferred, skip

def build_pairs(w, blocks, wit, census, cand):
    """cand: list of (helper, lender). Returns (new pair records, sim info)."""
    v, n = w['v'], 2 * w['v'] + w['R']
    frames = list(map(span, w['frames']))
    deferred, skip = deferred_map(w, blocks)
    early_tail = {}
    for e in wit['early_tail_events']: early_tail.setdefault(e['before_B'], []).append(e['gate'])
    # deletions/rewrites from existing pairs (none low in 48) plus candidates
    deleted, rewrites = set(), {}
    for h, L in cand:
        d = census[str(h)]
        deleted |= set(d['deleted_prefix_indices'])
        for k, gates in d['early_prefix_rewrites'].items(): rewrites[int(k)] = gates
    starts_existing = {}
    for i, x in enumerate(wit['pairs']):
        starts_existing.setdefault(x.get('handoff_B', x['deadline']), []).append(x)
    cand_by_deadline = {}
    dl = {}
    for h, L in cand:
        blk = next(b for b in blocks if h in b['helpers'])
        dl[h] = blk['first_input']
        cand_by_deadline.setdefault(dl[h], []).append((h, L))
    # frame-only simulation in replay order
    cur = {r: frames[w['start'][r]] for r in range(n)}
    mapping = {}
    def resolve(r): return mapping.get(r, r)
    def climb(e):
        f = frames[e[-1]]
        for r in incident(e):
            rr = resolve(r)
            assert rr in cur and cur[rr] <= f, ('nonnested/missing', e, rr)
            cur[rr] = f
    for e in w['precondition'] + w['compensation']: climb(e)
    for e in w['A']: climb(e)
    levels = {r: w['start'][r] for r in range(v, 2 * v)}
    for e in w['precondition'] + w['compensation']:
        for r in incident(e):
            if v <= r < 2 * v: levels[r] = e[-1]
    for r, f in levels.items(): cur[r] = frames[f]
    removed48 = {p['register'] for p in wit['pairs']}
    # registers removed in 48 are still in cur here; their gates resolve after
    # mapping is set at their deadline; before that, gates incident to them in
    # B are either deferred (executed at deadline) or early echoes for highs
    # (none).  Guards below follow replay scalar(): a gate touching an
    # unmapped removed register would fail there too.
    span2frame = {}
    for fi, fr in enumerate(w['frames']): span2frame.setdefault(span(fr), fi)
    # retirement_B_event in #2226's audit_witness sense: last ordinary B
    # index incident to the lender, then each moved early-tail gate sets
    # last[r] = before_B - 1 for both operands (in witness order).
    last_raw = {}
    for i, e in enumerate(w['B']):
        for r in incident(e): last_raw[r] = i
    for t in wit['early_tail_events']:
        for r in incident(t['gate']): last_raw[r] = t['before_B'] - 1
    last_ordinary = {L: last_raw.get(L, -1) for (h, L) in cand}
    new_pairs, sim = [], {}
    for i, e in enumerate(w['B']):
        for t in early_tail.get(i, []): climb(t)
        for x in starts_existing.get(i, []):
            cur[x['borrow_from']] = span(x['handoff_basis'])
            mapping[x['register']] = x['borrow_from']
        for (h, L) in cand_by_deadline.get(i, []):
            snap = cur[L]
            # first gate frame F1, emit_word search
            F1 = None
            for j in range(i, len(w['B'])):
                gl = list(deferred.get(j, [])) + list(rewrites.get(j, []))
                if j not in skip and j not in deleted: gl.append(w['B'][j])
                for g in gl:
                    if h in incident(g): F1 = frames[g[-1]]; break
                if F1 is not None: break
            assert F1 is not None, h
            fb = frame_basis(F1); du = dim(snap)
            assert 1 <= du <= len(fb), (h, L, du, len(fb))
            E_basis = fb[:du]
            blk = next(b for b in blocks if h in b['helpers'])
            sib = next((p for p in wit['pairs'] if p['base'] == blk['base']), None)
            common = sib['common_basis'] if sib else blk['common_frame']
            d = census[str(h)]
            rec = dict(
                register=h, base=blk['base'], common_basis=common,
                dimension=len(common), deadline=i,
                deleted_echo_indices=d['deleted_echo_indices'],
                deleted_prefix_indices=d['deleted_prefix_indices'],
                early_prefix_rewrites=d['early_prefix_rewrites'],
                low=True, borrow_from=L,
                retirement_B_event=last_ordinary[L],
                retirement_frame=span2frame[snap], retirement_dimension=du,
                old_final_dimension=len(w['frames'][w['final'][L]]),
                handoff_B=i, handoff_basis=E_basis, handoff_paid_rank=0,
                anticipate=True, retirement_basis=frame_basis(snap))
            new_pairs.append(rec)
            sim[h] = dict(lender=L, deadline=i, retirement_dimension=du,
                          f1_dim=len(fb), retirement_B_event=last_ordinary[L])
            cur[L] = span(E_basis); mapping[h] = L
        for d_ in deferred.get(i, []): climb(d_)
        for d_ in rewrites.get(i, []): climb(d_)
        if i not in skip and i not in deleted: climb(e)
    # candidate order as given (operator order), records may have been
    # appended in deadline order; return in the caller's order
    by_h = {p['register']: p for p in new_pairs}
    return [by_h[h] for h, _ in cand], sim

def diagnostic(w, blocks, pairs, early_tail_events, initial_corrections):
    """Free-operator forward replay to end of B. Returns (y_errors, handoffs)."""
    v, n = w['v'], 2 * w['v'] + w['R']
    frames = list(map(span, w['frames']))
    removed = {x['register'] for x in pairs}
    active = [r for r in range(n) if r not in removed]
    val = {r: {(r, ()): Q(1)} for r in active}
    for term in initial_corrections:
        add(val[term['target']], {(term['source'], tuple(term['operator_word'])): Q(1)},
            Q(term['coefficient']))
    mapping = {}
    def resolve(r): return mapping.get(r, r)
    def scalar(e):
        rs = [resolve(r) for r in incident(e)]
        assert all(r in val for r in rs), ('unallocated', e)
        if e[0] == 'add': add(val[rs[0]], val[rs[1]], Q(e[3], e[4]))
        else:
            c = Q(e[2], e[3]); val[rs[0]] = {k: c * x for k, x in val[rs[0]].items()}
    for e in w['precondition'] + w['compensation']:
        if e[0] == 'add' and e[2] in removed: continue
        scalar(e)
    for e in w['A']: scalar(e)
    for e in w['cut']: scalar(e)
    deferred, skip = deferred_map(w, blocks)
    starts = {}
    for i, x in enumerate(pairs): starts.setdefault(x.get('handoff_B', x['deadline']), []).append((i + 1, x))
    deleted = {i for x in pairs if x['low'] for i in x.get('deleted_prefix_indices', x['deleted_echo_indices'])}
    rewrites = {int(i): gates for x in pairs if x['low'] for i, gates in x.get('early_prefix_rewrites', {}).items()}
    early_tail = {}
    for e in early_tail_events: early_tail.setdefault(e['before_B'], []).append(e['gate'])
    handoffs = {}
    for i, e in enumerate(w['B']):
        for t in early_tail.get(i, []): scalar(t)
        for op, x in starts.get(i, []):
            old, new = x['borrow_from'], x['register']
            if x['low']:
                handoffs[op] = dict(register=new, lender=old,
                                    val={f'{var}|{",".join(map(str, word))}': str(c)
                                         for (var, word), c in sorted(val[old].items(), key=lambda kv: str(kv[0]))},
                                    exact=(val[old] == {(old, ()): Q(1)}))
            val[old] = warp(val[old], op); mapping[new] = old
        for d_ in deferred.get(i, []): scalar(d_)
        for d_ in rewrites.get(i, []): scalar(d_)
        if i not in skip and i not in deleted: scalar(e)
    for t in early_tail.get(len(w['B']), []): scalar(t)
    errors = {}
    for r in range(v, 2 * v):
        exp = {(r, ()): Q(1), (r - v, ()): Q(1)}
        err = dict(val[r])
        for k, c in exp.items():
            z = err.get(k, Q(0)) - c
            if z: err[k] = z
            else: err.pop(k, None)
        if err: errors[r] = err
    return errors, handoffs

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--tag', required=True, choices=['base', 'extra'])
    ap.add_argument('--pairs', required=True, help='helper:lender,... in operator order')
    ap.add_argument('--out', required=True, help='output witness filename in package dir')
    ap.add_argument('--report', required=True)
    a = ap.parse_args(); t0 = time.monotonic()
    cand = [tuple(map(int, s.split(':'))) for s in a.pairs.split(',')]
    w, blocks, wit, census = load(a.tag)
    # static candidate checks
    used_l = {p['borrow_from'] for p in wit['pairs']}
    removed = {p['register'] for p in wit['pairs']}
    assert len({h for h, _ in cand}) == len(cand) and len({L for _, L in cand}) == len(cand)
    for h, L in cand:
        assert h not in removed and str(h) in census, h
        assert L not in used_l and L not in removed, L
        assert len(w['frames'][w['start'][L]]) == 0, ('lender start not frame zero', L)
        assert len(w['frames'][w['final'][L]]) == 4, ('lender final dim', L)
    new_pairs, sim = build_pairs(w, blocks, wit, census, cand)
    pairs_all = wit['pairs'] + new_pairs
    op_of_lender = {p['borrow_from']: i + 1 for i, p in enumerate(pairs_all) if p['low']}
    errors, handoffs = diagnostic(w, blocks, pairs_all, wit['early_tail_events'], [])
    corrections, unhandled = [], []
    for r, err in sorted(errors.items()):
        for (var, word), c in sorted(err.items(), key=lambda kv: str(kv[0])):
            dy = (c.denominator & (c.denominator - 1)) == 0
            if var in op_of_lender and word == (op_of_lender[var],) and dy:
                corrections.append(dict(target=r, source=var,
                                        operator_word=[op_of_lender[var]],
                                        coefficient=str(-c)))
            else:
                unhandled.append(dict(target=r, var=var, word=list(word), coeff=str(c)))
    corrections.sort(key=lambda t: (t['target'], t['source']))
    errors2, handoffs2 = ({}, {})
    if not unhandled:
        errors2, handoffs2 = diagnostic(w, blocks, pairs_all, wit['early_tail_events'], corrections)
    handoff_exact = all(hh['exact'] for hh in handoffs.values()) if handoffs else False
    report = dict(tag=a.tag, candidates=[list(c) for c in cand],
                  sim={str(k): v for k, v in sim.items()},
                  handoffs={str(k): v for k, v in handoffs.items()},
                  handoff_all_exact=handoff_exact,
                  y_error_targets_before=sorted(errors),
                  n_error_terms_before=sum(len(e) for e in errors.values()),
                  corrections=corrections, unhandled_terms=unhandled,
                  y_error_targets_after=sorted(errors2),
                  solved=bool(not unhandled and not errors2 and handoff_exact),
                  seconds=time.monotonic() - t0)
    (OUT / a.report).write_text(json.dumps(report, indent=1) + '\n')
    print('solved' if report['solved'] else 'NOT SOLVED',
          'corrections', len(corrections), 'unhandled', len(unhandled),
          'err_targets_before', len(errors), 'after', len(errors2),
          'handoff_exact', handoff_exact, f"{report['seconds']:.1f}s")
    if unhandled[:8]: print('unhandled sample:', unhandled[:8])
    if not report['solved']: return 1
    ext = json.loads(json.dumps(wit))
    ext['variant'] = f"low{len(pairs_all)}_{a.tag}"
    ext['pairs'] = pairs_all
    ext['initial_corrections'] = corrections
    recs = {r['operator']: r for r in ext['gaussian']['records']}
    for p in new_pairs:
        op = pairs_all.index(p) + 1
        recs[op] = dict(operator=op,
                        G_columns=bw_gauss.change(p['retirement_basis'], p['handoff_basis'], 9),
                        handoff_exact_monomial_sha256=None,
                        full_exit_exact_monomial_sha256=None)
    ext['gaussian']['records'] = [recs[i] for i in sorted(recs)]
    ext['gaussian']['operators'] = len(recs)
    (OUT / a.out).write_text(json.dumps(ext, indent=1) + '\n')
    print('wrote', a.out, 'pairs', len(pairs_all), 'low', sum(p['low'] for p in pairs_all))
    return 0

if __name__ == '__main__': sys.exit(main())
