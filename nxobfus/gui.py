import tkinter as tk
from tkinter import messagebox
from pathlib import Path
from ttkbootstrap.widgets import ttk
from ttkbootstrap import Window
from ttkbootstrap.constants import *
import time
import ctypes
import sys

from . import core
from . import keys
from .gui_theme import get_style, refresh_style, palette, is_dark
from .gui_strategy_builder import StrategyBuilder
from .gui_preview import CharsetPreview
from .gui_log import CommandLog
from .gui_helpers import (
    load_file_dialog, save_file_dialog,
    save_key_dialog, load_key_dialog,
    copy_to_clipboard,
)

# ═══════════════════════════════════════════════════════════
#  WINDOWS DARK TITLE BAR HACK
# ═══════════════════════════════════════════════════════════
def _set_dark_titlebar(hwnd):
    """Force Windows 10/11 dark mode titlebar via DWM."""
    if sys.platform != "win32":
        return
    try:
        DWMWA_USE_IMMERSIVE_DARK_MODE = 20
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            hwnd,
            DWMWA_USE_IMMERSIVE_DARK_MODE,
            ctypes.byref(ctypes.c_int(1)),
            ctypes.sizeof(ctypes.c_int(1))
        )
    except Exception:
        pass

def _set_window_corner(hwnd, corner_type=1):
    """Rounded window corners on Windows 11. 1 = round, 2 = round-small."""
    if sys.platform != "win32":
        return
    try:
        DWMWA_WINDOW_CORNER_PREFERENCE = 33
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            hwnd,
            DWMWA_WINDOW_CORNER_PREFERENCE,
            ctypes.byref(ctypes.c_int(corner_type)),
            ctypes.sizeof(ctypes.c_int(corner_type))
        )
    except Exception:
        pass


