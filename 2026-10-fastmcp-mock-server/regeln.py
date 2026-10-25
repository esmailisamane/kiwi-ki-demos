"""Middleware für den Kiwi-Laden: Regeln, die für ALLE Werkzeug-Aufrufe gelten.

Middleware sitzt zwischen Client und Werkzeug. Jeder Aufruf läuft durch sie hindurch:
    Client -> ProtokollMiddleware -> RegelMiddleware -> Werkzeug
Sie kann mitschreiben, prüfen und einen Aufruf blockieren, bevor das Werkzeug überhaupt startet.
"""
import json
import os
import time
from pathlib import Path

from fastmcp.exceptions import ToolError
from fastmcp.server.middleware import Middleware, MiddlewareContext

from datenbank import HEUTE, euro, verbindung

TAGESBUDGET_CENT = 15000  # 150 Euro: mehr Gutschriften pro Tag gehen nie, auch nicht mit Freigabe
PROTOKOLL = Path(os.environ.get("KIWI_PROTOKOLL", Path(__file__).resolve().parent / "protokoll.jsonl"))


class ProtokollMiddleware(Middleware):
    """Schreibt jeden Werkzeug-Aufruf als eine JSON-Zeile mit: Name, Argumente, Ergebnis, Dauer."""

    async def on_call_tool(self, context: MiddlewareContext, call_next):
        start = time.perf_counter()
        eintrag = {"zeit": time.strftime("%H:%M:%S"), "werkzeug": context.message.name,
                   "argumente": context.message.arguments}
        try:
            ergebnis = await call_next(context)
            eintrag["ok"] = True
            return ergebnis
        except Exception as fehler:
            eintrag["ok"] = False
            eintrag["fehler"] = str(fehler)
            raise
        finally:
            eintrag["ms"] = round((time.perf_counter() - start) * 1000, 1)
            with PROTOKOLL.open("a", encoding="utf-8") as f:
                f.write(json.dumps(eintrag, ensure_ascii=False) + "\n")


class RegelMiddleware(Middleware):
    """Harte Regel: Alle Gutschriften zusammen dürfen das Tagesbudget nicht überschreiten, egal was das Modell will."""

    async def on_call_tool(self, context: MiddlewareContext, call_next):
        if context.message.name == "gutschrift_ausstellen":
            rid = str((context.message.arguments or {}).get("ruecksendung_id", ""))
            with verbindung() as con:
                r = con.execute("SELECT erstattung_cent FROM ruecksendungen WHERE id = ?",
                                (int(rid[2:]) if rid[2:].isdigit() else -1,)).fetchone()
                heute = con.execute("SELECT COALESCE(SUM(betrag_cent), 0) FROM gutschriften WHERE datum = ?",
                                    (HEUTE.isoformat(),)).fetchone()[0]
            if r and heute + r["erstattung_cent"] > TAGESBUDGET_CENT:
                raise ToolError(
                    f"Blockiert: Mit {euro(r['erstattung_cent']):.2f} Euro wären es heute "
                    f"{euro(heute + r['erstattung_cent']):.2f} Euro Gutschriften. Das Tagesbudget ist "
                    f"{euro(TAGESBUDGET_CENT):.2f} Euro. Bitte nicht erneut versuchen."
                )
        return await call_next(context)
