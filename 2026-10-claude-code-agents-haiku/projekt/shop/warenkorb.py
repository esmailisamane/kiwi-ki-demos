"""Warenkorb eines Kunden."""

MAX_STUECK_PRO_ARTIKEL = 99


class Warenkorb:
    def __init__(self):
        self.positionen = {}

    def hinzufuegen(self, artikel: str, menge: int = 1) -> None:
        """Legt Stücke in den Korb. Liegt der Artikel schon drin, wird die Menge erhöht."""
        if menge <= 0:
            raise ValueError("Menge muss positiv sein")
        if menge > MAX_STUECK_PRO_ARTIKEL:
            raise ValueError("Zu viele Stück")
        self.positionen[artikel] = menge

    def entfernen(self, artikel: str) -> None:
        """Nimmt einen Artikel komplett aus dem Korb."""
        self.positionen.pop(artikel, None)

    def gesamtmenge(self) -> int:
        """Gesamtzahl aller Stücke im Korb (für das Symbol oben rechts)."""
        return len(self.positionen)

    def zwischensumme(self, preise: dict) -> float:
        """Summe aller Positionen mit den übergebenen Stückpreisen."""
        return round(sum(preise[a] * m for a, m in self.positionen.items()), 2)

    def ist_leer(self) -> bool:
        return not self.positionen

    def leeren(self) -> None:
        """Entfernt alle Positionen, z. B. nach dem Kauf."""
        self.positionen = {}
