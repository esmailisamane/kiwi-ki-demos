# Brief-Vorlage für `/design`

Ein Brief ist die Aufgabe für den Designer. Je genauer er ist, desto weniger musst du später korrigieren.

## Die fünf Teile

1. **Was?** Welche Seite oder welcher Bildschirm? (z. B. Startseite, Einstellungen, Onboarding mit 4 Screens)
2. **Für wen?** Wer benutzt die Seite? (z. B. Hobbyköche, Admins, neue Nutzer)
3. **Was muss drauf?** Die wichtigsten Elemente in der Reihenfolge, in der man sie sieht.
4. **Welche Regeln?** Deine Dateien: Komponenten, Farben, Schrift – mit Dateinamen.
5. **Wie viele Varianten?** Zwei oder drei sind gut zum Vergleichen.

## Schablone

```
/design <Seite> für <Zielgruppe>: <Element 1>, <Element 2>, <Element 3>.
Nutze <Komponente> aus <Datei> und die Farben aus <Datei>. <Anzahl> Varianten.
```

## Beispiel aus dem Video

Schwach:

```
/design Mach die Startseite schöner.
```

Gut:

```
/design Startseite für Hobbyköche: oben eine Suche, darunter Rezept-Karten mit Foto und Kochzeit.
Nutze die Komponente RecipeCard und die Farben aus src/styles/colors.ts. Drei Varianten.
```

## Danach

- Andere Ideen: `Zeig mir zwei bis drei andere Layouts für diese Seite.`
- Umsetzen: `Setz Variante 2 um, mit dem größeren Knopf.`
- Vor dem Übernehmen: den Diff in VS Code ansehen (rot = fällt weg, grün = neu).
