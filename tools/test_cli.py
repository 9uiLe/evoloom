import tempfile
import unittest
from pathlib import Path

from shadcn_ios import (
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
            self.assertTrue(source_for(name).is_file())
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
            install(root, files)
            tokens = root / "Sources/ShadcnIOSCopied/Tokens/DesignTokens.swift"
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
            tokens = root / "Sources/ShadcnIOSCopied/Tokens/DesignTokens.swift"
            tokens.write_text("custom tokens")
            files = plan(root, ["input"])
            self.assertEqual(len(files), 1)
            install(root, files)
            self.assertEqual(tokens.read_text(), "custom tokens")

    def test_legacy_theme_requires_explicit_migration(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / ".shadcn-ios.json").write_text("{}")
            legacy = root / "Sources/ShadcnIOSCopied/Theme/Theme.swift"
            legacy.parent.mkdir(parents=True)
            legacy.write_text("custom theme")
            with self.assertRaisesRegex(InstallError, "Legacy Theme"):
                plan(root, ["button"])
            self.assertEqual(legacy.read_text(), "custom theme")

    def test_traversal_and_symlink(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            with self.assertRaisesRegex(InstallError, "Unsafe"):
                safe_destination(root, Path("../outside.swift"))
            (root / ".shadcn-ios.json").write_text("{}")
            outside = root.parent / "outside-target"
            (root / "Sources").symlink_to(outside)
            with self.assertRaisesRegex(InstallError, "Symlink"):
                plan(root, ["button"])


if __name__ == "__main__":
    unittest.main()
