import tkinter as tk


STRATEGIES = ["token", "index"]
POOLS = ["basic", "extended"]


class RoundRow(tk.Frame):
    def __init__(self, parent, on_remove, **kwargs):
        from .gui_theme import palette
        self.COL = palette()
        COL = self.COL
        
        super().__init__(parent, bg=COL["bg"], **kwargs)
        self.on_remove = on_remove

        self.strat_var = tk.StringVar(value=STRATEGIES[0])
        self.pool_var = tk.StringVar(value=POOLS[0])
        
        # Strategy combobox (using ttk via parent would need style pass, using tk.Entry-like for now with ttk)
        # Actually keep ttk but override colors via style is tricky; let's use tk.OptionMenu styled
        # Or better: use ttk.Combobox but wrapped in dark styling
        self._build_combos()

    def _build_combos(self):
        COL = self.COL
        
        # Custom styled tk spinbox-like selector using frame + label + dropdown
        # Simpler: use tk.OptionMenu with dark colors
        self.strat_var.trace_add("write", lambda *a: None)
        
        self.strat_om = tk.OptionMenu(
            self,
            self.strat_var,
            *STRATEGIES,
        )
        self.strat_om.configure(
            bg=COL["surface"],
            fg=COL["text"],
            activebackground=COL["surface_hover"],
            activeforeground=COL["text"],
            highlightthickness=0,
            bd=0,
            relief="flat",
            font=("Segoe UI Variable", 9),
            width=8,
        )
        self.strat_om["menu"].configure(
            bg=COL["surface"],
            fg=COL["text"],
            activebackground=COL["accent"],
            activeforeground="#ffffff",
            bd=0,
        )
        self.strat_om.pack(side=tk.LEFT, padx=(0, 4))
        
        mul = tk.Label(self, text="×", bg=COL["bg"], fg=COL["text_dim"], font=("Segoe UI Variable", 10))
        mul.pack(side=tk.LEFT, padx=2)
        
        self.pool_om = tk.OptionMenu(self, self.pool_var, *POOLS)
        self.pool_om.configure(
            bg=COL["surface"],
            fg=COL["text"],
            activebackground=COL["surface_hover"],
            activeforeground=COL["text"],
            highlightthickness=0,
            bd=0,
            relief="flat",
            font=("Segoe UI Variable", 9),
            width=10,
        )
        self.pool_om["menu"].configure(
            bg=COL["surface"],
            fg=COL["text"],
            activebackground=COL["accent"],
            activeforeground="#ffffff",
            bd=0,
        )
        self.pool_om.pack(side=tk.LEFT, padx=(4, 4))
        
        # Remove button — fancy X
        btn = tk.Label(
            self,
            text="✕",
            font=("Segoe UI Variable", 10, "bold"),
            bg=COL["error"],
            fg="#ffffff",
            padx=6,
            pady=1,
            cursor="hand2",
        )
        btn.pack(side=tk.LEFT, padx=(6, 0))
        btn.bind("<Enter>", lambda e: btn.configure(bg="#e11d48"))
        btn.bind("<Leave>", lambda e: btn.configure(bg=COL["error"]))
        btn.bind("<Button-1>", lambda e: self._remove())

    def _remove(self):
        self.on_remove(self)

    def get_value(self):
        return self.strat_var.get(), self.pool_var.get()

    def set_value(self, strat, pool):
        self.strat_var.set(strat)
        self.pool_var.set(pool)
        # Update option menus if needed
        self.strat_om["textvariable"] = self.strat_var
        self.pool_om["textvariable"] = self.pool_var


class StrategyBuilder(tk.LabelFrame):
    def __init__(self, parent, **kwargs):
        from .gui_theme import palette
        self.COL = palette()
        COL = self.COL
        
        super().__init__(
            parent,
            text=" Strategy Chain ",
            bg=COL["bg"],
            fg=COL["accent"],
            font=("Segoe UI Variable", 9, "bold"),
            padx=10,
            pady=8,
            **kwargs,
        )
        self.configure(highlightbackground=COL["border"], highlightthickness=1, bd=0)
        self.rows: list[RoundRow] = []

        self._inner = tk.Frame(self, bg=COL["bg"])
        self._inner.pack(fill=tk.X, expand=True)

        btn_frame = tk.Frame(self, bg=COL["bg"])
        btn_frame.pack(fill=tk.X, pady=(6, 0))

        add_btn = tk.Label(
            btn_frame,
            text="+ Add Round",
            font=("Segoe UI Variable", 9, "bold"),
            bg=COL["success"],
            fg="#ffffff",
            padx=14,
            pady=4,
            cursor="hand2",
        )
        add_btn.pack(side=tk.LEFT)
        add_btn.bind("<Enter>", lambda e: add_btn.configure(bg="#059669"))
        add_btn.bind("<Leave>", lambda e: add_btn.configure(bg=COL["success"]))
        add_btn.bind("<Button-1>", lambda e: self._add_row())

        self._add_row()

    def _add_row(self):
        row = RoundRow(self._inner, on_remove=self._remove_row)
        row.pack(fill=tk.X, pady=2)
        self.rows.append(row)

    def _remove_row(self, row):
        if len(self.rows) <= 1:
            return
        row.pack_forget()
        row.destroy()
        self.rows.remove(row)

    def get_rounds(self):
        return [r.get_value() for r in self.rows]

    def set_rounds(self, rounds: list[tuple[str, str]]):
        for r in self.rows[:]:
            r.pack_forget()
            r.destroy()
        self.rows.clear()
        for strat, pool in rounds:
            self._add_row()
            self.rows[-1].set_value(strat, pool)

    def clear(self):
        for r in self.rows[:]:
            self._remove_row(r)
        self._add_row()
