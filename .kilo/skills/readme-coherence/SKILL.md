---
name: readme-coherence
description: "Audit that every README*.md in the repo accurately reflects its host directory (no 404 [[wikilinks]], no missing files in 'Files produced' sections, aspirational READMEs marked with 'Structure cible' / 'Awaiting content'). Use when the user says 'audit readme', 'check structure', 'wikilinks', 'coherence', 'missing files in README', or after adding/renaming files under any folder that has a README."
---

# README coherence audit

Every `README*.md` in the repo must accurately reflect the structure of its host directory. Wikilinks must resolve, mentioned files must exist, and aspirational READMEs (planning future content) must be marked so the audit can skip them.

## When to invoke

- After creating or renaming files in any folder that has a `README*.md`.
- After editing a README (new section that mentions files, new wikilinks).
- Before committing a structural change (new subfolder, rename).
- As a periodic sanity check (`--quiet` for a one-line summary).
- In CI: add `--fail-on-error` to block PRs that introduce drift.

## The 3 invariants

1. **Wikilinks resolve.** Every `[[wikilink]]` in a README must point to an existing file (otherwise the link is a 404 in Obsidian / the rendered KB).
2. **Mentioned files exist.** If a README has a "Files produced" / "Structure" / "Files in this folder" section, every file mentioned there must exist in the host directory. Conversely, files that ARE in the directory should be mentioned when such a section exists.
3. **Aspirational READMEs are marked.** READMEs describing future or planned content (not yet implemented) must have a "Structure cible" or "Awaiting content" header so the audit script can skip them. Without the marker, missing files are reported as errors.

## Quick audit

```bash
# Whole repo
python _Helpers/scripts/diagnostic/auditReadmeCoherence.py

# Scope to one subtree (much faster on a large repo)
python _Helpers/scripts/diagnostic/auditReadmeCoherence.py --scope odin-knowledge-base/docs/official

# One-line summary only
python _Helpers/scripts/diagnostic/auditReadmeCoherence.py --quiet

# CI mode (non-zero exit on issues)
python _Helpers/scripts/diagnostic/auditReadmeCoherence.py --fail-on-error
```

| Exit | Meaning      | Action                                              |
| ---- | ------------ | --------------------------------------------------- |
| 0    | Clean        | All READMEs coherent with their host directory      |
| 1    | Issues found | Read the output, fix or mark the README (see below) |
| 2    | Tool error   | Path missing, etc. - read the message               |

## Common issues and fixes

| Issue                                             | Cause                                                | Fix                                                                                                               |
| ------------------------------------------------- | ---------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| `wikilink [[foo]]` not found                      | Target file was renamed or deleted                   | Update the README OR restore the file at the wikilinked path                                                      |
| `file bar.md present but not mentioned in README` | New file added under a folder with a "Files" section | Add the file to the README's "Files produced" / "Structure" section                                               |
| `file baz.md mentioned in README but missing`     | Planned content never written                        | Either write the file, OR add a "Structure cible" / "Awaiting content" header to the README so the audit skips it |
| README lists 5 files but folder has 7             | New files added without updating README              | Update the README                                                                                                 |

### How to mark an aspirational README

Add ONE of these headers to the README (audit picks them up case-insensitively):

```markdown
## Structure cible

This README describes the planned structure. Files not yet present will be skipped by `auditReadmeCoherence.py`.

## Awaiting content

(documented above as "Structure cible")
```

The marker tells the script: "missing files here are intentional, don't flag them."

## Anti-patterns

- **Never** delete a README to silence the audit. The README is the documentation contract; fix the structure instead.
- **Never** add a "Structure cible" header to hide real drift - it's for planned content only. If the content was supposed to exist and doesn't, write it.
- **Never** add `--fail-on-error` to a CI job that runs on every commit unless you also triage existing failures first - it will block all merges until drift is fixed.
- **Never** assume a passing audit means a perfect README. The audit catches structure drift; it does not catch typos, factual errors, or style issues (those are `markdownlint-cli2` + `reflow_md.py`).

## Reference

- Rule (in `AGENTS.md` § "Markdown structure"): READMEs must reflect their directory, wikilinks must resolve, aspirational READMEs must be marked.
- Style of the README itself: load the [`markdown-style`](../markdown-style/SKILL.md) skill (one-paragraph-one-line, ASCII punctuation, etc.).
- Frontmatter schema (if the README has YAML): see [`_Helpers/docs/003_yaml_frontmatter_conventions.md`](../../_Helpers/docs/003_yaml_frontmatter_conventions.md).

## Diagnostic pattern quick reference

```bash
# Read all the issues without fixing them
python _Helpers/scripts/diagnostic/auditReadmeCoherence.py 2>&1 | tee /tmp/readme-audit.log

# Count by category
grep -c "wikilink" /tmp/readme-audit.log
grep -c "present but not mentioned" /tmp/readme-audit.log
grep -c "missing" /tmp/readme-audit.log
```
