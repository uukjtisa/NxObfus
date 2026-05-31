"""
NxObfus — Config File (replaces v2.0.0 Keyfile)
Saves/loads seed + strategy chain as a portable .nxob config.
"""

import json
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import List, Tuple


VERSION = "2.1.0"


@dataclass
class NxObfusConfig:
    seed: int | None = None
    rounds: List[Tuple[str, str]] = field(default_factory=list)
    version: str = VERSION

    def save(self, path: Path | str):
        p = Path(path)
        data = {
            "meta": {
                "name": "NxObfus Config",
                "version": self.version,
            },
            "seed": self.seed,
            "rounds": [[s, p] for s, p in self.rounds],
        }
        p.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    @classmethod
    def load(cls, path: Path | str):
        p = Path(path)
        raw = json.loads(p.read_text(encoding="utf-8"))
        rounds_raw = raw.get("rounds", [])
        return cls(
            version=raw.get("meta", {}).get("version", VERSION),
            seed=raw.get("seed"),
            rounds=[(s, p) for s, p in rounds_raw],
        )
