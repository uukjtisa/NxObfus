
"""
NxObfus — Obfuscation Strategies
Replaces ambiguous r1/r2/r3/r4 with explicit strategy classes.
"""

import random
from typing import List, Dict
from . import charset


class TokenStrategy:
    """
    Legacy r1/r3 style: each char maps to a prefixed token.
    Output is space-separated tokens. Whitespace-safe in EXTENDED mode.
    """

    PREFIXES = {
        "letters": "/xo",
        "digits": "/nx",
        "punct": "\\xp",
        "currency": "|xc",
        "trademark": "||xt",
        "math": "\x02xm\x03",
        "symbols": "\x7fxs\x1b",
        "space": "(-",
        "null": "|xn",
    }

    def __init__(self, char_pool: List[str], seed: int | None = None):
        self.char_pool = char_pool[:]
        if seed is not None:
            random.seed(seed)
        random.shuffle(self.char_pool)
        self._build_token_pool()
        self.forward: Dict[str, str] = {}
        self.reverse: Dict[str, str] = {}
        self._build_maps()

    def _build_token_pool(self):
        """Assign prefixed tokens deterministically."""
        self.tokens = []
        # Simplified: all chars get /xoNN style with shuffled numeric suffix
        pool = [f"/xo{i:03d}" for i in range(len(self.char_pool))]
        random.shuffle(pool)
        self.tokens = pool

    def _build_maps(self):
        for ch, tok in zip(self.char_pool, self.tokens):
            self.forward[ch] = tok
            self.reverse[tok] = ch

    def obfuscate(self, text: str) -> str:
        out = []
        for ch in text:
            out.append(self.forward.get(ch, ch))
        return " ".join(out)

    def deobfuscate(self, text: str) -> str:
        out = []
        for tok in text.split():
            out.append(self.reverse.get(tok, tok))
        return "".join(out)


class IndexStrategy:
    """
    Legacy r2/r4 style: each char maps to a shuffled character from the pool.
    Output is a continuous string. Not whitespace-safe unless pool includes it.
    """

    def __init__(self, char_pool: List[str], seed: int | None = None):
        self.char_pool = char_pool[:]
        self.source_pool = char_pool[:]
        if seed is not None:
            random.seed(seed)
        random.shuffle(self.source_pool)
        self.forward: Dict[str, str] = {}
        self.reverse: Dict[str, str] = {}
        self._build_maps()

    def _build_maps(self):
        for ch, sub in zip(self.char_pool, self.source_pool):
            self.forward[ch] = sub
            self.reverse[sub] = ch

    def obfuscate(self, text: str) -> str:
        return "".join(self.forward.get(ch, ch) for ch in text)

    def deobfuscate(self, text: str) -> str:
        return "".join(self.reverse.get(ch, ch) for ch in text)
