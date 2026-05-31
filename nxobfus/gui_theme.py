import ttkbootstrap as tb
from ttkbootstrap.constants import *

# ═══════════════════════════════════════════════════════════
#  NXOBFUS DARK THEME SYSTEM
# ═══════════════════════════════════════════════════════════

# Force dark only — no light mode, no toggle. Pure darkness.
_THEME_NAME = "darkly"

# Base style singleton
_style = None

def get_style():
    global _style
    if _style is None:
        _style = tb.Style(theme=_THEME_NAME)
        _apply_nxobfus_overrides(_style)
    return _style

def refresh_style(root):
    root.style.theme_use(_THEME_NAME)
    _apply_nxobfus_overrides(root.style)

# ── Color Palette ─────────────────────────────────────────
DARK = {
    "bg": "#0a0a0f",
    "surface": "#13131f",
    "surface_hover": "#1a1a2e",
    "surface_light": "#1e1e2d",
    "border": "#2a2a3a",
    "border_accent": "#00d4aa",
    "text": "#e2e8f0",
    "text_dim": "#64748b",
    "accent": "#00d4aa",
    "accent_secondary": "#7c3aed",
    "accent_glow": "#00f5d4",
    "error": "#f43f5e",
    "warn": "#f59e0b",
    "success": "#10b981",
    "info": "#3b82f6",
}

def _apply_nxobfus_overrides(style):
    """Inject custom NXObfus aesthetics into ttkbootstrap Darkly."""
    
    # Main text areas — deep dark with subtle border
    style.configure(
        "NX.TText",
        background=DARK["surface"],
        foreground=DARK["text"],
        insertbackground=DARK["accent"],
        selectbackground=DARK["accent_secondary"],
        selectforeground="#ffffff",
        borderwidth=1,
        relief="solid",
        highlightcolor=DARK["border_accent"],
        font=("Consolas", 10),
    )
    
    # Notebook tabs — sleek dark
    style.configure(
        "TNotebook",
        background=DARK["bg"],
        tabmargins=[2, 5, 2, 0],
    )
    style.configure(
        "TNotebook.Tab",
        font=("Segoe UI Variable", 10, "bold"),
        padding=[16, 8],
        background=DARK["surface"],
        foreground=DARK["text_dim"],
        bordercolor=DARK["border"],
        lightcolor=DARK["surface"],
        darkcolor=DARK["surface"],
    )
    style.map(
        "TNotebook.Tab",
        background=[("selected", DARK["surface_light"]), ("active", DARK["surface_hover"])],
        foreground=[("selected", DARK["accent"]), ("active", DARK["text"])],
        expand=[("selected", [2, 2, 2, 0])],
    )
    
    # Primary accent button (teal glow)
    style.configure(
        "NXAccent.TButton",
        font=("Segoe UI Variable", 9, "bold"),
        foreground="#ffffff",
        background=DARK["accent"],
        bordercolor=DARK["accent"],
        lightcolor=DARK["accent"],
        darkcolor=DARK["accent"],
    )
    style.map(
        "NXAccent.TButton",
        background=[("active", DARK["accent_glow"]), ("pressed", "#00b894")],
        foreground=[("disabled", DARK["text_dim"])],
    )
    
    # Danger / remove button
    style.configure(
        "NXDanger.TButton",
        background=DARK["error"],
        bordercolor=DARK["error"],
        lightcolor=DARK["error"],
        darkcolor=DARK["error"],
        font=("Segoe UI Variable", 9, "bold"),
    )
    
    # Success / add button
    style.configure(
        "NXSuccess.TButton",
        background=DARK["success"],
        bordercolor=DARK["success"],
        lightcolor=DARK["success"],
        darkcolor=DARK["success"],
        font=("Segoe UI Variable", 9, "bold"),
    )
    
    # Labels
    style.configure(
        "NXTitle.TLabel",
        font=("Segoe UI Variable", 11, "bold"),
        foreground=DARK["text"],
        background=DARK["bg"],
    )
    style.configure(
        "NXSubtitle.TLabel",
        font=("Segoe UI Variable", 9),
        foreground=DARK["text_dim"],
        background=DARK["bg"],
    )
    
    # Scrollbar
    style.configure(
        "NX.TScrollbar",
        background=DARK["surface_light"],
        troughcolor=DARK["bg"],
        bordercolor=DARK["bg"],
        arrowcolor=DARK["text_dim"],
        lightcolor=DARK["surface_light"],
        darkcolor=DARK["surface_light"],
    )
    style.map(
        "NX.TScrollbar",
        background=[("active", DARK["accent"])],
    )
    
    # Entry fields
    style.configure(
        "NX.TEntry",
        fieldbackground=DARK["surface"],
        foreground=DARK["text"],
        insertcolor=DARK["accent"],
        bordercolor=DARK["border"],
        lightcolor=DARK["surface"],
        darkcolor=DARK["surface"],
    )
    
    # Combobox
    style.configure(
        "NX.TCombobox",
        fieldbackground=DARK["surface"],
        foreground=DARK["text"],
        selectbackground=DARK["accent_secondary"],
        arrowcolor=DARK["accent"],
        bordercolor=DARK["border"],
    )
    
    # LabelFrame
    style.configure(
        "NX.TLabelframe",
        background=DARK["bg"],
        foreground=DARK["text_dim"],
        bordercolor=DARK["border"],
        borderwidth=1,
        relief="solid",
        lightcolor=DARK["bg"],
        darkcolor=DARK["bg"],
    )
    style.configure(
        "NX.TLabelframe.Label",
        font=("Segoe UI Variable", 9, "bold"),
        foreground=DARK["accent"],
        background=DARK["bg"],
    )
    
    # Progress / horizontal bars
    style.configure(
        "NX.Horizontal.TProgressbar",
        background=DARK["accent"],
        troughcolor=DARK["surface"],
        bordercolor=DARK["bg"],
        lightcolor=DARK["accent"],
        darkcolor=DARK["accent"],
    )

def is_dark():
    return True  # Always dark. Always.

def palette():
    return DARK.copy()
