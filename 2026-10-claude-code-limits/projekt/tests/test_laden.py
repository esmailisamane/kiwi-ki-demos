import unittest

from laden.preise import netto_zu_brutto, rabatt_anwenden, staffelpreis
from laden.versand import versandkosten
from laden.warenkorb import Warenkorb


class TestPreise(unittest.TestCase):
    def test_brutto(self):
        self.assertEqual(netto_zu_brutto(10.00), 11.90)

    def test_rabatt_zehn_prozent(self):
        self.assertEqual(rabatt_anwenden(100.00, 10), 90.00)

    def test_kein_rabatt(self):
        self.assertEqual(rabatt_anwenden(19.99, 0), 19.99)

    def test_staffel_ab_zehn(self):
        self.assertEqual(staffelpreis(2.00, 10), 19.00)

    def test_ungueltiger_rabatt(self):
        with self.assertRaises(ValueError):
            rabatt_anwenden(10.00, 120)


class TestVersand(unittest.TestCase):
    def test_unter_grenze(self):
        self.assertEqual(versandkosten(49.99), 4.90)

    def test_genau_fuenfzig_ist_gratis(self):
        self.assertEqual(versandkosten(50.00), 0.0)

    def test_express(self):
        self.assertEqual(versandkosten(80.00, express=True), 9.90)


class TestWarenkorb(unittest.TestCase):
    def test_gesamt_mit_versand(self):
        korb = Warenkorb()
        korb.hinzufuegen("Kiwi-Tasse", 10.00, 2)
        self.assertEqual(korb.gesamt(), 28.70)  # 23,80 brutto + 4,90 Versand

    def test_menge_null(self):
        with self.assertRaises(ValueError):
            Warenkorb().hinzufuegen("Nichts", 1.00, 0)


if __name__ == "__main__":
    unittest.main()
