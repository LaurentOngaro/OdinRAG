"""Tests for OdinRAG public/private split safety guards and single-source config."""

from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = REPO_ROOT / "_Helpers" / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from diagnostic import audit_public_safety, publish_public  # noqa: E402
from lib.private_paths import load_private_paths  # noqa: E402
from lib.user_config import load_jsonc_file  # noqa: E402


def _extract_hook_regex(hook_path: Path) -> re.Pattern[str]:
    text = hook_path.read_text(encoding="utf-8")
    m = re.search(r"^personal_pattern='([^']+)'", text, re.MULTILINE)
    if not m:
        raise AssertionError(f"Could not find personal_pattern in {hook_path}")
    return re.compile(m.group(1))


class PublicSafetyTests(unittest.TestCase):
    """Verify consistency across private_paths.jsonc, audit, publish, and pre-push hook."""

    def test_private_links_from_manifest_are_included(self) -> None:
        links_data = load_jsonc_file(REPO_ROOT / "_Helpers" / "links.jsonc")
        expected_private_links = {
            str(entry["link"]).strip("/")
            for entry in links_data.get("links", [])
            if isinstance(entry, dict) and entry.get("scope") == "private"
        }
        cfg = load_private_paths(repo_root=REPO_ROOT)
        for link in expected_private_links:
            self.assertIn(link, cfg.strip_rules)
            self.assertIn(link, publish_public.STRIP_RULES)

    def test_forbidden_paths_rejected_by_audit_and_hook(self) -> None:
        hook_re = _extract_hook_regex(REPO_ROOT / "_Helpers" / "scripts" / "dev" / "hooks" / "pre-push")
        forbidden_samples = [
            "_Archives/README.md",
            "_Archives/_Private/docs/audits/004_audit_odinrag_repository_archived_2026-11-17.md",
            "nested/dir/_Private/secret.md",
            "nested/dir/_Archives/old.md",
            "_Private/planning/daily/J_2026-07-01.md",
            "code/projects/PVG03_RPG/source/main.odin",
            "code/projects/PVG02_Metroidvania/main.odin",
            "code/projects/Odin_Skeleton/main.odin",
            "odin-knowledge-base/courses/programvideogames/the-course-is-here/README.md",
            "odin-knowledge-base/docs/karl_zylinski/odin-book/01-introduction.md",
        ]
        violations = dict(audit_public_safety.find_violations(forbidden_samples))
        for sample in forbidden_samples:
            self.assertIn(sample, violations, f"audit_public_safety missed {sample}")
            self.assertRegex(sample, hook_re, f"pre-push hook missed {sample}")

    def test_public_paths_allowed_by_audit_and_hook(self) -> None:
        hook_re = _extract_hook_regex(REPO_ROOT / "_Helpers" / "scripts" / "dev" / "hooks" / "pre-push")
        public_samples = [
            "README.md",
            "AGENTS.md",
            "SOURCES.md",
            "code/projects/README - projects.md",
            "_Helpers/docs/001_folder_structure.md",
            "_Helpers/config/private_paths.jsonc",
            "odin-knowledge-base/docs/official/spec.md",
        ]
        violations = audit_public_safety.find_violations(public_samples)
        self.assertEqual(violations, [])
        for sample in public_samples:
            self.assertNotRegex(sample, hook_re, f"pre-push hook falsely matched {sample}")

    def test_allowed_readme_exception_in_audit(self) -> None:
        allowed = ["odin-knowledge-base/docs/karl_zylinski/odin-book/README.md"]
        self.assertEqual(audit_public_safety.find_violations(allowed), [])


if __name__ == "__main__":
    unittest.main()
