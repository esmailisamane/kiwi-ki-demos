"""Kiwi-Laden: ein ausgedachter Online-Shop als MCP-Server (FastMCP 4 + SQLite).

    uv run python datenbank.py --neu              # Datenbank laden.db mit Beispieldaten anlegen / zurücksetzen
    uv run fastmcp run laden_server.py            # stdio (so startet ihn auch Claude Code)
    uv run fastmcp list laden_server.py           # alle Werkzeuge ansehen
    uv run fastmcp call laden_server.py produkt_suchen suchbegriff=wasserkocher

Nur zum Lernen: Alle Daten sind erfunden (datenbank.py).
"""
import os
import sqlite3
from datetime import date, timedelta
from typing import Annotated, Literal

from fastmcp import Context, FastMCP
from fastmcp.dependencies import CurrentContext
from fastmcp.exceptions import ResourceError, ToolError
from mcp.types import InputRequiredResult, ToolAnnotations
from pydantic import BaseModel, Field

from datenbank import HEUTE, RUECKGABE_TAGE, euro, verbindung
from freigabe import frage_mensch
from regeln import TAGESBUDGET_CENT, ProtokollMiddleware, RegelMiddleware

mcp = FastMCP(
    "kiwi-laden",
    instructions=(
        "Werkzeuge für den Kundenservice des ausgedachten Kiwi-Ladens. "
        "Prüfe zuerst die Bestellung, bevor du eine Rücksendung oder Gutschrift anlegst."
    ),
    mask_error_details=True,  # unerwartete Fehler verraten keine Interna, ToolError-Texte schon
    middleware=[ProtokollMiddleware(), RegelMiddleware()],
)

NUR_LESEN = ToolAnnotations(readOnlyHint=True, openWorldHint=False)
SCHREIBEN = ToolAnnotations(readOnlyHint=False, destructiveHint=False, idempotentHint=False, openWorldHint=False)
FREIGABE_AB_CENT = 5000  # 50 Euro: darüber fragt der Server einen Menschen


# ---------- Rückgabe-Formen (daraus baut FastMCP das Output-Schema) ----------

class Produkt(BaseModel):
    sku: str
    name: str
    kategorie: str
    preis: float
    lieferbar: bool


class Position(BaseModel):
    sku: str
    name: str
    menge: int
    preis: float
    schon_zurueckgemeldet: int


class RuecksendungKurz(BaseModel):
    ruecksendung_id: str
    sku: str
    menge: int
    erstattung: float
    gutschrift_ausgezahlt: bool


class Bestellung(BaseModel):
    bestellnummer: str
    kunde: str
    status: str
    geliefert_am: str | None
    rueckgabe_moeglich_bis: str | None
    positionen: list[Position]
    ruecksendungen: list[RuecksendungKurz]


class Ruecksendung(BaseModel):
    ruecksendung_id: str
    bestellnummer: str
    sku: str
    menge: int
    erstattung: float
    grund: str


class Gutschrift(BaseModel):
    gutschrift_id: str
    ruecksendung_id: str
    betrag: float


# ---------- Werkzeuge (Tools) ----------

@mcp.tool(annotations=NUR_LESEN)
def produkt_suchen(
    suchbegriff: Annotated[str, Field(description="Wort im Produktnamen, z. B. 'wasserkocher'", min_length=2)],
    kategorie: Annotated[Literal["Küche", "Büro", "Gutschein"] | None, Field(description="Optional: nur diese Kategorie")] = None,
    max_preis: Annotated[float | None, Field(description="Optional: höchster Preis in Euro", gt=0)] = None,
) -> list[Produkt]:
    """Sucht Produkte im Katalog. Gibt höchstens 10 Treffer zurück."""
    # Nie Eingaben in den SQL-Text einbauen (kein f-String)! Die ? sind Platzhalter, sqlite3 setzt die Werte sicher ein.
    # % und _ sind in LIKE Joker - wir entschärfen sie, damit "%" nicht alles findet.
    muster = "%" + suchbegriff.replace("!", "!!").replace("%", "!%").replace("_", "!_") + "%"
    sql = "SELECT * FROM produkte WHERE name LIKE ? ESCAPE '!'"
    werte: list = [muster]
    if kategorie:
        sql += " AND kategorie = ?"
        werte.append(kategorie)
    if max_preis is not None:
        sql += " AND preis_cent <= ?"
        werte.append(round(max_preis * 100))
    with verbindung() as con:
        zeilen = con.execute(sql + " ORDER BY sku LIMIT 10", werte).fetchall()
    return [Produkt(sku=z["sku"], name=z["name"], kategorie=z["kategorie"], preis=euro(z["preis_cent"]),
                    lieferbar=z["lager"] > 0) for z in zeilen]


