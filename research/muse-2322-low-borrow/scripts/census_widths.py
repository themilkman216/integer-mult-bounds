#!/usr/bin/env python3
"""Per-register width / frame census of the shipped #2322 words.

Width formula is #2322's own (generate_words.paid_profile, lines 196-197):
for a live helper role >= 2v, width = dim(end frame) - dim(start_extra),
where the end frame is helper_final[role] if present else the full
9-dimensional frame.  This script imports basis()/paid_profile() from the
#2322 package itself, recounts both words as a positive control (must
reproduce PROFILE/WIDTHS), then reports widths and entrance dimensions
for every candidate port target: remaining high helpers, all block low
helpers, the 32 prior-round low lenders, and #2322's current warp lenders.
Output: CENSUS-WIDTHS.json.
"""
import gzip, importlib.util, json
from pathlib import Path

PKG = Path(__file__).resolve().parent.parent
WS = Path(__file__).resolve().parents[3]
SRC = WS / 'research/t74-joint-owner-hillclimb'

spec = importlib.util.spec_from_file_location('gw2322', SRC / 'generate_words.py')
gw = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gw)
basis = gw.basis

BLOCKS = list(range(592, 704, 8))          # 14 blocks of 8: 592..696
LOW_OFF = (0, 1, 2, 4)
HIGH_OFF = (3, 5, 6, 7)
PRIOR_LOW_LENDERS = [273, 275, 277, 282, 289, 291, 293, 298, 305, 307, 309, 314,
                     321, 323, 325, 330, 337, 339, 341, 346, 353, 355, 357, 362,
                     369, 371, 373, 378, 385, 387, 389, 394]
PRIOR_LOW_HELPERS = [592, 593, 594, 596, 600, 601, 602, 604, 608, 609, 610, 612,
                     624, 625, 626, 628, 672, 673, 674, 676, 680, 681, 682, 684,
                     688, 689, 690, 692, 696, 697, 698, 700]
REMAINING_HIGH = [606, 635, 637, 638, 639, 653]

def load(tag):
    return json.loads(gzip.decompress((SRC / 'words' / f'{tag}.json.gz').read_bytes()))

def dims(word):
    v, h = word['report']['v'], word['report']['h']
    full_dim = h
    out = {}
    removed = set(word['removed'])
    for role in range(2 * v, 2 * v + word['report']['R']):
        start = len(basis(word['start_extra'].get(str(role), [])))
        end = len(basis(word['helper_final'][str(role)])) if str(role) in word['helper_final'] else full_dim
        out[role] = dict(start_dim=start, end_dim=end, width=end - start,
                         removed=role in removed,
                         has_helper_final=str(role) in word['helper_final'],
                         has_start_extra=str(role) in word['start_extra'])
    return out

report = {}
for tag in ('base', 'extra'):
    word = load(tag)
    prof, widths = gw.paid_profile(word)
    assert prof == {1: 2335, 2: 512, 3: 426, 4: 120, 5: 38, 8: 8}, (tag, prof)
    assert widths == {4: 33, 5: 9, 7: 38, 8: 114, 9: 240}, (tag, widths)
    d = dims(word)
    lenders_used = sorted({rec[1] for rec in word['warps']})
    blocks = {}
    for b in BLOCKS:
        blocks[str(b)] = {
            'low': {str(b + o): d[b + o] for o in LOW_OFF},
            'high': {str(b + o): d[b + o] for o in HIGH_OFF},
        }
    width5_regs = sorted(r for r, x in d.items() if not x['removed'] and x['width'] == 5)
    width4_regs = sorted(r for r, x in d.items() if not x['removed'] and x['width'] == 4)
    report[tag] = dict(
        control_profile={str(k): v for k, v in prof.items()},
        control_widths={str(k): v for k, v in widths.items()},
        removed=sorted(word['removed']),
        warp_lenders=lenders_used,
        initial_corrections=len(word['initial_corrections']),
        remaining_high={str(r): d[r] for r in REMAINING_HIGH},
        prior_low_helpers={str(r): d[r] for r in PRIOR_LOW_HELPERS},
        prior_low_lenders={str(r): d[r] for r in PRIOR_LOW_LENDERS},
        low_lenders_already_used=sorted(set(PRIOR_LOW_LENDERS) & set(lenders_used)),
        width5_registers=width5_regs, width4_registers=width4_regs,
        blocks=blocks)
    print(f'[{tag}] control PASS profile/widths; removed {len(word["removed"])}; '
          f'warp lenders {len(lenders_used)}; init corrections {len(word["initial_corrections"])}')
    print(f'  remaining highs (width,start,end):',
          {r: (d[r]['width'], d[r]['start_dim'], d[r]['end_dim']) for r in REMAINING_HIGH})
    from collections import Counter
    print('  prior low helpers width histogram:', Counter(d[r]['width'] for r in PRIOR_LOW_HELPERS))
    print('  prior low lenders width histogram:', Counter(d[r]['width'] for r in PRIOR_LOW_LENDERS),
          'start dims:', Counter(d[r]['start_dim'] for r in PRIOR_LOW_LENDERS),
          'end dims:', Counter(d[r]['end_dim'] for r in PRIOR_LOW_LENDERS))
    print('  low lenders already warp lenders:', report[tag]['low_lenders_already_used'])
    print('  width5 registers:', width5_regs)
    print('  width4 registers:', width4_regs)
    for b in BLOCKS:
        lo = [d[b + o]['width'] for o in LOW_OFF]
        hi = [(d[b + o]['width'], d[b + o]['removed']) for o in HIGH_OFF]
        print(f'  block {b}: low widths {lo} high (width,removed) {hi}')

# cross-word agreement on candidate registers
agree = report['base']['blocks'] == report['extra']['blocks']
print('block dims identical across words:', agree)
cand = REMAINING_HIGH + PRIOR_LOW_HELPERS + PRIOR_LOW_LENDERS
db, de = dims(load('base')), dims(load('extra'))
width_agree = all(db[r] == de[r] for r in cand)
print('candidate dims identical base vs extra:', width_agree)

out = dict(source='research/t74-joint-owner-hillclimb/words/{base,extra}.json.gz',
           method='generate_words.paid_profile width definition imported from #2322 package',
           candidate_dims_identical_across_words=width_agree, words=report)
(PKG / 'CENSUS-WIDTHS.json').write_text(json.dumps(out, indent=1) + '\n')
print('wrote CENSUS-WIDTHS.json')
