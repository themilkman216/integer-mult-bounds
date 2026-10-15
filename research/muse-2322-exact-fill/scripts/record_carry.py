#!/usr/bin/env python3
"""Harvest a finished cold_replay run into CARRY-THROUGH.json.

Usage: record_carry.py <cold_work_dir> [driver_exit_code]
Reads REPLAY.json + delta/DELTA-ADMISSION.json + strict ASSEMBLY and the
outer LEDGER from the cold work tree, binds them to CANDIDATE-OWNERS by
sha256, and compares the final kappa exactly (rational) against #2322's
published final kappa (its evidence/full-replay/REPLAY.json) and CLAIM.
On an incomplete/failed run, records the furthest stage evidence found
instead of raising, so the outcome is still machine-readable.
"""
import gzip, hashlib, json, sys
from fractions import Fraction as Q
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from model2322 import OUT, PKG, rd

work = Path(sys.argv[1]).resolve()
exit_code = int(sys.argv[2]) if len(sys.argv) > 2 else None
res = dict(work_dir=str(work), driver_exit_code=exit_code,
           candidate_owners_sha256=hashlib.sha256(
               (OUT / 'CANDIDATE-OWNERS.json.gz').read_bytes()).hexdigest())
replay_p = work / 'REPLAY.json'
delta_p = work / 'delta/DELTA-ADMISSION.json'
try:
    replay = rd(replay_p); delta = rd(delta_p)
    assembly = rd(work / 'delta/strict/ASSEMBLY.json')
    ledger = rd(work / 'delta/fine-padding/outer/LEDGER.json')
    shipped_replay = rd(PKG / 'evidence/full-replay/REPLAY.json')
    k_new = Q(replay['final_kappa']); k_ship = Q(shipped_replay['final_kappa'])
    k_claim = Q(rd(PKG / 'CLAIM.json')['kappa'])
    res.update(
        status=replay['status'], delta_status=delta['status'],
        strict_status=rd(work / 'delta/strict/RESULT.json')['status'],
        assembly_status=assembly['status'],
        assembly_kappa=assembly['kappa'], complex_lower=assembly['complex_lower'],
        profile={str(k): v for k, v in assembly['complex_profile'].items()}
        if isinstance(assembly.get('complex_profile'), dict) else assembly.get('complex_profile'),
        final_kappa=str(k_new), final_kappa_dec=float(k_new),
        shipped_final_kappa=str(k_ship), gain_over_2322_dec=float(k_new - k_ship),
        exceeds_2322_final=bool(k_new > k_ship), exceeds_2322_claim=bool(k_new > k_claim),
        genuine_improvement_over_pr2312=delta['genuine_improvement_over_pr2312'],
        delta_receipt_sha256=hashlib.sha256(delta_p.read_bytes()).hexdigest(),
        stages=delta.get('stages'))
except Exception as exc:  # incomplete run: record furthest evidence
    found = []
    for p in sorted(work.rglob('*.json')) if work.exists() else []:
        found.append(str(p.relative_to(work)))
    logs = {}
    for p in sorted(work.rglob('*.log')) if work.exists() else []:
        logs[str(p.relative_to(work))] = p.read_text(errors='replace')[-800:]
    res.update(status='CARRY_THROUGH_INCOMPLETE', error=repr(exc),
               json_files_found=found, log_tails=logs)
(OUT / 'CARRY-THROUGH.json').write_text(json.dumps(res, indent=1) + '\n')
print(json.dumps({k: res[k] for k in res if k not in ('stages', 'log_tails', 'json_files_found')}, indent=1))
