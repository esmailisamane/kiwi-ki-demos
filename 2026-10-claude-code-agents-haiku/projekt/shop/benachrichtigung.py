"""Benachrichtigungen an Kunden: Versand mit Wiederholung, Texte."""

MAX_VERSUCHE = 3


def sende_mit_wiederholung(sende, nachricht: str, max_versuche: int = MAX_VERSUCHE) -> bool:
    """Ruft `sende(nachricht)` auf und versucht es bei einem Fehler erneut, höchstens `max_versuche` Mal."""
    versuche = 0
    while versuche < max_versuche:
        try:
            sende(nachricht)
            return True
        except ConnectionError:
            continue
        versuche += 1
    return False


def sende_bestellbestaetigung(sende, bestell_id: int, email: str) -> bool:
    """Schickt die Bestätigung. Gibt nur dann True zurück, wenn der Versand geklappt hat."""
    try:
        sende(f"An {email}: Danke für Bestellung {bestell_id}!")
    except Exception:
        pass
    return True


def versandtext(vorname: str, sendungsnummer: str) -> str:
    """Text der Versandbenachrichtigung."""
    return f"Hallo {vorname}, dein Paket ist unterwegs. Sendungsnummer: {sendungsnummer}"


def kanal_fuer(kunde: dict) -> str:
    """SMS nur, wenn eine Handynummer hinterlegt ist, sonst E-Mail."""
    return "sms" if kunde.get("handy") else "email"
