# Hermes Agent Deutsch: Installieren & einrichten – lokal mit Ollama

Begleitmaterial zum Video **„Hermes Agent Deutsch: Installieren & einrichten – lokal mit Ollama“** vom Kanal
KIwi – KI einfach erklärt.

> **Hinweis:** Alle Befehle und Einstellungen stammen aus der offiziellen Doku von Nous Research
> (github.com/NousResearch/hermes-agent, Doku-Stand 19.11.2026, Version v0.23.2) und Ollama (docs.ollama.com).
> Die Bildschirme im Video sind danach nachgebaut. Kein offizielles Video von Nous Research oder Ollama.

## Inhalt

- `CHECKLISTE.md` – alle Schritte aus dem Video in der richtigen Reihenfolge
- `beispiel-konfig/config.yaml` – vorsichtige Start-Konfiguration (lokales Modell, Freigaben `manual`, Sperrliste,
  Checkpoints, Memory-Freigabe, optional Cloud-Reserve)
- `beispiel-konfig/env.beispiel` – Platzhalter für Telegram (echte Werte nie ins Git!)

## Kurz erklärt

Hermes Agent ist ein kostenloser Open-Source-KI-Agent (MIT). Er führt Befehle aus, liest und schreibt Dateien, merkt sich
Vorlieben (Memory) und schreibt gute Abläufe als Skills auf. Mit Ollama läuft das Modell auf deinem eigenen Rechner.

**Wichtigste Einstellung:** Hermes braucht mindestens **64.000 Tokens Kontext**. Ollama gibt bei weniger als 24 GiB
Grafikspeicher standardmäßig nur 4k – also in der Ollama-App unter Settings „Context length“ auf 64k stellen oder
`OLLAMA_CONTEXT_LENGTH=64000 ollama serve`.

**Modell:** Es muss Tool Calling können (Etikett `tools` in der Ollama-Bibliothek). Stark: `gemma4:31b` (≈ 20 GB) oder
`qwen3.8:27b` (≈ 18 GB). Für normale Laptops: `gemma4:e4b`. Namen mit `-cloud` laufen NICHT lokal.

## Quellen

- Hermes Agent: https://github.com/NousResearch/hermes-agent
- Hermes Doku: https://hermes-agent.nousresearch.com/docs/
- Hermes + Ollama (Ollama-Doku): https://docs.ollama.com/integrations/hermes
- Kontextlänge (Ollama-Doku): https://docs.ollama.com/context-length
- Modelle: https://ollama.com/library/gemma4 · https://ollama.com/library/qwen3.8
