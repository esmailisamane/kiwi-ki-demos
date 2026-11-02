"""Macht die Agenten-Schleife von Claude Code sichtbar.

    claude -p "Deine Aufgabe" --output-format stream-json --verbose | python zeige_schleife.py

Liest die JSON-Ereignisse Zeile für Zeile und druckt: was Claude will (tool_use), was der Harness
zurückgibt (tool_result) und wie der Lauf endet (result). Den eigenen Ordnerpfad ersetzt es durch ".".
"""
import getpass
import io
import json
import sys

sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding="utf-8-sig")
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
ordner = None


def kurz(text, laenge=90):
    text = str(text)
    if ordner:
        for pfad in (ordner, ordner.replace("\\", "/"), ordner.replace("\\", "\\\\")):
            text = text.replace(pfad + "/", "").replace(pfad + "\\", "").replace(pfad, ".")
    text = text.replace(getpass.getuser(), "nutzer")   # eigenen Benutzernamen nicht zeigen
    text = " ".join(text.split())
    return text if len(text) <= laenge else text[:laenge - 1] + "…"


runde, letzte_id = 0, None
for zeile in sys.stdin:
    zeile = zeile.strip()
    if not zeile.startswith("{"):
        continue
    e = json.loads(zeile)
    art = e.get("type")
    if art == "system" and e.get("subtype") == "init":
        ordner = e.get("cwd")
        print(f"[Start]  Modell: {e.get('model')} | Werkzeuge: {len(e.get('tools', []))} | "
              f"Rechte-Modus: {e.get('permissionMode')}")
    elif art == "assistant":
        nachricht = e["message"]
        if nachricht.get("id") != letzte_id:
            runde, letzte_id = runde + 1, nachricht.get("id")
        for block in nachricht.get("content", []):
            if block.get("type") == "tool_use":
                argumente = ", ".join(f"{k}={kurz(v, 40)}" for k, v in block["input"].items())
                print(f"[Runde {runde}] Claude will:  {block['name']}({argumente})")
            elif block.get("type") == "text" and block["text"].strip():
                print(f"[Runde {runde}] Claude sagt:  {kurz(block['text'], 160)}")
    elif art == "user":
        for block in e["message"].get("content", []):
            if isinstance(block, dict) and block.get("type") == "tool_result":
                inhalt = block.get("content")
                if isinstance(inhalt, list):
                    inhalt = " ".join(t.get("text", "") for t in inhalt if isinstance(t, dict))
                fehler = " (FEHLER)" if block.get("is_error") else ""
                print(f"[Runde {runde}] Harness gibt zurück{fehler}: {kurz(inhalt)}")
    elif art == "result":
        print(f"[Ende]   {e.get('subtype')} | Runden: {e.get('num_turns')} | "
              f"Dauer: {e.get('duration_ms', 0) / 1000:.1f} s | stop_reason: {e.get('stop_reason')}")
        for verweigert in e.get("permission_denials") or []:
            print(f"[Ende]   verweigert: {verweigert.get('tool_name')}({kurz(verweigert.get('tool_input'), 60)})")
