"""Kleiner Testshop: liest den Shop-Namen aus der Umgebung."""
import os

print("Willkommen im", os.environ.get("SHOP_NAME", "Kiwi Testshop"))
