"""Minimal offline regression tests for the read-only skill auditor."""
import importlib.util
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "audit_skills.py"
SPEC = importlib.util.spec_from_file_location("audit_skills", SCRIPT)
AUDITOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUDITOR)


class AuditTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.skill = self.root / "skills" / "example-skill"
        self.skill.mkdir(parents=True)
        (self.skill / "LICENSE.txt").write_text("Test fixture license\n", encoding="utf-8")
        (self.skill / "SKILL.md").write_text(
            "---\nname: example-skill\ndescription: Example test skill.\n---\n\n# Example\n", encoding="utf-8")

    def test_valid_fixture(self):
        report = AUDITOR.audit(self.root)
        self.assertEqual(report["count"], 1)
        self.assertEqual(report["issues"], [])
        self.assertEqual(len(report["skills"][0]["skill_sha256"]), 64)

    def test_reject_missing_frontmatter(self):
        (self.skill / "SKILL.md").write_text("# Missing metadata\n", encoding="utf-8")
        codes = {x["code"] for x in AUDITOR.audit(self.root)["issues"]}
        self.assertTrue({"frontmatter_missing", "name_missing", "description_missing"} <= codes)

    def test_report_broken_relative_link(self):
        with (self.skill / "SKILL.md").open("a", encoding="utf-8") as handle:
            handle.write("[missing](references/nope.md)\n")
        issues = AUDITOR.audit(self.root)["issues"]
        self.assertEqual([i["code"] for i in issues], ["link_missing"])
        self.assertEqual(issues[0]["severity"], "warning")

    def test_flags_duplicate_name(self):
        other = self.root / "skills" / "other-skill"
        other.mkdir()
        (other / "SKILL.md").write_text(
            "---\nname: example-skill\ndescription: Duplicate.\n---\n", encoding="utf-8")
        codes = {i["code"] for i in AUDITOR.audit(self.root)["issues"]}
        self.assertIn("name_duplicate", codes)
        self.assertIn("name_mismatch", codes)


    def test_ignores_links_in_fenced_examples(self):
        with (self.skill / "SKILL.md").open("a", encoding="utf-8") as handle:
            handle.write("\n~~~markdown\n[example](fake/path)\n~~~\n")
        self.assertEqual(AUDITOR.audit(self.root)["issues"], [])

    def test_cross_tier_collision_is_advisory(self):
        curated = self.root / "skills" / ".curated" / "openai-docs"
        system = self.root / "skills" / ".system" / "openai-docs"
        for path in (curated, system):
            path.mkdir(parents=True)
            (path / "LICENSE.txt").write_text("fixture\n")
            (path / "SKILL.md").write_text(
                "---\nname: openai-docs\ndescription: Sample.\n---\n")
        issues = [i for i in AUDITOR.audit(self.root)["issues"] if i["code"] == "name_shadowed"]
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0]["severity"], "warning")


if __name__ == "__main__":
    unittest.main()
