---
name: planning-helper
description: Manage day-by-day planning files (_Private/planning/daily/J_YYYY-MM-DD.md). Create today's daily from the template, update a section (objectives, tasks, bilan), list existing dailies.
---

# Planning helper - daily management

Skill for managing daily notes in `_Private/planning/daily/`.
The format is detailed in [`_Helpers/templates/planning-daily/J_YYYY-MM-DD.md`] and the YAML convention in [`_Helpers/docs/003_yaml_frontmatter_conventions.md`]

## When to invoke

- The user wants to create today's daily.
- The user wants to add / check a task in a daily.
- The user wants to list existing dailies (overview).
- The user wants to find a specific daily (by date or keyword).

## Operations

### 1. Create today's daily

```bash
# 1. Get today's date (local UTC)
$today = python -c "from datetime import date; print(date.today().isoformat())"
# -> "2026-06-28"

# 2. Check it doesn't already exist
$test -f "_Private/planning/daily/J_$today.md" && echo "EXISTS" || echo "OK to create"

# 3. Copy the template and adapt the frontmatter + H1 title
$cp _Helpers/templates/planning-daily/J_YYYY-MM-DD.md _Private/planning/daily/J_$today.md
# Then edit: frontmatter (date) + H1 title ("# Daily YYYY-MM-DD - Subject")
```

The H1 title must follow the convention: `# Daily YYYY-MM-DD - <subject>`.

### 2. List existing dailies

```bash
$ls _Private/planning/daily/
# -> J_2026-06-28.md  J_2026-06-29.md  ...

# With titles (H1 excerpt)
$grep -h "^# Daily" _Private/planning/daily/*.md | sort
```

### 3. Add a task to today's daily

```bash
$today = "J_$(python -c 'from datetime import date; print(date.today().isoformat())').md"
# Add "- [ ] new task" after the "## Tasks" line
# OR check an existing one: replace "[ ]" with "[x]"
```

### 4. Find a daily by topic

```bash
# Lists dailies that talk about a topic (grep in title + body)
$grep -l "hot-reload\|format" _Private/planning/daily/*.md
```

### 5. End-of-day bilan

The bilan is added **at the end of the file**, in the section `## Bilan (end of day)`. Recommended sections:

- **Delivered**: what was actually done
- **Postponed**: what could not be done + why
- **Mood note**: optional, short

### 6. Archiving

When a roadmap phase ends, **do not delete** the dailies. Leave them in place; `git log` keeps the history. The frontmatter `status` can switch to `archived` but this is not required.

## Daily format conventions

### Mandatory frontmatter

```yaml
---
title: "Daily 2026-06-28 - Kilo setup"
date: 2026-06-28
tags: [OdinRAG, planning, daily, status/active]
type: daily
status: active
---
```

### Body sections (in this order)

1. `# Daily YYYY-MM-DD - <subject>`
2. `## Goal of the day` - one sentence
3. `## Tasks` - checklist
4. `## Blockers / Questions` - optional
5. `## Decisions taken` - optional
6. `## Odin patterns / KB consulted` - optional, links
7. `## Tomorrow` - top 1-3
8. `## Bilan (end of day)` - mandatory, written **after** the session

## Anti-patterns

- **DO NOT** create a daily retroactively (except for exceptional catch-up).
- **DO NOT** modify the template `_Helpers/templates/planning-daily/J_YYYY-MM-DD.md`. It is the reference - to add a section, create a new version of the template + migrate existing dailies.
- **DO NOT** write the bilan **during** the session. The bilan is a retrospective, not a logbook.
- **DO NOT** leave a daily empty (without any task checked / bilan). If there is nothing to do on a day, do not create the file.
