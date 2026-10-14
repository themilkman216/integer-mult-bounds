"""Regression controls for registered replay invalidation across workflow and Git.

Charles Bethin, with OpenAI Codex assistance. Apache-2.0.
"""
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ".github/workflows/research-packages.yml"


class ReplaySelectionTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name) / "repo"
        self.root.mkdir()
        self.output = Path(temp.name) / "github-output.txt"
        self.git("init", "-q")
        for key, value in (("user.name", "Fixture"), ("user.email", "fixture@example.invalid"),
                           ("core.autocrlf", "false"), ("diff.renames", "true")):
            self.git("config", key, value)
        for name in ("scripts/research_package.py", WORKFLOW):
            target = self.root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((ROOT / name).read_bytes())
        self.inputs = ["certificates/input.json", "docs/research/proof.md",
                       "src/solver.py", "fixtures/space name.json"]
        for name in self.inputs + ["data/other.json", "README.md"]:
            self.write(name, "original fixture\n")
        # Routing fixtures only: planning deliberately does not validate or run a package.
        for slug, inputs in (("alpha", self.inputs), ("beta", ["data/other.json"])):
            self.write(f"research/{slug}/VERIFY.json", json.dumps({"inputs": inputs}))
        self.commit()

    def git(self, *args):
        return subprocess.check_output(["git", *args], cwd=self.root).decode().strip()

    def write(self, name, text):
        target = self.root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")

    def commit(self):
        self.git("add", "--all")
        self.git("-c", "maintenance.auto=false", "-c", "gc.auto=0", "commit", "-qm", "fixture")
        return self.git("rev-parse", "HEAD")

    def selected(self, base):
        output = self.output
        output.unlink(missing_ok=True)
        result = subprocess.run(
            [sys.executable, "-B", str(self.root / "scripts/research_package.py"),
             "--changed-since", base, "--github-output", str(output)],
            cwd=self.root, capture_output=True, text=True, encoding="utf-8", timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        matrix = json.loads(result.stdout)
        fields = dict(line.split("=", 1) for line in output.read_text(encoding="utf-8").splitlines())
        self.assertEqual(json.loads(fields["matrix"]), matrix)
        self.assertEqual(int(fields["count"]), len(matrix["include"]))
        return [entry["package"] for entry in matrix["include"]]

    def test_declared_inputs_outside_research_reach_the_planner(self):
        for name in self.inputs:
            with self.subTest(name=name):
                base = self.git("rev-parse", "HEAD")
                self.write(name, "changed input\n")
                self.commit()
                self.assertEqual(self.selected(base), ["research/alpha"])

    def test_deleted_input_still_selects_its_consumer(self):
        base = self.git("rev-parse", "HEAD")
        (self.root / self.inputs[0]).unlink()
        self.commit()
        self.assertEqual(self.selected(base), ["research/alpha"])

    def test_renamed_input_still_selects_its_old_consumer(self):
        base = self.git("rev-parse", "HEAD")
        self.git("mv", self.inputs[0], "data/renamed.json")
        self.commit()
        # Establish the adversarial case: Git's ordinary name-only output loses the old path.
        self.assertEqual(self.git("diff", "--name-only", base, "HEAD"), "data/renamed.json")
        self.assertEqual(self.selected(base), ["research/alpha"])

    def test_global_controls_select_all_registered_packages(self):
        for name in (WORKFLOW, "scripts/research_package.py"):
            with self.subTest(name=name):
                base = self.git("rev-parse", "HEAD")
                with (self.root / name).open("a", encoding="utf-8") as stream:
                    stream.write("\n# changed replay control\n")
                self.commit()
                self.assertEqual(self.selected(base), ["research/alpha", "research/beta"])

    def test_unrelated_change_has_no_replay_and_package_addition_does(self):
        base = self.git("rev-parse", "HEAD")
        self.write("README.md", "unrelated edit\n")
        self.commit()
        self.assertEqual(self.selected(base), [])
        base = self.git("rev-parse", "HEAD")
        self.write("research/beta/evidence.txt", "new local artifact\n")
        self.commit()
        self.assertEqual(self.selected(base), ["research/beta"])

    def test_workflow_does_not_filter_out_declared_input_paths(self):
        text = (ROOT / WORKFLOW).read_text(encoding="utf-8")
        # Static policy guard, not a YAML interpreter. actionlint checks the YAML separately.
        events = text.split("\npermissions:", 1)[0]
        self.assertIn("\n  pull_request:", events)
        self.assertIn("\n  push:\n    branches: [main]", events)
        self.assertNotRegex(events, re.compile(r"^\s*['\"]?paths(?:-ignore)?['\"]?\s*:", re.M))


if __name__ == "__main__":
    unittest.main()
