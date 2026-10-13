"""Zeigt jeden der 36 eingebauten Fehler mit einem kurzen, echten Aufruf.

Start (im Ordner des Videos): python auswertung/beweis.py
"""
import inspect
import io
import logging
import os
import sys
from datetime import date, datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "projekt"))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from shop import (  # noqa: E402
    benachrichtigung, bewertungen, export, kunden, newsletter, passwort, rechnung, retoure, sitzung, steuer, suche,
    versand, zahlung,
)
from shop.warenkorb import Warenkorb  # noqa: E402
from shop.bestellung import Position, entferne_leere_positionen, gesamtsumme  # noqa: E402
from shop.gutscheine import Gutschein, GutscheinVerwaltung  # noqa: E402
from shop.lager import Lager  # noqa: E402
from shop.preise import runde_cent, staffelrabatt  # noqa: E402

bestaetigt = 0


def zeige(nr, text, bedingung, wert):
    global bestaetigt
    bestaetigt += bool(bedingung)
    status = "bestätigt" if bedingung else "NICHT bestätigt"
    print(f"F{nr:02d} {status}: {text} -> {wert!r}")


w = runde_cent(19.999)
zeige(1, "runde_cent(19.999) schneidet ab statt zu runden (erwartet 20.0)", w != 20.0, w)

w = staffelrabatt(10)
zeige(2, "staffelrabatt(10), laut Text 'ab 10 Stück 5 %' (erwartet 5)", w != 5, w)

lager = Lager({"tasse": 10})
lager.reservieren("tasse", 10)
lager.reservieren("tasse", -10)
w = lager.verfuegbar("tasse")
zeige(3, "reservieren mit negativer Menge hebt fremde Reservierungen auf (erwartet ValueError)", w == 10, w)

erstes = Lager()
erstes.einlagern("teller", 3)
w = Lager().bestand
zeige(4, "ein neues Lager() sieht den Bestand eines anderen Lagers (erwartet {})", w != {}, w)

verwaltung = GutscheinVerwaltung()
verwaltung.anlegen(Gutschein("SOMMER10", 10, date(2026, 12, 31)))
try:
    verwaltung.pruefen("SOMMER10", date(2026, 12, 31))
    w = "gültig"
except ValueError as fehler:
    w = str(fehler)
zeige(5, "Gutschein am letzten Gültigkeitstag (erwartet gültig)", w != "gültig", w)

w = [verwaltung.einloesen("sommer10", date(2026, 10, 1)), verwaltung.einloesen("sommer10", date(2026, 10, 2))]
zeige(6, "einmaliger Gutschein, klein geschrieben, zweimal eingelöst (erwartet ValueError)", len(w) == 2, w)

w = gesamtsumme([Position("kanne", 45.0, 1)], gutschein_prozent=20)
zeige(7, "Warenwert nach Gutschein 42,84 Euro, also Versand fällig (erwartet 47.74)", w != 47.74, w)

positionen = [Position("a", 1.0, 0), Position("b", 1.0, 0), Position("c", 1.0, 1)]
w = [p.artikel for p in entferne_leere_positionen(positionen)]
zeige(8, "zwei leere Positionen hintereinander (erwartet ['c'])", w != ["c"], w)

con = kunden.verbinde()
kunden.kunde_anlegen(con, "Anna Lang", "anna@example.org.uk")
w = kunden.finde_per_email(con, "anna@example.org")
zeige(9, "finde_per_email liefert eine andere, längere Adresse (erwartet None)", w is not None, w)

kunden.kunde_anlegen(con, "Ben", "ben@example.org")
w = kunden.suche_nach_name(con, "gibtesnicht%' OR 1=1 --")
zeige(10, "SQL-Injection in suche_nach_name liefert alle Kunden (erwartet [])", len(w) == 2, w)

try:
    w = export.durchschnittlicher_bestellwert([])
except ZeroDivisionError as fehler:
    w = f"ZeroDivisionError: {fehler}"
zeige(11, "Durchschnitt ohne Bestellungen (erwartet 0.0)", w != 0.0, w)

w = os.path.normpath(export.export_pfad("../../geheim"))
zeige(12, "export_pfad verlässt den Export-Ordner, Path Traversal (erwartet Pfad in exporte)", not w.startswith("exporte"), w)

w = versand.paketanzahl(12)
zeige(13, "paketanzahl(12 kg): jede Bestellung braucht mindestens ein Paket (erwartet 1)", w != 1, w)

w = versand.lieferdatum(date(2026, 10, 9), 2)  # ein Freitag
zeige(14, "Freitag + 2 Werktage, Samstag zählt mit (erwartet Dienstag 2026-10-13)", w != date(2026, 10, 13), str(w))

w = rechnung.naechste_rechnungsnummer(["2026-8", "2026-9", "2026-10"], 2026)
zeige(15, "nächste Rechnungsnummer nach 2026-10 (erwartet '2026-11')", w != "2026-11", w)

daten = [{"preis": 5.0, "menge": 3}]
rechnung.positionssummen(daten)
w = daten[0]["preis"]
zeige(16, "positionssummen verändert die übergebenen Daten (erwartet Preis 5.0)", w != 5.0, w)

w = newsletter.empfaenger_mit_einwilligung([{"email": "a@example.org"}, {"email": "b@example.org", "opt_in": True}])
zeige(17, "Kunde ohne Einwilligung bekommt den Newsletter (erwartet nur b@example.org)", "a@example.org" in w, w)

