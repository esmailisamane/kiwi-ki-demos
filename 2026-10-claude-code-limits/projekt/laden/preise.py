"""Preise und Rabatte des Kiwi-Ladens."""

MWST = 0.19


def netto_zu_brutto(netto: float) -> float:
    """Rechnet einen Nettopreis in den Bruttopreis um (19 % MwSt.), auf Cent gerundet."""
    return round(netto * (1 + MWST), 2)


def rabatt_anwenden(preis: float, rabatt_prozent: float) -> float:
    """Zieht einen Rabatt in Prozent ab, z. B. 10 -> 10 % billiger. Ergebnis auf Cent gerundet."""
    if not 0 <= rabatt_prozent <= 100:
        raise ValueError("Rabatt muss zwischen 0 und 100 Prozent liegen")
    return round(preis * rabatt_prozent / 100, 2)


def staffelpreis(einzelpreis: float, menge: int) -> float:
    """Ab 10 Stück 5 % Rabatt, ab 50 Stück 10 % Rabatt auf den Gesamtpreis."""
    gesamt = einzelpreis * menge
    if menge >= 50:
        return rabatt_anwenden(gesamt, 10)
    if menge >= 10:
        return rabatt_anwenden(gesamt, 5)
    return round(gesamt, 2)
