import ttkbootstrap as tb
from ttkbootstrap.constants import *

THEMES = {
    "light": "flatly",
    "dark": "darkly",
}

_current_theme = "light"

def get_style():
    return tb.Style(theme=THEMES[_current_theme])

def toggle_theme():
    global _current_theme
    _current_theme = "dark" if _current_theme == "light" else "light"

def is_dark():
    return _current_theme == "dark"

def retheme(root):
    root.style.theme_use(THEMES[_current_theme])
