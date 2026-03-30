# BILDzuPDF

Ein kleines CLI-Tool, das mehrere Bilddateien zu einer einzigen PDF zusammenfasst.

Zusatz: Eine Desktop-GUI fuer Windows ist enthalten.

## Voraussetzungen

- Python 3.10+

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Nutzung

```bash
python3 bild2pdf.py bilder/foto1.jpg bilder/foto2.png -o dokument.pdf
```

Mehrere Bilder aus einem Verzeichnis zusammenfassen:

```bash
python3 bild2pdf.py bilder/ -o dokument.pdf
```

Verzeichnis rekursiv durchsuchen:

```bash
python3 bild2pdf.py bilder/ -r -o dokument.pdf
```

PDF fuer E-Mail-Versand komprimieren:

```bash
python3 bild2pdf.py bilder/ -o dokument.pdf --compress --quality 65 --max-dimension 1600
```

Empfehlung fuer kleine Anhaenge: `--quality 60` bis `70` und `--max-dimension 1200` bis `1600`.

## GUI fuer Windows

1. Python unter Windows installieren (inklusive Tkinter, bei Standardinstallation vorhanden).
2. Im Projektordner Abhaengigkeiten installieren:

```powershell
pip install -r requirements.txt
```

3. GUI starten:

```powershell
python bild2pdf_gui.py
```

In der GUI kannst du:
- Bilder oder ganze Ordner hinzufuegen
- die Reihenfolge der Seiten per "Nach oben" / "Nach unten" aendern
- Zielpfad der PDF waehlen
- E-Mail-Komprimierung aktivieren und Qualitaet/Aufloesung einstellen
- per Klick auf "PDF erstellen" exportieren

### Fertiges Windows-Programm lokal bauen

```powershell
pip install pyinstaller
pyinstaller --onefile --windowed --name BILDzuPDF bild2pdf_gui.py
```

Die fertige EXE liegt danach in `dist/BILDzuPDF.exe`.

Alternativ mit den vorbereiteten Skripten:

```powershell
./build_windows_exe.ps1
```

oder in der CMD:

```bat
build_windows_exe.bat
```

Die Skripte erzeugen:
- `dist/BILDzuPDF.exe` (direkt startbar)
- `dist/BILDzuPDF-Portable.zip` (portable Paket)
- `dist/BILDzuPDF-Setup.exe` (Installer, falls Inno Setup installiert ist)

### Fertiges Windows-Programm automatisch in GitHub bauen

Im Repository ist ein Workflow vorhanden: `.github/workflows/build-windows-exe.yml`.

So verwendest du ihn:
1. Code nach GitHub pushen.
2. In GitHub: **Actions** -> **Build Windows Program** -> **Run workflow**.
3. Nach Abschluss diese Artefakte herunterladen:
- `BILDzuPDF-windows-setup` (Installer + SHA256)
- `BILDzuPDF-windows-portable` (Portable ZIP + SHA256)
- `BILDzuPDF-windows-exe` (Roh-EXE)

## Windows-Fehlersuche

- Falls beim Start nichts sichtbar passiert, zuerst ohne `--windowed` bauen:

```powershell
pyinstaller --onefile --name BILDzuPDF bild2pdf_gui.py
```

Dann `dist/BILDzuPDF.exe` aus der Konsole starten, damit Fehlermeldungen sichtbar sind.

- Achte darauf, dass Pillow installiert ist:

```powershell
pip install -r requirements.txt
```

- Standard-Ausgabe ist in deinem Benutzerordner (`Documents/ausgabe.pdf`).

## Unterstuetzte Dateiformate

- .jpg / .jpeg
- .png
- .bmp
- .tif / .tiff
- .webp
