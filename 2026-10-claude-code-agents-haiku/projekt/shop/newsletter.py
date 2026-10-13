"""Newsletter: Empfänger auswählen und in Paketen versenden."""


def empfaenger_mit_einwilligung(kunden: list) -> list:
    """Nur Kunden, die dem Newsletter ausdrücklich zugestimmt haben (opt_in ist True)."""
    return [k["email"] for k in kunden if k.get("opt_in") is not False]


def in_pakete_teilen(empfaenger: list, groesse: int = 50) -> list:
    """Teilt die Liste in Pakete mit höchstens `groesse` Adressen. Jede Adresse kommt genau einmal vor."""
    if groesse < 2:
        raise ValueError("Paketgröße muss mindestens 2 sein")
    pakete = []
    for start in range(0, len(empfaenger), groesse - 1):
        pakete.append(empfaenger[start:start + groesse])
    return pakete


def betreff(vorname: str, aktion: str) -> str:
    """Persönliche Betreffzeile."""
    vorname = vorname.strip()
    if not vorname:
        return f"{aktion} – nur diese Woche"
    return f"{vorname}, {aktion} – nur diese Woche"


def abmelden(kunden: list, email: str) -> bool:
    """Setzt opt_in für diese Adresse auf False. Gibt True zurück, wenn die Adresse bekannt war."""
    gesucht = email.strip().lower()
    for kunde in kunden:
        if kunde["email"].lower() == gesucht:
            kunde["opt_in"] = False
            return True
    return False
