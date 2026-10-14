#!/usr/bin/env python3
"""Replay frozen checks against authenticated historical inputs in a temporary copy.

Dennis, with substantial OpenAI Codex assistance; Apache-2.0.
The checkers, their pins, and the live selected record remain unchanged.
"""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
INPUTS = Path(__file__).with_name('historical-ci-inputs')
# Each replacement must also match the unchanged predecessor manifest.
CONFIG = {
    'r420': {
        'manifest': 'research/r420-two-sided-basis/SOURCES.json',
        'field': 'files',
        'path': 'certificates/selected-result.json',
        'input': 'selected-result.json',
        'sha256': 'b3bf402f31a69bde0629936a9b569bed48281568d7b16d5fba120b5311ea1f53',
        'commands': [['research/r420-two-sided-basis/verify.py'],
                     ['-m', 'unittest', 'discover', '-s', 'research/r420-two-sided-basis', '-p', 'test_*.py']],
    },
    'reconciliation92': {
        'manifest': 'research/community-reconciliation92-audit/MANIFEST.json',
        'field': 'integrated_files',
        'preserve_prefix': True,
        'path': 'Makefile',
        'input': 'Makefile',
        'sha256': 'ea8830dd79da493e2d75baf753d733ff7efbcf2b4794afe41fae0ac8f3055646',
        'commands': [['research/community-reconciliation92-audit/verify.py']],
    },
    'split-skip': {
        'manifest': 'research/split-skip/SOURCE.json',
        'field': 'files',
        'path': 'scripts/audit_fused_block.py',
        'input': 'audit_fused_block.py',
        'sha256': '2afb83ca8e5f193ca8a4c242becf267ad1d9dc2578ba238b820e98d5185f6288',
        'commands': [['research/split-skip/witness.py'],
                     ['research/split-skip/independent_arithmetic.py'],
                     ['-m', 'unittest', 'discover', '-s', 'tests', '-p', 'test_split_skip.py', '-v']],
    },
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def safe_path(root, name):
    path = PurePosixPath(name)
    require(bool(path.parts) and not path.is_absolute() and '..' not in path.parts
            and '\\' not in name and ':' not in name, 'Unsafe repository path')
    return root.joinpath(*path.parts)


def authenticated_input(root, config, inputs=INPUTS):
    manifest = json.loads(safe_path(root, config['manifest']).read_bytes())
    entry = manifest[config['field']].get(config['path'])
    if isinstance(entry, dict):
        require(entry.get('representation') == 'bytes', 'Expected exact byte representation')
        entry = entry.get('sha256')
    require(entry == config['sha256'], 'Missing or changed predecessor source pin')
    data = safe_path(inputs, config['input']).read_bytes()
    require(hashlib.sha256(data).hexdigest() == entry, 'Changed historical input')
    if config.get('preserve_prefix'):
        require(data.endswith(b'\n') and safe_path(root, config['path']).read_bytes().startswith(data),
                'Historical Makefile prefix changed')
    return data


def tracked_paths(root):
    raw = subprocess.check_output(['git', 'ls-files', '-z'], cwd=root)
    return [p.decode('utf-8') for p in raw.split(b'\0') if p]


def materialize(root, destination, config, paths, inputs=INPUTS):
    """Copy tracked working bytes only; never share writable links with the checkout."""
    data = authenticated_input(root, config, inputs)
    require(config['path'] in paths and config['manifest'] in paths,
            'Historical input or manifest is not tracked')
    require(not destination.exists(), 'Replay destination already exists')
    destination.mkdir(parents=True)
    expected = {}
    for name in paths:
        source = safe_path(root, name)
        require(not source.is_symlink() and source.is_file(), 'Non-file tracked source: ' + name)
        target = safe_path(destination, name)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        expected[name] = hashlib.sha256(target.read_bytes()).hexdigest()
    safe_path(destination, config['path']).write_bytes(data)
    expected[config['path']] = config['sha256']
    # Authenticate again in the copied tree before executing any checker.
    authenticated_input(destination, config, inputs)
    return expected


def verify_unchanged(snapshot, expected):
    """Retain the original CI reproducibility gate inside the isolated replay tree."""
    for name, digest in expected.items():
        target = safe_path(snapshot, name)
        require(target.is_file() and hashlib.sha256(target.read_bytes()).hexdigest() == digest,
                'Replay changed tracked artifact: ' + name)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('package', choices=CONFIG)
    parser.add_argument('--native', action='store_true', help='also run R420 C++ checks (requires C++17/Boost)')
    args = parser.parse_args()
    require(not args.native or args.package == 'r420', '--native applies only to r420')
    config = CONFIG[args.package]
    paths = tracked_paths(ROOT)
    with tempfile.TemporaryDirectory(prefix='historical-ci-') as temporary:
        snapshot = Path(temporary) / 'repo'
        print('REPLAY_HISTORICAL_CHECK', args.package, 'copying tracked inputs', flush=True)
        expected = materialize(ROOT, snapshot, config, paths)
        commands = list(config['commands'])
        if args.native:
            commands.append(['research/r420-two-sided-basis/native.py'])
        for command in commands:
            subprocess.run([sys.executable, '-B'] + command, cwd=snapshot, check=True)
        verify_unchanged(snapshot, expected)
    print('PASS_HISTORICAL_CHECK', args.package, 'input_sha256=' + config['sha256'], flush=True)


if __name__ == '__main__':
    main()
