---
title: "Tasks and launch wiring (root workspace)"
date: "2026-07-15"
tags: [OdinRAG, reference, vscode, tasks, launch, odin, raddebugger]
type: reference
status: active
version: 1.0.0
lastUpdated: "2026-07-15"
updatedBy: "Kilo Code (built from this conversation)"
---

# 008_tasks_and_launch_wiring

> **Why this document exists.** The root `.vscode/tasks.json` and `.vscode/launch.json` in OdinRAG look unusual (many hardcoded paths to a single sub-project, two parallel PowerShell tasks, four `BUILD-LAUNCH` `type: "process"` tasks).
> They are the result of a specific debugging session against a "Waiting for preLaunchTask ..." hang, and the rules below are what keep them stable. Read this before touching `tasks.json`, `launch.json`, or adding a new Odin sub-project under `code/projects/`.

## TL;DR

- F5 from the OdinRAG root workspace builds and runs `code/projects/PVG03_RPG` with 6 launch configurations.
- Builds are delegated to 4 `type: "process"` tasks under the `[BUILD-LAUNCH] Odin: PVG03_RPG ...` prefix. They invoke `odin` directly (no PowerShell wrapper) to avoid pipe-tracking hangs.
- The Raddebugger flow is special: it goes through `_tools/build_and_run_OdinRAG.bat` (mirror of the child project's `_tools/build_and_run.bat`) so the behavior matches whether you open the child project directly or F5 from OdinRAG.
- Old PowerShell-wrapper tasks (with the `[BUILD] Odin:` prefix) still exist for menu-driven workflows (`Ctrl+Shift+P > Run Task`) where auto-detection of the project via `${file}` is useful.
- To add a new sub-project, you duplicate four things. See [Adding a new sub-project](#adding-a-new-sub-project).

## The hang we fixed

When a `preLaunchTask` is `type: "shell"` and invokes `powershell.exe -File ...odin_task.ps1 ...`, three processes get spawned in series (`cmd.exe` → `powershell.exe` → `odin`). VS Code tracks the foreground `cmd.exe` PID but does not always observe early termination of the inner PowerShell pipe, so it stays on "Waiting for preLaunchTask '[BUILD] Odin: Build Debug'..." indefinitely even though the build actually succeeded and the binary was launched.

Two real fixes were applied together:

1. The 4 tasks called by F5 were switched to `type: "process"` with `command: "odin"` (no shell wrapper). VS Code tracks the process directly, no pipe ambiguity.
2. The Raddebugger task uses `cmd /c _tools\build_and_run_OdinRAG.bat ...`. The `.bat` ends with `start "" cmd /c "...raddbg_start.bat"`, which **detaches** `raddbg.exe` from the `cmd` chain. The task exits in ~50 ms, leaving raddbg as a free-floating window. Without this, "Waiting for preLaunchTask ..." comes back immediately because `raddbg.exe` keeps the cmd pipe alive.

Other hang sources we removed:

- `${input:odinProject}` (pickString) inside a `program` field combined with a `preLaunchTask`. The pickString prompt can resolve after the task starts in some VS Code versions, blocking the launch loop. We hardcoded `PVG03_RPG` everywhere to keep both task and program resolution deterministic.
- `preLaunchTask` that itself launched the binary (the legacy `[BUILD] Odin: Run Debug` task did `odin build` then `& $exePath`). VS Code waits for the task to exit; if the task holds the binary open, the wait never completes. The new debug configs use `[BUILD-LAUNCH] Build Debug (process)` (build-only) and let VS Code's `cppvsdbg` attach.

## File map

| Path                                          | Role                                                                                                                                                                                                                    |
| --------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `.vscode/tasks.json`                          | Both workspace menus (Run Task) AND `preLaunchTask` targets. 4 `BUILD-LAUNCH` `type: "process"` tasks are used by F5; older `[BUILD] Odin:` / `[DEV] Odin:` `type: "shell"` tasks remain for menu use.                  |
| `.vscode/launch.json`                         | 6 debug configurations (5 `cppvsdbg`, 1 `cppvsdbg` + `noDebug: true`). Every config has a `preLaunchTask` from the `BUILD-LAUNCH` family.                                                                               |
| `_tools/build_and_run_OdinRAG.bat`            | Mirror of `code/projects/PVG03_RPG/_tools/build_and_run.bat`. Runs the full pipeline (`odin build` → copy raddbg config → spawn raddbg detached). This is the task entry point for the Raddebugger flow.                |
| `code/projects/PVG03_RPG/.vscode/tasks.json`  | Child project menu tasks (legacy, `type: "process"` calling `odin` directly). Used when PVG03_RPG is opened standalone via its own `project.code-workspace`.                                                            |
| `code/projects/PVG03_RPG/.vscode/launch.json` | Child project launch configs. 6 entries, identical in spirit to the parent.                                                                                                                                             |
| `_Helpers/scripts/dev/odin_task.ps1`          | PowerShell wrapper used by the **legacy** `[BUILD] Odin:` / `[DEV] Odin:` tasks. Detects the project from `${file}` via regex `^code[\\/]projects[\\/]([^\\/]+)`. Kept for menu workflows where auto-detection matters. |

## The 4 BUILD-LAUNCH tasks

All four are `type: "process"`, hardcoded to `PVG03_RPG`, and live at the top of `.vscode/tasks.json`.

| Label                                                           | Command | Args (key points)                                                                                               | Called by                               |
| --------------------------------------------------------------- | ------- | --------------------------------------------------------------------------------------------------------------- | --------------------------------------- |
| `[BUILD-LAUNCH] Odin: PVG03_RPG - Build Debug (process)`        | `odin`  | `build`, `source`, `-debug`, `-vet`, `-strict-style`, `-use-separate-modules`, `-out:build/PVG03_RPG_debug.exe` | 4 debug launches                        |
| `[BUILD-LAUNCH] Odin: PVG03_RPG - Build Release (process)`      | `odin`  | `build`, `source`, `-o:speed`, `-no-bounds-check`, `-use-separate-modules`, `-out:build/PVG03_RPG.exe`          | `build_and_run Source (release)`        |
| `[BUILD-LAUNCH] Odin: PVG03_RPG - Check vet only (process)`     | `odin`  | `check`, `source`, `-vet`, `-strict-style`                                                                      | `[DIAG] Odin: Check ...` launch         |
| `[BUILD-LAUNCH] Odin: PVG03_RPG - Launch Raddebugger (process)` | `cmd`   | `/c`, `_tools\build_and_run_OdinRAG.bat`, `build`, `--src`, `--out`, `--debug`, `--raddebugger`, `--verbose`    | `Build + open Raddebugger on PVG03_RPG` |

Shared options across the three `odin` tasks: a `problemMatcher` matching the Odin compiler error regex `^(.*?)(\\((\\d+):(\\d+)\\))\\s+(Syntax\\s+)?(Error|Warning):\\s+(.+)$`, so warnings/errors surface in the Problems panel.

The Raddebugger task has an empty `problemMatcher` (cmd /c + .bat chain does not produce Odin-style errors) and `presentation.clear: true` so the panel does not keep "task running" indefinitely.

## The 6 launch configurations

| Name                                          | Type       | preLaunchTask                  | Behavior                                                                                                                                                                                                |
| --------------------------------------------- | ---------- | ------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `Build Source using Odin (debug)`             | `cppvsdbg` | `Build Debug (process)`        | Build then attach VS Code debugger. Exe launched by VS Code, breakpoints honored.                                                                                                                       |
| `build_and_run Source (debug)`                | `cppvsdbg` | `Build Debug (process)`        | Same as above (alias; matches the child project's naming).                                                                                                                                              |
| `build_and_run Source (release)`              | `cppvsdbg` | `Build Release (process)`      | Release build, `cppvsdbg` attach.                                                                                                                                                                       |
| `build_and_run Src (debug)`                   | `cppvsdbg` | `Build Debug (process)`        | Mirrors the child variant in case `src/` is used instead of `source/` (the wrapper detects whichever exists).                                                                                           |
| `Build + open Raddebugger on PVG03_RPG`       | `cppvsdbg` | `Launch Raddebugger (process)` | `noDebug: true`, `presentation.hidden: true`. The preLaunchTask opens `raddbg.exe` detached; the launch itself is a no-op so VS Code does not attach a second debugger that would conflict with raddbg. |
| `[DIAG] Odin: Check (vet only) - then attach` | `cppvsdbg` | `Check vet only (process)`     | Runs `odin check -vet -strict-style` then attaches to the existing debug binary. Useful as a CI-style smoke test before launching.                                                                      |

All configs use `${workspaceFolder}/code/projects/PVG03_RPG/...` for paths. There is **no** `${input:odinProject}` anywhere - we learned that the hard way (see "The hang we fixed").

## Flow walkthrough

### F5 - `build_and_run Source (debug)`

```
VS Code (F5)
  |
  preLaunchTask: [BUILD-LAUNCH] Build Debug (process)
    -> odin build source -out:build/PVG03_RPG_debug.exe -debug -vet -strict-style -use-separate-modules
    -> exit 0
  |
  request: "launch", type: "cppvsdbg", program = build/PVG03_RPG_debug.exe
    -> VS Code (Windows debugger) attaches and runs the binary
```

### F5 - `Build + open Raddebugger on PVG03_RPG`

```
VS Code (F5)
  |
  preLaunchTask: [BUILD-LAUNCH] Launch Raddebugger (process)
    -> cmd /c _tools\build_and_run_OdinRAG.bat build --src ... --out ... --debug --raddebugger --verbose
         |
         | 1) odin build source -out:build/PVG03_RPG_debug.exe -debug -o:none ...
         | 2) copy code/projects/PVG03_RPG/_tools/project.raddbg_project     -> build\
         |    copy code/projects/PVG03_RPG/_tools/project.raddbg_user         -> build\
         | 3) write build\raddbg_start.bat:
         |      @echo off
         |      "<raddbg.exe>" --user:"<build>\project.raddbg_user" \
         |                    --project:"<build>\project.raddbg_project" \
         |                    "<build>\PVG03_RPG_debug.exe"
         | 4) start "" cmd /c "build\raddbg_start.bat"
         |    -> raddbg.exe opens in its own window, detached from this cmd
         -> cmd (the parent of step 4) exits in ~50ms
    -> task done, "Waiting for preLaunchTask ..." status cleared
  |
  request: "launch", type: "cppvsdbg", noDebug: true
    -> VS Code marks the launch as complete (no debugger attached)
```

The arg order `--user:` then `--project:` then target exe is required by RAD Debugger (cf. `raddbg_readme.md` on the project's `E:\Apps\Raddebugger` install).

## Why `raddbg.exe` resolution uses `%FLD_APPS%` first

The child project's `build_and_run.bat` uses `set raddebuggerExe=%FLD_APPS%\Raddebugger\raddbg.exe` and **never** looks in `PATH`. The OdinRAG mirror follows the same logic with a `where raddbg.exe` fallback for users who installed Raddebugger elsewhere. If both fail, the task still exits 0 and prints the binary path so you can attach manually.

## `presentation.clear: true`

All 4 `BUILD-LAUNCH` tasks (and the 3 legacy Odin tasks where it matters) set:

```jsonc
"presentation": { "reveal": "always", "panel": "shared", "clear": true }
```

`clear: true` forces VS Code to wipe the terminal panel before each run. Without it, the panel keeps the previous build's output and the status bar can stay on "task is running" after the task has actually finished (because the output never drained properly after the PowerShell wrapper closed its pipe).

## Why legacy `[BUILD] Odin:` tasks still exist

The `type: "shell"` + PowerShell wrapper combo has one feature the new `type: "process"` tasks don't: **auto-detection of the project from `${file}`**. So `Ctrl+Shift+P > Run Task > [BUILD] Odin: Build Debug` works regardless of which `code/projects/*/source/main.odin` you have open. We kept these tasks because they are useful for menu workflows where you are not choosing a specific project.

They are **not** used by any `preLaunchTask`. Don't reference them from `launch.json`.

## Adding a new sub-project

Suppose you add `code/projects/PVG02_Raylib/`.

1. **Duplicate the 4 `BUILD-LAUNCH` tasks** in `.vscode/tasks.json` (search for `[BUILD-LAUNCH] Odin: PVG03_RPG` and replace `PVG03_RPG` by `PVG02_Raylib`). Keep the same options.
2. **Duplicate the 6 launches** in `.vscode/launch.json` (search for `PVG03_RPG` and replace). For the Raddebugger config, also edit the `preLaunchTask` label to point at the new Raddebugger task.
3. If you want full project-local fidelity, also copy `code/projects/PVG03_RPG/.vscode/{launch,tasks}.json` into `code/projects/PVG02_Raylib/.vscode/` and adjust the paths.
4. Update `_tools/build_and_run_OdinRAG.bat`: change `defaultProject=PVG03_RPG` to `PVG02_Raylib` (or add a `--project` flag if you want both). The `childToolsDir` resolution is relative to `defaultProject`, so it works out.

There is no `pickString` to update - we learned to keep the prompt out of `launch.json`.

## If "Waiting for preLaunchTask ..." comes back

Diagnose in this order:

1. Open `Ctrl+Shift+P > Developer: Reload Window`. Stale caches from previous edits cause spurious hangs.
2. Check the task you triggered really is one of the `BUILD-LAUNCH` `type: "process"` tasks (or `Launch Raddebugger (process)`). Open `.vscode/launch.json`, find the config name, read its `preLaunchTask` value.
3. Run the task standalone via `Ctrl+Shift+P > Run Task > <name>`. If it exits 0 in the panel and you see the expected log, the task itself is fine - the hang is launch-side. Confirm `request: "launch"` and `type: "cppvsdbg"`/`type: "cppvsdbg" + noDebug: true` are set.
4. If the task still hangs standalone, the pipe is leaking. Switch the task back to a direct `odin` invocation (no `powershell`, no `cmd /c` wrapper). The `.bat` is the only allowed exception because it ends with `start ""` to detach the long-lived process.
5. If `raddbg.exe` is being launched but does not honor the project file, verify that `build/project.raddbg_project` exists. The `.bat` copies it from `code/projects/PVG03_RPG/_tools/project.raddbg_project` on first run, but if you wiped `build/` it copies again. If the file is missing at the source, the `.bat` warns and continues without it (raddbg then has no breakpoint on `main.odin:1`).

## Reference: full launch.json

The file lives at `.vscode/launch.json`. Six entries; all `type: "cppvsdbg"`; all `request: "launch"`; all hardcode `PVG03_RPG` in `${workspaceFolder}/code/projects/PVG03_RPG/...`. Only the Raddebugger entry uses `noDebug: true` + `presentation.hidden: true`.

## Reference: full build_and_run_OdinRAG.bat

The `.bat` lives at `_tools/build_and_run_OdinRAG.bat`. Its default project is `PVG03_RPG` (override at the top of the script or via future flags). Pipeline: `odin build` → copy raddbg project/user files into `build/` → write `build/raddbg_start.bat` → `start "" cmd /c "...raddbg_start.bat"` (detaches raddbg).
