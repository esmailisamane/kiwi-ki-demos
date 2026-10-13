"""Rechnungen: Nummernkreis, Summen, Skonto."""

from datetime import date

SKONTO_PROZENT = 2
SKONTO_TAGE = 14


def naechste_rechnungsnummer(vorhandene: list, jahr: int) -> str:
    """Nächste freie Nummer im Format '2026-17' (fortlaufend pro Jahr, ohne führende Nullen)."""
    dieses_jahr = [n for n in vorhandene if n.startswith(f"{jahr}-")]
    if not dieses_jahr:
        return f"{jahr}-1"
    letzte = max(dieses_jahr)
    laufende = int(letzte.split("-")[1])
    return f"{jahr}-{laufende + 1}"


def positionssummen(positionen: list) -> list:
    """Gibt je Position die Summe (Preis mal Menge) zurück. Die übergebenen Daten bleiben unverändert."""
    summen = []
    for position in positionen:
        position["preis"] = round(position["preis"] * position["menge"], 2)
        summen.append(position["preis"])
    return summen


def rechnungsbetrag(positionen: list) -> float:
    """Gesamtbetrag einer Rechnung."""
    return round(sum(p["preis"] * p["menge"] for p in positionen), 2)


def skonto_betrag(betrag: float, rechnungsdatum: date, zahltag: date) -> float:
    """Skonto in Euro, wenn innerhalb von 14 Tagen nach Rechnungsdatum gezahlt wird, sonst 0.0."""
    tage = (zahltag - rechnungsdatum).days
    if 0 <= tage <= SKONTO_TAGE:
        return round(betrag * SKONTO_PROZENT / 100, 2)
    return 0.0


def ist_ueberfaellig(faellig_am: date, heute: date, bezahlt: bool) -> bool:
    """Eine Rechnung ist überfällig, wenn sie nach dem Fälligkeitstag noch offen ist."""
    return not bezahlt and heute > faellig_am