@mcp.tool(annotations=NUR_LESEN)
def bestellung_abrufen(
    bestellnummer: Annotated[str, Field(description="Bestellnummer im Format B-1234", pattern=r"^B-\d{4}$")],
) -> Bestellung:
    """Zeigt Status, Lieferdatum, Positionen, Rückgabefrist und alle bisherigen Rücksendungen samt Gutschrift-Status."""
    with verbindung() as con:
        b = con.execute("SELECT b.*, k.name AS kunde FROM bestellungen b JOIN kunden k ON k.id = b.kunde_id "
                        "WHERE b.nummer = ?", (bestellnummer,)).fetchone()
        if b is None:
            raise ToolError(f"Bestellung {bestellnummer} gibt es nicht.")
        positionen = con.execute(
            "SELECT p.sku, pr.name, p.menge, p.preis_cent, "
            "  (SELECT COALESCE(SUM(r.menge), 0) FROM ruecksendungen r "
            "   WHERE r.bestellnummer = p.bestellnummer AND r.sku = p.sku) AS zurueck "
            "FROM positionen p JOIN produkte pr ON pr.sku = p.sku WHERE p.bestellnummer = ? ORDER BY p.sku",
            (bestellnummer,)).fetchall()
        ruecksendungen = con.execute(
            "SELECT r.id, r.sku, r.menge, r.erstattung_cent, g.id IS NOT NULL AS ausgezahlt "
            "FROM ruecksendungen r LEFT JOIN gutschriften g ON g.ruecksendung_id = r.id "
            "WHERE r.bestellnummer = ? ORDER BY r.id", (bestellnummer,)).fetchall()
    geliefert = date.fromisoformat(b["geliefert_am"]) if b["geliefert_am"] else None
    return Bestellung(
        bestellnummer=bestellnummer,
        kunde=b["kunde"],
        status=b["status"],
        geliefert_am=geliefert.isoformat() if geliefert else None,
        rueckgabe_moeglich_bis=(geliefert + timedelta(days=RUECKGABE_TAGE)).isoformat() if geliefert else None,
        positionen=[Position(sku=p["sku"], name=p["name"], menge=p["menge"], preis=euro(p["preis_cent"]),
                             schon_zurueckgemeldet=p["zurueck"]) for p in positionen],
        ruecksendungen=[RuecksendungKurz(ruecksendung_id=f"R-{r['id']:03d}", sku=r["sku"], menge=r["menge"],
                                         erstattung=euro(r["erstattung_cent"]), gutschrift_ausgezahlt=bool(r["ausgezahlt"]))
                        for r in ruecksendungen],
    )


