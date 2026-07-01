---
title: "Odin project template - PVG subagent"
date: 2026-07-01
tags: [OdinRAG, template, odin-project, agent, subagent]
type: template
status: active
version: 1.0.0
lastUpdated: "2026-07-01"
updatedBy: "MiniMax-M3 (Kilo Code)"
---

# odin-project

## When to invoke

The orchestrator (`code` agent) delegates questions specific to this project to me. I know:

- The **patterns** already implemented (see the project's `AGENTS.md`)
- The **pitfalls** already identified (to NOT reproduce)
- The **main KB sources** (see `AGENTS.md`)

## Sources of truth (relative paths from this file)

| Topic            | File in the repo                                                    |
| ---------------- | ------------------------------------------------------------------- |
| _e.g. pattern X_ | `../../../odin-knowledge-base/.../<lesson>.md`                      |
| _e.g. concept Y_ | `../../../odin-knowledge-base/docs/karl_zylinski/odin-book/<NN>.md` |

## Rules

- NEVER invent Odin syntax. Check against `odin-knowledge-base/docs/karl_zylinski/odin-book/`.
- NEVER copy-paste KB code without adapting it to the project context.
- Always cite the **KB file path** that inspired the code.

## Anti-patterns

- No tabs in code: `odinfmt.json` at the root, `tabs: false, spaces: 2`.
