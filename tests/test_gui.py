import sys
sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent.parent))

import tkinter as tk
import pytest


@pytest.fixture(scope="module")
def tk_root():
    root = tk.Tk()
    root.withdraw()
    yield root
    root.destroy()


class TestGUIModules:
    def test_import_gui_theme(self):
        from nxobfus.gui_theme import get_style, refresh_style, is_dark, palette
        assert callable(get_style)
        assert callable(refresh_style)
        assert callable(is_dark)
        assert callable(palette)

    def test_import_gui_helpers(self):
        from nxobfus.gui_helpers import load_file_dialog, save_file_dialog, copy_to_clipboard
        assert callable(load_file_dialog)
        assert callable(save_file_dialog)
        assert callable(copy_to_clipboard)

    def test_import_gui_strategy_builder(self):
        from nxobfus.gui_strategy_builder import StrategyBuilder, RoundRow, STRATEGIES, POOLS
        assert STRATEGIES == ["token", "index"]
        assert POOLS == ["basic", "extended"]

    def test_import_gui_preview(self):
        from nxobfus.gui_preview import CharsetPreview
        assert CharsetPreview is not None

    def test_import_gui_log(self):
        from nxobfus.gui_log import CommandLog
        assert CommandLog is not None

    def test_import_core_functions(self):
        from nxobfus import obfuscate, deobfuscate, generate_key
        assert callable(obfuscate)
        assert callable(deobfuscate)
        assert callable(generate_key)

    def test_strategy_builder_construction(self, tk_root):
        from nxobfus.gui_strategy_builder import StrategyBuilder
        builder = StrategyBuilder(tk_root)
        assert len(builder.rows) == 1
        rounds = builder.get_rounds()
        assert len(rounds) == 1
        assert rounds[0][0] in ("token", "index")
        assert rounds[0][1] in ("basic", "extended")

    def test_strategy_builder_add_remove(self, tk_root):
        from nxobfus.gui_strategy_builder import StrategyBuilder
        builder = StrategyBuilder(tk_root)
        builder._add_row()
        assert len(builder.rows) == 2
        builder._remove_row(builder.rows[-1])
        assert len(builder.rows) == 1

    def test_strategy_builder_set_rounds(self, tk_root):
        from nxobfus.gui_strategy_builder import StrategyBuilder
        builder = StrategyBuilder(tk_root)
        rounds = [("token", "basic"), ("index", "extended"), ("token", "extended")]
        builder.set_rounds(rounds)
        assert len(builder.rows) == 3
        assert builder.get_rounds() == rounds

    def test_dark_mode_toggle(self):
        from nxobfus.gui_theme import is_dark, palette
        assert is_dark() is True
        p = palette()
        assert "accent" in p
        assert "bg" in p
        assert "text" in p

    def test_charset_preview_basic(self, tk_root):
        from nxobfus.gui_preview import CharsetPreview
        preview = CharsetPreview(tk_root)
        preview.show_pool("basic")
        preview.show_pool("extended")

    def test_command_log(self, tk_root):
        from nxobfus.gui_log import CommandLog
        log = CommandLog(tk_root)
        log.log("Test message")
        log.clear()


class TestCoreObfuscation:
    def test_roundtrip_basic(self):
        from nxobfus import obfuscate, deobfuscate
        rounds = [("token", "basic"), ("index", "basic")]
        original = "Hello,World!123"
        obf = obfuscate(original, rounds, seed=42)
        deobf = deobfuscate(obf, rounds, seed=42)
        assert deobf == original

    def test_roundtrip_extended(self):
        from nxobfus import obfuscate, deobfuscate
        rounds = [("token", "extended"), ("index", "extended")]
        original = "Hello, World!\n123\t₱€©™"
        obf = obfuscate(original, rounds, seed=1337)
        deobf = deobfuscate(obf, rounds, seed=1337)
        assert deobf == original

    def test_keyfile_roundtrip(self, tmp_path):
        from nxobfus import generate_key, obfuscate, deobfuscate
        from nxobfus.keys import NxObfusConfig
        key_path = tmp_path / "test_key.nxob"
        generate_key(key_path, "token", "basic", seed=42)
        assert key_path.exists()

        config = NxObfusConfig.load(key_path)
        assert config.rounds == [("token", "basic")]
        assert config.seed == 42
        assert config.version == "2.1.0"

        original = "TestKey123!"
        rounds = config.rounds
        obf = obfuscate(original, rounds, seed=config.seed)
        deobf = deobfuscate(obf, rounds, seed=config.seed)
        assert deobf == original

    def test_config_save_load_roundtrip(self, tmp_path):
        from nxobfus.keys import NxObfusConfig
        config = NxObfusConfig(seed=99, rounds=[("token", "basic"), ("index", "extended")])
        path = tmp_path / "test_config.nxob"
        config.save(path)
        assert path.exists()

        loaded = NxObfusConfig.load(path)
        assert loaded.seed == 99
        assert loaded.rounds == [("token", "basic"), ("index", "extended")]
        assert loaded.version == "2.1.0"