@mcp.tool(annotations=SCHREIBEN)
def ruecksendung_anlegen(
    bestellnummer: Annotated[str, Field(description="Bestellnummer im Format B-1234", pattern=r"^B-\d{4}$")],
    sku: Annotated[str, Field(description="Artikelnummer aus der Bestellung, z. B. K-100")],
    grund: Annotated[Literal["defekt", "falscher_artikel", "gefaellt_nicht"], Field(description="Grund der Rücksendung")],
    menge: Annotated[int, Field(description="Wie viele Stück zurückgehen", ge=1)] = 1,
) -> Ruecksendung:
    """Legt eine Rücksendung an. Die Erstattung berechnet der Server selbst aus dem Kaufpreis."""
    with verbindung() as con:
        con.execute("BEGIN IMMEDIATE")  # Schreibsperre: Prüfen und Speichern passieren als ein Schritt
        b = con.execute("SELECT * FROM bestellungen WHERE nummer = ?", (bestellnummer,)).fetchone()
        if b is None:
            raise ToolError(f"Bestellung {bestellnummer} gibt es nicht.")
        # Geschäftsregeln: Der Server prüft sie, nicht das Modell.
        if b["status"] != "geliefert":
            raise ToolError(f"Bestellung {bestellnummer} ist noch nicht geliefert (Status: {b['status']}). "
                            "Rücksendung erst nach Lieferung.")
        frist = date.fromisoformat(b["geliefert_am"]) + timedelta(days=RUECKGABE_TAGE)
        if HEUTE > frist:
            raise ToolError(f"Die Rückgabefrist für {bestellnummer} ist am {frist.isoformat()} abgelaufen.")
        position = con.execute("SELECT p.*, pr.kategorie FROM positionen p JOIN produkte pr ON pr.sku = p.sku "
                               "WHERE p.bestellnummer = ? AND p.sku = ?", (bestellnummer, sku)).fetchone()
        if position is None:
            raise ToolError(f"Artikel {sku} ist nicht in Bestellung {bestellnummer}.")
        if position["kategorie"] == "Gutschein":
            raise ToolError("Gutscheine können nicht zurückgegeben werden.")
        schon = con.execute("SELECT COALESCE(SUM(menge), 0) FROM ruecksendungen WHERE bestellnummer = ? AND sku = ?",
                            (bestellnummer, sku)).fetchone()[0]
        if schon + menge > position["menge"]:
            raise ToolError(f"Bestellt: {position['menge']}, schon zurückgemeldet: {schon}. {menge} weitere geht nicht.")
        erstattung = position["preis_cent"] * menge
        cur = con.execute("INSERT INTO ruecksendungen (bestellnummer, sku, menge, erstattung_cent, grund, angelegt_am) "
                          "VALUES (?, ?, ?, ?, ?, ?)", (bestellnummer, sku, menge, erstattung, grund, HEUTE.isoformat()))
    return Ruecksendung(ruecksendung_id=f"R-{cur.lastrowid:03d}", bestellnummer=bestellnummer, sku=sku, menge=menge,
                        erstattung=euro(erstattung), grund=grund)


@mcp.tool(annotations=SCHREIBEN)
async def gutschrift_ausstellen(
    ruecksendung_id: Annotated[str, Field(description="ID aus ruecksendung_anlegen, z. B. R-001", pattern=r"^R-\d{3,}$")],
    ctx: Context = CurrentContext(),
) -> Gutschrift | InputRequiredResult:
    """Zahlt die Erstattung einer Rücksendung als Gutschrift aus. Der Betrag kommt aus der Rücksendung.
    Über 50 Euro fragt der Server vorher einen Menschen um Freigabe."""
    with verbindung() as con:
        r = con.execute("SELECT * FROM ruecksendungen WHERE id = ?", (int(ruecksendung_id[2:]),)).fetchone()
    if r is None:
        raise ToolError(f"Rücksendung {ruecksendung_id} gibt es nicht. Lege sie zuerst mit ruecksendung_anlegen an.")
    if r["erstattung_cent"] > FREIGABE_AB_CENT:
        antwort = await frage_mensch(
            ctx, f"Gutschrift über {euro(r['erstattung_cent']):.2f} Euro für {r['bestellnummer']} freigeben?")
        if isinstance(antwort, InputRequiredResult):
            return antwort  # neues Protokoll: erst fragen, dann ruft der Client noch einmal auf
        if antwort != "freigegeben":
            # Ehrlich sagen, was passiert ist: "cancel" heißt oft, dass niemand geantwortet hat.
            raise ToolError(f"Keine Freigabe erhalten (Antwort des Clients: {antwort}). Die Gutschrift wurde nicht "
                            "ausgezahlt. Nicht erneut versuchen, sondern den Menschen informieren.")
    try:
        with verbindung() as con:
            cur = con.execute("INSERT INTO gutschriften (ruecksendung_id, betrag_cent, datum) VALUES (?, ?, ?)",
                              (r["id"], r["erstattung_cent"], HEUTE.isoformat()))
    except sqlite3.IntegrityError:  # UNIQUE in der Tabelle: die Datenbank selbst verhindert doppeltes Auszahlen
        raise ToolError(f"Für {ruecksendung_id} gibt es schon eine Gutschrift.")
    return Gutschrift(gutschrift_id=f"G-{cur.lastrowid:03d}", ruecksendung_id=ruecksendung_id,
                      betrag=euro(r["erstattung_cent"]))


