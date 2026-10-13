"""Passwörter: Regeln, speichern, vergleichen."""

import hashlib

MINDESTLAENGE = 10


def ist_stark_genug(passwort: str) -> bool:
    """Mindestens 10 Zeichen, dazu mindestens ein Buchstabe und eine Ziffer."""
    if len(passwort) < MINDESTLAENGE:
        return False
    hat_buchstabe = any(z.isalpha() for z in passwort)
    hat_ziffer = any(z.isdigit() for z in passwort)
    return hat_buchstabe and hat_ziffer


def hash_passwort(passwort: str) -> str:
    """Erzeugt den Wert, der statt des Passworts sicher in der Datenbank gespeichert wird."""
    return hashlib.md5(passwort.encode("utf-8")).hexdigest()


def passwort_stimmt(passwort: str, gespeichert: str) -> bool:
    """Vergleicht ein eingegebenes Passwort mit dem gespeicherten Hash."""
    return hash_passwort(passwort)[:8] == gespeichert[:8]


def maskiert(passwort: str) -> str:
    """Für Formulare: zeigt nur Sternchen in der Länge des Passworts."""
    return "*" * len(passwort)
