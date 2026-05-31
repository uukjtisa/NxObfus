"""
NxObfus — Core Engine
Composable multi-round obfuscation with named strategies.
"""

from typing import List, Tuple
from .strategies import TokenStrategy, IndexStrategy
from .keys import Keyfile
from . import charset


STRATEGY_MAP = {
    "token": TokenStrategy,
    "index": IndexStrategy,
}


def _resolve_pool(pool_name: str) -> List[str]:
    if pool_name == "basic":
        return charset.BASIC
    elif pool_name == "extended":
        return charset.EXTENDED
    else:
        raise ValueError(f"Unknown pool: {pool_name!r}. Use 'basic' or 'extended'.")


def obfuscate(text: str, rounds: List[Tuple[str, str]], seed: int | None = None) -> str:
    """
    Multi-round obfuscation. Applies rounds left-to-right.
    """
    result = text
    for strat_name, pool_name in rounds:
        pool = _resolve_pool(pool_name)
        strat_cls = STRATEGY_MAP[strat_name]
        strat = strat_cls(pool, seed=seed)
        result = strat.obfuscate(result)
    return result


def deobfuscate(text: str, rounds: List[Tuple[str, str]], seed: int | None = None) -> str:
    """
    Reverse multi-round obfuscation. Applies rounds right-to-left.
    Each strategy is self-inverting, but order matters.
    """
    result = text
    for strat_name, pool_name in reversed(rounds):
        pool = _resolve_pool(pool_name)
        strat_cls = STRATEGY_MAP[strat_name]
        strat = strat_cls(pool, seed=seed)
        result = strat.deobfuscate(result)
    return result


def generate_key(key_path, strategy_name: str, pool_name: str, seed: int | None = None):
    pool = _resolve_pool(pool_name)
    strat_cls = STRATEGY_MAP[strategy_name]
    strat = strat_cls(pool, seed=seed)
    key = Keyfile(
        strategy_name=strategy_name,
        char_pool=strat.char_pool,
        source_pool=strat.source_pool if hasattr(strat, "source_pool") else strat.tokens,
        seed=seed,
    )
    key.save(key_path)
    return key