@mcp.tool(annotations=SCHREIBEN, tags={"admin"})
def lager_setzen(
    sku: Annotated[str, Field(description="Artikelnummer")],
    bestand: Annotated[int, Field(description="Neuer Lagerbestand", ge=0)],
) -> str:
    """Nur für Admins: setzt den Lagerbestand eines Produkts."""
    with verbindung() as con:
        if con.execute("UPDATE produkte SET lager = ? WHERE sku = ?", (bestand, sku)).rowcount == 0:
            raise ToolError(f"Produkt {sku} gibt es nicht.")
    return f"Lagerbestand von {sku} ist jetzt {bestand}."


# Admin-Werkzeuge sind unsichtbar und nicht aufrufbar, außer KIWI_ADMIN=1 ist gesetzt.
if os.environ.get("KIWI_ADMIN") != "1":
    mcp.disable(tags={"admin"})


# ---------- Ressourcen (Resources): Daten zum Lesen ----------

@mcp.resource("laden://richtlinien/rueckgabe", mime_type="text/markdown")
def rueckgabe_richtlinie() -> str:
    """Die Rückgaberegeln des Kiwi-Ladens."""
    return (
        "# Rückgabe im Kiwi-Laden\n"
        f"- Rückgabe innerhalb von {RUECKGABE_TAGE} Tagen nach Lieferung.\n"
        "- Nur gelieferte Bestellungen. Gutscheine sind ausgeschlossen.\n"
        "- Erstattet wird der Kaufpreis als Gutschrift.\n"
        f"- Gutschriften über {euro(FREIGABE_AB_CENT):.0f} Euro gibt ein Mensch frei.\n"
        f"- Pro Tag höchstens {euro(TAGESBUDGET_CENT):.0f} Euro Gutschriften insgesamt.\n"
    )


@mcp.resource("laden://produkte/{sku}", mime_type="application/json")
def produkt_datenblatt(sku: str) -> dict:
    """Datenblatt eines Produkts als JSON."""
    with verbindung() as con:
        p = con.execute("SELECT * FROM produkte WHERE sku = ?", (sku,)).fetchone()
    if p is None:
        raise ResourceError(f"Produkt {sku} gibt es nicht.")
    return {"sku": p["sku"], "name": p["name"], "kategorie": p["kategorie"], "preis": euro(p["preis_cent"]),
            "lager": p["lager"]}


# ---------- Vorlagen (Prompts): fertige Aufträge für den Menschen ----------

@mcp.prompt
def kundenanfrage_bearbeiten(bestellnummer: str, anliegen: str) -> str:
    """Bearbeitet eine Kundenanfrage zu einer Bestellung Schritt für Schritt."""
    return (
        f"Eine Kundin schreibt zu Bestellung {bestellnummer}: \"{anliegen}\"\n"
        "1. Rufe die Bestellung ab.\n"
        "2. Lies die Rückgaberegeln (laden://richtlinien/rueckgabe).\n"
        "3. Lege nur dann eine Rücksendung und Gutschrift an, wenn die Regeln es erlauben.\n"
        "4. Schreibe zum Schluss eine kurze, freundliche Antwort an die Kundin."
    )


if __name__ == "__main__":
    mcp.run()
