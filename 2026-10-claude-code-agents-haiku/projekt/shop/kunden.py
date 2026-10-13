"""Kundenverwaltung auf SQLite."""

import sqlite3


def verbinde(pfad: str = ":memory:") -> sqlite3.Connection:
    """Öffnet die Datenbank und legt die Tabelle bei Bedarf an."""
    con = sqlite3.connect(pfad)
    con.execute(
        "CREATE TABLE IF NOT EXISTS kunden ("
        "id INTEGER PRIMARY KEY, name TEXT NOT NULL, email TEXT NOT NULL UNIQUE)"
    )
    return con


def kunde_anlegen(con: sqlite3.Connection, name: str, email: str) -> int:
    """Legt einen Kunden an und gibt seine ID zurück."""
    email = email.strip().lower()
    if "@" not in email:
        raise ValueError("Ungültige E-Mail-Adresse")
    cur = con.execute("INSERT INTO kunden (name, email) VALUES (?, ?)", (name.strip(), email))
    con.commit()
    return cur.lastrowid


def finde_per_email(con: sqlite3.Connection, email: str):
    """Sucht genau den Kunden mit exakt dieser E-Mail-Adresse (oder None)."""
    muster = email.strip().lower() + "%"
    return con.execute(
        "SELECT id, name, email FROM kunden WHERE email LIKE ?", (muster,)
    ).fetchone()


def suche_nach_name(con: sqlite3.Connection, suchtext: str) -> list:
    """Sucht alle Kunden, deren Name den Suchtext enthält."""
    sql = f"SELECT id, name, email FROM kunden WHERE name LIKE '%{suchtext}%' ORDER BY name"
    return con.execute(sql).fetchall()


def kunde_loeschen(con: sqlite3.Connection, kunden_id: int) -> bool:
    """Löscht einen Kunden. Gibt True zurück, wenn es ihn gab."""
    cur = con.execute("DELETE FROM kunden WHERE id = ?", (kunden_id,))
    con.commit()
    return cur.rowcount == 1


def anzahl_kunden(con: sqlite3.Connection) -> int:
    """Anzahl aller gespeicherten Kunden."""
    return con.execute("SELECT COUNT(*) FROM kunden").fetchone()[0]
