
"""
NxObfus — Key Generation and I/O
Replaces keyworker.py chaos with structured, metadata-rich key files.
"""

import json
import hashlib
from pathlib import Path
from typing import List
from . import charset


class Keyfile:
    """
    Structured .nxob keyfile format:
        [metadata block]
        ---
        [forward char pool — one per line]
    """

    def __init__(self, strategy_name: str, char_pool: List[str], source_pool: List[str], seed: int | None):
        self.strategy_name = strategy_name
        self.char_pool = char_pool
        self.source_pool = source_pool
        self.seed = seed
        self.version = "2.0.0"
        self._digest = self._make_digest()

    def _make_digest(self) -> str:
        payload = "".join(self.char_pool) + "".join(self.source_pool) + str(self.seed)
        return hashlib.sha256(payload.encode()).hexdigest()[:16]

    def save(self, path: Path | str):
        p = Path(path)
        data = {
            "meta": {
                "name": "NxObfus Key",
                "version": self.version,
                "strategy": self.strategy_name,
                "seed": self.seed,
                "digest": self._digest,
            },
            "char_pool": self.char_pool,
            "source_pool": self.source_pool,
        }
        p.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    @classmethod
    def load(cls, path: Path | str):
        p = Path(path)
        raw = json.loads(p.read_text(encoding="utf-8"))
        meta = raw["meta"]
        inst = cls.__new__(cls)
        inst.version = meta["version"]
        inst.strategy_name = meta["strategy"]
        inst.seed = meta["seed"]
        inst.char_pool = raw["char_pool"]
        inst.source_pool = raw["source_pool"]
        inst._digest = meta["digest"]
        return inst
