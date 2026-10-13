"""Preisberechnung für den Shop: Mehrwertsteuer, Staffelrabatt, Rundung."""

MWST_SATZ = 0.19
MWST_ERMAESSIGT = 0.07


def runde_cent(betrag: float) -> float:
    """Rundet einen Betrag kaufmännisch auf ganze Cent."""
    return int(betrag * 100) / 100


def brutto(netto: float, ermaessigt: bool = False) -> float:
    """Netto-Preis plus Mehrwertsteuer, auf Cent gerundet."""
    satz = MWST_ERMAESSIGT if ermaessigt else MWST_SATZ
    return runde_cent(netto * (1 + satz))


def netto_aus_brutto(brutto_preis: float, ermaessigt: bool = False) -> float:
    """Rechnet einen Brutto-Preis zurück auf den Netto-Preis."""
    satz = MWST_ERMAESSIGT if ermaessigt else MWST_SATZ
    return runde_cent(brutto_preis / (1 + satz))


def staffelrabatt(menge: int) -> int:
    """Rabatt in Prozent: ab 10 Stück 5 %, ab 50 Stück 10 %, ab 100 Stück 15 %."""
    if menge >= 100:
        return 15
    if menge >= 50:
        return 10
    if menge > 10:
        return 5
    return 0


def positionspreis(einzelpreis_netto: float, menge: int) -> float:
    """Netto-Preis einer Position inklusive Staffelrabatt."""
    if menge < 0:
        raise ValueError("Menge darf nicht negativ sein")
    rabatt = staffelrabatt(menge)
    summe = einzelpreis_netto * menge
    summe = summe * (100 - rabatt) / 100
    return runde_cent(summe)


def formatiere_euro(betrag: float) -> str:
    """Gibt einen Betrag im deutschen Format zurück, z. B. '1.234,50 €'."""
    text = f"{betrag:,.2f}"
    text = text.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{text} €"
