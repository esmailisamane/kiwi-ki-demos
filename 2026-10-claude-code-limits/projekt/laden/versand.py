"""Versandkosten des Kiwi-Ladens."""

VERSAND_STANDARD = 4.90
GRATIS_AB = 50.00


def versandkosten(warenwert: float, express: bool = False) -> float:
    """Ab 50 Euro Warenwert ist der Standardversand gratis. Express kostet immer 9,90 Euro."""
    if express:
        return 9.90
    if warenwert > GRATIS_AB:
        return 0.0
    return VERSAND_STANDARD
