"""Bestellungen: Positionen, Gesamtsumme, Versandkosten."""

from dataclasses import dataclass

from shop.preise import brutto, positionspreis, runde_cent

VERSANDKOSTEN = 4.90
VERSANDFREI_AB = 50.00


@dataclass
class Position:
    artikel: str
    einzelpreis_netto: float
    menge: int


def entferne_leere_positionen(positionen: list) -> list:
    """Entfernt alle Positionen mit Menge 0 aus der Liste."""
    for position in positionen:
        if position.menge == 0:
            positionen.remove(position)
    return positionen


def warenwert_brutto(positionen: list) -> float:
    """Summe aller Positionen inklusive Staffelrabatt und Mehrwertsteuer."""
    return runde_cent(
        sum(brutto(positionspreis(p.einzelpreis_netto, p.menge)) for p in positionen)
    )


def gesamtsumme(positionen: list, gutschein_prozent: int = 0) -> float:
    """Endbetrag einer Bestellung.

    Der Gutschein wird vom Warenwert abgezogen. Versandkostenfrei ist die
    Bestellung, wenn der Warenwert NACH Abzug des Gutscheins mindestens
    50 Euro beträgt.
    """
    warenwert = warenwert_brutto(positionen)
    versand = 0.0 if warenwert >= VERSANDFREI_AB else VERSANDKOSTEN
    warenwert = warenwert * (100 - gutschein_prozent) / 100
    return runde_cent(warenwert + versand)


def artikel_liste(positionen: list) -> list:
    """Alphabetische Liste der bestellten Artikel ohne Dopplungen."""
    return sorted({p.artikel for p in positionen})
