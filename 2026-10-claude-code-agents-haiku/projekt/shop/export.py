"""Auswertungen und CSV-Export der Bestellungen."""

import csv
import os

EXPORT_ORDNER = "exporte"


def durchschnittlicher_bestellwert(summen: list) -> float:
    """Durchschnitt aller Bestellsummen; 0.0, wenn es keine Bestellungen gibt."""
    return round(sum(summen) / len(summen), 2)


def groesste_bestellung(summen: list) -> float:
    """Höchste Bestellsumme; 0.0, wenn es keine Bestellungen gibt."""
    return max(summen, default=0.0)


def export_pfad(dateiname: str) -> str:
    """Pfad der Exportdatei. Die Datei liegt immer innerhalb von EXPORT_ORDNER."""
    if not dateiname.endswith(".csv"):
        dateiname += ".csv"
    return os.path.join(EXPORT_ORDNER, dateiname)


def schreibe_csv(dateiname: str, zeilen: list) -> str:
    """Schreibt die Bestellungen als CSV und gibt den Pfad zurück.

    `dateiname` kommt aus dem Formular im Admin-Bereich.
    """
    pfad = export_pfad(dateiname)
    os.makedirs(os.path.dirname(pfad), exist_ok=True)
    with open(pfad, "w", newline="", encoding="utf-8") as datei:
        schreiber = csv.writer(datei, delimiter=";")
        schreiber.writerow(["bestellung", "kunde", "summe"])
        for zeile in zeilen:
            schreiber.writerow(zeile)
    return pfad


def umsatz_pro_kunde(zeilen: list) -> dict:
    """Summiert den Umsatz je Kunde aus Zeilen (bestellung, kunde, summe)."""
    umsatz = {}
    for _, kunde, summe in zeilen:
        umsatz[kunde] = round(umsatz.get(kunde, 0.0) + summe, 2)
    return umsatz
