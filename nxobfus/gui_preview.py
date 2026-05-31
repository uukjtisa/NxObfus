import tkinter as tk
from ttkbootstrap.widgets import ttk
from ttkbootstrap.constants import *
from . import charset


class CharsetPreview(ttk.LabelFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, text="Character Set Preview", padding=6, **kwargs)
        self._text = tk.Text(self, height=4, wrap=tk.WORD, state=tk.DISABLED, font=("Consolas", 9))
        self._text.pack(fill=tk.BOTH, expand=True)

    def show_pool(self, pool_name: str):
        pool = charset.BASIC if pool_name == "basic" else charset.EXTENDED
        label = f"Pool: {pool_name} ({len(pool)} chars)\n"
        lines = []
        chunk = ""
        for ch in pool:
            if ch.isprintable() or ch in ("\t", "\n", " "):
                display = repr(ch).strip("'")
            else:
                display = f"\\x{ord(ch):02x}"
            if len(chunk) + len(display) + 1 > 80:
                lines.append(chunk)
                chunk = ""
            chunk += display + " "
        if chunk:
            lines.append(chunk)
        content = label + "\n".join(lines)

        self._text.config(state=tk.NORMAL)
        self._text.delete("1.0", tk.END)
        self._text.insert("1.0", content)
        self._text.config(state=tk.DISABLED)
