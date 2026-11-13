"""Erzeugt erfundene Beispiel-Rechnungen im Ordner rechnungen/ (alle Firmen sind ausgedacht).

Start: pip install reportlab pillow   dann   python beispiele_erzeugen.py
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

ORDNER = Path("rechnungen")

RECHNUNGEN = [
    # Dateiname,      Lieferant,                  Datum,        Posten,                         netto,  MwSt-Satz
    ("scan_0012.pdf", "Stadtwerke Kiwistadt",     "03.11.2026", "Strom Oktober 2026",           70.76, 19),
    ("scan_0013.pdf", "Bürobedarf Sonnenblume",   "05.11.2026", "Druckerpapier, 5 Pakete",      23.45, 19),
    ("IMG_2041.pdf",  "Serverhaus Nordlicht",     "01.11.2026", "Webhosting November",          8.32,  19),
    ("dokument.pdf",  "Druckerei Blattwerk",      "28.10.2026", "Visitenkarten, 250 Stück",     41.18, 19),
    ("rechnung(3).pdf", "Café Morgenrot",         "06.11.2026", "Kuchen zum Mitnehmen, 6 Stück", 17.29, 7),
]


def euro(betrag):
    return f"{betrag:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + " €"


def pdf_rechnung(datei, lieferant, datum, posten, netto, satz, nummer):
    mwst = round(netto * satz / 100, 2)
    brutto = round(netto + mwst, 2)
    c = canvas.Canvas(str(ORDNER / datei), pagesize=A4)
    b, h = A4
    c.setFont("Helvetica-Bold", 18)
    c.drawString(60, h - 80, lieferant)
    c.setFont("Helvetica", 10)
    c.drawString(60, h - 98, "Musterstraße 1 · 12345 Kiwistadt  (Beispiel-Firma, erfunden)")
    c.setFont("Helvetica-Bold", 14)
    c.drawString(60, h - 160, "RECHNUNG")
    c.setFont("Helvetica", 11)
    c.drawString(60, h - 185, f"Rechnungsnummer: RE-2026-{nummer:04d}")
    c.drawString(60, h - 202, f"Rechnungsdatum: {datum}")
    c.line(60, h - 230, b - 60, h - 230)
    c.drawString(60, h - 250, posten)
    c.drawRightString(b - 60, h - 250, euro(netto))
    c.line(60, h - 265, b - 60, h - 265)
    c.drawString(300, h - 285, "Netto")
    c.drawRightString(b - 60, h - 285, euro(netto))
    c.drawString(300, h - 302, f"MwSt {satz} %")
    c.drawRightString(b - 60, h - 302, euro(mwst))
    c.setFont("Helvetica-Bold", 12)
    c.drawString(300, h - 324, "Gesamtbetrag")
    c.drawRightString(b - 60, h - 324, euro(brutto))
    c.save()


def foto_beleg():
    """Ein schiefes, verwischtes Kassenbon-Foto: der Betrag ist nicht lesbar."""
    bild = Image.new("RGB", (600, 800), (238, 234, 225))
    zeichne = ImageDraw.Draw(bild)
    schrift = ImageFont.load_default(size=30)
    zeilen = ["Tankstelle am Ring", "(Beispiel, erfunden)", "", "Datum: 04.11.2026", "", "Super E10   38,21 l"]
    for i, zeile in enumerate(zeilen):
        zeichne.text((60, 80 + i * 45), zeile, fill=(40, 40, 40), font=schrift)
    zeichne.text((60, 430), "SUMME EUR", fill=(40, 40, 40), font=schrift)
    # Betrag verwischt: Kaffeefleck drüber
    zeichne.ellipse((280, 400, 560, 500), fill=(160, 120, 80))
    bild = bild.rotate(7, expand=True, fillcolor=(90, 90, 90)).filter(ImageFilter.GaussianBlur(1.2))
    bild.save(ORDNER / "WhatsApp Image 2026-11-04.jpg", quality=80)


if __name__ == "__main__":
    ORDNER.mkdir(exist_ok=True)
    for nummer, (datei, lieferant, datum, posten, netto, satz) in enumerate(RECHNUNGEN, start=1):
        pdf_rechnung(datei, lieferant, datum, posten, netto, satz, nummer)
    foto_beleg()
    print("Beispiel-Rechnungen erzeugt in", ORDNER)
