"""
NxObfus — Next Obfuscator
The honest successor to NxerEncrypt0r.

Provides composable character-substitution obfuscation.
Not encryption. Just obfuscation. Honestly named. ✨
"""

__version__ = "2.0.0"

from .core import obfuscate, deobfuscate, generate_key
from .strategies import TokenStrategy, IndexStrategy
from .keys import Keyfile
from .charset import BASIC, EXTENDED

__all__ = [
    "obfuscate",
    "deobfuscate",
    "generate_key",
    "TokenStrategy",
    "IndexStrategy",
    "Keyfile",
    "BASIC",
    "EXTENDED",
]
