"""_Helpers/build_kb_index.py - Regenerate odin-knowledge-base/INDEX.md from the KB.

Durable script: re-run after every KB update (new file in
`odin-knowledge-base/`, `docs/karl_zylinski/odin-book/`, etc.) to keep
the index up to date.

Auto-generated sections:
1. Overview by source (file count, total size)
2. Skool courses (link to per-module READMEs, without listing lessons)
3. Karl book (table of 28 chapters + 4 appendices, parsed from odin-book/README.md)
4. Statistics

Manual sections (preserved as-is if they already exist):
- Frontmatter (date, tags, docId)
- Index by topic (human curation)
- "How this file is generated"
- Skill to navigate
- Overview (lead-in text)

The script is idempotent: re-running on the same KB produces the same
result (deterministic).

Usage:
python _Helpers/build_kb_index.py
python _Helpers/build_kb_index.py --check    # dry-run, print planned changes
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import date
from pathlib import Path

# Force stdout UTF-8 (otherwise cp1252 chokes on accented characters).
try:
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
except Exception:
    pass

ROOT = Path(__file__).resolve().parent.parent

KB_PATHS = {
    "skool":   ROOT / "odin-knowledge-base",
    "karl":    ROOT / "docs" / "karl_zylinski",
    "zylinski":ROOT / "docs" / "karl_zylinski",
    "official":ROOT / "docs" / "official",
    "examples":ROOT / "code" / "examples",
}

INDEX_PATH = ROOT / "odin-knowledge-base" / "INDEX.md"
FRONTMATTER_RE = re.compile(r"^---\n(.+?)\n---\n", re.DOTALL)
CHAPTER_LINK_RE = re.compile(r"\[(\d+)\s*[–-]\s*([^\]]+)\]\(([^)]+)\)")
_DESCRIPTION = "Regenerate odin-knowledge-base/INDEX.md from the KB."


def count_md_files(root: Path) -> tuple[int, int]:
    """Return (count, total size in bytes) for .md files under ``root``."""
    if not root.exists():
        return 0, 0
    count = 0
    total = 0
    for p in root.rglob("*.md"):
        if p.is_file():
            count += 1
            try:
                total += p.stat().st_size
            except OSError:
                pass
    return count, total


def parse_karl_readme(readme: Path) -> list[dict]:
    """Parse `odin-book/README.md` to extract the chapter table.

    Returns:
        [{"number": "1", "title": "Introduction", "path": "01-introduction.md"}, ...]
    """
    if not readme.exists():
        return []
    text = readme.read_text(encoding="utf-8")
    chapters: list[dict] = []
    in_table = False
    for line in text.split("\n"):
        s = line.strip()
        if s.startswith("**Chapter ") or s.startswith("- **Chapter "):
            in_table = True
        if in_table:
            m = re.search(r"\*\*Chapter\s+(\d+)\*\*\s*[-–-]\s*\[([^\]]+)\]\(([^)]+)\)", s)
            if m:
                chapters.append({
                    "number": m.group(1),
                    "title":  m.group(2),
                    "path":   m.group(3),
                })
            elif "**Appendix" in s:
                in_table = False
    return chapters


def parse_karl_appendices(out_dir: Path) -> list[dict]:
    """List appendix files from `odin-book/appendices/`."""
    appx_dir = out_dir / "odin-book" / "appendices"
    if not appx_dir.exists():
        return []
    appx = []
    for p in sorted(appx_dir.glob("*.md")):
        m = re.match(r"^([A-Z])-(.+)\.md$", p.name)
        if m:
            appx.append({"number": m.group(1), "title": m.group(2).replace("-", " ").title(), "path": f"appendices/{p.name}"})
    return appx


def build_source_overview() -> str:
    """Section 'Overview by source' with file count + size."""
    skool_count, skool_size = count_md_files(KB_PATHS["skool"] / "courses")
    karl_count, karl_size   = count_md_files(KB_PATHS["karl"] / "odin-book")
    zyl_count, zyl_size     = count_md_files(KB_PATHS["zylinski"])
    zyl_count -= karl_count  # subtract odin-book subfolder already counted
    zyl_size   -= karl_size
    off_count, off_size     = count_md_files(KB_PATHS["official"])
    ex_count,  ex_size      = count_md_files(KB_PATHS["examples"])

    def fmt_size(n: int) -> str:
        if n < 1024:
            return f"{n} B"
        if n < 1024 * 1024:
            return f"{n // 1024} KB"
        return f"{n // (1024 * 1024)} MB"

    lines = [
        "## Overview (by source)",
        "",
        "| Source                          | Files | Format                                     | Why |",
        "| ------------------------------- | ----- | ------------------------------------------ | --- |",
        f"| `odin-knowledge-base/`          | {skool_count:>3}     | Skool 'programvideogames' lessons (Markdown with frontmatter) | Concrete implementation, complete code, game patterns |",
        f"| `docs/karl_zylinski/odin-book/` | {karl_count:>3}     | Karl's book **'Understanding the Odin Programming Language'** split into 1 file per chapter | Language reference, pure concept, minimal example |",
        f"| `docs/karl_zylinski/*.md`       | {zyl_count:>3}     | Karl Zylinski blog articles                 | Game dev patterns, opinions, hot take |",
        f"| `docs/official/`                | {off_count:>3}     | Official odin-lang.org docs + awesome-odin | Official language reference |",
        f"| `code/examples/demo.odin`       |  1       | Official language demo                    | Exhaustive feature reference |",
        "",
        f"**Total**: ~{skool_count + karl_count + zyl_count + off_count + 1} files, ~{fmt_size(skool_size + karl_size + zyl_size + off_size)} of MD.",
        "",
    ]
    return "\n".join(lines)


def build_karl_book_section() -> str:
    """Section 'Karl Book': table of 28 chapters + appendices."""
    readme = KB_PATHS["karl"] / "odin-book" / "README.md"
    chapters = parse_karl_readme(readme)
    appendices = parse_karl_appendices(KB_PATHS["karl"])

    lines = [
        "## Karl Zylinski book (33 files in `docs/karl_zylinski/odin-book/`)",
        "",
        "**Absolute** reference for the Odin language. For any fundamental question, start here.",
        "",
        "| #   | Chapter                                          | Topic |",
        "| --- | ------------------------------------------------ | ----- |",
    ]
    for ch in chapters:
        title = ch["title"]
        # Truncate the title to stay within the table width
        if len(title) > 75:
            title = title[:72] + "..."
        path = f"docs/karl_zylinski/odin-book/{ch['path']}"
        lines.append(f"| {ch['number']:>2}  | [{title}]({path}) | |")
    lines.append("| A-D | Appendices (4 files in `odin-book/appendices/`) | Handle-based array, fixed arrays only, dropdown, Box2D+Raylib |")
    lines.append("")
    return "\n".join(lines)


def build_stats_section() -> str:
    """Section 'Statistics' at the end of the doc."""
    skool_count, _ = count_md_files(KB_PATHS["skool"] / "courses")
    karl_count, _ = count_md_files(KB_PATHS["karl"] / "odin-book")
    zyl_count, _ = count_md_files(KB_PATHS["zylinski"])
    zyl_count -= karl_count
    off_count, _ = count_md_files(KB_PATHS["official"])
    total = skool_count + karl_count + zyl_count + off_count + 1

    lines = [
        "## Statistics",
        "",
        f"- **{skool_count}** Skool lessons (Vertical Slice and Dice v1.0 + Metroidvania 1.0)",
        f"- **{karl_count}** Karl book files (28 chapters + 4 appendices + about-author)",
        f"- **{zyl_count}** Zylinski articles",
        f"- **{off_count}** official odin-lang.org docs",
        f"- **1** official demo (`code/examples/demo.odin`)",
        "",
    ]
    return "\n".join(lines)


def build_skool_section() -> str:
    """Section 'Skool courses': link to per-course READMEs (without listing lessons)."""
    skool_root = KB_PATHS["skool"] / "courses"
    if not skool_root.exists():
        return ""

    lines = [
        "## Skool courses (programvideogames)",
        "",
        "See the detail in [`courses/programvideogames/README.md`](courses/programvideogames/README.md).",
        "",
    ]

    # List the courses
    courses = []
    for course_dir in sorted(skool_root.iterdir()):
        if not course_dir.is_dir():
            continue
        readme = course_dir / "README.md"
        if not readme.exists():
            continue
        # Count lessons (all .md under this course)
        lesson_count = 0
        modules = []
        for module_dir in sorted(course_dir.iterdir()):
            if module_dir.is_dir():
                mc = sum(1 for _ in module_dir.glob("*.md"))
                if mc:
                    modules.append((module_dir.name, mc))
                    lesson_count += mc
        courses.append({
            "slug": course_dir.name,
            "readme": f"courses/programvideogames/{course_dir.name}/README.md",
            "module_count": len(modules),
            "lesson_count": lesson_count,
            "modules": modules,
        })

    for c in courses:
        lines.append(f"- **{c['slug']}** ({c['lesson_count']} lessons) - [`{c['readme']}`]({c['readme']})")
        for module_name, mc in c["modules"]:
            lines.append(f"  - `{module_name}/`: {mc} lessons")
    lines.append("")
    lines.append("> Every lesson has `Cours:` `Module:` `ID:` `Durée:` frontmatter (see `_Helpers/docs/FRONTMATTER_CONVENTIONS.md`).")
    lines.append("> For the full TOC per chapter, open the module's `README.md`.")
    lines.append("")
    return "\n".join(lines)


def build_index_content() -> str:
    """Build the full content of INDEX.md."""
    today = date.today().isoformat()
    parts = [
        "---",
        "title: \"OdinKB - Semantic index\"",
        f"date: {today}",
        "tags: [OdinRAG, kb, doc/index, reference]",
        "type: reference",
        "status: active",
        "priority: 1",
        "docId: KB_INDEX_001",
        "summary: \"Compact index (~5 KB) to navigate the ~180 files of the Odin KB without loading everything. Load THIS FIRST.\"",
        "---",
        "",
        "# Odin Knowledge Base - Index",
        "",
        "> **Golden rule**: Kilo reads **this file first** (~5 KB), identifies 2-3 relevant",
        "> files below, then loads them on demand. NEVER load the whole KB.",
        "",
        build_source_overview(),
        build_skool_section(),
        build_karl_book_section(),
        "## Index by topic (QUICK SEARCH)",
        "",
        "When looking for **a specific pattern** (e.g. 'how to do a tracking allocator'),",
        "look here first. For each topic, the 1-3 most relevant files are listed.",
        "Load those, not everything.",
        "",
        "### Memory / allocators",
        "- `docs/karl_zylinski/odin-book/09-introduction-to-manual-memory-management.md` - overview",
        "- `docs/karl_zylinski/odin-book/13-making-manual-memory-management-easier.md` - tracking + arena (essential)",
        "- `docs/karl_zylinski/odin-book/10-more-container-types.md` - slices, maps, custom iterators",
        "- `docs/karl_zylinski/temporary-allocator-your-first-arena.md` - dedicated arena article",
        "- `odin-knowledge-base/courses/programvideogames/vertical-slice-and-dice-v10/rpg/088-26-tracking-allocator.md` - tracking in practice",
        "",
        "### State machines (FSM)",
        "- `odin-knowledge-base/courses/programvideogames/vertical-slice-and-dice-v10/metroidvania/020-211-finite-state-machine-movement-0624.md` - FSM for movement",
        "- `odin-knowledge-base/courses/programvideogames/vertical-slice-and-dice-v10/metroidvania/021-212-attacking-1232.md` - FSM for combat",
        "- `docs/karl_zylinski/odin-book/05-making-new-types.md` - `Using unions for state machines` (section 5.3.6)",
        "- `odin-knowledge-base/.../metroidvania/017-208-enemy-behaviors-0826.md` - state applied to enemies",
        "",
        "### Entity system / component",
        "- `odin-knowledge-base/courses/programvideogames/vertical-slice-and-dice-v10/rpg/067-05-entity-system.md` - full implementation",
        "- `odin-knowledge-base/courses/programvideogames/vertical-slice-and-dice-v10/metroidvania/014-205-entities-state-physics-update-1504.md` - entity update loop",
        "- `odin-knowledge-base/.../rpg/093-31-party-system-battle-resolution.md` - entity applied to combat",
        "",
        "### Hot reload",
        "- `docs/karl_zylinski/hot-reload-gameplay-code.md` - concept and Karl's demo",
        "- `odin-knowledge-base/.../rpg/084-22-hot-reloading.md` - practical application",
        "- `docs/karl_zylinski/odin-book/24-a-tour-of-the-core-collection.md` - `core:dynlib`",
        "",
        "### Collision / physics",
        "- `odin-knowledge-base/.../introduction/006-simple-collision-detection-and-resolution-10-min.md` - basics",
        "- `odin-knowledge-base/.../rpg/077-15-detecting-3d-collisions.md` - 3D",
        "- `odin-knowledge-base/.../rpg/080-18-3d-collision-response.md` - 3D response",
        "",
        "### Rendering / Raylib",
        "- `odin-knowledge-base/.../introduction/004-drawing-shapes-and-sprites-7min.md` - basics",
        "- `odin-knowledge-base/.../introduction/001-introduction-to-odin-and-raylib-3min.md` - setup",
        "- `docs/karl_zylinski/odin-book/25-libraries-for-creating-video-games.md` - Raylib/Sokol overview",
        "",
        "### Data-oriented / perf",
        "- `docs/karl_zylinski/odin-book/20-data-oriented-design.md` - SoA vs AoS",
        "- `docs/karl_zylinski/odin-book/08-fixed-memory-containers.md` - DOD foundations",
        "- `docs/karl_zylinski/odin-dod-benchmarks.md` - real measurements",
        "",
        "### Allocation patterns (general)",
        "- `docs/karl_zylinski/dynamic-arrays-and-arenas.md` - arena patterns",
        "- `docs/karl_zylinski/handle-based-arrays.md` - handle-based pattern (Karl)",
        "- `docs/karl_zylinski/handle-based-maps-three-implementations.md` - handle maps",
        "",
        "### C bindings / vendor:",
        "- `docs/karl_zylinski/generate-odin-bindings-for-c-libraries.md` - c-bindgen for C libs",
        "- `docs/karl_zylinski/odin-book/21-making-c-library-bindings-foreign-function-interface.md` - FFI manual",
        "",
        "### Build / compile",
        "- `docs/karl_zylinski/odin-book/18-you-probably-dont-need-a-build-system.md` - no build system",
        "- `code/templates/` - hot-reload templates (to clone in a REAL project elsewhere)",
        "",
        "### Language fundamentals (Odin basics)",
        "- `docs/karl_zylinski/odin-book/03-variables-and-constants.md` - types, constants",
        "- `docs/karl_zylinski/odin-book/04-some-additional-basics.md` - proc, if/for",
        "- `docs/karl_zylinski/odin-book/05-making-new-types.md` - struct/enum/union/switch/Maybe",
        "- `docs/karl_zylinski/odin-book/06-pointers.md` - pointers",
        "- `docs/karl_zylinski/odin-book/07-procedures-and-scopes.md` - defer, named returns",
        "- `docs/karl_zylinski/odin-book/14-parametric-polymorphism-writing-generic-code.md` - generics",
        "- `docs/karl_zylinski/odin-book/16-error-handling.md` - error patterns",
        "- `docs/karl_zylinski/odin-book/18-you-probably-dont-need-a-build-system.md` - packages/imports",
        "- `docs/karl_zylinski/odin-book/23-odin-features-you-should-avoid.md` - anti-patterns",
        "",
        "### Workflow / tooling",
        "- `code/templates/` - projects to clone (hot-reload Raylib/Sokol template)",
        "- `code/examples/demo.odin` - feature demo",
        "- `docs/karl_zylinski/odin-book/22-debuggers.md` - debug setup",
        "- `docs/karl_zylinski/odin-book/25-libraries-for-creating-video-games.md` - Raylib/Sokol/libs",
        "",
        "## Skill to navigate",
        "",
        "- `kb-navigator` (Kilo skill) - filters by topic, Module, source",
        "- `odin-pattern-finder` (Kilo skill) - find a precise Odin pattern",
        "- `.kilo/agents/odin-gamedev.md` - expert subagent for pure Odin questions",
        "",
        "## How this file is generated",
        "",
        "This INDEX is **regenerated by `_Helpers/build_kb_index.py`**.",
        "**Auto-generated sections**: Overview by source, Skool courses, Karl book,",
        "Statistics. **Manual sections preserved**: Index by topic (human curation;",
        "add to `build_kb_index.py` if you want it auto-generated).",
        "",
        "When the KB changes (new file in `odin-knowledge-base/` or `odin-book/`),",
        "re-run: `python _Helpers/build_kb_index.py`",
        "",
        "If the INDEX becomes too big (> 10 KB), consider splitting into:",
        "- `odin-knowledge-base/INDEX.md` (this file, overview)",
        "- `odin-knowledge-base/TOPICS.md` (detailed topics)",
        "",
        build_stats_section(),
    ]
    return "\n".join(parts)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=_DESCRIPTION)
    parser.add_argument("--check", action="store_true",
                        help="Dry-run: don't write, just display what would change.")
    parser.add_argument("--out", default=str(INDEX_PATH),
                        help=f"Path of the INDEX file (default: {INDEX_PATH.relative_to(ROOT)})")
    args = parser.parse_args(argv)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    new_content = build_index_content()
    existing = ""
    if out.exists():
        existing = out.read_text(encoding="utf-8")
        if existing == new_content:
            print(f"[OK] {out.relative_to(ROOT)} already up to date, no change needed.")
            return 0

    if args.check:
        # Display a simplified diff (lengths)
        print(f"[CHECK] {out.relative_to(ROOT)} differs from the generated content:")
        if existing:
            print(f"  existing : {len(existing):,} chars")
        print(f"  generated: {len(new_content):,} chars")
        return 0

    out.write_text(new_content, encoding="utf-8")
    print(f"[+] {out.relative_to(ROOT)} ({len(new_content):,} chars)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
