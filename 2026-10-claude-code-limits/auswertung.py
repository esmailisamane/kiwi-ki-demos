"""Wertet outputs/laeufe.jsonl aus: Durchschnitt je Gruppe, Anteil am 5-Stunden-Fenster, Resume-Kosten pro Aufruf.

    python auswertung.py            -> Tabelle auf dem Bildschirm und outputs/auswertung.txt
"""
import json
from pathlib import Path
from statistics import mean

HERE = Path(__file__).parent
ZEILEN = [json.loads(z) for z in (HERE / "outputs" / "laeufe.jsonl").read_text(encoding="utf-8").splitlines() if z.strip()]

AUFGABEN = ["opus_medium", "sonnet_medium", "haiku_medium", "opus_low", "opus_max", "opus_claudemd"]
# Bei --resume ist total_cost_usd kumuliert: Preis eines Aufrufs = Differenz zum vorherigen Aufruf derselben Sitzung.
RESUME_KETTEN = [("resume_gross", "gross_warm", "resume_warm"), ("resume_gross", "gross_kalt", "resume_kalt"),
                 ("resume_kalt", None, "resume_kalt_danach_warm")]


def zeile(gruppe, lauf=None):
    return [z for z in ZEILEN if z["gruppe"] == gruppe and (lauf is None or z.get("lauf") == lauf)]


def main() -> None:
    aus = []
    aus.append("Gleiche Aufgabe (2 Fehler finden und reparieren, Tests ausführen), je Lauf eine frische Kopie")
    aus.append(f"{'Gruppe':15} {'Läufe':>5} {'grün':>5} {'Listenpreis Ø':>14} {'Output Ø':>9} {'Denk Ø':>7} {'Zeit Ø':>7} {'5h-Fenster':>11}")
    # Anteil am Fenster je Block aufeinanderfolgender Läufe: Stand beim ersten Lauf bis zum Stand-Lauf direkt danach
    bloecke = {}
    i = 0
    while i < len(ZEILEN):
        g = ZEILEN[i]["gruppe"]
        if g in AUFGABEN:
            j = i
            while j + 1 < len(ZEILEN) and ZEILEN[j + 1]["gruppe"] == g:
                j += 1
            nach = next((z for z in ZEILEN[j + 1:] if z["gruppe"] == "stand"), None)
            if nach:
                d, n = bloecke.get(g, (0.0, 0))
                bloecke[g] = (d + nach["fuenf_h_vorher"] - ZEILEN[i]["fuenf_h_vorher"], n + j - i + 1)
            i = j
        i += 1
    for g in AUFGABEN:
        rs = zeile(g)
        if not rs:
            continue
        d, n = bloecke.get(g, (None, 0))
        prozent = f"+{round(d * 100)} % / {n}" if n else "?"
        aus.append(f"{g:15} {len(rs):>5} {sum(z['tests_gruen'] for z in rs):>5} {mean(z['kosten_usd'] for z in rs):>13.3f}$"
                   f" {mean(z['output'] for z in rs):>9.0f} {mean(z['denk_tokens'] for z in rs):>7.0f}"
                   f" {mean(z['sekunden'] for z in rs):>6.0f}s {prozent:>11}")

    aus.append("")
    aus.append("Resume: eine kurze Frage an eine große Sitzung (Preis nur dieses Aufrufs)")
    for g in ["resume_warm", "resume_kalt", "resume_kalt_danach_warm", "frage_frisch"]:
        r = zeile(g)
        if not r:
            continue
        r = r[0]
        if g == "frage_frisch":
            preis = r["kosten_usd"]
        else:
            vorher = {"resume_warm": zeile("resume_gross", "gross_warm"), "resume_kalt": zeile("resume_gross", "gross_kalt"),
                      "resume_kalt_danach_warm": zeile("resume_kalt")}[g][0]["kosten_usd"]
            preis = r["kosten_usd"] - vorher
        pause = f", Pause {r['pause_min']} min" if "pause_min" in r else ""
        aus.append(f"{g:25} {preis:7.3f}$  Cache schreiben {r['cache_schreiben']:>7}  Cache lesen {r['cache_lesen']:>7}"
                   f"  Output {r['output']:>5}{pause}")

    staende = [z for z in ZEILEN if z["gruppe"] == "stand"]
    aus.append("")
    aus.append("Stand des 5-Stunden-Fensters (ganzes Konto): " + ", ".join(f"{z['zeit']} {z['fuenf_h_vorher']:.0%}" for z in staende))
    aus.append("Woche: " + ", ".join(f"{z['zeit']} {z['woche_vorher']:.0%}" for z in staende))
    text = "\n".join(aus)
    print(text)
    (HERE / "outputs" / "auswertung.txt").write_text(text + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
