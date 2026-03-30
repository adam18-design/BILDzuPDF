#!/usr/bin/env python3
"""Desktop-GUI fuer das Zusammenfassen von Bildern zu einer PDF."""

from __future__ import annotations

from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import traceback

from PIL import UnidentifiedImageError

from bild2pdf import SUPPORTED_EXTENSIONS, convert_to_pdf


class BildZuPdfApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("BILDzuPDF")
        self.root.geometry("760x520")
        self.root.minsize(680, 420)

        self.image_paths: list[Path] = []

        self._build_ui()

    def _build_ui(self) -> None:
        container = ttk.Frame(self.root, padding=12)
        container.pack(fill="both", expand=True)

        title = ttk.Label(
            container,
            text="Bilder zu PDF zusammenfassen",
            font=("Segoe UI", 15, "bold"),
        )
        title.pack(anchor="w", pady=(0, 8))

        controls = ttk.Frame(container)
        controls.pack(fill="x", pady=(0, 8))

        ttk.Button(controls, text="Bilder hinzufuegen", command=self.add_images).pack(
            side="left", padx=(0, 6)
        )
        ttk.Button(controls, text="Ordner hinzufuegen", command=self.add_folder).pack(
            side="left", padx=(0, 6)
        )
        ttk.Button(controls, text="Auswahl entfernen", command=self.remove_selected).pack(
            side="left", padx=(0, 6)
        )
        ttk.Button(controls, text="Liste leeren", command=self.clear_list).pack(side="left")

        list_frame = ttk.Frame(container)
        list_frame.pack(fill="both", expand=True)

        self.listbox = tk.Listbox(list_frame, selectmode=tk.EXTENDED)
        self.listbox.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.listbox.yview)
        scrollbar.pack(side="left", fill="y")
        self.listbox.configure(yscrollcommand=scrollbar.set)

        order_controls = ttk.Frame(list_frame)
        order_controls.pack(side="left", fill="y", padx=(8, 0))

        ttk.Button(order_controls, text="Nach oben", command=self.move_up).pack(
            fill="x", pady=(0, 4)
        )
        ttk.Button(order_controls, text="Nach unten", command=self.move_down).pack(fill="x")

        output_frame = ttk.LabelFrame(container, text="Ausgabe", padding=10)
        output_frame.pack(fill="x", pady=(10, 8))

        self.output_var = tk.StringVar(value=str(self._default_output_path()))

        ttk.Entry(output_frame, textvariable=self.output_var).pack(
            side="left", fill="x", expand=True, padx=(0, 6)
        )
        ttk.Button(output_frame, text="Speicherort...", command=self.choose_output).pack(side="left")

        compression_frame = ttk.LabelFrame(container, text="Komprimierung", padding=10)
        compression_frame.pack(fill="x", pady=(0, 8))

        self.compress_var = tk.BooleanVar(value=True)
        self.quality_var = tk.IntVar(value=65)
        self.max_dimension_var = tk.IntVar(value=1600)

        ttk.Checkbutton(
            compression_frame,
            text="Fuer E-Mail komprimieren",
            variable=self.compress_var,
        ).grid(row=0, column=0, sticky="w", padx=(0, 12))

        ttk.Label(compression_frame, text="Qualitaet:").grid(row=0, column=1, sticky="e")
        ttk.Scale(
            compression_frame,
            from_=30,
            to=95,
            variable=self.quality_var,
            orient="horizontal",
            length=180,
        ).grid(row=0, column=2, padx=(6, 6), sticky="w")
        ttk.Label(compression_frame, textvariable=self.quality_var, width=3).grid(
            row=0, column=3, sticky="w"
        )

        ttk.Label(compression_frame, text="Max. Kante:").grid(row=0, column=4, sticky="e", padx=(12, 0))
        max_dimension_combo = ttk.Combobox(
            compression_frame,
            width=8,
            state="readonly",
            values=("1200", "1600", "2000", "2400"),
        )
        max_dimension_combo.grid(row=0, column=5, padx=(6, 0), sticky="w")
        max_dimension_combo.set(str(self.max_dimension_var.get()))

        def on_dimension_change(_: object) -> None:
            self.max_dimension_var.set(int(max_dimension_combo.get()))

        max_dimension_combo.bind("<<ComboboxSelected>>", on_dimension_change)

        footer = ttk.Frame(container)
        footer.pack(fill="x")

        self.count_var = tk.StringVar(value="0 Bilder")
        ttk.Label(footer, textvariable=self.count_var).pack(side="left")
        ttk.Button(footer, text="PDF erstellen", command=self.create_pdf).pack(side="right")

    def add_images(self) -> None:
        filetypes = [
            (
                "Bilddateien",
                " ".join(f"*{ext}" for ext in sorted(SUPPORTED_EXTENSIONS)),
            ),
            ("Alle Dateien", "*.*"),
        ]
        paths = filedialog.askopenfilenames(title="Bilder auswaehlen", filetypes=filetypes)
        self._append_paths(Path(p) for p in paths)

    def add_folder(self) -> None:
        folder = filedialog.askdirectory(title="Ordner mit Bildern auswaehlen")
        if not folder:
            return

        folder_path = Path(folder)
        candidates = sorted(
            p for p in folder_path.iterdir() if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS
        )
        self._append_paths(candidates)

    def _append_paths(self, paths) -> None:
        existing = set(self.image_paths)
        added = 0

        for path in paths:
            resolved = Path(path).expanduser().resolve()
            if resolved in existing:
                continue
            if resolved.suffix.lower() not in SUPPORTED_EXTENSIONS:
                continue
            self.image_paths.append(resolved)
            self.listbox.insert(tk.END, str(resolved))
            existing.add(resolved)
            added += 1

        self._update_count()
        if added == 0:
            messagebox.showinfo("Hinweis", "Keine neuen gueltigen Bilddateien hinzugefuegt.")

    def remove_selected(self) -> None:
        selected = list(self.listbox.curselection())
        if not selected:
            return

        for idx in reversed(selected):
            del self.image_paths[idx]
            self.listbox.delete(idx)

        self._update_count()

    def clear_list(self) -> None:
        self.image_paths.clear()
        self.listbox.delete(0, tk.END)
        self._update_count()

    def move_up(self) -> None:
        selected = list(self.listbox.curselection())
        if not selected or selected[0] == 0:
            return

        for idx in selected:
            self.image_paths[idx - 1], self.image_paths[idx] = self.image_paths[idx], self.image_paths[idx - 1]

        self._refresh_listbox()
        for idx in [i - 1 for i in selected]:
            self.listbox.selection_set(idx)

    def move_down(self) -> None:
        selected = list(self.listbox.curselection())
        if not selected or selected[-1] == len(self.image_paths) - 1:
            return

        for idx in reversed(selected):
            self.image_paths[idx + 1], self.image_paths[idx] = self.image_paths[idx], self.image_paths[idx + 1]

        self._refresh_listbox()
        for idx in [i + 1 for i in selected]:
            self.listbox.selection_set(idx)

    def _refresh_listbox(self) -> None:
        self.listbox.delete(0, tk.END)
        for path in self.image_paths:
            self.listbox.insert(tk.END, str(path))

    def choose_output(self) -> None:
        filename = filedialog.asksaveasfilename(
            title="PDF speichern unter",
            defaultextension=".pdf",
            filetypes=[("PDF", "*.pdf")],
            initialfile="ausgabe.pdf",
        )
        if filename:
            self.output_var.set(filename)

    def create_pdf(self) -> None:
        if not self.image_paths:
            messagebox.showerror("Fehler", "Bitte zuerst mindestens ein Bild hinzufuegen.")
            return

        output_text = self.output_var.get().strip()
        if not output_text:
            messagebox.showerror("Fehler", "Bitte einen Speicherort fuer die PDF angeben.")
            return

        output_path = Path(output_text).expanduser()
        if not output_path.is_absolute():
            output_path = (self._default_base_dir() / output_path).resolve()
        if output_path.suffix.lower() != ".pdf":
            output_path = output_path.with_suffix(".pdf")

        try:
            convert_to_pdf(
                self.image_paths,
                output_path,
                compress=self.compress_var.get(),
                quality=int(self.quality_var.get()),
                max_dimension=int(self.max_dimension_var.get()),
            )
        except (OSError, ValueError, UnidentifiedImageError) as exc:
            messagebox.showerror("Fehler", str(exc))
            return

        file_size_mb = output_path.stat().st_size / (1024 * 1024)
        compression_text = "ja" if self.compress_var.get() else "nein"

        messagebox.showinfo(
            "Erfolg",
            f"PDF erfolgreich erstellt:\n{output_path}\n\nSeiten: {len(self.image_paths)}\nKomprimiert: {compression_text}\nDateigroesse: {file_size_mb:.2f} MB",
        )

    def _update_count(self) -> None:
        count = len(self.image_paths)
        label = "Bild" if count == 1 else "Bilder"
        self.count_var.set(f"{count} {label}")

    def _default_base_dir(self) -> Path:
        documents = Path.home() / "Documents"
        if documents.exists() and documents.is_dir():
            return documents
        return Path.home()

    def _default_output_path(self) -> Path:
        return self._default_base_dir() / "ausgabe.pdf"


def show_fatal_error(exc: BaseException) -> None:
    # Bei --windowed/ohne Konsole unter Windows Fehler sichtbar machen.
    details = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
    message = f"Die Anwendung konnte nicht gestartet werden.\n\n{exc}\n\nDetails:\n{details}"
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror("BILDzuPDF - Startfehler", message)
    root.destroy()


def main() -> None:
    try:
        root = tk.Tk()
        app = BildZuPdfApp(root)
        root.mainloop()
    except Exception as exc:  # pragma: no cover
        show_fatal_error(exc)


if __name__ == "__main__":
    main()
