import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path


FILETYPES_TEXT = [("Text files", "*.txt"), ("Python files", "*.py"), ("All files", "*.*")]
FILETYPES_KEY = [("NxObfus Key", "*.nxob"), ("JSON files", "*.json"), ("All files", "*.*")]


def load_file_dialog(title="Open File") -> str | None:
    path = filedialog.askopenfilename(title=title, filetypes=FILETYPES_TEXT)
    if path:
        try:
            return Path(path).read_text(encoding="utf-8")
        except Exception as e:
            messagebox.showerror("Error", f"Could not read file:\n{e}")
    return None


def save_file_dialog(title="Save File", default_ext=".txt") -> str | None:
    path = filedialog.asksaveasfilename(title=title, defaultextension=default_ext, filetypes=FILETYPES_TEXT)
    return path


def save_key_dialog(title="Save Key") -> str | None:
    path = filedialog.asksaveasfilename(title=title, defaultextension=".nxob", filetypes=FILETYPES_KEY)
    return path


def load_key_dialog(title="Open Key") -> str | None:
    path = filedialog.askopenfilename(title=title, filetypes=FILETYPES_KEY)
    return path


def copy_to_clipboard(widget: tk.Widget, text: str):
    widget.clipboard_clear()
    widget.clipboard_append(text)
    widget.update()
