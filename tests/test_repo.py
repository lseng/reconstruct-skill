import json
import os
import re
import unittest

from _load import ROOT

SKILLS = ["reconstruct-recon", "reconstruct-architect", "reconstruct-build",
          "reconstruct-test", "reconstruct-diff", "reconstruct-sweep"]

# REA tools the skills name. Keep in step with the rea-agents version in README.
REA_TOOLS = {
    "analyze_javascript_application", "list_browser_targets", "capture_browser_scenario",
    "capture_native_ui_scenario", "capture_process_scenario", "open_binary",
    "binary_overview", "project_apple_application_graph", "project_android_application_graph",
    "analyze_swift_types", "inspect_android_package", "trace_application_feature",
    "inspect_sqlite_database", "record_unknown", "inspect_asset_catalog",
    "compare_web_captures", "compare_process_captures", "compare_web_screenshots",
    "verify_reconstruction", "build_reconstruction_obligation_ledger",
    "evaluate_reconstruction_coverage",
}
NOT_TOOLS = {"created_at", "updated_at", "node_modules"}


def frontmatter(path):
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    return (m.group(1) if m else ""), text


class Repo(unittest.TestCase):
    def test_skill_folders_at_the_root(self):
        found = sorted(d for d in os.listdir(ROOT)
                       if os.path.isfile(os.path.join(ROOT, d, "SKILL.md")))
        self.assertEqual(found, sorted(SKILLS))

    def test_frontmatter_name_and_description(self):
        for s in SKILLS:
            fm, text = frontmatter(os.path.join(ROOT, s, "SKILL.md"))
            self.assertIn("name: %s\n" % s, fm + "\n", s)
            self.assertRegex(fm, r"description: ", s)
            self.assertGreater(len(fm), 200, "%s description is too thin" % s)

    def test_plugin_manifest(self):
        with open(os.path.join(ROOT, ".claude-plugin", "plugin.json")) as fh:
            plugin = json.load(fh)
        self.assertEqual(plugin["name"], "reconstruct-skill")
        self.assertEqual(plugin["skills"], "./")
        with open(os.path.join(ROOT, ".claude-plugin", "marketplace.json")) as fh:
            market = json.load(fh)
        self.assertEqual(market["plugins"][0]["name"], "reconstruct-skill")

    def test_readme_lists_every_skill(self):
        with open(os.path.join(ROOT, "README.md"), encoding="utf-8") as fh:
            readme = fh.read()
        for s in SKILLS:
            self.assertIn("`/%s`" % s, readme)

    def test_backticked_rea_tools_are_known(self):
        # Catches a renamed or misspelled REA tool in the instructions.
        unknown = set()
        for s in SKILLS:
            _, text = frontmatter(os.path.join(ROOT, s, "SKILL.md"))
            for name in re.findall(r"`([a-z]+(?:_[a-z]+){1,})`", text):
                if name not in REA_TOOLS and name not in NOT_TOOLS:
                    unknown.add((s, name))
        self.assertEqual(unknown, set())

    def test_every_skill_honours_the_clean_room(self):
        for s in SKILLS:
            _, text = frontmatter(os.path.join(ROOT, s, "SKILL.md"))
            self.assertRegex(text.lower(), r"clean.room|private endpoints|never paste|leak", s)

    def test_stages_that_can_use_rea_check_the_mode_gate(self):
        for s in ("reconstruct-build", "reconstruct-test", "reconstruct-diff",
                  "reconstruct-sweep"):
            _, text = frontmatter(os.path.join(ROOT, s, "SKILL.md"))
            self.assertIn("Read `reconstruct/scope.md` first", text, s)

    def test_scripts_are_called_through_the_skill_dir(self):
        # A bare "python3 parity.py" only works from inside the skill folder.
        bare = []
        for s in SKILLS:
            _, text = frontmatter(os.path.join(ROOT, s, "SKILL.md"))
            for line in text.splitlines():
                if re.search(r"python3 \S*\.py", line) and "CLAUDE_SKILL_DIR" not in line \
                        and "$T/" not in line:
                    bare.append((s, line.strip()))
        self.assertEqual(bare, [])

    def test_no_em_dashes_anywhere(self):
        bad = []
        for dirpath, dirnames, filenames in os.walk(ROOT):
            dirnames[:] = [d for d in dirnames if d not in (".git", "__pycache__")]
            for fn in filenames:
                if fn.endswith((".md", ".py", ".json", ".ts", ".csv")):
                    path = os.path.join(dirpath, fn)
                    with open(path, encoding="utf-8") as fh:
                        if chr(0x2014) in fh.read():
                            bad.append(os.path.relpath(path, ROOT))
        self.assertEqual(bad, [])


if __name__ == "__main__":
    unittest.main()
