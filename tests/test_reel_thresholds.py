import json
import unittest
from pathlib import Path

from r3_riflesso.decide import ReflexDecider

ROOT = Path(__file__).resolve().parents[1]


class ReelThresholds(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cfg = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
        cfg["backend"] = "demo"
        cls.d = ReflexDecider(cfg)

    def test_abre_el_fermo(self):
        x = self.d.decide("abre el")
        self.assertLess(x.complete, 0.55)
        self.assertEqual(x.action, "open_app")

    def test_abre_el_bloc_attesa(self):
        x = self.d.decide("abre el bloc")
        self.assertGreaterEqual(x.complete, 0.55)
        self.assertLess(x.complete, 0.80)
        self.assertEqual(x.target, "none")

    def test_bloc_de_notas_scatto(self):
        x = self.d.decide("abre el bloc de notas")
        self.assertGreaterEqual(x.complete, 0.80)
        self.assertEqual(x.action, "open_app")
        self.assertEqual(x.target, "bloc de notas")

    def test_catalogo_chiuso(self):
        x = self.d.decide("apri photoshop quantum")
        self.assertEqual(x.target, "none")


if __name__ == "__main__":
    unittest.main()
