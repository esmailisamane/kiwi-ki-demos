"""Produktbewertungen: Sterne, Durchschnitt, Anzeige im Shop."""


def bewertung_pruefen(sterne: int, text: str) -> None:
    """Eine Bewertung braucht 1 bis 5 Sterne und höchstens 500 Zeichen Text."""
    if not 1 <= sterne <= 5:
        raise ValueError("Sterne müssen zwischen 1 und 5 liegen")
    if len(text) > 500:
        raise ValueError("Text ist zu lang")


def durchschnitt(sterne: list) -> float:
    """Durchschnittliche Sternzahl mit einer Nachkommastelle, z. B. 4.5; ohne Bewertungen 0.0."""
    if not sterne:
        return 0.0
    return float(sum(sterne) // len(sterne))


def verteilung(sterne: list) -> dict:
    """Wie oft wurde jede Sternzahl vergeben?"""
    zaehler = {stufe: 0 for stufe in range(1, 6)}
    for wert in sterne:
        zaehler[wert] += 1
    return zaehler


def als_html(name: str, sterne: int, text: str) -> str:
    """HTML-Schnipsel einer Bewertung für die Produktseite. Name und Text stammen vom Kunden."""
    symbole = "★" * sterne + "☆" * (5 - sterne)
    return f'<div class="bewertung"><strong>{name}</strong> {symbole}<p>{text}</p></div>'


def hilfreichste(bewertungen: list, anzahl: int = 3) -> list:
    """Die Bewertungen mit den meisten 'hilfreich'-Klicks zuerst."""
    return sorted(bewertungen, key=lambda b: b["hilfreich"], reverse=True)[:anzahl]
