import tkinter as tk
from datetime import datetime


class CommandLog(tk.LabelFrame):
    def __init__(self, parent, **kwargs):
        from .gui_theme import palette
        self.COL = palette()
        COL = self.COL
        
        super().__init__(
            parent,
            text=" Command Log ",
            bg=COL["bg"],
            fg=COL["accent"],
            font=("Segoe UI Variable", 9, "bold"),
            padx=8,
            pady=6,
            **kwargs,
        )
        self.configure(highlightbackground=COL["border"], highlightthickness=1, bd=0)
        
        self._text = tk.Text(
            self,
            height=5,
            wrap=tk.WORD,
            state=tk.DISABLED,
            font=("Consolas", 9),
            bg=COL["surface"],
            fg=COL["text"],
            insertbackground=COL["accent"],
            selectbackground=COL["accent_secondary"],
            selectforeground="#ffffff",
            relief="flat",
            padx=6,
            pady=4,
        )
        self._text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scroll = tk.Scrollbar(
            self,
            orient=tk.VERTICAL,
            command=self._text.yview,
            bg=COL["surface_light"],
            troughcolor=COL["bg"],
            highlightbackground=COL["bg"],
            activebackground=COL["accent"],
            bd=0,
            width=10,
        )
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self._text.configure(yscrollcommand=scroll.set)

    def log(self, message: str):
        stamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        self._text.config(state=tk.NORMAL)
        self._text.insert(tk.END, f"[{stamp}] {message}\n")
        self._text.see(tk.END)
        self._text.config(state=tk.DISABLED)

    def clear(self):
        self._text.config(state=tk.NORMAL)
        self._text.delete("1.0", tk.END)
        self._text.config(state=tk.DISABLED)
