from datetime import date

import pytest

from shop import export, kunden
from shop.bestellung import Position, artikel_liste, entferne_leere_positionen, gesamtsumme
from shop.gutscheine import Gutschein, GutscheinVerwaltung
from shop.lager import Lager
from shop.preise import brutto, formatiere_euro, positionspreis, staffelrabatt


def test_brutto():
    assert brutto(100.0) == 119.0


def test_staffelrabatt():
    assert staffelrabatt(1) == 0
    assert staffelrabatt(20) == 5
    assert staffelrabatt(50) == 10
    assert staffelrabatt(100) == 15


def test_positionspreis_mit_rabatt():
    assert positionspreis(2.0, 50) == 90.0


def test_formatiere_euro():
    assert formatiere_euro(1234.5) == "1.234,50 €"


def test_lager_reservieren():
    lager = Lager({"tasse": 10})
    lager.reservieren("tasse", 4)
    assert lager.verfuegbar("tasse") == 6
    with pytest.raises(ValueError):
        lager.reservieren("tasse", 7)


def test_lager_ausliefern():
    lager = Lager({"tasse": 10})
    lager.reservieren("tasse", 4)
    lager.ausliefern("tasse", 4)
    assert lager.bestand["tasse"] == 6


def test_gutschein_einloesen():
    verwaltung = GutscheinVerwaltung()
    verwaltung.anlegen(Gutschein("SOMMER10", 10, date(2026, 12, 31)))
    assert verwaltung.einloesen("SOMMER10", date(2026, 10, 1)) == 10
    with pytest.raises(ValueError):
        verwaltung.einloesen("SOMMER10", date(2026, 10, 2))


def test_gutschein_abgelaufen():
    verwaltung = GutscheinVerwaltung()
    verwaltung.anlegen(Gutschein("ALT", 5, date(2026, 1, 31)))
    with pytest.raises(ValueError):
        verwaltung.pruefen("ALT", date(2026, 2, 15))


def test_leere_positionen():
    positionen = [Position("tasse", 5.0, 2), Position("teller", 8.0, 0)]
    assert len(entferne_leere_positionen(positionen)) == 1


def test_gesamtsumme_mit_versand():
    assert gesamtsumme([Position("tasse", 25.0, 1)]) == 34.65


def test_gesamtsumme_versandfrei():
    assert gesamtsumme([Position("kanne", 50.0, 1)]) == 59.5


def test_artikel_liste():
    positionen = [Position("b", 1.0, 1), Position("a", 1.0, 1), Position("b", 1.0, 2)]
    assert artikel_liste(positionen) == ["a", "b"]


def test_kunden():
    con = kunden.verbinde()
    kunden_id = kunden.kunde_anlegen(con, "Anna Beispiel", "Anna@Example.org")
    assert kunden.finde_per_email(con, "anna@example.org")[0] == kunden_id
    assert len(kunden.suche_nach_name(con, "Anna")) == 1
    assert kunden.kunde_loeschen(con, kunden_id) is True


def test_export(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    pfad = export.schreibe_csv("oktober", [(1, "anna", 16.8)])
    assert pfad.endswith("oktober.csv")
    assert export.durchschnittlicher_bestellwert([10.0, 20.0]) == 15.0
    assert export.umsatz_pro_kunde([(1, "anna", 16.8), (2, "anna", 3.2)]) == {"anna": 20.0}
