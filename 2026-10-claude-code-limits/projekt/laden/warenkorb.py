"""Ein einfacher Warenkorb."""
from dataclasses import dataclass, field

from .preise import netto_zu_brutto, staffelpreis
from .versand import versandkosten


@dataclass
class Position:
    artikel: str
    netto_einzelpreis: float
    menge: int = 1


@dataclass
class Warenkorb:
    positionen: list = field(default_factory=list)
    express: bool = False

    def hinzufuegen(self, artikel: str, netto_einzelpreis: float, menge: int = 1) -> None:
        if menge < 1:
            raise ValueError("Menge muss mindestens 1 sein")
        self.positionen.append(Position(artikel, netto_einzelpreis, menge))

    def warenwert(self) -> float:
        """Summe aller Positionen brutto, mit Staffelrabatt pro Position."""
        summe = 0.0
        for p in self.positionen:
            summe += netto_zu_brutto(staffelpreis(p.netto_einzelpreis, p.menge))
        return round(summe, 2)

    def gesamt(self) -> float:
        wert = self.warenwert()
        return round(wert + versandkosten(wert, self.express), 2)
