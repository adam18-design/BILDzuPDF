#!/usr/bin/env python3
"""CLI-Tool: Mehrere Bilddateien zu einer PDF zusammenfassen."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Iterable, List

from PIL import Image, ImageOps, UnidentifiedImageError


SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"}


def _prepare_page(img: Image.Image, compress: bool, quality: int, max_dimension: int) -> Image.Image:
    """Bereitet eine Seite fuer PDF-Ausgabe vor, optional komprimiert fuer E-Mail-Versand."""
    page = ImageOps.exif_transpose(img).convert("RGB")

    if compress:
        width, height = page.size
        largest = max(width, height)
        if largest > max_dimension:
            scale = max_dimension / largest
            new_size = (max(1, int(width * scale)), max(1, int(height * scale)))
            page = page.resize(new_size, Image.Resampling.LANCZOS)

    return page


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


def convert_to_pdf(
    image_paths: list[Path],
    output: Path,
    compress: bool = False,
    quality: int = 65,
    max_dimension: int = 1600,
) -> None:
    """Konvertiert Bilder in eine mehrseitige PDF-Datei."""
    if compress and not (30 <= quality <= 95):
        raise ValueError("Qualitaet muss zwischen 30 und 95 liegen.")
    if compress and max_dimension < 600:
        raise ValueError("Maximale Kantenlaenge muss mindestens 600 Pixel sein.")

    pages: list[Image.Image] = []

    try:
        for image_path in image_paths:
            with Image.open(image_path) as img:
                normalized = _prepare_page(
                    img,
                    compress=compress,
                    quality=quality,
                    max_dimension=max_dimension,
                )
                pages.append(normalized.copy())

        if not pages:
            raise ValueError("Keine Bildseiten fuer PDF vorhanden.")

        output.parent.mkdir(parents=True, exist_ok=True)
        first, *rest = pages
        save_kwargs: dict[str, object] = {
            "save_all": True,
            "append_images": rest,
        }
        if compress:
            save_kwargs["optimize"] = True
            save_kwargs["quality"] = quality

        first.save(output, **save_kwargs)
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
    parser.add_argument(
        "--compress",
        action="store_true",
        help="PDF fuer E-Mail-Versand komprimieren.",
    )
    parser.add_argument(
        "--quality",
        type=int,
        default=65,
        help="Kompressionsqualitaet von 30-95 (Standard: 65).",
    )
    parser.add_argument(
        "--max-dimension",
        type=int,
        default=1600,
        help="Maximale Kantenlaenge pro Seite in Pixel bei Komprimierung (Standard: 1600).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        image_paths = collect_images(args.inputs, recursive=args.recursive)
        output = Path(args.output).expanduser().resolve()
        convert_to_pdf(
            image_paths,
            output,
            compress=args.compress,
            quality=args.quality,
            max_dimension=args.max_dimension,
        )
    except (FileNotFoundError, ValueError, UnidentifiedImageError) as exc:
        print(f"Fehler: {exc}", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"Dateifehler: {exc}", file=sys.stderr)
        return 1

    print(f"PDF erstellt: {output}")
    print(f"Seiten: {len(image_paths)}")
    if args.compress:
        size_mb = output.stat().st_size / (1024 * 1024)
        print(f"Komprimiert: ja (Qualitaet={args.quality}, MaxKante={args.max_dimension}px)")
        print(f"Dateigroesse: {size_mb:.2f} MB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
