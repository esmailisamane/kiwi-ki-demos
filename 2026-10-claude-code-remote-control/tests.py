"""Kleine Test-Suite fuer den Remote-Control-Versuch: 8 Tests, dauert etwa 20 Sekunden."""
import time

TESTS = ["warenkorb_leer", "preis_mit_mwst", "rabatt_10_prozent", "versandkosten",
         "gutschein_abgelaufen", "lager_bestand", "rechnung_pdf", "bestellung_speichern"]

start = time.time()
for i, name in enumerate(TESTS, 1):
    time.sleep(2.5)
    print(f"[{i}/{len(TESTS)}] test_{name} ... ok", flush=True)
print(f"8 passed in {time.time() - start:.1f}s")
