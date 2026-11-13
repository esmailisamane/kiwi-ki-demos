"""Offline-Test der drei Werkzeuge - ohne API-Key, ohne Modell.

Start: python -m pytest test_werkzeuge.py
"""

import asyncio
import csv

import rechnungs_agent as agent


def lauf(werkzeug, args):
    return asyncio.run(werkzeug.handler(args))


def ordner_vorbereiten(tmp_path, monkeypatch):
    monkeypatch.setattr(agent, "ORDNER", tmp_path)
    monkeypatch.setattr(agent, "TABELLE", tmp_path / "rechnungen.csv")
    (tmp_path / "scan_0012.pdf").write_bytes(b"%PDF-1.4")
    (tmp_path / "notiz.txt").write_text("keine Rechnung")


def test_list_invoices_zeigt_nur_rechnungen(tmp_path, monkeypatch):
    ordner_vorbereiten(tmp_path, monkeypatch)
    text = lauf(agent.list_invoices, {})["content"][0]["text"]
    assert text == "scan_0012.pdf"


def test_save_invoice_schreibt_kopf_nur_einmal(tmp_path, monkeypatch):
    ordner_vorbereiten(tmp_path, monkeypatch)
    zeile = {"datei": "a.pdf", "lieferant": "Bäckerei Kiwi", "datum": "2026-11-03", "brutto": "12,40", "mwst": "0,81"}
    lauf(agent.save_invoice, zeile)
    lauf(agent.save_invoice, {**zeile, "datei": "b.pdf", "brutto": "unklar"})
    roh = (tmp_path / "rechnungen.csv").read_bytes()
    assert roh.count(b"\xef\xbb\xbf") == 1  # BOM nur am Anfang, auch beim Anhängen
    with open(tmp_path / "rechnungen.csv", encoding="utf-8-sig", newline="") as f:
        zeilen = list(csv.DictReader(f, delimiter=";"))
    assert [z["datei"] for z in zeilen] == ["a.pdf", "b.pdf"]
    assert zeilen[0]["lieferant"] == "Bäckerei Kiwi"
    assert zeilen[1]["brutto"] == "unklar"


def test_rename_file_benennt_um(tmp_path, monkeypatch):
    ordner_vorbereiten(tmp_path, monkeypatch)
    ergebnis = lauf(agent.rename_file, {"alt": "scan_0012.pdf", "neu": "2026-11-03_Kiwi_12,40.pdf"})
    assert "is_error" not in ergebnis
    assert (tmp_path / "2026-11-03_Kiwi_12,40.pdf").exists()


def test_rename_file_bleibt_im_ordner(tmp_path, monkeypatch):
    ordner_vorbereiten(tmp_path, monkeypatch)
    ergebnis = lauf(agent.rename_file, {"alt": "scan_0012.pdf", "neu": "../weg.pdf"})
    assert ergebnis["is_error"] is True
    assert (tmp_path / "scan_0012.pdf").exists()


def test_rename_file_ueberschreibt_nichts(tmp_path, monkeypatch):
    ordner_vorbereiten(tmp_path, monkeypatch)
    (tmp_path / "schon_da.pdf").write_bytes(b"%PDF-1.4")
    ergebnis = lauf(agent.rename_file, {"alt": "scan_0012.pdf", "neu": "schon_da.pdf"})
    assert ergebnis["is_error"] is True


def test_freigabe_nein_heisst_nein(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "n")
    antwort = asyncio.run(agent.frage_mich("mcp__rechnungen__rename_file", {"alt": "a", "neu": "b"}, None))
    assert antwort.behavior == "deny"


def test_freigabe_ja(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "j")
    antwort = asyncio.run(agent.frage_mich("mcp__rechnungen__rename_file", {"alt": "a", "neu": "b"}, None))
    assert antwort.behavior == "allow"


def test_bash_wird_abgelehnt():
    antwort = asyncio.run(agent.frage_mich("Bash", {"command": "rm -rf rechnungen"}, None))
    assert antwort.behavior == "deny"
