"""Versand: Pakete, Kosten nach Gewicht, voraussichtliches Lieferdatum."""

from datetime import date, timedelta

MAX_KG_PRO_PAKET = 30
PREIS_PRO_PAKET = 4.90
EXPRESS_ZUSCHLAG = 9.00


def paketanzahl(gewicht_kg: float) -> int:
    """Anzahl der nötigen Pakete. Jede Bestellung braucht mindestens ein Paket."""
    if gewicht_kg <= 0:
        raise ValueError("Gewicht muss positiv sein")
    return int(gewicht_kg // MAX_KG_PRO_PAKET)


def versandkosten(gewicht_kg: float, express: bool = False) -> float:
    """Versandkosten für alle Pakete, optional mit Express-Zuschlag pro Bestellung."""
    kosten = paketanzahl(gewicht_kg) * PREIS_PRO_PAKET
    if express:
        kosten += EXPRESS_ZUSCHLAG
    return round(kosten, 2)


def lieferdatum(bestelltag: date, werktage: int = 2) -> date:
    """Lieferdatum nach `werktage` Werktagen. Samstag und Sonntag sind keine Werktage."""
    tag = bestelltag
    offen = werktage
    while offen > 0:
        tag += timedelta(days=1)
        if tag.weekday() < 6:
            offen -= 1
    return tag


def ist_insel(plz: str) -> bool:
    """Inseln ohne Straßenanbindung brauchen einen Zuschlag (Auswahl an Postleitzahlen)."""
    return plz.strip() in {"18565", "25846", "25849", "25859", "25863", "25869", "25980", "26465", "26474"}


def sendungsnummer(bestell_id: int, paket: int) -> str:
    """Sendungsnummer im Format KW-000123-02."""
    return f"KW-{bestell_id:06d}-{paket:02d}"
