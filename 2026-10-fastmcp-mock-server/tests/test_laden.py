"""Tests für den Kiwi-Laden: Der Client spricht direkt im Speicher mit dem Server (kein Netz, kein Prozess).
Jeder Test bekommt eine eigene, frische SQLite-Datenbank."""
import sys
from pathlib import Path

import pytest
from fastmcp import Client
from fastmcp.exceptions import ToolError
from mcp.types import ElicitResult

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import datenbank  # noqa: E402
from laden_server import mcp  # noqa: E402


@pytest.fixture(autouse=True)
def frische_datenbank(tmp_path, monkeypatch):
    import regeln
    monkeypatch.setenv("KIWI_DB", str(tmp_path / "test.db"))
    monkeypatch.setattr(regeln, "PROTOKOLL", tmp_path / "protokoll.jsonl")
    datenbank.neu_anlegen()


def gutschriften() -> list[float]:
    with datenbank.verbindung() as con:
        return [datenbank.euro(z[0]) for z in con.execute("SELECT betrag_cent FROM gutschriften ORDER BY id")]


@pytest.fixture
async def client():
    async with Client(mcp) as c:
        yield c


async def test_werkzeuge_sichtbar(client):
    namen = {t.name for t in await client.list_tools()}
    assert namen == {"produkt_suchen", "bestellung_abrufen", "ruecksendung_anlegen", "gutschrift_ausstellen"}
    # lager_setzen ist ohne KIWI_ADMIN=1 versteckt


async def test_produkt_suchen(client):
    r = await client.call_tool("produkt_suchen", {"suchbegriff": "wasserkocher"})
    assert [p["sku"] for p in r.structured_content["result"]] == ["K-100", "K-101"]
    r = await client.call_tool("produkt_suchen", {"suchbegriff": "wasserkocher", "max_preis": 40})
    assert [p["sku"] for p in r.structured_content["result"]] == ["K-100"]


@pytest.mark.parametrize("boese", ["' OR 1=1 --", "%%", "__", "x'; DROP TABLE produkte; --"])
async def test_sql_injection_und_joker(client, boese):
    r = await client.call_tool("produkt_suchen", {"suchbegriff": boese})
    assert r.structured_content["result"] == []
    r = await client.call_tool("produkt_suchen", {"suchbegriff": "maus"})
    assert len(r.structured_content["result"]) == 1  # Tabelle ist noch da


async def test_eingabe_wird_geprueft(client):
    with pytest.raises(ToolError):
        await client.call_tool("bestellung_abrufen", {"bestellnummer": "1042"})  # Format falsch


async def test_ganzer_ablauf(client):
    b = await client.call_tool("bestellung_abrufen", {"bestellnummer": "B-1042"})
    assert b.data.rueckgabe_moeglich_bis == "2026-11-09"
    r = await client.call_tool("ruecksendung_anlegen", {"bestellnummer": "B-1042", "sku": "K-100", "grund": "defekt"})
    assert r.data.erstattung == 39.90
    g = await client.call_tool("gutschrift_ausstellen", {"ruecksendung_id": r.data.ruecksendung_id})
    assert g.data.betrag == 39.90
    assert gutschriften() == [39.90]  # steht wirklich in der Datenbank
    b = await client.call_tool("bestellung_abrufen", {"bestellnummer": "B-1042"})
    assert {p.sku: p.schon_zurueckgemeldet for p in b.data.positionen} == {"B-301": 0, "K-100": 1}
    assert b.data.ruecksendungen[0].gutschrift_ausgezahlt is True  # das Modell sieht den Stand


@pytest.mark.parametrize("args, meldung", [
    ({"bestellnummer": "B-1043", "sku": "B-302", "grund": "defekt"}, "noch nicht geliefert"),
    ({"bestellnummer": "B-0977", "sku": "B-300", "grund": "defekt"}, "abgelaufen"),
    ({"bestellnummer": "B-1042", "sku": "K-200", "grund": "defekt"}, "nicht in Bestellung"),
    ({"bestellnummer": "B-1042", "sku": "B-301", "grund": "defekt", "menge": 3}, "geht nicht"),
    ({"bestellnummer": "B-1061", "sku": "G-400", "grund": "gefaellt_nicht"}, "Gutscheine"),
])
async def test_geschaeftsregeln(client, args, meldung):
    with pytest.raises(ToolError, match=meldung):
        await client.call_tool("ruecksendung_anlegen", args)


