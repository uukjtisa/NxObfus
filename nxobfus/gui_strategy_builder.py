import tkinter as tk
from ttkbootstrap.widgets import ttk
from ttkbootstrap.constants import *


STRATEGIES = ["token", "index"]
POOLS = ["basic", "extended"]


class RoundRow(ttk.Frame):
    def __init__(self, parent, on_remove, **kwargs):
        super().__init__(parent, **kwargs)
        self.on_remove = on_remove

        self.strat_var = tk.StringVar(value=STRATEGIES[0])
        self.pool_var = tk.StringVar(value=POOLS[0])

        self.strat_cb = ttk.Combobox(self, textvariable=self.strat_var, values=STRATEGIES, state="readonly", width=10)
        self.strat_cb.pack(side=tk.LEFT, padx=(0, 4))

        ttk.Label(self, text="×").pack(side=tk.LEFT, padx=2)

        self.pool_cb = ttk.Combobox(self, textvariable=self.pool_var, values=POOLS, state="readonly", width=12)
        self.pool_cb.pack(side=tk.LEFT, padx=(4, 4))

        btn = ttk.Button(self, text="✕", command=self._remove, width=3, style="danger.TButton")
        btn.pack(side=tk.LEFT, padx=(4, 0))

    def _remove(self):
        self.on_remove(self)

    def get_value(self):
        return self.strat_var.get(), self.pool_var.get()

    def set_value(self, strat, pool):
        self.strat_var.set(strat)
        self.pool_var.set(pool)


class StrategyBuilder(ttk.LabelFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, text="Strategy Chain", padding=6, **kwargs)
        self.rows: list[RoundRow] = []

        self._inner = ttk.Frame(self)
        self._inner.pack(fill=tk.X, expand=True)

        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=tk.X, pady=(4, 0))

        ttk.Button(btn_frame, text="+ Add Round", command=self._add_row, style="success.TButton").pack(side=tk.LEFT)

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
