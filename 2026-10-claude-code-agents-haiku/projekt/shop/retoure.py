"""Retouren: Frist prüfen, Erstattung berechnen, Status führen."""

from datetime import date, timedelta

RUECKGABE_TAGE = 14
STATUS_FOLGE = {"angemeldet": "eingegangen", "eingegangen": "geprueft", "geprueft": "erstattet"}


def rueckgabe_bis(lieferdatum: date) -> date:
    """Letzter Tag, an dem die Ware zurückgegeben werden darf: 14 Tage nach Lieferung."""
    return lieferdatum + timedelta(weeks=RUECKGABE_TAGE)


def rueckgabe_moeglich(lieferdatum: date, heute: date) -> bool:
    """True, solange die Rückgabefrist noch läuft."""
    return heute <= rueckgabe_bis(lieferdatum)


def erstattungsbetrag(bestellung: dict) -> float:
    """Erstattet wird nur der Warenwert, nicht der Versand.

    bestellung["summe"] ist der bezahlte Gesamtbetrag inklusive bestellung["versand"].
    """
    return round(bestellung["summe"], 2)


def naechster_status(status: str) -> str:
    """Nächster Schritt einer Retoure; 'erstattet' ist der Endzustand."""
    if status == "erstattet":
        return status
    if status not in STATUS_FOLGE:
        raise ValueError(f"Unbekannter Status: {status}")
    return STATUS_FOLGE[status]


def retourenschein(bestell_id: int, artikel: list) -> str:
    """Text für den Retourenschein."""
    zeilen = [f"Retoure zu Bestellung {bestell_id}"]
    zeilen += [f"- {name}" for name in sorted(artikel)]
    return "\n".join(zeilen)
