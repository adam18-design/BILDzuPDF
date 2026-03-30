#!/usr/bin/env python3
"""CLI-Tool: Mehrere Bilddateien zu einer PDF zusammenfassen."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Iterable, List

from PIL import Image, ImageOps, UnidentifiedImageError


SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"}


def collect_images(inputs: Iterable[str], recursive: bool = False) -> List[Path]:
    """Sammelt Bilddateien aus Dateipfaden und Verzeichnissen."""
    images: list[Path] = []

    for item in inputs:
        path = Path(item).expanduser().resolve()

        if not path.exists():
            raise FileNotFoundError(f"Pfad nicht gefunden: {path}")

        if path.is_dir():
            pattern = "**/*" if recursive else "*"
            for candidate in sorted(path.glob(pattern)):
                if candidate.is_file() and candidate.suffix.lower() in SUPPORTED_EXTENSIONS:
                    images.append(candidate)
        elif path.is_file():
            if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
                raise ValueError(f"Nicht unterstuetztes Dateiformat: {path}")
            images.append(path)

    deduped = list(dict.fromkeys(images))
    if not deduped:
        raise ValueError("Keine gueltigen Bilddateien gefunden.")

    return deduped


def convert_to_pdf(image_paths: list[Path], output: Path) -> None:
    """Konvertiert Bilder in eine mehrseitige PDF-Datei."""
    pages: list[Image.Image] = []

    try:
        for image_path in image_paths:
            with Image.open(image_path) as img:
                # Korrigiert Orientierung aus EXIF und konvertiert fuer PDF-Ausgabe zu RGB.
                normalized = ImageOps.exif_transpose(img).convert("RGB")
                pages.append(normalized.copy())

        if not pages:
            raise ValueError("Keine Bildseiten fuer PDF vorhanden.")

        output.parent.mkdir(parents=True, exist_ok=True)
        first, *rest = pages
        first.save(output, save_all=True, append_images=rest)
    finally:
        for page in pages:
            page.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="bild2pdf",
        description="Fasst mehrere Bilddateien zu einer PDF zusammen.",
    )
    parser.add_argument(
        "inputs",
        nargs="+",
        help="Bilddateien und/oder Verzeichnisse mit Bildern.",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="ausgabe.pdf",
        help="Name der Zieldatei (Standard: ausgabe.pdf)",
    )
    parser.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help="Verzeichnisse rekursiv durchsuchen.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        image_paths = collect_images(args.inputs, recursive=args.recursive)
        output = Path(args.output).expanduser().resolve()
        convert_to_pdf(image_paths, output)
    except (FileNotFoundError, ValueError, UnidentifiedImageError) as exc:
        print(f"Fehler: {exc}", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"Dateifehler: {exc}", file=sys.stderr)
        return 1

    print(f"PDF erstellt: {output}")
    print(f"Seiten: {len(image_paths)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