w = newsletter.in_pakete_teilen(list("abcdef"), 3)
zeige(18, "Pakete überlappen, Adressen doppelt (erwartet zwei Pakete mit je 3)", sum(len(x) for x in w) != 6, w)

w = bewertungen.durchschnitt([5, 4])
zeige(19, "Durchschnitt aus 5 und 4 Sternen (erwartet 4.5)", w != 4.5, w)

w = bewertungen.als_html("Max", 5, "<script>alert(1)</script>")
zeige(20, "Kundentext landet ohne Escaping im HTML (XSS)", "<script>" in w, w[-37:])

w = "random.choice" in inspect.getsource(sitzung.neues_token)
zeige(21, "Sitzungs-Token kommt aus random statt aus secrets (vorhersagbar)", w, "random.choice")

start = datetime(2026, 10, 12, 12, 0)
sitz = sitzung.neue_sitzung(1, start)
w = [sitzung.ist_gueltig(sitz, start + timedelta(minutes=5)), sitzung.ist_gueltig(sitz, start + timedelta(minutes=45))]
zeige(22, "Sitzung nach 5 und nach 45 Minuten gültig? (erwartet [True, False])", w != [True, False], w)

w = passwort.hash_passwort("geheim1234")
zeige(23, "Passwort-Hash ist ungesalzenes MD5 (32 Hex-Zeichen, immer gleich)", len(w) == 32, w)

w = passwort.passwort_stimmt("irgendwas", passwort.hash_passwort("irgendwas")[:8] + "x" * 24)
zeige(24, "Vergleich prüft nur die ersten 8 Zeichen des Hashes (erwartet False)", w is True, w)

strom = io.StringIO()
logging.getLogger("shop.zahlung").addHandler(logging.StreamHandler(strom))
logging.getLogger("shop.zahlung").setLevel(logging.INFO)
zahl = zahlung.zahlung_buchen(7, 50.0, "4111 1111 1111 4242")
w = strom.getvalue().strip()
zeige(25, "volle Kartennummer steht im Protokoll (erwartet maskiert)", "4111 1111 1111 4242" in w, w)

zahlung.erstatten(zahl, 50.0)
zahlung.erstatten(zahl, 60.0)
w = zahl["erstattet"]
zeige(26, "50 Euro gezahlt, danach insgesamt erstattet (erwartet ValueError)", w > 50, w)

artikel = [{"name": "a", "preis": 3.0}, {"name": "b", "preis": 1.0}, {"name": "c", "preis": 2.0}]
w = [a["preis"] for a in suche.sortiere_nach_preis(artikel)]
zeige(27, "Standard-Sortierung, günstigster zuerst (erwartet [1.0, 2.0, 3.0])", w != [1.0, 2.0, 3.0], w)

w = suche.seite(list(range(25)), 1)
zeige(28, "Seite 1 von 25 Treffern (erwartet 0 bis 9)", w != list(range(10)), w)

korb = Warenkorb()
korb.hinzufuegen("tasse", 2)
korb.hinzufuegen("tasse", 3)
w = korb.positionen["tasse"]
zeige(29, "2 Tassen + 3 Tassen im Korb (erwartet 5)", w != 5, w)

w = korb.gesamtmenge()
zeige(30, "Gesamtzahl aller Stücke bei 3 Tassen (erwartet 3)", w != 3, w)

w = retoure.rueckgabe_bis(date(2026, 10, 1))
zeige(31, "Rückgabe bis 14 Tage nach dem 1.10. (erwartet 2026-10-15)", w != date(2026, 10, 15), str(w))

w = retoure.erstattungsbetrag({"summe": 54.9, "versand": 4.9})
zeige(32, "Erstattung ohne Versand (erwartet 50.0)", w != 50.0, w)

try:
    w = steuer.mwst_satz("DE")
except ValueError as fehler:
    w = f"ValueError: {fehler}"
zeige(33, "mwst_satz('DE') (erwartet 0.19)", w != 0.19, w)

steuer.satz_fuer("DE")
w = steuer.satz_fuer("DE", ermaessigt=True)
zeige(34, "ermäßigter Satz nach einem normalen Aufruf, falscher Cache (erwartet 0.07)", w != 0.07, w)


def immer_verbindungsfehler(_):
    immer_verbindungsfehler.aufrufe += 1
    if immer_verbindungsfehler.aufrufe > 50:
        raise KeyboardInterrupt
    raise ConnectionError


immer_verbindungsfehler.aufrufe = 0
try:
    benachrichtigung.sende_mit_wiederholung(immer_verbindungsfehler, "hallo")
    w = immer_verbindungsfehler.aufrufe
except KeyboardInterrupt:
    w = "nach 50 Aufrufen von Hand abgebrochen"
zeige(35, "Wiederholung bei Dauerfehler (erwartet 3 Versuche, dann False)", w != 3, w)


def mailserver_weg(_):
    raise RuntimeError("Mailserver weg")


w = benachrichtigung.sende_bestellbestaetigung(mailserver_weg, 1, "a@example.org")
zeige(36, "Versand scheitert, Funktion meldet trotzdem Erfolg (erwartet False)", w is True, w)

print(f"\n{bestaetigt} von 36 eingebauten Fehlern bestätigt")