def mensch(antwort: bool | None, fragen: list):
    """Spielt den Menschen am Client: True = freigeben, False = Nein, None = Fenster weggeklickt."""
    async def handler(message, response_type, params, context):
        fragen.append(message)
        if antwort is None:
            return ElicitResult(action="cancel")
        feld = next(iter(params.requested_schema["properties"]))  # "freigeben" (neu) oder "value" (alt)
        return ElicitResult(action="accept", content={feld: antwort})
    return handler


async def toaster_ruecksendung(c):
    r = await c.call_tool("ruecksendung_anlegen",
                          {"bestellnummer": "B-1050", "sku": "K-200", "grund": "gefaellt_nicht", "menge": 4})
    assert r.data.erstattung == 119.60
    return r.data.ruecksendung_id


@pytest.mark.parametrize("modus", ["auto", "legacy"])  # auto = neues Protokoll 2026-07-28, legacy = alter Weg
async def test_freigabe_ja(modus):
    fragen = []
    async with Client(mcp, mode=modus, elicitation_handler=mensch(True, fragen)) as c:
        g = await c.call_tool("gutschrift_ausstellen", {"ruecksendung_id": await toaster_ruecksendung(c)})
    assert g.data.betrag == 119.60
    assert fragen == ["Gutschrift über 119.60 Euro für B-1050 freigeben?"]


@pytest.mark.parametrize("antwort, meldung", [(False, "Antwort des Clients: nein"), (None, "Antwort des Clients: cancel")])
@pytest.mark.parametrize("modus", ["auto", "legacy"])
async def test_freigabe_nein(modus, antwort, meldung):
    async with Client(mcp, mode=modus, elicitation_handler=mensch(antwort, [])) as c:
        rid = await toaster_ruecksendung(c)
        with pytest.raises(ToolError, match=meldung):
            await c.call_tool("gutschrift_ausstellen", {"ruecksendung_id": rid})
    assert gutschriften() == []


async def test_kleine_gutschrift_ohne_frage():
    fragen = []
    async with Client(mcp, elicitation_handler=mensch(True, fragen)) as c:
        r = await c.call_tool("ruecksendung_anlegen", {"bestellnummer": "B-1042", "sku": "K-100", "grund": "defekt"})
        await c.call_tool("gutschrift_ausstellen", {"ruecksendung_id": r.data.ruecksendung_id})
    assert fragen == []


async def test_tagesbudget():
    async with Client(mcp, elicitation_handler=mensch(True, [])) as c:
        r1 = await c.call_tool("ruecksendung_anlegen", {"bestellnummer": "B-1042", "sku": "K-100", "grund": "defekt"})
        await c.call_tool("gutschrift_ausstellen", {"ruecksendung_id": r1.data.ruecksendung_id})  # 39,90
        rid = await toaster_ruecksendung(c)                                                       # +119,60
        with pytest.raises(ToolError, match="Tagesbudget"):
            await c.call_tool("gutschrift_ausstellen", {"ruecksendung_id": rid})
    assert gutschriften() == [39.90]


async def test_keine_doppelte_gutschrift(client):
    r = await client.call_tool("ruecksendung_anlegen", {"bestellnummer": "B-1042", "sku": "K-100", "grund": "defekt"})
    await client.call_tool("gutschrift_ausstellen", {"ruecksendung_id": r.data.ruecksendung_id})
    with pytest.raises(ToolError, match="schon eine Gutschrift"):  # kommt aus der UNIQUE-Regel der Datenbank
        await client.call_tool("gutschrift_ausstellen", {"ruecksendung_id": r.data.ruecksendung_id})
    assert gutschriften() == [39.90]


async def test_daten_bleiben_nach_neustart():
    async with Client(mcp) as c:
        await c.call_tool("ruecksendung_anlegen", {"bestellnummer": "B-1042", "sku": "K-100", "grund": "defekt"})
    async with Client(mcp) as c:  # neue Verbindung: die Rücksendung ist noch da
        with pytest.raises(ToolError, match="schon zurückgemeldet: 1"):
            await c.call_tool("ruecksendung_anlegen", {"bestellnummer": "B-1042", "sku": "K-100", "grund": "defekt"})


async def test_ressource_und_prompt(client):
    text = (await client.read_resource("laden://richtlinien/rueckgabe"))[0].text
    assert "30 Tagen" in text and "über 50 Euro" in text and "150 Euro" in text
    blatt = (await client.read_resource("laden://produkte/K-100"))[0].text
    assert "Wasserkocher" in blatt
    p = await client.get_prompt("kundenanfrage_bearbeiten", {"bestellnummer": "B-1042", "anliegen": "kaputt"})
    assert "B-1042" in p.messages[0].content.text
