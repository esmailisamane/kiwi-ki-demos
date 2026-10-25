"""Die Datenbank des Kiwi-Ladens: SQLite aus der Python-Standardbibliothek (sqlite3), keine Installation nötig.

    uv run python datenbank.py --neu      # Datenbank laden.db neu anlegen und mit Beispieldaten füllen

Alle Daten sind erfunden. Geld wird in Cent gespeichert (ganze Zahlen), nie als Kommazahl:
0.1 + 0.2 ergibt in Python 0.30000000000000004 – bei Geld will man das nicht.
"""
import os
import sqlite3
import sys
from contextlib import contextmanager
from datetime import date
from pathlib import Path

# Fester Stichtag statt date.today(): Tests und Video zeigen jeden Tag dieselben Ergebnisse.
HEUTE = date(2026, 10, 24)
RUECKGABE_TAGE = 30


def pfad() -> Path:
    return Path(os.environ.get("KIWI_DB", Path(__file__).resolve().parent / "laden.db"))


SCHEMA = """
CREATE TABLE produkte (
    sku        TEXT PRIMARY KEY,
    name       TEXT NOT NULL,
    kategorie  TEXT NOT NULL CHECK (kategorie IN ('Küche', 'Büro', 'Gutschein')),
    preis_cent INTEGER NOT NULL CHECK (preis_cent > 0),
    lager      INTEGER NOT NULL CHECK (lager >= 0)
);
CREATE TABLE kunden (
    id    TEXT PRIMARY KEY,
    name  TEXT NOT NULL,
    email TEXT NOT NULL
);
CREATE TABLE bestellungen (
    nummer       TEXT PRIMARY KEY,
    kunde_id     TEXT NOT NULL REFERENCES kunden(id),
    status       TEXT NOT NULL CHECK (status IN ('unterwegs', 'geliefert')),
    geliefert_am TEXT                      -- ISO-Datum, leer solange unterwegs
);
CREATE TABLE positionen (
    bestellnummer TEXT NOT NULL REFERENCES bestellungen(nummer),
    sku           TEXT NOT NULL REFERENCES produkte(sku),
    menge         INTEGER NOT NULL CHECK (menge > 0),
    preis_cent    INTEGER NOT NULL,        -- Preis beim Kauf, nicht der heutige
    PRIMARY KEY (bestellnummer, sku)
);
CREATE TABLE ruecksendungen (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    bestellnummer   TEXT NOT NULL,
    sku             TEXT NOT NULL,
    menge           INTEGER NOT NULL CHECK (menge > 0),
    erstattung_cent INTEGER NOT NULL,
    grund           TEXT NOT NULL,
    angelegt_am     TEXT NOT NULL,
    FOREIGN KEY (bestellnummer, sku) REFERENCES positionen(bestellnummer, sku)
);
CREATE TABLE gutschriften (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    ruecksendung_id INTEGER NOT NULL UNIQUE REFERENCES ruecksendungen(id),  -- nie zwei Gutschriften für eine Rücksendung
    betrag_cent     INTEGER NOT NULL CHECK (betrag_cent > 0),
    datum           TEXT NOT NULL
);
"""

BEISPIELDATEN = {
    "produkte": [
        ("K-100", "Wasserkocher Kiwi Classic", "Küche", 3990, 12),
        ("K-101", "Wasserkocher Kiwi Glas", "Küche", 5490, 0),
        ("K-200", "Toaster Zwei Scheiben", "Küche", 2990, 7),
        ("B-300", "Schreibtischlampe LED", "Büro", 4450, 3),
        ("B-301", "Ergonomische Maus", "Büro", 2499, 25),
        ("B-302", "Tastatur leise", "Büro", 6900, 4),
        ("G-400", "Gutschein 25 Euro", "Gutschein", 2500, 999),
    ],
    "kunden": [("C-1", "Anna Beispiel", "anna@example.com"), ("C-2", "Ben Muster", "ben@example.com")],
    "bestellungen": [
        ("B-1042", "C-1", "geliefert", "2026-10-10"),
        ("B-1043", "C-1", "unterwegs", None),
        ("B-0977", "C-2", "geliefert", "2026-08-30"),
        ("B-1050", "C-2", "geliefert", "2026-10-20"),
        ("B-1061", "C-1", "geliefert", "2026-10-18"),
    ],
    "positionen": [
        ("B-1042", "K-100", 1, 3990), ("B-1042", "B-301", 2, 2499),
        ("B-1043", "B-302", 1, 6900),
        ("B-0977", "B-300", 1, 4450),
        ("B-1050", "K-200", 4, 2990),
        ("B-1061", "G-400", 1, 2500),
    ],
}


def neu_anlegen(ziel: Path | None = None) -> Path:
    """Löscht die Datenbank und legt sie mit den Beispieldaten neu an."""
    ziel = ziel or pfad()
    ziel.unlink(missing_ok=True)
    with sqlite3.connect(ziel) as con:
        con.executescript(SCHEMA)
        for tabelle, zeilen in BEISPIELDATEN.items():
            platzhalter = ", ".join("?" * len(zeilen[0]))
            con.executemany(f"INSERT INTO {tabelle} VALUES ({platzhalter})", zeilen)
    con.close()
    return ziel


@contextmanager
def verbindung():
    """Eine Verbindung pro Aufruf. `with` sorgt für COMMIT bei Erfolg und ROLLBACK bei einem Fehler."""
    if not pfad().exists():
        neu_anlegen()
    con = sqlite3.connect(pfad(), timeout=5)
    con.row_factory = sqlite3.Row          # Zeilen wie ein dict lesen: zeile["name"]
    con.execute("PRAGMA foreign_keys = ON")  # SQLite prüft Fremdschlüssel nur mit diesem Schalter
    try:
        with con:
            yield con
    finally:
        con.close()


def euro(cent: int) -> float:
    return round(cent / 100, 2)


if __name__ == "__main__":
    if "--neu" in sys.argv:
        print(f"Neu angelegt: {neu_anlegen().name}")
    else:
        print(__doc__)
