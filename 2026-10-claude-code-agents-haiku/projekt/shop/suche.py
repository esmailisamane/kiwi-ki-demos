"""Produktsuche: filtern, sortieren, seitenweise ausgeben."""


def filtere(artikel: list, suchtext: str) -> list:
    """Alle Artikel, deren Name den Suchtext enthält (Groß-/Kleinschreibung egal)."""
    gesucht = suchtext.strip().lower()
    return [a for a in artikel if gesucht in a["name"].lower()]


def sortiere_nach_preis(artikel: list, aufsteigend: bool = True) -> list:
    """Sortiert nach Preis; standardmäßig der günstigste Artikel zuerst."""
    return sorted(artikel, key=lambda a: a["preis"], reverse=aufsteigend)


def seite(artikel: list, nummer: int, pro_seite: int = 10) -> list:
    """Gibt eine Ergebnisseite zurück. Die erste Seite hat die Nummer 1."""
    if nummer < 1:
        raise ValueError("Seitennummer beginnt bei 1")
    start = nummer * pro_seite
    return artikel[start:start + pro_seite]


def seitenanzahl(anzahl_artikel: int, pro_seite: int = 10) -> int:
    """Wie viele Seiten braucht man für alle Treffer?"""
    return max(1, -(-anzahl_artikel // pro_seite))


def preisspanne(artikel: list) -> tuple:
    """Kleinster und größter Preis der Treffer, (0.0, 0.0) ohne Treffer."""
    if not artikel:
        return (0.0, 0.0)
    preise = [a["preis"] for a in artikel]
    return (min(preise), max(preise))
