import io
import os
import unittest
from contextlib import redirect_stdout
from unittest import mock

from _load import load

doctor = load("reconstruct-recon", "doctor")


class Doctor(unittest.TestCase):
    def test_node_versions_follow_rea_engines(self):
        for ok in ("v22.19.0", "v22.20.1", "v24.11.0", "v26.0.0", "v27.1.0"):
            self.assertTrue(doctor.node_supported(ok), ok)
        for bad in ("v20.11.0", "v22.18.0", "v23.5.0", "v24.10.0", "v25.9.0", "", None):
            self.assertFalse(doctor.node_supported(bad), bad)

    def test_nothing_installed_prints_every_fix(self):
        env = {"PATH": "/nonexistent", "CLAUDE_CONFIG_DIR": "/nonexistent",
               "HOME": "/nonexistent"}
        with mock.patch.dict(os.environ, env, clear=True), \
                mock.patch.object(doctor, "GHIDRA_BREW", "/nonexistent"):
            out = io.StringIO()
            with redirect_stdout(out):
                code = doctor.main([])
        text = out.getvalue()
        self.assertEqual(code, 1)
        self.assertIn("MISSING  [mode B]    node not found", text)
        for key in ("node", "rea", "skill", "ghidra", "java"):
            self.assertIn(doctor.FIX[key], text, key)

    def test_optional_gaps_do_not_fail(self):
        results = [("python", "need", True, ""), ("rea", "mode B", None, "skipped"),
                   ("ghidra", "optional", False, "not set")]
        with mock.patch.object(doctor, "checks", return_value=results):
            with redirect_stdout(io.StringIO()):
                self.assertEqual(doctor.main(["--offline"]), 0)

    def test_empty_or_relative_ghidra_dir_is_flagged(self):
        # REA refuses to start on either, so they must not read as "not set".
        for value in ("", "ghidra"):
            with mock.patch.dict(os.environ, {"GHIDRA_INSTALL_DIR": value}):
                key, level, ok, detail = doctor.check_ghidra()
            self.assertFalse(ok, value)
            self.assertIn("refuse to start", detail, value)

    def test_fixes_use_the_pinned_rea(self):
        self.assertIn("npx -y %s mcp" % doctor.REA, doctor.FIX["rea"])
        self.assertIn(doctor.REA, doctor.FIX["skill"])


if __name__ == "__main__":
    unittest.main()
