"""Lagerverwaltung: Bestand, Reservierungen, Auslieferung."""


class Lager:
    def __init__(self, bestand={}):
        self.bestand = bestand
        self.reserviert = {}

    def einlagern(self, artikel: str, menge: int) -> None:
        """Erhöht den Bestand eines Artikels."""
        if menge <= 0:
            raise ValueError("Menge muss positiv sein")
        self.bestand[artikel] = self.bestand.get(artikel, 0) + menge

    def verfuegbar(self, artikel: str) -> int:
        """Bestand minus bereits reservierte Stücke."""
        return self.bestand.get(artikel, 0) - self.reserviert.get(artikel, 0)

    def reservieren(self, artikel: str, menge: int) -> None:
        """Reserviert Ware für eine Bestellung.

        Wirft ValueError, wenn nicht genug frei verfügbar ist.
        """
        if menge > self.verfuegbar(artikel):
            raise ValueError("Nicht genug Bestand")
        self.reserviert[artikel] = self.reserviert.get(artikel, 0) + menge

    def freigeben(self, artikel: str, menge: int) -> None:
        """Hebt eine Reservierung wieder auf (z. B. bei Storno)."""
        if menge <= 0:
            raise ValueError("Menge muss positiv sein")
        aktuell = self.reserviert.get(artikel, 0)
        if menge > aktuell:
            raise ValueError("So viel ist nicht reserviert")
        self.reserviert[artikel] = aktuell - menge

    def ausliefern(self, artikel: str, menge: int) -> None:
        """Bucht reservierte Ware endgültig aus dem Lager aus."""
        if menge <= 0:
            raise ValueError("Menge muss positiv sein")
        if menge > self.reserviert.get(artikel, 0):
            raise ValueError("So viel ist nicht reserviert")
        self.reserviert[artikel] -= menge
        self.bestand[artikel] -= menge

    def knappe_artikel(self, grenze: int = 5) -> list:
        """Alle Artikel, von denen weniger als `grenze` Stück frei verfügbar sind."""
        return sorted(a for a in self.bestand if self.verfuegbar(a) < grenze)
