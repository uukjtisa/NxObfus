import tkinter as tk
from tkinter import messagebox
from pathlib import Path
from ttkbootstrap.widgets import ttk
from ttkbootstrap import Window
from ttkbootstrap.constants import *
import time

from . import core
from . import keys
from .gui_theme import toggle_theme, is_dark, retheme
from .gui_strategy_builder import StrategyBuilder
from .gui_preview import CharsetPreview
from .gui_log import CommandLog
from .gui_helpers import (
    load_file_dialog, save_file_dialog,
    save_key_dialog, load_key_dialog,
    copy_to_clipboard,
)


class NxObfusGUI(Window):
    def __init__(self):
        super().__init__(themename="flatly")
        self.title("NxObfus v2.0.0")
        self.geometry("860x780")
        self.minsize(700, 600)

        self._build_menu()
        self._build_notebook()
        self._build_obfuscate_tab()
        self._build_deobfuscate_tab()
        self._build_key_tab()
        self._build_log()

        self._current_obf_seed = None
        self._current_deobf_seed = None

    # ── Menu Bar ────────────────────────────────────────────

    def _build_menu(self):
        bar = tk.Menu(self)
        self.config(menu=bar)

        file_menu = tk.Menu(bar, tearoff=0)
        file_menu.add_command(label="Load Input Text...", command=self._menu_load_input)
        file_menu.add_command(label="Save Output As...", command=self._menu_save_output)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.destroy)
        bar.add_cascade(label="File", menu=file_menu)

        view_menu = tk.Menu(bar, tearoff=0)
        view_menu.add_command(label="Toggle Dark Mode", command=self._toggle_dark_mode)
        bar.add_cascade(label="View", menu=view_menu)

    def _toggle_dark_mode(self):
        toggle_theme()
        retheme(self)
        dark = is_dark()
        self.log.log(f"Switched to {'dark' if dark else 'light'} mode")

    def _menu_load_input(self):
        tab = self._notebook.index(self._notebook.select())
        text = load_file_dialog()
        if text:
            if tab == 0:
                self.obf_input.delete("1.0", tk.END)
                self.obf_input.insert("1.0", text)
                self.log.log(f"Loaded {len(text)} chars into Obfuscate input")
            elif tab == 1:
                self.deobf_input.delete("1.0", tk.END)
                self.deobf_input.insert("1.0", text)
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

    # ── Notebook ────────────────────────────────────────────

    def _build_notebook(self):
        self._notebook = ttk.Notebook(self)
        self._notebook.pack(fill=tk.BOTH, expand=True, padx=8, pady=(4, 8))

    # ── Shared helper ──────────────────────────────────────

    def _make_text_area(self, parent, height=6, readonly=False):
        state = tk.DISABLED if readonly else tk.NORMAL
        txt = tk.Text(parent, height=height, wrap=tk.WORD, state=state, font=("Consolas", 10))
        scroll = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=txt.yview)
        txt.configure(yscrollcommand=scroll.set)
        return txt, scroll

    def _make_button_row(self, parent, buttons):
        f = ttk.Frame(parent)
        f.pack(fill=tk.X, pady=(4, 0))
        for text, cmd, style in buttons:
            kwargs = dict(text=text, command=cmd, width=14)
            if style:
                kwargs["style"] = style
            b = ttk.Button(f, **kwargs)
            b.pack(side=tk.LEFT, padx=(0, 6))
        return f

    def _random_seed(self):
        import random
        return random.randint(1, 999999)

    def _build_log(self):
        self.log = CommandLog(self)
        self.log.pack(fill=tk.X, padx=8, pady=(0, 8))
        self.log.log("NxObfus GUI ready")

    # ══════════════════════════════════════════════════════════
    #  FILE CHOICE DIALOG
    # ══════════════════════════════════════════════════════════

    def _file_choice_dialog(self, title, file_content, file_path, mode="obfuscate"):
        dialog = tk.Toplevel(self)
        dialog.title(title)
        dialog.geometry("520x280")
        dialog.transient(self)
        dialog.grab_set()
        dialog.resizable(False, False)

        main = ttk.Frame(dialog, padding=16)
        main.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main, text="How do you want to handle this file?", font=("Segoe UI", 11, "bold")).pack(anchor=tk.W, pady=(0, 12))

        btn_frame = ttk.Frame(main)
        btn_frame.pack(fill=tk.X)

        process_btn = ttk.Button(
            btn_frame,
            text="  🔁  Process Directly",
            command=lambda: self._process_directly(dialog, file_content, file_path, mode),
            style="primary.TButton",
            width=28,
        )
        process_btn.pack(side=tk.LEFT, padx=(0, 12))

        append_btn = ttk.Button(
            btn_frame,
            text="  📝  Append to Input",
            command=lambda: self._append_to_input(dialog, file_content, mode),
            width=28,
        )
        append_btn.pack(side=tk.LEFT)

        warn_frame = ttk.Frame(main)
        warn_frame.pack(fill=tk.X, pady=(14, 0))

        label = ttk.Label(
            warn_frame,
            text=(
                "⚠ Process Directly will apply obfuscation/deobfuscation\n"
                "immediately using current rounds + seed, then prompt to\n"
                "replace or save the result. No need to click the main button."
            ),
            justify=tk.LEFT,
            foreground="#888888",
            wraplength=460,
        )
        label.pack(anchor=tk.W)

        cancel_btn = ttk.Button(main, text="Cancel", command=dialog.destroy)
        cancel_btn.pack(anchor=tk.E, pady=(12, 0))

    def _process_directly(self, dialog, file_content, file_path, mode):
        dialog.destroy()

        is_obf = mode == "obfuscate"
        builder = self.obf_builder if is_obf else self.deobf_builder
        seed_var = self.obf_seed_var if is_obf else self.deobf_seed_var
        current_seed_attr = "_current_obf_seed" if is_obf else "_current_deobf_seed"
        randomize_fn = self._obf_randomize_seed if is_obf else self._deobf_randomize_seed
        output_widget = self.obf_output if is_obf else self.deobf_output
        preview_fn = self._obf_update_preview if is_obf else None
        core_fn = core.obfuscate if is_obf else core.deobfuscate
        action = "Obfuscated" if is_obf else "Deobfuscated"

        rounds = builder.get_rounds()
        if not rounds:
            messagebox.showwarning("No rounds", "Add at least one round first.")
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
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.log.log(f"ERROR: {e}")

    def _append_to_input(self, dialog, file_content, mode):
        dialog.destroy()
        target = self.obf_input if mode == "obfuscate" else self.deobf_input
        target.insert(tk.END, file_content)
        label = "Obfuscate" if mode == "obfuscate" else "Deobfuscate"
        self.log.log(f"Appended {len(file_content)} chars to {label} input")

    # ══════════════════════════════════════════════════════════
    #  OBFUSCATE TAB
    # ══════════════════════════════════════════════════════════

    def _build_obfuscate_tab(self):
        tab = ttk.Frame(self._notebook, padding=8)
        self._notebook.add(tab, text="  Obfuscate  ")

        # Input
        ttk.Label(tab, text="Input Text:", font=("Segoe UI", 10, "bold")).pack(anchor=tk.W)
        self.obf_input, sc = self._make_text_area(tab, height=6)
        self.obf_input.pack(fill=tk.BOTH, expand=True)
        sc.pack(side=tk.RIGHT, fill=tk.Y, before=self.obf_input)

        self._make_button_row(tab, [
            ("📂 Obfuscate File...", self._obf_process_file, None),
            ("Clear", self._obf_clear_input, None),
        ])

        # Config row: strategy builder + seed
        cfg_frame = ttk.Frame(tab)
        cfg_frame.pack(fill=tk.X, pady=(6, 0))

        self.obf_builder = StrategyBuilder(cfg_frame)
        self.obf_builder.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))

        seed_frame = ttk.LabelFrame(cfg_frame, text="Seed", padding=6)
        seed_frame.pack(side=tk.RIGHT, fill=tk.Y)
        self.obf_seed_var = tk.StringVar()
        seed_entry = ttk.Entry(seed_frame, textvariable=self.obf_seed_var, width=10)
        seed_entry.pack(side=tk.LEFT, padx=(0, 4))
        ttk.Button(seed_frame, text="🎲", command=self._obf_randomize_seed, width=3).pack(side=tk.LEFT)

        # Actions
        self._make_button_row(tab, [
            ("▸ Obfuscate", self._obfuscate, "primary.TButton"),
            ("📂 Load Key...", self._obf_load_key, None),
            ("💾 Save Key...", self._obf_save_key, None),
        ])

        self._make_button_row(tab, [
            ("⋮ Copy Output", self._obf_copy_output, None),
            ("💾 Save Output...", self._obf_save_output, None),
        ])

        # Preview
        self.obf_preview = CharsetPreview(tab)
        self.obf_preview.pack(fill=tk.X, pady=(4, 0))
        self.obf_preview.show_pool("basic")
        self.obf_builder.rows[0].pool_cb.bind("<<ComboboxSelected>>", lambda e: self._obf_update_preview())

        # Output
        ttk.Label(tab, text="Output:", font=("Segoe UI", 10, "bold")).pack(anchor=tk.W, pady=(6, 0))
        self.obf_output, sc2 = self._make_text_area(tab, height=5, readonly=True)
        self.obf_output.pack(fill=tk.BOTH, expand=True)
        sc2.pack(side=tk.RIGHT, fill=tk.Y, before=self.obf_output)



    def _obf_process_file(self):
        path = tk.filedialog.askopenfilename(
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
        self.obf_input.delete("1.0", tk.END)
        self.obf_output.config(state=tk.NORMAL)
        self.obf_output.delete("1.0", tk.END)
        self.obf_output.config(state=tk.DISABLED)
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
        raw = self.obf_input.get("1.0", tk.END).strip()
        if not raw:
            messagebox.showwarning("No input", "Enter or load some text first.")
            return

        rounds = self.obf_builder.get_rounds()
        seed_raw = self.obf_seed_var.get().strip()
        seed = int(seed_raw) if seed_raw else self._current_obf_seed

        if seed is None:
            self._obf_randomize_seed()
            seed = self._current_obf_seed

        try:
            start = time.perf_counter()
            result = core.obfuscate(raw, rounds, seed=seed)
            elapsed = time.perf_counter() - start

            self.obf_output.config(state=tk.NORMAL)
            self.obf_output.delete("1.0", tk.END)
            self.obf_output.insert("1.0", result)
            self.obf_output.config(state=tk.DISABLED)

            # Update preview from first round
            self._obf_update_preview()

            seq = " → ".join(f"{s}/{p}" for s, p in rounds)
            self.log.log(f"Obfuscated {len(raw)}→{len(result)} chars [{seq}, seed={seed}] in {elapsed*1000:.1f}ms")
        except Exception as e:
            messagebox.showerror("Obfuscation Error", str(e))
            self.log.log(f"ERROR: {e}")

    def _obf_copy_output(self):
        text = self.obf_output.get("1.0", tk.END).strip()
        if text:
            copy_to_clipboard(self.obf_output, text)
            self.log.log("Output copied to clipboard")

    def _obf_save_output(self):
        path = save_file_dialog()
        if path:
            content = self.obf_output.get("1.0", tk.END).strip()
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

    # ══════════════════════════════════════════════════════════
    #  DEOBFUSCATE TAB
    # ══════════════════════════════════════════════════════════

    def _build_deobfuscate_tab(self):
        tab = ttk.Frame(self._notebook, padding=8)
        self._notebook.add(tab, text="  Deobfuscate  ")

        # Input
        ttk.Label(tab, text="Obfuscated Text:", font=("Segoe UI", 10, "bold")).pack(anchor=tk.W)
        self.deobf_input, sc = self._make_text_area(tab, height=6)
        self.deobf_input.pack(fill=tk.BOTH, expand=True)
        sc.pack(side=tk.RIGHT, fill=tk.Y, before=self.deobf_input)

        self._make_button_row(tab, [
            ("📂 Deobfuscate File...", self._deobf_process_file, None),
            ("📂 Load Key...", self._deobf_load_key, None),
            ("Clear", self._deobf_clear_all, None),
        ])

        # Config
        cfg_frame = ttk.Frame(tab)
        cfg_frame.pack(fill=tk.X, pady=(6, 0))

        self.deobf_builder = StrategyBuilder(cfg_frame)
        self.deobf_builder.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))

        seed_frame = ttk.LabelFrame(cfg_frame, text="Seed", padding=6)
        seed_frame.pack(side=tk.RIGHT, fill=tk.Y)
        self.deobf_seed_var = tk.StringVar()
        seed_entry = ttk.Entry(seed_frame, textvariable=self.deobf_seed_var, width=10)
        seed_entry.pack(side=tk.LEFT, padx=(0, 4))
        ttk.Button(seed_frame, text="🎲", command=self._deobf_randomize_seed, width=3).pack(side=tk.LEFT)

        # Actions
        self._make_button_row(tab, [
            ("◂ Deobfuscate", self._deobfuscate, "primary.TButton"),
            ("💾 Save Key...", self._deobf_save_key, None),
        ])

        self._make_button_row(tab, [
            ("⋮ Copy Output", self._deobf_copy_output, None),
            ("💾 Save Output...", self._deobf_save_output, None),
        ])

        # Preview
        self.deobf_preview = CharsetPreview(tab)
        self.deobf_preview.pack(fill=tk.X, pady=(4, 0))
        self.deobf_preview.show_pool("basic")

        # Output
        ttk.Label(tab, text="Output:", font=("Segoe UI", 10, "bold")).pack(anchor=tk.W, pady=(6, 0))
        self.deobf_output, sc2 = self._make_text_area(tab, height=5, readonly=True)
        self.deobf_output.pack(fill=tk.BOTH, expand=True)
        sc2.pack(side=tk.RIGHT, fill=tk.Y, before=self.deobf_output)

    def _deobf_process_file(self):
        path = tk.filedialog.askopenfilename(
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
        self.deobf_output.config(state=tk.NORMAL)
        self.deobf_output.delete("1.0", tk.END)
        self.deobf_output.config(state=tk.DISABLED)
        self.deobf_builder.clear()
        self.deobf_seed_var.set("")
        self.log.log("Cleared deobfuscate input, output, and config")

    def _deobfuscate(self):
        raw = self.deobf_input.get("1.0", tk.END).strip()
        if not raw:
            messagebox.showwarning("No input", "Enter or load some obfuscated text first.")
            return

        rounds = self.deobf_builder.get_rounds()
        seed_raw = self.deobf_seed_var.get().strip()
        seed = int(seed_raw) if seed_raw else self._current_deobf_seed

        if seed is None:
            self._deobf_randomize_seed()
            seed = self._current_deobf_seed

        try:
            start = time.perf_counter()
            result = core.deobfuscate(raw, rounds, seed=seed)
            elapsed = time.perf_counter() - start

            self.deobf_output.config(state=tk.NORMAL)
            self.deobf_output.delete("1.0", tk.END)
            self.deobf_output.insert("1.0", result)
            self.deobf_output.config(state=tk.DISABLED)

            seq = " → ".join(f"{s}/{p}" for s, p in rounds)
            self.log.log(f"Deobfuscated {len(raw)}→{len(result)} chars [{seq}, seed={seed}] in {elapsed*1000:.1f}ms")
        except Exception as e:
            messagebox.showerror("Deobfuscation Error", str(e))
            self.log.log(f"ERROR: {e}")

    def _deobf_copy_output(self):
        text = self.deobf_output.get("1.0", tk.END).strip()
        if text:
            copy_to_clipboard(self.deobf_output, text)
            self.log.log("Output copied to clipboard")

    def _deobf_save_output(self):
        path = save_file_dialog()
        if path:
            content = self.deobf_output.get("1.0", tk.END).strip()
            Path(path).write_text(content, encoding="utf-8")
            self.log.log(f"Output saved to {path}")

    # ══════════════════════════════════════════════════════════
    #  KEY MANAGER TAB
    # ══════════════════════════════════════════════════════════

    def _build_key_tab(self):
        tab = ttk.Frame(self._notebook, padding=8)
        self._notebook.add(tab, text="  Key Manager  ")

        left = ttk.Frame(tab)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))

        right = ttk.Frame(tab)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # ── Generate ──
        gen_frame = ttk.LabelFrame(left, text="Generate Key File", padding=8)
        gen_frame.pack(fill=tk.X)

        ttk.Button(gen_frame, text="Open Generator...", command=self._key_generate_dialog, style="primary.TButton").pack(fill=tk.X, pady=(4, 6))

        desc = ("Configure strategy chain and seed in a dedicated window.\n"
                "Seed is auto-generated; you can refresh it.\n"
                "Saves as a .nxob config file.")
        ttk.Label(gen_frame, text=desc, justify=tk.LEFT, wraplength=300).pack(fill=tk.X)

        # Preview for key manager
        self.key_preview = CharsetPreview(left)
        self.key_preview.pack(fill=tk.X, pady=(6, 0))
        self.key_preview.show_pool("basic")

        # ── Load / Inspect ──
        load_frame = ttk.LabelFrame(right, text="Load Key File", padding=8)
        load_frame.pack(fill=tk.X)

        ttk.Button(load_frame, text="Open .nxob File...", command=self._key_load).pack(fill=tk.X, pady=(0, 6))

        self.key_meta_text = tk.Text(load_frame, height=10, wrap=tk.WORD, state=tk.DISABLED, font=("Consolas", 9))
        self.key_meta_text.pack(fill=tk.BOTH, expand=True)

        self._make_button_row(load_frame, [
            ("Apply to Obfuscate", self._key_apply_obf, None),
            ("Apply to Deobfuscate", self._key_apply_deobf, None),
        ])

    def _key_generate_dialog(self):
        dialog = tk.Toplevel(self)
        dialog.title("Generate Key File")
        dialog.geometry("480x300")
        dialog.transient(self)
        dialog.grab_set()

        main = ttk.Frame(dialog, padding=12)
        main.pack(fill=tk.BOTH, expand=True)

        # Strategy chain builder
        builder = StrategyBuilder(main)
        builder.pack(fill=tk.X, expand=False)

        # Seed
        seed_frame = ttk.LabelFrame(main, text="Seed", padding=6)
        seed_frame.pack(fill=tk.X, pady=(8, 0))

        seed_var = tk.StringVar(value=str(self._random_seed()))
        seed_entry = ttk.Entry(seed_frame, textvariable=seed_var, width=12)
        seed_entry.pack(side=tk.LEFT, padx=(0, 4))
        ttk.Button(seed_frame, text="🎲", command=lambda: seed_var.set(str(self._random_seed())), width=3).pack(side=tk.LEFT)

        # Buttons
        btn_frame = ttk.Frame(main)
        btn_frame.pack(fill=tk.X, pady=(12, 0))

        ttk.Button(btn_frame, text="Cancel", command=dialog.destroy, width=12).pack(side=tk.RIGHT, padx=(6, 0))
        ttk.Button(btn_frame, text="Generate & Save", command=lambda: self._key_generate_from_dialog(dialog, builder, seed_var), style="primary.TButton", width=18).pack(side=tk.RIGHT)

        # Preview update
        preview = CharsetPreview(main)
        preview.pack(fill=tk.X, pady=(6, 0))
        preview.show_pool(builder.rows[0].pool_var.get())
        builder.rows[0].pool_cb.bind("<<ComboboxSelected>>", lambda e: preview.show_pool(builder.rows[0].pool_var.get()))

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
