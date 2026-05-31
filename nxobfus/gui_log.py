import tkinter as tk
from ttkbootstrap.widgets import ttk
from datetime import datetime


class CommandLog(ttk.LabelFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, text="Command Log", padding=6, **kwargs)
        self._text = tk.Text(self, height=6, wrap=tk.WORD, state=tk.DISABLED, font=("Consolas", 9))
        self._text.pack(fill=tk.BOTH, expand=True)

        scroll = ttk.Scrollbar(self._text, orient=tk.VERTICAL, command=self._text.yview)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self._text.configure(yscrollcommand=scroll.set)

    def log(self, message: str):
        stamp = datetime.now().strftime("%H:%M:%S")
        self._text.config(state=tk.NORMAL)
        self._text.insert(tk.END, f"[{stamp}] {message}\n")
        self._text.see(tk.END)
        self._text.config(state=tk.DISABLED)

    def clear(self):
        self._text.config(state=tk.NORMAL)
        self._text.delete("1.0", tk.END)
        self._text.config(state=tk.DISABLED)
