import sys
sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent.parent))

from nxobfus import obfuscate, deobfuscate, BASIC, EXTENDED

def test_roundtrip_basic():
    rounds = [("token", "basic"), ("index", "basic")]
    original = "Hello,World!123"
    obf = obfuscate(original, rounds, seed=42)
    deobf = deobfuscate(obf, rounds, seed=42)
    print(f"Original: {original!r}")
    print(f"Obf:      {obf!r}")
    print(f"Deobf:    {deobf!r}")
    assert deobf == original, f"Mismatch! {deobf!r} != {original!r}"
    print("[PASS] Basic roundtrip passed")

def test_roundtrip_extended():
    rounds = [("token", "extended"), ("index", "extended")]
    original = "Hello, World!\n123\t₱€©™"
    obf = obfuscate(original, rounds, seed=1337)
    deobf = deobfuscate(obf, rounds, seed=1337)
    # Safe print for Windows cp1252 console
    print("Original:", ascii(original))
    print("Obf:     ", ascii(obf))
    print("Deobf:   ", ascii(deobf))
    assert deobf == original, f"Mismatch! {ascii(deobf)} != {ascii(original)}"
    print("[PASS] Extended roundtrip passed")

def test_single_index():
    rounds = [("index", "basic")]
    original = "Test123!"
    obf = obfuscate(original, rounds, seed=7)
    deobf = deobfuscate(obf, rounds, seed=7)
    assert deobf == original
    print("[PASS] Single index roundtrip passed")

def test_single_token():
    rounds = [("token", "extended")]
    original = "Obfus\tcation"
    obf = obfuscate(original, rounds, seed=99)
    deobf = deobfuscate(obf, rounds, seed=99)
    assert deobf == original
    print("[PASS] Single token roundtrip passed")

if __name__ == "__main__":
    test_roundtrip_basic()
    test_roundtrip_extended()
    test_single_index()
    test_single_token()
    print("\n[DONE] All tests passed! NxObfus is functional.")
