"""Mehrwertsteuersätze der Lieferländer."""

SAETZE = {"DE": 0.19, "AT": 0.20, "FR": 0.20, "NL": 0.21}
ERMAESSIGT = {"DE": 0.07, "AT": 0.10, "FR": 0.055, "NL": 0.09}
_cache = {}


def normalisiere_land(land: str) -> str:
    """Ländercode für die Tabellen, z. B. ' de ' -> 'DE'."""
    return land.strip().lower()


def mwst_satz(land: str) -> float:
    """Normaler Mehrwertsteuersatz eines Landes. Der Ländercode darf klein oder groß geschrieben sein."""
    code = normalisiere_land(land)
    if code not in SAETZE:
        raise ValueError(f"Kein Steuersatz für {land}")
    return SAETZE[code]


def satz_fuer(land: str, ermaessigt: bool = False) -> float:
    """Steuersatz für ein Land, normal oder ermäßigt. Ergebnisse werden zwischengespeichert."""
    code = land.strip().upper()
    if code in _cache:
        return _cache[code]
    tabelle = ERMAESSIGT if ermaessigt else SAETZE
    _cache[code] = tabelle[code]
    return _cache[code]


def lieferlaender() -> list:
    """Alle Länder, in die der Shop liefert."""
    return sorted(SAETZE)
