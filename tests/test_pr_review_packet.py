import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('packets', Path(__file__).resolve().parents[1] / 'scripts/pr_review_packet.py')
packets = importlib.util.module_from_spec(spec)
spec.loader.exec_module(packets)


class PacketTests(unittest.TestCase):
    def test_complete_diff_and_mode_identity(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            def g(*args):
                return subprocess.check_output(['git', '-C', tmp, '-c', 'user.name=Test',
                                                '-c', 'user.email=test@example.invalid', *args], stderr=subprocess.DEVNULL).decode().strip()
            g('init')
            (root / 'old').write_text('old')
            (root / 'script').write_text('same')
            g('add', '.'); g('commit', '-m', 'base')
            base = g('rev-parse', 'HEAD')
            (root / 'old').unlink()
            (root / 'new').write_text('new')
            g('add', '-A'); g('update-index', '--chmod=+x', 'script'); g('commit', '-m', 'change')
            head = g('rev-parse', 'HEAD')
            metadata = dict(number=1, title='test', author={'login': 'test'}, headRefOid=head,
                            baseRefOid=base, files=[{'path': 'new'}])
            result = packets.packet(root, metadata, base)
            self.assertEqual(result['complete_git_file_count'], 3)
            bypath = {r['path']: r for r in result['files']}
            self.assertEqual(bypath['old']['change'], 'delete')
            self.assertEqual(bypath['script']['baseline_relation'], 'different_on_baseline')
            self.assertEqual(bypath['new']['baseline_relation'], 'absent_on_baseline')
            same = packets.packet(root, metadata, head)
            self.assertTrue(all(r['baseline_relation'] == 'identical' for r in same['files']))
            self.assertIsNone(same['decision'])


if __name__ == '__main__':
    unittest.main()
