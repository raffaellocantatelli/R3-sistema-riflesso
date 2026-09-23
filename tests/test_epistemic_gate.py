import unittest

from r3_riflesso.epistemic import decide, gate


class EpistemicGate(unittest.TestCase):
    def test_desiderio_non_esegue(self):
        r = decide("voglio che lo inseriamo nel protocollo rosso")
        self.assertEqual(r.layer, "DESIDERIO")
        self.assertIn("non eseguire", gate(r))

    def test_tesi_resta_ipotesi(self):
        r = decide("la tesi del già esiste già ora")
        self.assertEqual(r.layer, "IPOTESI")
        self.assertNotEqual(r.layer, "RECUPERATO")

    def test_chiusura_blocco(self):
        r = decide("è dimostrato, non serve verificare")
        self.assertEqual(r.stance, "BLOCCO")
        self.assertTrue(gate(r).startswith("STOP"))

    def test_commit_recuperato(self):
        r = decide("ho committato su protocollo-rosso-bot")
        self.assertEqual(r.layer, "RECUPERATO")
        self.assertEqual(r.stance, "SCATTO")

    def test_frammento_fermo(self):
        r = decide("abre el")
        self.assertEqual(r.stance, "FERMO")


if __name__ == "__main__":
    unittest.main()
