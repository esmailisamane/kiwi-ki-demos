# Messung zu Schritt 3: drei Harness-Varianten, dieselbe Aufgabe, je N Läufe mit temperature 0.7.
# A: Hinweis nur in der Werkzeug-Beschreibung, B: zusätzlich Dateiliste in der Fehlermeldung,
# C: Dateiliste von Anfang an im Kontext (System-Nachricht).  Start: python messung_schritt3.py 10
import io, json, sys, time
sys.path.insert(0, ".")
import schritt1_nur_modell as s1
import schritt3_schleife as s3

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
N = int(sys.argv[1]) if len(sys.argv) > 1 else 10
AUFGABE = "Wann ist mein Zahnarzttermin? Ich weiß nicht mehr, in welcher Datei er steht."

orig = s1.frage_modell
def frage_warm(nachrichten, werkzeuge=None):
    import urllib.request
    daten = {"model": s1.MODELL, "messages": nachrichten, "stream": False,
             "options": {"temperature": 0.7, "num_ctx": 8192}}
    if werkzeuge: daten["tools"] = werkzeuge
    r = urllib.request.Request(s1.URL, data=json.dumps(daten).encode(), headers={"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(r, timeout=600))["message"]

def lauf(system, fehler_mit_liste):
    def lies(datei):
        p = s3.ORDNER / datei
        if not p.is_file():
            return f"FEHLER: Datei {datei} gibt es nicht." + (" Vorhandene Dateien: " + s3.liste_dateien() if fehler_mit_liste else "")
        return p.read_text(encoding="utf-8")
    funcs = {"liste_dateien": s3.liste_dateien, "lies_datei": lies}
    msgs = [{"role": "system", "content": system}, {"role": "user", "content": AUFGABE}]
    spur = []
    for _ in range(8):
        a = frage_warm(msgs, s3.WERKZEUGE); msgs.append(a)
        calls = a.get("tool_calls")
        if not calls:
            return spur, a["content"]
        for c in calls:
            n = c["function"]["name"]; arg = c["function"]["arguments"] or {}
            spur.append(f"{n}({json.dumps(arg, ensure_ascii=False)})")
            f = funcs.get(n)
            try: e = f(**arg) if f else "FEHLER: unbekanntes Werkzeug"
            except TypeError as ex: e = f"FEHLER: {ex}"
            msgs.append({"role": "tool", "tool_name": n, "content": e})
    return spur, "(Grenze 8 erreicht)"

VARIANTEN = {
    "A_basis": (s3.REGELN, False),
    "B_fehler_mit_liste": (s3.REGELN, True),
    "C_liste_im_kontext": (s3.SYSTEM, True),
}
ergebnisse = []
for name, (system, fl) in VARIANTEN.items():
    ok = 0
    for i in range(N):
        t = time.time(); spur, antwort = lauf(system, fl)
        gelesen = any("termine.txt" in s and s.startswith("lies_datei") for s in spur)
        richtig = gelesen and "14:30" in antwort and "onnerstag" in antwort
        ok += richtig
        ergebnisse.append({"variante": name, "lauf": i + 1, "spur": spur, "antwort": antwort, "richtig": richtig,
                           "sekunden": round(time.time() - t, 1)})
        print(name, i + 1, "OK " if richtig else "NEIN", spur, "|", antwort.replace("\n", " ")[:110], flush=True)
    print(f"== {name}: {ok}/{N} richtig\n", flush=True)
with io.open("outputs/messung_schritt3.jsonl", "w", encoding="utf-8") as f:
    for e in ergebnisse:
        f.write(json.dumps(e, ensure_ascii=False) + "\n")
