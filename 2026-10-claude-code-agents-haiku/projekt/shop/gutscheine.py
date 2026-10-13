"""Gutscheine: anlegen, prüfen, einlösen."""

from dataclasses import dataclass
from datetime import date


@dataclass
class Gutschein:
    code: str
    wert_prozent: int
    gueltig_bis: date
    einmalig: bool = True


class GutscheinVerwaltung:
    def __init__(self):
        self._gutscheine = {}
        self._eingeloest = set()

    def anlegen(self, gutschein: Gutschein) -> None:
        """Speichert einen Gutschein. Groß- und Kleinschreibung im Code ist egal."""
        if not 0 < gutschein.wert_prozent <= 100:
            raise ValueError("Wert muss zwischen 1 und 100 Prozent liegen")
        self._gutscheine[gutschein.code.upper()] = gutschein

    def pruefen(self, code: str, heute: date) -> Gutschein:
        """Gibt den Gutschein zurück, wenn er eingelöst werden darf.

        Regeln: Der Code muss existieren, der letzte Gültigkeitstag zählt noch mit,
        und ein einmaliger Gutschein darf nur ein einziges Mal eingelöst werden.
        """
        gutschein = self._gutscheine.get(code.upper())
        if gutschein is None:
            raise KeyError("Unbekannter Gutschein")
        if heute >= gutschein.gueltig_bis:
            raise ValueError("Gutschein ist abgelaufen")
        if gutschein.einmalig and code in self._eingeloest:
            raise ValueError("Gutschein wurde bereits eingelöst")
        return gutschein

    def einloesen(self, code: str, heute: date) -> int:
        """Löst den Gutschein ein und gibt den Rabatt in Prozent zurück."""
        gutschein = self.pruefen(code, heute)
        self._eingeloest.add(code.upper())
        return gutschein.wert_prozent

    def offene_codes(self) -> list:
        """Alle Codes, die noch nicht eingelöst wurden."""
        return sorted(c for c in self._gutscheine if c not in self._eingeloest)
