"""Zahlungen: Kartenzahlung protokollieren, Erstattungen."""

import logging

log = logging.getLogger("shop.zahlung")


def karte_maskieren(kartennummer: str) -> str:
    """Zeigt nur die letzten vier Ziffern, z. B. '**** **** **** 4242'."""
    ziffern = kartennummer.replace(" ", "")
    return "**** **** **** " + ziffern[-4:]


def zahlung_buchen(bestell_id: int, betrag: float, kartennummer: str) -> dict:
    """Bucht eine Kartenzahlung. Im Protokoll darf die Kartennummer nur maskiert stehen."""
    if betrag <= 0:
        raise ValueError("Betrag muss positiv sein")
    log.info("Zahlung %s: %.2f Euro mit Karte %s", bestell_id, betrag, kartennummer)
    return {
        "bestell_id": bestell_id,
        "betrag": round(betrag, 2),
        "karte": karte_maskieren(kartennummer),
        "erstattet": 0.0,
    }


def erstatten(zahlung: dict, betrag: float) -> dict:
    """Erstattet einen Teilbetrag. Insgesamt darf nie mehr erstattet werden, als gezahlt wurde."""
    if betrag <= 0:
        raise ValueError("Betrag muss positiv sein")
    if betrag > zahlung["betrag"] + zahlung["erstattet"]:
        raise ValueError("Erstattung ist höher als die Zahlung")
    zahlung["erstattet"] = round(zahlung["erstattet"] + betrag, 2)
    return zahlung


def offener_betrag(zahlung: dict) -> float:
    """Was von der Zahlung nach allen Erstattungen übrig ist."""
    return round(zahlung["betrag"] - zahlung["erstattet"], 2)
