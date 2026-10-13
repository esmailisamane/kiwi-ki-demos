"""Fasst alle Läufe in outputs/ je Variante zusammen (Mittelwerte) und schreibt outputs/ergebnis.md.

Start (im Ordner des Videos): python auswertung/zusammenfassung.py
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from auswerten import LOESUNG, ORDNER, ZEILE, passender_fehler  # noqa: E402

NAMEN = {
    "allein-sonnet": "Sonnet 5.5 allein",
    "allein-haiku": "Haiku 5.5 allein",
    "sub-haiku": "Sonnet-Chef + Haiku-Subagents",
    "sub-sonnet": "Sonnet-Chef + Sonnet-Subagents",
    "team-haiku": "Haiku-Chef + Haiku-Subagents",
}

gruppen = defaultdict(list)
for datei in sorted((ORDNER / "outputs").glob("*-*-*.json")):
    groesse, _, rest = datei.stem.partition("-")
    variante = rest.rsplit("-", 1)[0]
    if variante not in NAMEN:
        continue
    daten = json.loads(datei.read_text(encoding="utf-8"))
    erlaubt = set(range(1, 13)) if groesse == "klein" else {f["nr"] for f in LOESUNG}
    gefunden = set()
    for name, zeile, text in ZEILE.findall(str(daten.get("result", ""))):
        nr = passender_fehler(name, int(zeile), text, erlaubt)
        if nr:
            gefunden.add(nr)
    haupt = "claude-haiku-5-5" if variante in ("allein-haiku", "team-haiku") else "claude-sonnet-5-5"
    kosten = daten.get("total_cost_usd", 0)
    helfer = sum(u["costUSD"] for m, u in daten.get("modelUsage", {}).items() if m != haupt)
    gruppen[(groesse, variante)].append(
        (daten["wanduhr_sekunden"], kosten, len(gefunden), len(erlaubt), helfer if variante == "sub-haiku" else None)
    )

zeilen = ["| Runde | Variante | Läufe | Zeit (Mittel) | Verbrauch* (Mittel) | gefundene Fehler je Lauf |", "|---|---|---|---|---|---|"]
for groesse in ("klein", "gross"):
    for variante, name in NAMEN.items():
        laeufe = gruppen.get((groesse, variante), [])
        if not laeufe:
            continue
        zeit = sum(lauf[0] for lauf in laeufe) / len(laeufe)
        kosten = sum(lauf[1] for lauf in laeufe) / len(laeufe)
        funde = ", ".join(f"{lauf[2]}/{lauf[3]}" for lauf in laeufe)
        runde = "6 Dateien, 12 Fehler" if groesse == "klein" else "18 Dateien, 36 Fehler"
        zeilen.append(f"| {runde} | {name} | {len(laeufe)} | {zeit:.1f} s | {kosten * 100:.2f} Cent | {funde} |")
        if variante == "sub-haiku":
            anteil = sum(lauf[4] for lauf in laeufe) / sum(lauf[1] for lauf in laeufe)
            zeilen.append(
                f"| | davon die Haiku-Subagents zusammen | | | {anteil * kosten * 100:.2f} Cent "
                f"({anteil * 100:.0f} % des Laufs) | |"
            )
zeilen.append("")
zeilen.append("\\* rechnerischer API-Listenpreis in US-Cent, so wie Claude Code ihn je Lauf ausgibt (total_cost_usd). "
              "Im Abo wird das nicht einzeln berechnet; die Zahl zeigt, wie viel ein Lauf verbraucht.")
text = "\n".join(zeilen)
print(text)
(ORDNER / "outputs" / "ergebnis.md").write_text(text + "\n", encoding="utf-8")
