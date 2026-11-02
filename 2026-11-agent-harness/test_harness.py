"""Offline-Tests für mini_harness.py – ohne Ollama: ein erfundenes "Modell" liefert feste Antworten.

Start:  python -m unittest test_harness.py -v
"""
import io
import os
import shutil
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

import mini_harness as h


def aufruf(name, **argumente):
    return {"role": "assistant", "content": "", "tool_calls": [{"function": {"name": name, "arguments": argumente}}]}


def text(inhalt):
    return {"role": "assistant", "content": inhalt}


class MiniHarnessTest(unittest.TestCase):
    def setUp(self):
        self.alt = os.getcwd()
        self.ordner = Path(tempfile.mkdtemp())
        os.chdir(self.ordner)
        (self.ordner / "notizen").mkdir()
        (self.ordner / "notizen" / "termine.txt").write_text("Donnerstag 14:30 Zahnarzt\n", encoding="utf-8")
        (self.ordner / "geheim.txt").write_text("PASSWORT=nur-ein-Beispiel\n", encoding="utf-8")
        h.ORDNER = (self.ordner / "notizen").resolve()
        h.GEDAECHTNIS = self.ordner / "GEDAECHTNIS.md"
        h.SICHERUNG = self.ordner / "sicherung"

    def tearDown(self):
        os.chdir(self.alt)
        shutil.rmtree(self.ordner, ignore_errors=True)

    def lauf(self, antworten, eingaben=(), max_schritte=8):
        """Lässt die Agenten-Schleife mit festen Modell-Antworten und festen Nutzer-Eingaben laufen."""
        nachrichten = [h.system_nachricht(), {"role": "user", "content": "Test"}]
        with mock.patch.object(h, "frage_modell", side_effect=list(antworten)), \
             mock.patch("builtins.input", side_effect=list(eingaben)), \
             mock.patch.object(h, "MAX_SCHRITTE", max_schritte), redirect_stdout(io.StringIO()):
            return h.agent(nachrichten), nachrichten

    def test_schleife_fuehrt_werkzeug_aus_und_endet_ohne_wunsch(self):
        antwort, verlauf = self.lauf([aufruf("lies_datei", datei="termine.txt"), text("Donnerstag 14:30")])
        self.assertEqual(antwort, "Donnerstag 14:30")
        self.assertIn("Zahnarzt", verlauf[-2]["content"])          # Ergebnis ging als role "tool" zurück

    def test_dateiliste_steht_von_anfang_an_im_kontext(self):
        self.assertIn("termine.txt", h.system_nachricht()["content"])

    def test_zaun_blockiert_pfad_ausserhalb(self):
        _, verlauf = self.lauf([aufruf("lies_datei", datei="../geheim.txt"), text("geht nicht")])
        self.assertIn("außerhalb", verlauf[-2]["content"])
        self.assertNotIn("PASSWORT", verlauf[-2]["content"])

    def test_loeschen_mit_nein_laesst_datei_stehen(self):
        _, verlauf = self.lauf([aufruf("loesche_datei", datei="termine.txt"), text("abgelehnt")], eingaben=["n"])
        self.assertTrue((h.ORDNER / "termine.txt").exists())
        self.assertTrue(verlauf[-2]["content"].startswith("ABGELEHNT"))

    def test_schreiben_mit_ja_legt_vorher_sicherung_an(self):
        self.lauf([aufruf("schreibe_datei", datei="termine.txt", inhalt=" "), text("ok")], eingaben=["j"])
        self.assertEqual((h.ORDNER / "termine.txt").read_text(encoding="utf-8"), " ")
        kopien = list(h.SICHERUNG.glob("*_termine.txt"))
        self.assertEqual(len(kopien), 1)
        self.assertIn("Zahnarzt", kopien[0].read_text(encoding="utf-8"))

    def test_merke_braucht_freigabe(self):
        self.lauf([aufruf("merke", notiz="Liste alphabetisch"), text("ok")], eingaben=["n"])
        self.assertFalse(h.GEDAECHTNIS.exists())
        self.lauf([aufruf("merke", notiz="Liste alphabetisch"), text("ok")], eingaben=["j"])
        self.assertIn("Liste alphabetisch", h.GEDAECHTNIS.read_text(encoding="utf-8"))
        self.assertIn("Liste alphabetisch", h.system_nachricht()["content"])   # beim nächsten Start im Kontext

    def test_schrittgrenze_stoppt_endlosschleife(self):
        antwort, _ = self.lauf([aufruf("liste_dateien")] * 5, max_schritte=3)
        self.assertIn("Stopp nach 3 Schritten", antwort)

    def test_unbekanntes_werkzeug_wird_gemeldet(self):
        _, verlauf = self.lauf([aufruf("sortiere_datei", datei="x"), text("ok")])
        self.assertIn("gibt es nicht", verlauf[-2]["content"])


if __name__ == "__main__":
    unittest.main()
