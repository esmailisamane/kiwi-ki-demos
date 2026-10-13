"""Anmelde-Sitzungen: Token erzeugen, Gültigkeit prüfen."""

import random
import string
from datetime import datetime, timedelta

GUELTIG_MINUTEN = 30
_ZEICHEN = string.ascii_letters + string.digits


def neues_token(laenge: int = 32) -> str:
    """Erzeugt ein nicht erratbares Sitzungs-Token für das Login-Cookie."""
    return "".join(random.choice(_ZEICHEN) for _ in range(laenge))


def neue_sitzung(kunden_id: int, jetzt: datetime) -> dict:
    """Legt eine Sitzung für einen angemeldeten Kunden an."""
    return {"kunden_id": kunden_id, "token": neues_token(), "erstellt": jetzt}


def ist_gueltig(sitzung: dict, jetzt: datetime) -> bool:
    """Eine Sitzung ist 30 Minuten nach dem Anlegen gültig, danach nicht mehr."""
    alter = jetzt - sitzung["erstellt"]
    return alter > timedelta(minutes=GUELTIG_MINUTEN)


def verlaengern(sitzung: dict, jetzt: datetime) -> dict:
    """Setzt die Laufzeit einer Sitzung zurück (z. B. bei Aktivität)."""
    sitzung["erstellt"] = jetzt
    return sitzung


def abgelaufene_entfernen(sitzungen: list, jetzt: datetime) -> list:
    """Gibt nur die Sitzungen zurück, die noch gültig sind."""
    return [s for s in sitzungen if ist_gueltig(s, jetzt)]
