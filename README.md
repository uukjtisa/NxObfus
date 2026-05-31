# NxObfus

**The honest successor to NxerEncrypt0r.**

Composable character-substitution obfuscation. Not encryption. Just obfuscation. Honestly named.

## Quick Start

```bash
# Windows
setup.bat
run.bat

# Linux
chmod +x setup.sh run.sh
./setup.sh
./run.sh
```

## GUI Overview

| Tab | Purpose |
|---|---|
| **Obfuscate** | Enter or load text → configure strategy chain + seed → obfuscate → copy or save |
| **Deobfuscate** | Enter or load obfuscated text → configure matching chain + seed → restore original |
| **Key Manager** | Generate `.nxob` key files, load existing ones, apply to either tab |

### File Processing

Click **Obfuscate File…** or **Deobfuscate File…** to process files directly:
- **Process Directly** — obfuscates/deobfuscates the file immediately and prompts to replace or save-as
- **Append to Input** — loads file content into the text area for manual editing

### Auto-Seed

If the seed field is empty when you obfuscate, deobfuscate, save a key, or process a file, a random seed is auto-generated and filled in.

## Strategies

| Strategy | How it works | Output |
|---|---|---|
| **Token** | Each character → prefixed token (e.g. `/xo042`) | Space-separated tokens |
| **Index** | Each character → shuffled character from pool | Continuous string |

Multiple rounds can be chained (e.g. Token → Index) for layered obfuscation.

## Character Pools

| Pool | Includes |
|---|---|
| **basic** | Letters (a-z, A-Z), digits (0-9), punctuation, common symbols |
| **extended** | Everything in basic + whitespace, currency, trademark, math, symbols, control chars |

## Key File Format (`.nxob`)

```json
{
  "meta": {
    "name": "NxObfus Config",
    "version": "2.1.0"
  },
  "seed": 42,
  "rounds": [
    ["token", "basic"],
    ["index", "extended"]
  ]
}
```

The seed + rounds are fully deterministic — the same input always produces the same output.

## API Usage

```python
from nxobfus import obfuscate, deobfuscate

rounds = [("token", "basic"), ("index", "basic")]
original = "Hello, World!"

obf = obfuscate(original, rounds, seed=42)
deobf = deobfuscate(obf, rounds, seed=42)
assert deobf == original
```

## Requirements

- Python 3.10+
- `ttkbootstrap` (installed by `setup.bat` / `setup.sh`)

## License

MIT
