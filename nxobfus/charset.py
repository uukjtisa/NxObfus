"""
NxObfus — Unified Character Sets
Clean, deduplicated, actual control characters. No ambiguity.
"""

import string


def _deduped(*lists):
    """Preserve order, remove duplicates across categories."""
    seen = set()
    result = []
    for lst in lists:
        for ch in lst:
            if ch not in seen:
                seen.add(ch)
                result.append(ch)
    return result


# ── Core Categories ───────────────────────────────────────────
LETTERS = list(string.ascii_letters)          # a-zA-Z
DIGITS = list(string.digits)                  # 0-9
PUNCTUATION = list(string.punctuation)        # !"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~

# Actual control chars, not literal backslash sequences
SPACE_TAB_NEWLINE = [chr(0x20), chr(0x09), chr(0x0A)]  # space, tab, newline

# ── Extended Categories ───────────────────────────────────────
CURRENCY = ["₱", "$", "€", "¥", "£", "₹", "₽", "₿", "฿", "₺", "₴", "¢"]
TRADEMARK = ["©", "®", "™", "℗", "℠", "℡"]
MATH_MISC = list("•†‡°¤‰′″+−=×÷±∓√∞∑∏∫∂∇∆∅∈∉∋∌∩∪∧∨¬¦‖≠≡≤≥≈≉≪≫⊂⊃⊆⊇⊕⊗⊥⋅∙∗※")
SYMBOLS = list("§¶☎✉✂✍✎✏✐✑✒✓✔✕✖✘❌❎❓❔❕❗➕➖➗✈✌❤❥❦❧❂❁✄☠☢☣☤☥☦☧☨☩☪☫☬☭☮☯☸☹☺☻☼☽☾♀♂♠♣♥♦♪♫♬♭♯")
NULL_CHARS = [chr(i) for i in (*range(0x00, 0x09), 0x0B, 0x0C, 0x1B, 0x7F)]


def make_basic() -> list[str]:
    """Letters, digits, punctuation, misc symbols. No whitespace."""
    etc = list("₱€¥¢©®™~¿[]{}<>^¡`;÷|¦¬×§¶°")
    return _deduped(LETTERS, DIGITS, PUNCTUATION, etc)


def make_extended() -> list[str]:
    """Everything + whitespace + null chars. Fully deduplicated."""
    return _deduped(
        LETTERS, DIGITS, PUNCTUATION,
        CURRENCY, TRADEMARK, MATH_MISC, SYMBOLS,
        SPACE_TAB_NEWLINE, NULL_CHARS
    )


# Pre-built
BASIC = make_basic()
EXTENDED = make_extended()