class NxObfusGUI(Window):
    def __init__(self):
        super().__init__(themename="darkly")
        
        # ── Core window config ──────────────────────────────
        self.title("NxObfus v2.1.0  —  Obfuscation Engine")
        self.geometry("960x820")
        self.minsize(800, 650)
        
        COL = palette()
        self.palette = COL
        
        # Kill the default ttkbootstrap background with our deeper black
        self.configure(background=COL["bg"])
        
        # Force dark native titlebar + rounded corners
        self.update_idletasks()
        hwnd = ctypes.windll.user32.GetParent(self.winfo_id())
        _set_dark_titlebar(hwnd)
        _set_window_corner(hwnd, corner_type=1)
        
        # Override ttkbootstrap's default bg
        self.style.configure(".", background=COL["bg"], foreground=COL["text"])
        self.style.configure("TFrame", background=COL["bg"])
        self.style.configure("TMenu", background=COL["bg"], foreground=COL["text"])
        
        # ── Build UI ────────────────────────────────────────
        self._build_custom_title()
        self._build_menu()
        self._build_notebook()
        self._build_obfuscate_tab()
        self._build_deobfuscate_tab()
        self._build_key_tab()
        self._build_log()
        
        self._current_obf_seed = None
        self._current_deobf_seed = None
        
        # Final style polish after widgets exist
        self.after(50, lambda: _set_dark_titlebar(hwnd))
    
    # ── Custom Title / Header Bar ─────────────────────────
    def _build_custom_title(self):
        """A subtle header with logo-like branding."""
        COL = self.palette
        
        hdr = tk.Frame(self, bg=COL["bg"], height=48)
        hdr.pack(fill=tk.X, padx=0, pady=0)
        hdr.pack_propagate(False)
        
        # Accent line on top (the glow)
        glow = tk.Frame(hdr, bg=COL["accent"], height=2)
        glow.pack(fill=tk.X, side=tk.TOP)
        
        # Left: title with monospaced accent
        left = tk.Frame(hdr, bg=COL["bg"])
        left.pack(side=tk.LEFT, padx=16, pady=8)
        
        tk.Label(
            left,
            text="NX",
            font=("Consolas", 14, "bold"),
            bg=COL["bg"],
            fg=COL["accent"],
        ).pack(side=tk.LEFT)
        tk.Label(
            left,
            text="OBFUS",
            font=("Consolas", 14, "bold"),
            bg=COL["bg"],
            fg=COL["text"],
        ).pack(side=tk.LEFT)
        tk.Label(
            left,
            text="  //  v2.1.0",
            font=("Consolas", 9),
            bg=COL["bg"],
            fg=COL["text_dim"],
        ).pack(side=tk.LEFT, padx=(8, 0))
        
        # Right: status pill
        self._status_pill = tk.Label(
            hdr,
            text="● Ready",
            font=("Segoe UI Variable", 8),
            bg=COL["surface"],
            fg=COL["success"],
            padx=10,
            pady=2,
        )
        self._status_pill.pack(side=tk.RIGHT, padx=16, pady=10)
    
    def _set_status(self, text, color_key="success"):
        COL = self.palette
        self._status_pill.configure(text=text, fg=COL.get(color_key, COL["text"]))
    
    # ── Menu Bar ──────────────────────────────────────────
    def _build_menu(self):
        COL = self.palette
        
        bar = tk.Menu(self, bg=COL["bg"], fg=COL["text"], 
                      activebackground=COL["surface_hover"], activeforeground=COL["accent"],
                      borderwidth=0, font=("Segoe UI Variable", 9))
        self.config(menu=bar)
        
        file_menu = tk.Menu(bar, tearoff=0, bg=COL["bg"], fg=COL["text"],
                            activebackground=COL["surface_hover"], activeforeground=COL["accent"],
                            borderwidth=0, font=("Segoe UI Variable", 9))
        file_menu.add_command(label="Load Input Text…", command=self._menu_load_input)
        file_menu.add_command(label="Save Output As…", command=self._menu_save_output)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.destroy)
        bar.add_cascade(label="File", menu=file_menu)
        
        view_menu = tk.Menu(bar, tearoff=0, bg=COL["bg"], fg=COL["text"],
                            activebackground=COL["surface_hover"], activeforeground=COL["accent"],
                            borderwidth=0, font=("Segoe UI Variable", 9))
        view_menu.add_command(label="Refresh Style", command=self._refresh_style)
        bar.add_cascade(label="View", menu=view_menu)
    
    def _refresh_style(self):
        refresh_style(self)
        self.configure(background=self.palette["bg"])
        self._set_status("● Style refreshed", "info")
        self.log.log("Theme style refreshed")
    
    def _menu_load_input(self):
        tab = self._notebook.index(self._notebook.select())
        text = load_file_dialog()
        if text:
            if tab == 0:
                self.obf_input[1].delete("1.0", tk.END)
                self.obf_input[1].insert("1.0", text)
                self.log.log(f"Loaded {len(text)} chars into Obfuscate input")
            elif tab == 1:
                self.deobf_input[1].delete("1.0", tk.END)
                self.deobf_input[1].insert("1.0", text)
                self.log.log(f"Loaded {len(text)} chars into Deobfuscate input")
    
    def _menu_save_output(self):
        tab = self._notebook.index(self._notebook.select())
        path = save_file_dialog()
        if path:
            if tab == 0:
                content = self.obf_output.get("1.0", tk.END).strip()
            elif tab == 1:
                content = self.deobf_output.get("1.0", tk.END).strip()
            else:
                return
            Path(path).write_text(content, encoding="utf-8")
            self.log.log(f"Saved output to {path}")
    
    # ── Notebook ──────────────────────────────────────────
    def _build_notebook(self):
        COL = self.palette
        
        outer = tk.Frame(self, bg=COL["bg"])
        outer.pack(fill=tk.BOTH, expand=True, padx=12, pady=(4, 4))
        
        self._notebook = ttk.Notebook(outer, style="TNotebook")
        self._notebook.pack(fill=tk.BOTH, expand=True)
        
        # Notebook inner padding via ttkbootstrap already styled in theme
    
    # ════════════════════════════════════════════════════════
    #  SHARED HELPERS
    # ════════════════════════════════════════════════════════
    def _make_text_area(self, parent, height=6, readonly=False):
        COL = self.palette
        state = tk.DISABLED if readonly else tk.NORMAL
        
        wrapper = tk.Frame(parent, bg=COL["surface"], bd=1, highlightbackground=COL["border"], highlightthickness=1)
        
        txt = tk.Text(
            wrapper,
            height=height,
            wrap=tk.WORD,
            state=state,
            font=("Consolas", 10),
            bg=COL["surface"],
            fg=COL["text"],
            insertbackground=COL["accent"],
            selectbackground=COL["accent_secondary"],
            selectforeground="#ffffff",
            relief="flat",
            padx=8,
            pady=6,
            borderwidth=0,
        )
        txt.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scroll = ttk.Scrollbar(wrapper, orient=tk.VERTICAL, command=txt.yview, style="NX.TScrollbar")
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        txt.configure(yscrollcommand=scroll.set)
        
        return wrapper, txt
    
    def _make_button_row(self, parent, buttons):
        COL = self.palette
        f = tk.Frame(parent, bg=COL["bg"])
        f.pack(fill=tk.X, pady=(6, 0))
        
        for i, (text, cmd, style_name) in enumerate(buttons):
            is_primary = style_name == "primary" or text.startswith("▸") or text.startswith("◂")
            is_danger = style_name == "danger" or "Remov" in text or text.startswith("✕")
            
            if is_primary:
                bg = COL["accent"]
                fg = "#ffffff"
                hover = COL["accent_glow"]
                font = ("Segoe UI Variable", 9, "bold")
            elif is_danger:
                bg = COL["error"]
                fg = "#ffffff"
                hover = "#e11d48"
                font = ("Segoe UI Variable", 9, "bold")
            else:
                bg = COL["surface_light"]
                fg = COL["text"]
                hover = COL["surface_hover"]
                font = ("Segoe UI Variable", 9)
            
            btn = tk.Label(
                f,
                text=text,
                font=font,
                bg=bg,
                fg=fg,
                padx=16,
                pady=5,
                cursor="hand2",
            )
            btn.pack(side=tk.LEFT, padx=(0, 8 if i < len(buttons)-1 else 0))
            
            # Rounded corners visual via border-radius not available in tk, 
            # but we can pad nicely and bind hover.
            btn.bind("<Enter>", lambda e, b=btn, h=hover: b.configure(bg=h))
            btn.bind("<Leave>", lambda e, b=btn, o=bg: b.configure(bg=o))
            btn.bind("<Button-1>", lambda e, c=cmd: c())
            
        return f
    
    def _random_seed(self):
        import random
        return random.randint(1, 999999)
    
    def _build_log(self):
        self.log = CommandLog(self)
        self.log.pack(fill=tk.X, padx=12, pady=(0, 10))
        self.log.log("NxObfus initialized — dark mode active")
    
    # ════════════════════════════════════════════════════════
    #  FILE CHOICE DIALOG
    # ════════════════════════════════════════════════════════
    def _file_choice_dialog(self, title, file_content, file_path, mode="obfuscate"):
        COL = self.palette
        
        dialog = tk.Toplevel(self)
        dialog.title(title)
        dialog.geometry("560x300")
        dialog.transient(self)
        dialog.grab_set()
        dialog.resizable(False, False)
        dialog.configure(bg=COL["bg"])
        
        # Dark titlebar for dialog
        dialog.update_idletasks()
        hwnd = ctypes.windll.user32.GetParent(dialog.winfo_id())
        _set_dark_titlebar(hwnd)
        _set_window_corner(hwnd, 1)
        
        # Accent glow top
        tk.Frame(dialog, bg=COL["accent"], height=2).pack(fill=tk.X)
        
        main = tk.Frame(dialog, bg=COL["bg"], padx=20, pady=16)
        main.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(
            main,
            text="How do you want to handle this file?",
            font=("Segoe UI Variable", 12, "bold"),
            bg=COL["bg"],
            fg=COL["text"],
        ).pack(anchor=tk.W, pady=(0, 16))
        
        btn_frame = tk.Frame(main, bg=COL["bg"])
        btn_frame.pack(fill=tk.X)
        
        # Process Directly — accent
        proc_btn = tk.Label(
            btn_frame,
            text="  🔁  Process Directly",
            font=("Segoe UI Variable", 10, "bold"),
            bg=COL["accent"],
            fg="#ffffff",
            padx=20,
            pady=10,
            cursor="hand2",
        )
        proc_btn.pack(side=tk.LEFT, padx=(0, 12))
        proc_btn.bind("<Enter>", lambda e: proc_btn.configure(bg=COL["accent_glow"]))
        proc_btn.bind("<Leave>", lambda e: proc_btn.configure(bg=COL["accent"]))
        proc_btn.bind("<Button-1>", lambda e: self._process_directly(dialog, file_content, file_path, mode))
        
        # Append to Input — surface
        app_btn = tk.Label(
            btn_frame,
            text="  📝  Append to Input",
            font=("Segoe UI Variable", 10),
            bg=COL["surface_light"],
            fg=COL["text"],
            padx=20,
            pady=10,
            cursor="hand2",
        )
        app_btn.pack(side=tk.LEFT)
        app_btn.bind("<Enter>", lambda e: app_btn.configure(bg=COL["surface_hover"]))
        app_btn.bind("<Leave>", lambda e: app_btn.configure(bg=COL["surface_light"]))
        app_btn.bind("<Button-1>", lambda e: self._append_to_input(dialog, file_content, mode))
        
        # Info text
        tk.Label(
            main,
            text=(
                "Process Directly applies obfuscation / deobfuscation\n"
                "immediately with the current chain & seed, then prompts to\n"
                "replace the original or save as a new file."
            ),
            justify=tk.LEFT,
            bg=COL["bg"],
            fg=COL["text_dim"],
            font=("Segoe UI Variable", 9),
            wraplength=500,
        ).pack(anchor=tk.W, pady=(16, 0))
        
        # Cancel
        cancel = tk.Label(
            main,
            text="Cancel",
            font=("Segoe UI Variable", 9),
            bg=COL["surface"],
            fg=COL["text_dim"],
            padx=14,
            pady=4,
            cursor="hand2",
        )
        cancel.pack(anchor=tk.E, pady=(16, 0))
        cancel.bind("<Enter>", lambda e: cancel.configure(bg=COL["error"], fg="#ffffff"))
        cancel.bind("<Leave>", lambda e: cancel.configure(bg=COL["surface"], fg=COL["text_dim"]))
        cancel.bind("<Button-1>", lambda e: dialog.destroy())
    
    def _process_directly(self, dialog, file_content, file_path, mode):
        dialog.destroy()
        self._set_status("● Working…", "warn")
        self.update()
        
        is_obf = mode == "obfuscate"
        builder = self.obf_builder if is_obf else self.deobf_builder
        seed_var = self.obf_seed_var if is_obf else self.deobf_seed_var
        current_seed_attr = "_current_obf_seed" if is_obf else "_current_deobf_seed"
        randomize_fn = self._obf_randomize_seed if is_obf else self._deobf_randomize_seed
        output_widget_parent, output_widget = self.obf_output if is_obf else self.deobf_output
        preview_fn = self._obf_update_preview if is_obf else None
        core_fn = core.obfuscate if is_obf else core.deobfuscate
        action = "Obfuscated" if is_obf else "Deobfuscated"
        
        rounds = builder.get_rounds()
        if not rounds:
            messagebox.showwarning("No rounds", "Add at least one round first.")
            self._set_status("● Idle")
            return
        
        current_seed = getattr(self, current_seed_attr)
        seed_raw = seed_var.get().strip()
        seed = int(seed_raw) if seed_raw else current_seed
        if seed is None:
            randomize_fn()
            seed = int(seed_var.get())
        
        try:
            start = time.perf_counter()
            result = core_fn(file_content, rounds, seed=seed)
            elapsed = time.perf_counter() - start
            
            output_widget.config(state=tk.NORMAL)
            output_widget.delete("1.0", tk.END)
            output_widget.insert("1.0", result)
            output_widget.config(state=tk.DISABLED)
            
            if preview_fn:
                preview_fn()
            
            replace = messagebox.askyesno(
                "Save Result",
                "Replace the original file?\n\n(No = save as a new file)"
            )
            if replace:
                Path(file_path).write_text(result, encoding="utf-8")
                self.log.log(f"{action} and replaced file: {len(file_content)}→{len(result)} chars")
            else:
                save_path = save_file_dialog("Save Result As")
                if save_path:
                    Path(save_path).write_text(result, encoding="utf-8")
                    self.log.log(f"{action} and saved to {save_path}")
            
            seq = " → ".join(f"{s}/{p}" for s, p in rounds)
            self.log.log(f"{action} file: {len(file_content)}→{len(result)} chars [{seq}, seed={seed}] in {elapsed*1000:.1f}ms")
            self._set_status("● Done", "success")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.log.log(f"ERROR: {e}")
            self._set_status("● Error", "error")
    
    def _append_to_input(self, dialog, file_content, mode):
        dialog.destroy()
        target = (self.obf_input if mode == "obfuscate" else self.deobf_input)[1]
        target.insert(tk.END, file_content)
        label = "Obfuscate" if mode == "obfuscate" else "Deobfuscate"
        self.log.log(f"Appended {len(file_content)} chars to {label} input")
    
    # ════════════════════════════════════════════════════════
    #  OBFUSCATE TAB
    # ════════════════════════════════════════════════════════
    def _build_obfuscate_tab(self):
        COL = self.palette
        tab = tk.Frame(self._notebook, bg=COL["bg"], padx=12, pady=10)
        self._notebook.add(tab, text="  Obfuscate  ")
        
        self._build_text_section(tab, "Input Text", "obf_input", height=6, readonly=False)
        
        self._make_button_row(tab, [
            ("📂 Obfuscate File…", self._obf_process_file, None),
            ("Clear", self._obf_clear_input, None),
        ])
        
        # Config row
        cfg_frame = tk.Frame(tab, bg=COL["bg"])
        cfg_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.obf_builder = StrategyBuilder(cfg_frame)
        self.obf_builder.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        seed_frame = tk.LabelFrame(
            cfg_frame,
            text=" Seed ",
            bg=COL["bg"],
            fg=COL["accent"],
            font=("Segoe UI Variable", 9, "bold"),
            padx=8,
            pady=6,
        )
        seed_frame.configure(highlightbackground=COL["border"], highlightthickness=1, bd=0)
        seed_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.obf_seed_var = tk.StringVar()
        seed_box = tk.Entry(
            seed_frame,
            textvariable=self.obf_seed_var,
            width=12,
            font=("Consolas", 10),
            bg=COL["surface"],
            fg=COL["text"],
            insertbackground=COL["accent"],
            relief="flat",
            highlightbackground=COL["border"],
            highlightthickness=1,
        )
        seed_box.pack(side=tk.LEFT, padx=(0, 6))
        
        dice = tk.Label(
            seed_frame,
            text="🎲",
            font=("Segoe UI Variable", 10),
            bg=COL["surface"],
            fg=COL["accent"],
            cursor="hand2",
            padx=6,
            pady=2,
        )
        dice.pack(side=tk.LEFT)
        dice.bind("<Enter>", lambda e: dice.configure(bg=COL["surface_hover"]))
        dice.bind("<Leave>", lambda e: dice.configure(bg=COL["surface"]))
        dice.bind("<Button-1>", lambda e: self._obf_randomize_seed())
        
        self._make_button_row(tab, [
            ("▸ Obfuscate", self._obfuscate, "primary"),
            ("📂 Load Key…", self._obf_load_key, None),
            ("💾 Save Key…", self._obf_save_key, None),
        ])
        
        self._make_button_row(tab, [
            ("⋮ Copy Output", self._obf_copy_output, None),
            ("💾 Save Output…", self._obf_save_output, None),
        ])
        
        # Preview
        self.obf_preview = CharsetPreview(tab)
        self.obf_preview.pack(fill=tk.X, pady=(6, 0))
        self.obf_preview.show_pool("basic")
        self.obf_builder.rows[0].pool_var.trace_add("write", lambda *a: self._obf_update_preview())
        
        self._build_text_section(tab, "Output", "obf_output", height=5, readonly=True)
    
    def _obf_process_file(self):
        import tkinter.filedialog as fd
        path = fd.askopenfilename(
            title="Select file to obfuscate",
            filetypes=[("Text files", "*.txt"), ("Python files", "*.py"), ("All files", "*.*")]
        )
        if not path:
            return
        try:
            text = Path(path).read_text(encoding="utf-8")
        except Exception as e:
            messagebox.showerror("Error", f"Could not read file:\n{e}")
            return
        self._file_choice_dialog("Obfuscate File", text, path, mode="obfuscate")
    
    def _obf_clear_input(self):
        self.obf_input[1].delete("1.0", tk.END)
        # Get the actual Text widget from the tuple
        _, out_txt = self.obf_output
        out_txt.config(state=tk.NORMAL)
        out_txt.delete("1.0", tk.END)
        out_txt.config(state=tk.DISABLED)
        self.log.log("Cleared input and output")
    
    def _obf_randomize_seed(self):
        self._current_obf_seed = self._random_seed()
        self.obf_seed_var.set(str(self._current_obf_seed))
    
    def _obf_update_preview(self):
        rounds = self.obf_builder.get_rounds()
        if rounds:
            _, pool = rounds[0]
            self.obf_preview.show_pool(pool)
    
    def _obfuscate(self):
        _, out_txt = self.obf_output
        raw = self.obf_input[1].get("1.0", tk.END).strip()
        if not raw:
            messagebox.showwarning("No input", "Enter or load some text first.")
            return
        
        rounds = self.obf_builder.get_rounds()
        seed_raw = self.obf_seed_var.get().strip()
        seed = int(seed_raw) if seed_raw else self._current_obf_seed
        
        if seed is None:
            self._obf_randomize_seed()
            seed = self._current_obf_seed
        
        self._set_status("● Obfuscating…", "warn")
        self.update()
        
        try:
            start = time.perf_counter()
            result = core.obfuscate(raw, rounds, seed=seed)
            elapsed = time.perf_counter() - start
            
            out_txt.config(state=tk.NORMAL)
            out_txt.delete("1.0", tk.END)
            out_txt.insert("1.0", result)
            out_txt.config(state=tk.DISABLED)
            
            self._obf_update_preview()
            
            seq = " → ".join(f"{s}/{p}" for s, p in rounds)
            self.log.log(f"Obfuscated {len(raw)}→{len(result)} chars [{seq}, seed={seed}] in {elapsed*1000:.1f}ms")
            self._set_status("● Done", "success")
        except Exception as e:
            messagebox.showerror("Obfuscation Error", str(e))
            self.log.log(f"ERROR: {e}")
            self._set_status("● Error", "error")
    
    def _obf_copy_output(self):
        _, out_txt = self.obf_output
        text = out_txt.get("1.0", tk.END).strip()
        if text:
            copy_to_clipboard(out_txt, text)
            self.log.log("Output copied to clipboard")
    
    def _obf_save_output(self):
        path = save_file_dialog()
        if path:
            _, out_txt = self.obf_output
            content = out_txt.get("1.0", tk.END).strip()
            Path(path).write_text(content, encoding="utf-8")
            self.log.log(f"Output saved to {path}")
    
    def _obf_save_key(self):
        path = save_key_dialog()
        if not path:
            return
        rounds = self.obf_builder.get_rounds()
        if not rounds:
            messagebox.showwarning("No rounds", "Add at least one round first.")
            return
        seed_raw = self.obf_seed_var.get().strip()
        seed = int(seed_raw) if seed_raw else self._current_obf_seed
        if seed is None:
            self._obf_randomize_seed()
            seed = self._current_obf_seed
        
        try:
            config = keys.NxObfusConfig(seed=seed, rounds=rounds)
            config.save(path)
            seq = " → ".join(f"{s}/{p}" for s, p in rounds)
            self.log.log(f"Key saved to {path} [{seq}, seed={seed}]")
        except Exception as e:
            messagebox.showerror("Save Error", str(e))
    
    def _obf_load_key(self):
        path = load_key_dialog()
        if not path:
            return
        try:
            config = keys.NxObfusConfig.load(path)
            self.obf_builder.set_rounds(config.rounds)
            seed_str = str(config.seed) if config.seed is not None else ""
            self.obf_seed_var.set(seed_str)
            self._current_obf_seed = config.seed
            if config.rounds:
                _, pool = config.rounds[0]
                self.obf_preview.show_pool(pool)
            seq = " → ".join(f"{s}/{p}" for s, p in config.rounds)
            self.log.log(f"Key loaded from {path} [{seq}, seed={config.seed}]")
        except Exception as e:
            messagebox.showerror("Load Error", f"Could not load key:\n{e}")
    
    # ════════════════════════════════════════════════════════
    #  DEOBFUSCATE TAB
    # ════════════════════════════════════════════════════════
    def _build_deobfuscate_tab(self):
        COL = self.palette
        tab = tk.Frame(self._notebook, bg=COL["bg"], padx=12, pady=10)
        self._notebook.add(tab, text="  Deobfuscate  ")
        
        self._build_text_section(tab, "Obfuscated Text", "deobf_input", height=6, readonly=False)
        
        self._make_button_row(tab, [
            ("📂 Deobfuscate File…", self._deobf_process_file, None),
            ("📂 Load Key…", self._deobf_load_key, None),
            ("Clear", self._deobf_clear_all, None),
        ])
        
        cfg_frame = tk.Frame(tab, bg=COL["bg"])
        cfg_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.deobf_builder = StrategyBuilder(cfg_frame)
        self.deobf_builder.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        seed_frame = tk.LabelFrame(
            cfg_frame,
            text=" Seed ",
            bg=COL["bg"],
            fg=COL["accent"],
            font=("Segoe UI Variable", 9, "bold"),
            padx=8,
            pady=6,
        )
        seed_frame.configure(highlightbackground=COL["border"], highlightthickness=1, bd=0)
        seed_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.deobf_seed_var = tk.StringVar()
        seed_box = tk.Entry(
            seed_frame,
            textvariable=self.deobf_seed_var,
            width=12,
            font=("Consolas", 10),
            bg=COL["surface"],
            fg=COL["text"],
            insertbackground=COL["accent"],
            relief="flat",
            highlightbackground=COL["border"],
            highlightthickness=1,
        )
        seed_box.pack(side=tk.LEFT, padx=(0, 6))
        
        dice = tk.Label(
            seed_frame,
            text="🎲",
            font=("Segoe UI Variable", 10),
            bg=COL["surface"],
            fg=COL["accent"],
            cursor="hand2",
            padx=6,
            pady=2,
        )
        dice.pack(side=tk.LEFT)
        dice.bind("<Enter>", lambda e: dice.configure(bg=COL["surface_hover"]))
        dice.bind("<Leave>", lambda e: dice.configure(bg=COL["surface"]))
        dice.bind("<Button-1>", lambda e: self._deobf_randomize_seed())
        
        self._make_button_row(tab, [
            ("◂ Deobfuscate", self._deobfuscate, "primary"),
            ("💾 Save Key…", self._deobf_save_key, None),
        ])
        
        self._make_button_row(tab, [
            ("⋮ Copy Output", self._deobf_copy_output, None),
            ("💾 Save Output…", self._deobf_save_output, None),
        ])
        
        self.deobf_preview = CharsetPreview(tab)
        self.deobf_preview.pack(fill=tk.X, pady=(6, 0))
        self.deobf_preview.show_pool("basic")
        
        self._build_text_section(tab, "Output", "deobf_output", height=5, readonly=True)
    
    def _build_text_section(self, parent, label_text, attr_name, height=6, readonly=False):
        """Helper: builds a label + text area combo, storing (wrapper, text) tuple."""
        COL = self.palette
        
        tk.Label(
            parent,
            text=label_text,
            font=("Segoe UI Variable", 10, "bold"),
            bg=COL["bg"],
            fg=COL["text"],
        ).pack(anchor=tk.W, pady=(10, 4))
        
        wrapper, txt = self._make_text_area(parent, height=height, readonly=readonly)
        wrapper.pack(fill=tk.BOTH, expand=True)
        setattr(self, attr_name, (wrapper, txt))
    
    def _deobf_process_file(self):
        import tkinter.filedialog as fd
        path = fd.askopenfilename(
            title="Select file to deobfuscate",
            filetypes=[("Text files", "*.txt"), ("Python files", "*.py"), ("All files", "*.*")]
        )
        if not path:
            return
        try:
            text = Path(path).read_text(encoding="utf-8")
        except Exception as e:
            messagebox.showerror("Error", f"Could not read file:\n{e}")
            return
        self._file_choice_dialog("Deobfuscate File", text, path, mode="deobfuscate")
    
    def _deobf_load_key(self):
        path = load_key_dialog()
        if not path:
            return
        try:
            config = keys.NxObfusConfig.load(path)
            self.deobf_builder.set_rounds(config.rounds)
            seed_str = str(config.seed) if config.seed is not None else ""
            self.deobf_seed_var.set(seed_str)
            self._current_deobf_seed = config.seed
            if config.rounds:
                _, pool = config.rounds[0]
                self.deobf_preview.show_pool(pool)
            seq = " → ".join(f"{s}/{p}" for s, p in config.rounds)
            self.log.log(f"Key loaded from {path} [{seq}, seed={config.seed}]")
        except Exception as e:
            messagebox.showerror("Load Error", f"Could not load key:\n{e}")
    
    def _deobf_save_key(self):
        path = save_key_dialog()
        if not path:
            return
        rounds = self.deobf_builder.get_rounds()
        if not rounds:
            messagebox.showwarning("No rounds", "Add at least one round first.")
            return
        seed_raw = self.deobf_seed_var.get().strip()
        seed = int(seed_raw) if seed_raw else self._current_deobf_seed
        if seed is None:
            self._deobf_randomize_seed()
            seed = self._current_deobf_seed
        
        try:
            config = keys.NxObfusConfig(seed=seed, rounds=rounds)
            config.save(path)
            seq = " → ".join(f"{s}/{p}" for s, p in rounds)
            self.log.log(f"Key saved to {path} [{seq}, seed={seed}]")
        except Exception as e:
            messagebox.showerror("Save Error", str(e))
    
    def _deobf_randomize_seed(self):
        self._current_deobf_seed = self._random_seed()
        self.deobf_seed_var.set(str(self._current_deobf_seed))
    
    def _deobf_clear_all(self):
        self.deobf_input.delete("1.0", tk.END)
        _, out_txt = self.deobf_output
        out_txt.config(state=tk.NORMAL)
        out_txt.delete("1.0", tk.END)
        out_txt.config(state=tk.DISABLED)
        self.deobf_builder.clear()
        self.deobf_seed_var.set("")
        self.log.log("Cleared deobfuscate input, output, and config")
    
    def _deobfuscate(self):
        raw = self.deobf_input[1].get("1.0", tk.END).strip()
        if not raw:
            messagebox.showwarning("No input", "Enter or load some obfuscated text first.")
            return
        
        rounds = self.deobf_builder.get_rounds()
        seed_raw = self.deobf_seed_var.get().strip()
        seed = int(seed_raw) if seed_raw else self._current_deobf_seed
        
        if seed is None:
            self._deobf_randomize_seed()
            seed = self._current_deobf_seed
        
        self._set_status("● Deobfuscating…", "warn")
        self.update()
        
        try:
            start = time.perf_counter()
            result = core.deobfuscate(raw, rounds, seed=seed)
            elapsed = time.perf_counter() - start
            
            _, out_txt = self.deobf_output
            out_txt.config(state=tk.NORMAL)
            out_txt.delete("1.0", tk.END)
            out_txt.insert("1.0", result)
            out_txt.config(state=tk.DISABLED)
            
            seq = " → ".join(f"{s}/{p}" for s, p in rounds)
            self.log.log(f"Deobfuscated {len(raw)}→{len(result)} chars [{seq}, seed={seed}] in {elapsed*1000:.1f}ms")
            self._set_status("● Done", "success")
        except Exception as e:
            messagebox.showerror("Deobfuscation Error", str(e))
            self.log.log(f"ERROR: {e}")
            self._set_status("● Error", "error")
    
    def _deobf_copy_output(self):
        _, out_txt = self.deobf_output
        text = out_txt.get("1.0", tk.END).strip()
        if text:
            copy_to_clipboard(out_txt, text)
            self.log.log("Output copied to clipboard")
    
    def _deobf_save_output(self):
        path = save_file_dialog()
        if path:
            _, out_txt = self.deobf_output
            content = out_txt.get("1.0", tk.END).strip()
            Path(path).write_text(content, encoding="utf-8")
            self.log.log(f"Output saved to {path}")
    
    # ════════════════════════════════════════════════════════
    #  KEY MANAGER TAB
    # ════════════════════════════════════════════════════════
    def _build_key_tab(self):
        COL = self.palette
        tab = tk.Frame(self._notebook, bg=COL["bg"], padx=12, pady=10)
        self._notebook.add(tab, text="  Key Manager  ")
        
        left = tk.Frame(tab, bg=COL["bg"])
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        right = tk.Frame(tab, bg=COL["bg"])
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # ── Generate ──
        gen_frame = tk.LabelFrame(
            left,
            text=" Generate Key File ",
            bg=COL["bg"],
            fg=COL["accent"],
            font=("Segoe UI Variable", 10, "bold"),
            padx=12,
            pady=10,
        )
        gen_frame.configure(highlightbackground=COL["border"], highlightthickness=1, bd=0)
        gen_frame.pack(fill=tk.X)
        
        gen_btn = tk.Label(
            gen_frame,
            text="Open Generator…",
            font=("Segoe UI Variable", 10, "bold"),
            bg=COL["accent"],
            fg="#ffffff",
            padx=20,
            pady=8,
            cursor="hand2",
        )
        gen_btn.pack(fill=tk.X, pady=(4, 8))
        gen_btn.bind("<Enter>", lambda e: gen_btn.configure(bg=COL["accent_glow"]))
        gen_btn.bind("<Leave>", lambda e: gen_btn.configure(bg=COL["accent"]))
        gen_btn.bind("<Button-1>", lambda e: self._key_generate_dialog())
        
        desc = (
            "Configure the strategy chain and seed in a dedicated window.\n"
            "Seed is auto-generated; hit the dice to refresh.\n"
            "Saves as a .nxob config file."
        )
        tk.Label(
            gen_frame,
            text=desc,
            justify=tk.LEFT,
            bg=COL["bg"],
            fg=COL["text_dim"],
            font=("Segoe UI Variable", 9),
            wraplength=320,
        ).pack(fill=tk.X)
        
        self.key_preview = CharsetPreview(left)
        self.key_preview.pack(fill=tk.X, pady=(10, 0))
        self.key_preview.show_pool("basic")
        
        # ── Load / Inspect ──
        load_frame = tk.LabelFrame(
            right,
            text=" Load Key File ",
            bg=COL["bg"],
            fg=COL["accent"],
            font=("Segoe UI Variable", 10, "bold"),
            padx=12,
            pady=10,
        )
        load_frame.configure(highlightbackground=COL["border"], highlightthickness=1, bd=0)
        load_frame.pack(fill=tk.X)
        
        open_btn = tk.Label(
            load_frame,
            text="Open .nxob File…",
            font=("Segoe UI Variable", 10, "bold"),
            bg=COL["surface_light"],
            fg=COL["text"],
            padx=20,
            pady=8,
            cursor="hand2",
        )
        open_btn.pack(fill=tk.X, pady=(4, 8))
        open_btn.bind("<Enter>", lambda e: open_btn.configure(bg=COL["surface_hover"]))
        open_btn.bind("<Leave>", lambda e: open_btn.configure(bg=COL["surface_light"]))
        open_btn.bind("<Button-1>", lambda e: self._key_load())
        
        self.key_meta_text = tk.Text(
            load_frame,
            height=10,
            wrap=tk.WORD,
            state=tk.DISABLED,
            font=("Consolas", 10),
            bg=COL["surface"],
            fg=COL["text"],
            insertbackground=COL["accent"],
            selectbackground=COL["accent_secondary"],
            selectforeground="#ffffff",
            relief="flat",
            padx=8,
            pady=6,
        )
        self.key_meta_text.pack(fill=tk.BOTH, expand=True)
        
        self._make_button_row(load_frame, [
            ("Apply to Obfuscate", self._key_apply_obf, None),
            ("Apply to Deobfuscate", self._key_apply_deobf, None),
        ])
    
    def _key_generate_dialog(self):
        COL = self.palette
        
        dialog = tk.Toplevel(self)
        dialog.title("Generate Key File")
        dialog.geometry("540x340")
        dialog.transient(self)
        dialog.grab_set()
        dialog.resizable(False, False)
        dialog.configure(bg=COL["bg"])
        
        dialog.update_idletasks()
        hwnd = ctypes.windll.user32.GetParent(dialog.winfo_id())
        _set_dark_titlebar(hwnd)
        _set_window_corner(hwnd, 1)
        
        tk.Frame(dialog, bg=COL["accent"], height=2).pack(fill=tk.X)
        
        main = tk.Frame(dialog, bg=COL["bg"], padx=20, pady=16)
        main.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(
            main,
            text="Generate Key File",
            font=("Segoe UI Variable", 14, "bold"),
            bg=COL["bg"],
            fg=COL["text"],
        ).pack(anchor=tk.W)
        
        builder = StrategyBuilder(main)
        builder.pack(fill=tk.X, expand=False, pady=(10, 0))
        
        seed_frame = tk.LabelFrame(
            main,
            text=" Seed ",
            bg=COL["bg"],
            fg=COL["accent"],
            font=("Segoe UI Variable", 9, "bold"),
            padx=8,
            pady=6,
        )
        seed_frame.configure(highlightbackground=COL["border"], highlightthickness=1, bd=0)
        seed_frame.pack(fill=tk.X, pady=(12, 0))
        
        seed_var = tk.StringVar(value=str(self._random_seed()))
        seed_box = tk.Entry(
            seed_frame,
            textvariable=seed_var,
            width=12,
            font=("Consolas", 10),
            bg=COL["surface"],
            fg=COL["text"],
            insertbackground=COL["accent"],
            relief="flat",
            highlightbackground=COL["border"],
            highlightthickness=1,
        )
        seed_box.pack(side=tk.LEFT, padx=(0, 6))
        
        dice = tk.Label(
            seed_frame,
            text="🎲",
            font=("Segoe UI Variable", 10),
            bg=COL["surface"],
            fg=COL["accent"],
            cursor="hand2",
            padx=6,
            pady=2,
        )
        dice.pack(side=tk.LEFT)
        dice.bind("<Enter>", lambda e: dice.configure(bg=COL["surface_hover"]))
        dice.bind("<Leave>", lambda e: dice.configure(bg=COL["surface"]))
        dice.bind("<Button-1>", lambda e: seed_var.set(str(self._random_seed())))
        
        btn_frame = tk.Frame(main, bg=COL["bg"])
        btn_frame.pack(fill=tk.X, pady=(16, 0))
        
        cancel = tk.Label(
            btn_frame,
            text="Cancel",
            font=("Segoe UI Variable", 9, "bold"),
            bg=COL["surface"],
            fg=COL["text_dim"],
            padx=16,
            pady=6,
            cursor="hand2",
        )
        cancel.pack(side=tk.RIGHT, padx=(8, 0))
        cancel.bind("<Enter>", lambda e: cancel.configure(bg=COL["error"], fg="#ffffff"))
        cancel.bind("<Leave>", lambda e: cancel.configure(bg=COL["surface"], fg=COL["text_dim"]))
        cancel.bind("<Button-1>", lambda e: dialog.destroy())
        
        gen = tk.Label(
            btn_frame,
            text="Generate & Save",
            font=("Segoe UI Variable", 9, "bold"),
            bg=COL["accent"],
            fg="#ffffff",
            padx=20,
            pady=6,
            cursor="hand2",
        )
        gen.pack(side=tk.RIGHT)
        gen.bind("<Enter>", lambda e: gen.configure(bg=COL["accent_glow"]))
        gen.bind("<Leave>", lambda e: gen.configure(bg=COL["accent"]))
        gen.bind("<Button-1>", lambda e: self._key_generate_from_dialog(dialog, builder, seed_var))
        
        preview = CharsetPreview(main)
        preview.pack(fill=tk.X, pady=(10, 0))
        preview.show_pool(builder.rows[0].pool_var.get())
        builder.rows[0].pool_var.trace_add("write", lambda *a: preview.show_pool(builder.rows[0].pool_var.get()))
    
    def _key_generate_from_dialog(self, dialog, builder, seed_var):
        rounds = builder.get_rounds()
        if not rounds:
            messagebox.showwarning("No rounds", "Add at least one round.")
            return
        seed_raw = seed_var.get().strip()
        seed = int(seed_raw) if seed_raw else self._random_seed()
        
        path = save_key_dialog("Save Key File")
        if not path:
            return
        try:
            config = keys.NxObfusConfig(seed=seed, rounds=rounds)
            config.save(path)
            seq = " → ".join(f"{s}/{p}" for s, p in rounds)
            self.log.log(f"Key file saved to {path} [{seq}, seed={seed}]")
            self.key_preview.show_pool(rounds[0][1])
            dialog.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def _key_load(self):
        path = load_key_dialog("Open Key File")
        if not path:
            return
        try:
            config = keys.NxObfusConfig.load(path)
            self._loaded_config = config
            rounds_str = " → ".join(f"{s}/{p}" for s, p in config.rounds) if config.rounds else "(empty)"
            meta = (
                f"Version:   {config.version}\n"
                f"Seed:      {config.seed}\n"
                f"Rounds:    {len(config.rounds)}\n"
                f"Chain:     {rounds_str}\n"
            )
            self.key_meta_text.config(state=tk.NORMAL)
            self.key_meta_text.delete("1.0", tk.END)
            self.key_meta_text.insert("1.0", meta)
            self.key_meta_text.config(state=tk.DISABLED)
            self.log.log(f"Key loaded from {path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def _key_apply_obf(self):
        if not hasattr(self, '_loaded_config') or self._loaded_config is None:
            messagebox.showwarning("No key loaded", "Load an .nxob file first.")
            return
        config = self._loaded_config
        self._notebook.select(0)
        self.obf_builder.set_rounds(config.rounds)
        seed_str = str(config.seed) if config.seed is not None else ""
        self.obf_seed_var.set(seed_str)
        self._current_obf_seed = config.seed
        if config.rounds:
            _, pool = config.rounds[0]
            self.obf_preview.show_pool(pool)
        seq = " → ".join(f"{s}/{p}" for s, p in config.rounds)
        self.log.log(f"Applied key to Obfuscate tab: [{seq}, seed={config.seed}]")
    
    def _key_apply_deobf(self):
        if not hasattr(self, '_loaded_config') or self._loaded_config is None:
            messagebox.showwarning("No key loaded", "Load an .nxob file first.")
            return
        config = self._loaded_config
        self._notebook.select(1)
        self.deobf_builder.set_rounds(config.rounds)
        seed_str = str(config.seed) if config.seed is not None else ""
        self.deobf_seed_var.set(seed_str)
        self._current_deobf_seed = config.seed
        if config.rounds:
            _, pool = config.rounds[0]
            self.deobf_preview.show_pool(pool)
        seq = " → ".join(f"{s}/{p}" for s, p in config.rounds)
        self.log.log(f"Applied key to Deobfuscate tab: [{seq}, seed={config.seed}]")


def main():
    app = NxObfusGUI()
    app.mainloop()


if __name__ == "__main__":
    main()
