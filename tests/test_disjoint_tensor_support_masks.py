#!/usr/bin/env python3
"""Focused controls for the DisjointTensor support-mask tooling package."""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import importlib.util
import json
import subprocess
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "research" / "disjoint-tensor-support-masks"
sys.path.insert(0, str(ROOT / "scripts"))

from experiments import disjoint_tensor as production  # noqa: E402

ORIGINAL_SHA256 = "102dd59bf96033f96ba0dab4c2aba77b3a7a73b67b0f96929ff8b20a98b91cd8"
OPTIMIZED_SHA256 = "085600fc922ae167b5981505e1a5caba4d1c1df15482f61d83d2c086fa89eac1"
BASE_COMMIT = "0b1cccf86e2f5132ed286a26ef0a681a495740ea"
H26_DAG_SHA = "5da8011dadf51d6121d343416fa38b6b4bf524fd689e5b1b2def91324660f19b"


def load_baseline():
    spec = importlib.util.spec_from_file_location("baseline_dt_test", PACKAGE / "baseline.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class DisjointTensorSupportMasksTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.baseline = load_baseline()

    def test_baseline_matches_base_commit_bytes(self):
        original = subprocess.check_output(
            ["git", "show", f"{BASE_COMMIT}:scripts/experiments/disjoint_tensor.py"],
            cwd=ROOT,
        )
        self.assertEqual((PACKAGE / "baseline.py").read_bytes(), original)
        self.assertEqual(sha256(original).hexdigest(), ORIGINAL_SHA256)
        self.assertEqual(
            sha256((ROOT / "scripts/experiments/disjoint_tensor.py").read_bytes()).hexdigest(),
            OPTIMIZED_SHA256,
        )

    def test_closed_form_matches_historical_genexpr(self):
        for h in (8, 12, 16, 20):
            circuit = production.DisjointTensor(h)
            full = (1 << len(circuit.inputs)) - 1
            vertex = [0] * circuit.h
            for i, S in enumerate(circuit.inputs):
                bits = S
                while bits:
                    bit = bits & -bits
                    bits ^= bit
                    vertex[bit.bit_length() - 1] |= 1 << i
            for T, node in circuit.outputs.items():
                old = sum(1 << i for i, S in enumerate(circuit.inputs) if not S & T)
                hit = 0
                bits = T
                while bits:
                    bit = bits & -bits
                    bits ^= bit
                    hit |= vertex[bit.bit_length() - 1]
                new = full ^ hit
                self.assertEqual(old, new)
                self.assertEqual(circuit.support[node], new)

    def test_xor_mutant_differs(self):
        circuit = production.DisjointTensor(12)
        full = (1 << len(circuit.inputs)) - 1
        vertex = [0] * circuit.h
        for i, S in enumerate(circuit.inputs):
            bits = S
            while bits:
                bit = bits & -bits
                bits ^= bit
                vertex[bit.bit_length() - 1] |= 1 << i
        T = next(iter(circuit.outputs))
        xor_hit = 0
        or_hit = 0
        bits = T
        while bits:
            bit = bits & -bits
            bits ^= bit
            p = bit.bit_length() - 1
            xor_hit ^= vertex[p]
            or_hit |= vertex[p]
        self.assertNotEqual(full ^ xor_hit, full ^ or_hit)

    def test_small_circuit_receipts_match(self):
        for h in (8, 10, 12, 16):
            circuit = production.DisjointTensor(h)
            self.assertEqual(
                self.baseline.DisjointTensor.verify(circuit),
                circuit.verify(),
            )

    def test_full_size_receipt_and_digest(self):
        circuit = production.DisjointTensor(26)
        old = self.baseline.DisjointTensor.verify(circuit)
        new = circuit.verify()
        self.assertEqual(old, new)
        self.assertEqual(new["additions"], 57772)
        self.assertEqual(new["roles"], 60372)
        self.assertEqual(new["dag_sha256"], H26_DAG_SHA)

    def test_support_rejection_preserved(self):
        circuit = production.DisjointTensor(10)
        _target, node = next(iter(circuit.outputs.items()))
        circuit.support[node] ^= 1
        with self.assertRaises(ValueError):
            circuit.verify()

    def test_certificates_only_change_disjoint_tensor_pin(self):
        for rel in (
            "certificates/disjoint-tensor-compression.json",
            "certificates/ternary-side.json",
            "certificates/dyadic-central-factor.json",
            "certificates/parity-side.json",
        ):
            base = json.loads(
                subprocess.check_output(["git", "show", f"{BASE_COMMIT}:{rel}"], cwd=ROOT)
            )
            live = json.loads((ROOT / rel).read_text(encoding="utf-8"))
            key = "scripts/experiments/disjoint_tensor.py"
            self.assertEqual(live["source_sha256"][key], OPTIMIZED_SHA256)
            restored = deepcopy(live)
            restored["source_sha256"][key] = ORIGINAL_SHA256
            if "scripts/exclusion_circuit.py" in live["source_sha256"]:
                restored["source_sha256"]["scripts/exclusion_circuit.py"] = (
                    "b253f9d7318becda1c1f3b24e2287ed44a9c27fcea00cf9d531afb950d0457a0"
                )
            self.assertEqual(restored, base)


if __name__ == "__main__":
    unittest.main()
