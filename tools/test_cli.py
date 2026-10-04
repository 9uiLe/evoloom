import tempfile
import unittest
from pathlib import Path

from evoloom import (
    REGISTRY,
    InstallError,
    install,
    plan,
    resolve,
    safe_destination,
    source_for,
)


class DistributionTests(unittest.TestCase):
    def test_registry_sources_and_order(self):
        for name in REGISTRY:
            source = source_for(name)
            self.assertTrue(source.is_file())
            self.assertNotIn("import Evoloom", source.read_text())
            self.assertNotIn("import AppMacros", source.read_text())
            self.assertNotIn("@AutoEquatableView", source.read_text())
        self.assertEqual(resolve(["empty"]), ["tokens", "button", "empty"])

    def test_unknown_and_cycle(self):
        with self.assertRaisesRegex(InstallError, "Unknown"):
            resolve(["missing"])
        with self.assertRaisesRegex(InstallError, "cycle"):
            resolve(["a"], {"a": {"dependencies": ["b"]}, "b": {"dependencies": ["a"]}})

    def test_dry_run_and_changed_file_protection(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            files = plan(root, ["button"], initialize=True)
            self.assertFalse((root / "Sources").exists())
            self.assertEqual(
                files[Path(".evoloom.json")],
                b'{"source": "evoloom", "copyRoot": "Sources/EvoloomCopied"}\n',
            )
            self.assertIn(
                b"Copyright (c) 2026 ShadcnIOS contributors",
                files[Path("EVOLOOM-LICENSE")],
            )
            install(root, files)
            tokens = root / "Sources/EvoloomCopied/Tokens/DesignTokens.swift"
            tokens.write_text("custom tokens")
            with self.assertRaisesRegex(InstallError, "Conflict"):
                plan(root, ["button"])
            self.assertEqual(tokens.read_text(), "custom tokens")

    def test_add_requires_init(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            with self.assertRaisesRegex(InstallError, "run init first"):
                plan(root, ["button"])

    def test_add_reuses_custom_tokens(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            install(root, plan(root, [], initialize=True))
            tokens = root / "Sources/EvoloomCopied/Tokens/DesignTokens.swift"
            tokens.write_text("custom tokens")
            files = plan(root, ["input"])
            self.assertEqual(len(files), 1)
            install(root, files)
            self.assertEqual(tokens.read_text(), "custom tokens")

    def test_legacy_installation_requires_manual_migration(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            legacy_config = root / ".shadcn-ios.json"
            legacy_config.write_text("custom config")
            legacy = root / "Sources/ShadcnIOSCopied/Theme/Theme.swift"
            legacy.parent.mkdir(parents=True)
            legacy.write_text("custom theme")
            for initialize in (False, True):
                with self.assertRaisesRegex(InstallError, "Legacy ShadcnIOS"):
                    plan(root, ["button"], initialize=initialize, overwrite=True)
            self.assertEqual(legacy_config.read_text(), "custom config")
            self.assertEqual(legacy.read_text(), "custom theme")
            self.assertFalse((root / ".evoloom.json").exists())

    def test_legacy_config_alone_blocks_new_install(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            legacy_config = root / ".shadcn-ios.json"
            legacy_config.write_text("custom config")
            with self.assertRaisesRegex(InstallError, "Legacy ShadcnIOS"):
                plan(root, ["button"], initialize=True, overwrite=True)
            self.assertEqual(legacy_config.read_text(), "custom config")
            self.assertFalse((root / "Sources").exists())

    def test_legacy_copy_root_is_rejected_even_with_new_config(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / ".evoloom.json").write_text("{}")
            legacy = root / "Sources/ShadcnIOSCopied/Tokens/DesignTokens.swift"
            legacy.parent.mkdir(parents=True)
            legacy.write_text("custom tokens")
            with self.assertRaisesRegex(InstallError, "Legacy ShadcnIOS"):
                plan(root, ["button"])
            self.assertEqual(legacy.read_text(), "custom tokens")

    def test_traversal_and_symlink(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            with self.assertRaisesRegex(InstallError, "Unsafe"):
                safe_destination(root, Path("../outside.swift"))
            (root / ".evoloom.json").write_text("{}")
            outside = root.parent / "outside-target"
            (root / "Sources").symlink_to(outside)
            with self.assertRaisesRegex(InstallError, "Symlink"):
                plan(root, ["button"])


if __name__ == "__main__":
    unittest.main()
