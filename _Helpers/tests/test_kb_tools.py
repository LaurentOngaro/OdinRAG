"""Tests for KB frontmatter injection, HTML->MD tagging, and index generation."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = REPO_ROOT / "_Helpers" / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from fixes import add_kb_frontmatter, format_kb_md  # noqa: E402
from indexing import build_kb_index  # noqa: E402
from lib import kb_frontmatter  # noqa: E402
from lib.html2md import _tag_odin_code_blocks  # noqa: E402


class KbFrontmatterTests(unittest.TestCase):
    """Verify deterministic frontmatter generation and idempotence."""

    def test_inject_and_idempotence(self) -> None:
        sample = (
            "# Temporary Allocator: Your First Arena\n\n"
            "2025-05-12\n\n"
            "Using `context.temp_allocator` and Raylib.\n\n"
            ">Source: https://zylinski.se/posts/temporary-allocator-your-first-arena\n"
        )
        fake_path = REPO_ROOT / "odin-knowledge-base" / "docs" / "karl_zylinski" / "temporary-allocator-your-first-arena.md"
        result, changed = kb_frontmatter.ensure_kb_frontmatter(sample, file_path=fake_path)
        self.assertTrue(changed)
        self.assertIn('title: "Temporary Allocator: Your First Arena"', result)
        self.assertIn("date: 2025-05-12", result)
        self.assertIn('source: "https://zylinski.se/posts/temporary-allocator-your-first-arena"', result)
        self.assertIn("source/zylinski", result)
        self.assertIn("topic/allocator", result)
        self.assertIn("topic/raylib", result)

        # Second pass must be a no-op
        result2, changed2 = kb_frontmatter.ensure_kb_frontmatter(result, file_path=fake_path)
        self.assertFalse(changed2)
        self.assertEqual(result, result2)

    def test_ordinal_date_parsing(self) -> None:
        sample = "# 2D Cloth Simulation\n\n26th January 2025 • 23 min read\n\nCloth in raylib.\n"
        fake_path = REPO_ROOT / "odin-knowledge-base" / "docs" / "marianpekar" / "2d-cloth.md"
        result, changed = kb_frontmatter.ensure_kb_frontmatter(sample, file_path=fake_path)
        self.assertTrue(changed)
        self.assertIn("date: 2025-01-26", result)
        self.assertIn("source/marianpekar", result)

    def test_iter_kb_targets_skips_readme_and_book(self) -> None:
        docs_dir = REPO_ROOT / "odin-knowledge-base" / "docs"
        targets = add_kb_frontmatter.iter_kb_targets(docs_dir)
        names = {p.name for p in targets}
        self.assertNotIn("README.md", names)
        self.assertNotIn("INDEX.md", names)
        self.assertFalse(any("odin-book" in p.parts for p in targets))


class Html2MdAndIndexTests(unittest.TestCase):
    """Verify code fence tagging and INDEX.md builder invariants."""

    def test_tag_odin_code_blocks_preserves_existing_and_closing_fences(self) -> None:
        raw = "Intro\n\n```\nmain :: proc() {}\n```\n\n```bash\necho hi\n```"
        tagged = _tag_odin_code_blocks(raw)
        self.assertEqual(tagged, "Intro\n\n```odin\nmain :: proc() {}\n```\n\n```bash\necho hi\n```")

    def test_format_markdown_table_aligns_columns(self) -> None:
        lines = build_kb_index.format_markdown_table(["A", "Longer"], [["1", "x"], ["222", "yy"]])
        widths = [len(line) for line in lines]
        self.assertEqual(len(set(widths)), 1)

    def test_index_date_stripping_is_day_invariant(self) -> None:
        c1 = build_kb_index.build_index_content(existing_manual="## Custom\n", index_date="2026-10-01")
        c2 = build_kb_index.build_index_content(existing_manual="## Custom\n", index_date="2026-11-17")
        self.assertEqual(build_kb_index._strip_date_line(c1), build_kb_index._strip_date_line(c2))

    def test_fix_closing_fences_repairs_broken_odin_closers(self) -> None:
        broken = "Intro\n\n```odin\nx := 1\n```odin\n\nText\n"
        fixed, changed = format_kb_md.fix_closing_fences(broken)
        self.assertTrue(changed)
        self.assertEqual(fixed, "Intro\n\n```odin\nx := 1\n```\n\nText\n")
        fixed2, changed2 = format_kb_md.fix_closing_fences(fixed)
        self.assertFalse(changed2)
        self.assertEqual(fixed2, fixed)


if __name__ == "__main__":
    unittest.main()
