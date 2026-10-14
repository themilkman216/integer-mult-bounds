"""Historical overlays authenticate exact bytes and leave live inputs untouched."""
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('historical_check', ROOT/'scripts/replay_historical_check.py')
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


class HistoricalReplay(unittest.TestCase):
    def fixture(self, temporary):
        root = Path(temporary)/'source'
        root.mkdir()
        inputs = Path(temporary)/'inputs'
        inputs.mkdir()
        original = b'historical input\n'
        (inputs/'old.txt').write_bytes(original)
        (root/'input.txt').write_bytes(b'new live input\n')
        (root/'unrelated.py').write_bytes(b'unchanged checker bytes\n')
        digest = hashlib.sha256(original).hexdigest()
        (root/'manifest.json').write_text(json.dumps({'files': {'input.txt': digest}}))
        config = dict(manifest='manifest.json', field='files', path='input.txt', input='old.txt', sha256=digest)
        return root, inputs, config, ['input.txt', 'manifest.json', 'unrelated.py']

    def test_overlay_is_isolated_and_other_inputs_stay_exact(self):
        with tempfile.TemporaryDirectory() as td:
            root, inputs, config, paths = self.fixture(td)
            before = {p: (root/p).read_bytes() for p in paths}
            target = Path(td)/'copy'
            expected = checker.materialize(root, target, config, paths, inputs)
            self.assertEqual((target/'input.txt').read_bytes(), (inputs/'old.txt').read_bytes())
            self.assertEqual((target/'unrelated.py').read_bytes(), before['unrelated.py'])
            checker.verify_unchanged(target, expected)
            (target/'unrelated.py').write_bytes(b'regenerated in temporary tree')
            with self.assertRaisesRegex(ValueError, 'Replay changed tracked artifact'):
                checker.verify_unchanged(target, expected)
            self.assertEqual({p: (root/p).read_bytes() for p in paths}, before)

    def test_corrupt_historical_blob_rejects_before_copy(self):
        with tempfile.TemporaryDirectory() as td:
            root, inputs, config, paths = self.fixture(td)
            (inputs/'old.txt').write_bytes(b'corrupted')
            target = Path(td)/'copy'
            with self.assertRaisesRegex(ValueError, 'Changed historical input'):
                checker.materialize(root, target, config, paths, inputs)
            self.assertFalse(target.exists())

    def test_missing_changed_and_nonbyte_pins_reject(self):
        with tempfile.TemporaryDirectory() as td:
            root, inputs, config, paths = self.fixture(td)
            for entry in [None, '0'*64, {'representation': 'gzip-payload', 'sha256': config['sha256']}]:
                (root/'manifest.json').write_text(json.dumps({'files': {'input.txt': entry}}))
                with self.subTest(entry=entry), self.assertRaises(ValueError):
                    checker.authenticated_input(root, config, inputs)

    def test_untracked_replacement_and_existing_destination_reject(self):
        with tempfile.TemporaryDirectory() as td:
            root, inputs, config, paths = self.fixture(td)
            target = Path(td)/'copy'
            with self.assertRaisesRegex(ValueError, 'not tracked'):
                checker.materialize(root, target, config, ['manifest.json'], inputs)
            target.mkdir()
            with self.assertRaisesRegex(ValueError, 'already exists'):
                checker.materialize(root, target, config, paths, inputs)

    def test_path_escape_and_symlinks_reject(self):
        with tempfile.TemporaryDirectory() as td:
            root, inputs, config, paths = self.fixture(td)
            for name in ['/absolute', '../escape', 'C:/escape', 'folder\\escape']:
                with self.subTest(name=name), self.assertRaisesRegex(ValueError, 'Unsafe'):
                    checker.safe_path(root, name)
            with patch.object(Path, 'is_symlink', return_value=True):
                with self.assertRaisesRegex(ValueError, 'Non-file tracked'):
                    checker.materialize(root, Path(td)/'copy', config, paths, inputs)

    def test_makefile_append_is_allowed_but_original_prefix_mutation_rejects(self):
        with tempfile.TemporaryDirectory() as td:
            root, inputs, config, paths = self.fixture(td)
            config['preserve_prefix'] = True
            original = (inputs/'old.txt').read_bytes()
            (root/'input.txt').write_bytes(original + b'new target\n')
            self.assertEqual(checker.authenticated_input(root, config, inputs), original)
            (root/'input.txt').write_bytes(original.replace(b'historical', b'changed') + b'new target\n')
            with self.assertRaisesRegex(ValueError, 'prefix changed'):
                checker.authenticated_input(root, config, inputs)

    def test_real_snapshots_match_unchanged_predecessor_pins(self):
        for name, config in checker.CONFIG.items():
            with self.subTest(package=name):
                checker.authenticated_input(ROOT, config)


if __name__ == '__main__':
    unittest.main()
