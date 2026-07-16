---
title: "Tasks and launch wiring (root workspace)"
date: "2026-07-16"
tags: [OdinRAG, reference, vscode, zed, tasks, launch, odin, raddebugger]
type: reference
status: active
version: 2.1.0
lastUpdated: "2026-07-16"
updatedBy: "Kilo Code (rewritten to match the actual .vscode/tasks.json, .vscode/launch.json and .zed/tasks.json; added child-project naming section after PVG03_RPG launch.json patch)"
---

# 008_tasks_and_launch_wiring

> **Why this document exists.** The root workspace has TWO parallel wiring systems for Odin tasks: VS Code (`.vscode/launch.json` + `.vscode/tasks.json`) and Zed (`.zed/tasks.json`). Each handles the project in a different way. The VS Code system also has TWO sub-families of tasks with very different semantics (`[BUILD_PVG03]` process tasks vs `[BUILD]/[RUN]/[DEV]` shell+PowerShell tasks). The rules below are what keep them stable and what they actually do today. Read this before touching any `tasks.json`, `launch.json`, or adding a new Odin sub-project under `code/projects/`.

## TL;DR

- F5 from the OdinRAG root workspace builds and runs `code/projects/PVG03_RPG` via **6 launch configurations**.
- The launches reference **4 `[BUILD_PVG03]` `type: "process"` tasks** that invoke `odin` directly (no PowerShell wrapper) to avoid pipe-tracking hangs.
- The Raddebugger flow goes through `_tools/build_and_run_OdinRAG.bat` (mirror of the child project's `_tools/build_and_run.bat`).
- **PowerShell-wrapper tasks** still exist with `[BUILD] / [RUN] / [DEV]` prefixes (`type: "shell"` calling `_Helpers/scripts/dev/odin_task.ps1`). They detect the project from `${file}` and are useful for `Ctrl+Shift+P > Run Task` workflows and for the `run-debug` mode (which builds then runs the binary in one go).
- **Zed** has its own `tasks.json` mirroring the PowerShell wrapper tasks (key use: `Odin: Run Debug`).
- To add a new sub-project, you duplicate four things. See [Adding a new sub-project](#adding-a-new-sub-project).

## The hang we fixed (historical context, still relevant)

When a `preLaunchTask` is `type: "shell"` and invokes `powershell.exe -File ...odin_task.ps1 ...`, three processes get spawned in series (`cmd.exe` → `powershell.exe` → `odin`). VS Code tracks the foreground `cmd.exe` PID but does not always observe early termination of the inner PowerShell pipe, so it stays on "Waiting for preLaunchTask ..." indefinitely even though the build actually succeeded and the binary was launched.

Two real fixes were applied together:

1. **The 4 F5 launches use `[BUILD_PVG03] Build with Odin (Debug/Release/Check)` + `[BUILD_PVG03] build_and_run (Raddebugger)` tasks with `type: "process"` and `command: "odin"` (or `cmd` for the Raddebugger one)**. VS Code tracks the process directly, no pipe ambiguity.
2. The Raddebugger task uses `cmd /c _tools\build_and_run_OdinRAG.bat ...`. The `.bat` ends with `start "" cmd /c "...raddbg_start.bat"`, which **detaches** `raddbg.exe` from the `cmd` chain. The task exits in ~50 ms, leaving raddbg as a free-floating window. Without this, "Waiting for preLaunchTask ..." comes back immediately because `raddbg.exe` keeps the cmd pipe alive.

Other hang sources we removed:

- `${input:odinProject}` (pickString) inside a `program` field combined with a `preLaunchTask`. The pickString prompt can resolve after the task starts in some VS Code versions, blocking the launch loop. We hardcoded `PVG03_RPG` everywhere to keep both task and program resolution deterministic.
- `preLaunchTask` that itself launched the binary. VS Code waits for the task to exit; if the task holds the binary open, the wait never completes. Note: `_Helpers/scripts/dev/odin_task.ps1 -Mode run-debug` STILL does `odin build` then `& $exePath`. It is therefore **not** used as a `preLaunchTask`. It is wired as `Ctrl+Shift+P > Run Task > [RUN] Run with odin_task (Debug)` only.

## File map

| Path                                                                            | Role                                                                                                                                                                                                                                              |
| ------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `.vscode/tasks.json`                                                            | Both workspace menus (Run Task) AND `preLaunchTask` targets. 4 `[BUILD_PVG03]` `type: "process"` tasks are used by F5. They hardcode `PVG03_RPG` paths.                                                                                           |
| `.vscode/launch.json`                                                           | 6 debug configurations (all `type: "cppvsdbg"`). Every config has a `preLaunchTask` referencing one of the `[BUILD_PVG03]` tasks.                                                                                                                 |
| `.zed/tasks.json`                                                               | Mirror of a subset of the PowerShell-wrapper tasks (build-debug, build-release, build-dll, run-debug, check, format). Variables: `$ZED_WORKTREE_ROOT`, `$ZED_FILE`.                                                                               |
| `_tools/build_and_run_OdinRAG.bat`                                              | Mirror of `code/projects/PVG03_RPG/_tools/build_and_run.bat`. Pipeline: `odin build` → copy raddbg config into `build/` → spawn raddbg detached. Entry point for the Raddebugger flow.                                                            |
| `code/projects/PVG03_RPG/_tools/build_and_run.bat`                              | The original. `_tools/build_and_run_OdinRAG.bat` mirrors it.                                                                                                                                                                                      |
| `code/projects/PVG03_RPG/.vscode/launch.json`                                   | Standalone-project mirror of the root `.vscode/launch.json` (7 configs). Uses **legacy** `[BUILD] *` / `build_and_run *` naming instead of `[BUILD_PVG03] *` - see the in-file `// NOMENCLATURE` block and the “Child project naming” note below. |
| `code/projects/PVG03_RPG/_tools/project.raddbg_project` / `project.raddbg_user` | Source of truth for the raddbg project/user files. Copied into `build/` by the `.bat` on first run.                                                                                                                                               |
| `_Helpers/scripts/dev/odin_task.ps1`                                            | PowerShell wrapper used by the `[BUILD] / [RUN] / [DEV]` shell tasks AND by all Zed tasks. Detects the project from `${file}` / `$ZED_FILE` via regex `^code[\\/]projects[\\/]([^\\/]+)`. Uses a `src/`-prefers-`source/` tie-breaker per mode.   |

## The 4 `[BUILD_PVG03]` tasks (F5-only)

All four are `type: "process"`, hardcoded to `PVG03_RPG`, and live at the top of `.vscode/tasks.json`. They are the **only** tasks referenced by `launch.json`.

| Label                                       | Command | Key args                                                                                                                                                   | Called by (launch.json configs)                                                                |
| ------------------------------------------- | ------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| `[BUILD_PVG03] Build with Odin (Debug)`     | `odin`  | `build`, `${workspaceFolder}/code/projects/PVG03_RPG/source`, `-debug`, `-vet`, `-strict-style`, `-use-separate-modules`, `-out:build/PVG03_RPG_debug.exe` | `Build Source using Odin (debug)`, `build_and_run Source (debug)`, `build_and_run Src (debug)` |
| `[BUILD_PVG03] Build with Odin (Release)`   | `odin`  | `build`, `...source`, `-o:speed`, `-no-bounds-check`, `-use-separate-modules`, `-out:build/PVG03_RPG.exe`                                                  | `build_and_run Source (release)`                                                               |
| `[BUILD_PVG03] Check with Odin (vet)`       | `odin`  | `check`, `...source`, `-vet`, `-strict-style`                                                                                                              | `[DIAG] Odin: Check (vet only) - then attach`                                                  |
| `[BUILD_PVG03] build_and_run (Raddebugger)` | `cmd`   | `/c`, `_tools\build_and_run_OdinRAG.bat`, `build`, `--src`, `--out`, `--debug`, `--raddebugger`, `--verbose`                                               | `Build + open Raddebugger on PVG03_RPG`                                                        |

- All three `odin` tasks use `options.cwd: ${workspaceFolder}/code/projects/PVG03_RPG` so Odin resolves relative paths from the project root.
- They share the `problemMatcher` regex `^(.*?)(\\((\\d+):(\\d+)\\))\\s+(Syntax\\s+)?(Error|Warning):\\s+(.+)$`, so warnings/errors surface in the Problems panel.
- The Raddebugger task has `problemMatcher: []` (cmd /c + .bat chain does not produce Odin-style errors) and `presentation.clear: true` so the panel does not keep "task running" indefinitely.
- `presentation.reveal: "always"` and `presentation.clear: true` on all four for the same reason (the panel must not keep stale output between runs).

## The 6 launch configurations

All in `.vscode/launch.json`, all `type: "cppvsdbg"`, all `request: "launch"`, all hardcode `PVG03_RPG`. Only the Raddebugger entry uses `noDebug: true`. There is **no** `${input:odinProject}` anywhere.

| Name                                          | preLaunchTask                               | Behavior                                                                                                                                                                          |
| --------------------------------------------- | ------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `Build Source using Odin (debug)`             | `[BUILD_PVG03] Build with Odin (Debug)`     | Build then attach VS Code debugger. Exe launched by VS Code, breakpoints honored.                                                                                                 |
| `build_and_run Source (debug)`                | `[BUILD_PVG03] Build with Odin (Debug)`     | Same as above (alias; matches the child project's naming).                                                                                                                        |
| `build_and_run Source (release)`              | `[BUILD_PVG03] Build with Odin (Release)`   | Release build, `cppvsdbg` attach.                                                                                                                                                 |
| `build_and_run Src (debug)`                   | `[BUILD_PVG03] Build with Odin (Debug)`     | Mirrors the child variant in case `src/` is used instead of `source/`. With the current PVG03_RPG layout (only `source/`), behaves identically to `build_and_run Source (debug)`. |
| `Build + open Raddebugger on PVG03_RPG`       | `[BUILD_PVG03] build_and_run (Raddebugger)` | `noDebug: true`. The preLaunchTask opens `raddbg.exe` detached; the launch itself is a no-op so VS Code does not attach a second debugger that would conflict with raddbg.        |
| `[DIAG] Odin: Check (vet only) - then attach` | `[BUILD_PVG03] Check with Odin (vet)`       | Runs `odin check -vet -strict-style` then attempts to attach to the existing `build/PVG03_RPG_debug.exe` binary. Useful as a CI-style smoke test.                                 |

## PowerShell-wrapper tasks (menu use, NOT used by F5)

These tasks are `type: "shell"`, invoke `powershell.exe -File _Helpers/scripts/dev/odin_task.ps1 ...`, and detect the project from `${file}`. They are **not** referenced by any `preLaunchTask`. Use them via `Ctrl+Shift+P > Run Task > <label>`.

| Label                                                | Mode arg         | Purpose                                                                                                                                                              | group             |
| ---------------------------------------------------- | ---------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------- |
| `[BUILD] Build with odin_task (Debug)`               | `build-debug`    | Debug build of the project containing `${file}`. Marked `isDefault: true` for the `build` group.                                                                     | `build` (default) |
| `[BUILD] Build with odin_task (Release)`             | `build-release`  | Release build (`-o:speed`).                                                                                                                                          | `build`           |
| `[BUILD] Hot Reload with odin_task (Build DLL)`      | `build-dll`      | Builds the hot-reload DLL (`-build-mode:dll`). For this mode the script prefers `source/` over `src/`.                                                               | `build`           |
| `[BUILD] Build with odin_task (Debug + Raddebugger)` | `build-raddebug` | Builds the debug binary and launches `raddbg.exe` (via the `.bat`).                                                                                                  | `build`           |
| `[RUN] Run with odin_task (Debug)`                   | `run-debug`      | Builds then runs the debug binary. The `odin_task.ps1 -Mode run-debug` script does `odin build` and then `& $exePath` - so it must NOT be used as a `preLaunchTask`. | `test` (default)  |
| `[DEV] Check Source folder with odin_task`           | `check`          | `odin check -vet -strict-style` on the project containing `${file}`.                                                                                                 | `build`           |

### `odin_task.ps1` - source-folder detection

The script computes `src` from two candidates under the detected project (`code/projects/<proj>/`):

- `build-dll` mode → prefers `source/` over `src/`.
- All other modes → prefers `src/` over `source/`.

For the current PVG03_RPG layout (only `source/` exists), the tie-breaker is a no-op - every mode resolves to `source/`. The `src/` branch only triggers when a project actually has both folders (legacy migration case).

### Why shell tasks exist at all

The `type: "shell"` + PowerShell wrapper combo has one feature the `type: "process"` `[BUILD_PVG03]` tasks don't: **auto-detection of the project from `${file}`**. So `Ctrl+Shift+P > Run Task > [RUN] Run with odin_task (Debug)` works regardless of which `code/projects/*/source/main.odin` you have open. They are useful for menu workflows where you are not committing to a single project.

They are also the only path that gives you `[BUILD] Hot Reload with odin_task (Build DLL)` and `[RUN] Run with odin_task (Debug)` (one-shot build + run) without writing a new VS Code launch.

## Diagnostic / utility tasks

Also in `.vscode/tasks.json`, all `type: "shell"`, all `python ...`. Not used by F5.

| Label                                                        | Script                                                                                                        |
| ------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------- |
| `[DIAG] Audit Consistency READMEs`                           | `_Helpers/scripts/diagnostic/auditReadmeCoherence.py`                                                         |
| `[DIAG] Vault Diagnostic`                                    | `_Helpers/scripts/diagnostic/vaultDiagnostic.py`                                                              |
| `[DIAG] Validate Frontmatter`                                | `_Helpers/scripts/diagnostic/validateFrontmatter.py --fail-on-error`                                          |
| `[DIAG PVG03] Code Audit with code_auditor`                  | `_Helpers/scripts/diagnostic/code_auditor/code_auditor.py --path code/projects/PVG03_RPG/source --report ...` |
| `[PUBLISH] publish_public --check (dry-run)`                 | `_Helpers/scripts/diagnostic/publish_public.py --check`                                                       |
| `[PUBLISH] publish_public --full (private + regen + public)` | `_Helpers/scripts/diagnostic/publish_public.py`                                                               |
| `[PUBLISH] publish_public --skip-private`                    | `_Helpers/scripts/diagnostic/publish_public.py --skip-private`                                                |
| `[SCRAPE] Run all scrapers (interactive)`                    | `_Helpers/scripts/scrapers/run_all_scrapers.py`                                                               |

## Zed tasks (`.zed/tasks.json`)

Zed has no equivalent of F5/launch.json. The `tasks.json` mirrors the PowerShell wrapper subset that matters for daily Odin flow (all invoke `_Helpers/scripts/dev/odin_task.ps1` with the same modes):

| Label                               | Mode arg                                                                                                  |
| ----------------------------------- | --------------------------------------------------------------------------------------------------------- |
| `Odin: Build Debug`                 | `build-debug`                                                                                             |
| `Odin: Build Release`               | `build-release`                                                                                           |
| `Odin: Hot Reload - Build DLL`      | `build-dll`                                                                                               |
| `Odin: Run Debug`                   | `run-debug`                                                                                               |
| `Odin: Check (vet only)`            | `check`                                                                                                   |
| `Odin: Format Odin blocks (manual)` | (runs `_Helpers/scripts/fixes/format_odin_in_files.py --file $ZED_FILE`, **not** through `odin_task.ps1`) |

Zed variables used: `$ZED_WORKTREE_ROOT` (workspace root), `$ZED_FILE` (active file). All tasks are scoped to `cwd: $ZED_WORKTREE_ROOT`.

Format on save is wired through `.zed/settings.json` (`languages.Odin.format_on_save: "on"`), so the `Odin: Format Odin blocks (manual)` task is for explicit re-runs, not the daily path.

## Flow walkthrough

### F5 - `Build Source using Odin (debug)`

```
VS Code (F5)
  |
  preLaunchTask: [BUILD_PVG03] Build with Odin (Debug)
    -> odin build ${workspaceFolder}/code/projects/PVG03_RPG/source -out:...build/PVG03_RPG_debug.exe -debug -vet -strict-style -use-separate-modules
    -> exit 0
  |
  request: "launch", type: "cppvsdbg", program = ${workspaceFolder}/code/projects/PVG03_RPG/build/PVG03_RPG_debug.exe
    -> VS Code (Windows debugger) attaches and runs the binary
```

### F5 - `Build + open Raddebugger on PVG03_RPG`

```
VS Code (F5)
  |
  preLaunchTask: [BUILD_PVG03] build_and_run (Raddebugger)
    -> cmd /c _tools\build_and_run_OdinRAG.bat build --src ...source --out ...build\PVG03_RPG_debug.exe --debug --raddebugger --verbose
         |
         | 1) odin build source -debug -o:none + -vet-unused/-vet-style/-vet-semicolon/...
         | 2) copy code/projects/PVG03_RPG/_tools/project.raddbg_project  -> build\
         |    copy code/projects/PVG03_RPG/_tools/project.raddbg_user      -> build\
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

The arg order `--user:` then `--project:` then target exe is required by RAD Debugger.

### `Ctrl+Shift+P > Run Task > [RUN] Run with odin_task (Debug)`

```
VS Code (menu picker)
  |
  Task: [RUN] Run with odin_task (Debug)
    -> powershell -File _Helpers/scripts/dev/odin_task.ps1 -WorkspaceFolder ... -ActiveFile ${file} -Mode run-debug
         -> Resolve-ProjectContext: detects project name from ${file} (regex ^code[\\/]projects[\\/]([^\\/]+))
         -> picks source/ or src/ (src preferred here)
         -> odin build <src> -out:build/<proj>_debug.exe -debug -vet -strict-style
         -> if OK: & "<build>\<proj>_debug.exe"
    -> the binary blocks the task until exit
```

## Child project naming (`code/projects/PVG03_RPG/.vscode/`)

The standalone project uses a **legacy naming** for its tasks/launches (`[BUILD] *` prefix / `build_and_run Source/Src *`) instead of the root's `[BUILD_PVG03] *`. That is **intentional**:

- Naming was already that way before the root workspace's `[BUILD_PVG03]` family was introduced.
- Anyone opening `code/projects/PVG03_RPG/project.code-workspace` standalone should not have to relearn muscle memory.
- Both families call the same Odin + same `_tools/build_and_run.bat`, so behavior is identical.

### Inventory of the child project's launches

7 configs (vs the 6 at the root). The extras are a `Src` mirror for when the project grows a `src/` folder:

| Name                                          | preLaunchTask                         | Notes                                                                      |
| --------------------------------------------- | ------------------------------------- | -------------------------------------------------------------------------- |
| `Build Source using Odin (debug)`             | `Build Source using Odin (debug)`     | Same as root `[BUILD_PVG03] Build with Odin (Debug)` + attach.             |
| `Build Src using Odin (debug)`                | `Build Src using Odin (debug)`        | Mirror for the (future) `src/` folder.                                     |
| `build_and_run Source (debug)`                | `build_and_run Source (debug)`        | Same as root `[BUILD_PVG03] Build with Odin (Debug)` via `.bat`.           |
| `build_and_run Source (release)`              | `build_and_run Source (release)`      | Same as root `[BUILD_PVG03] Build with Odin (Release)`.                    |
| `build_and_run Src (debug)`                   | `build_and_run Src (debug)`           | Mirror for `src/`.                                                         |
| `build_and_run Source (Raddebug)`             | `build_and_run Source (Raddebug)`     | Same as root `[BUILD_PVG03] build_and_run (Raddebug)` (detached, noDebug). |
| `[DIAG] Odin: Check (vet only) - then attach` | `[DEV] Check Source folder with odin` | Vet-only attach - mirrors root `[DIAG]` config.                            |

## Why `raddbg.exe` resolution uses `%FLD_APPS%` first

The child project's `build_and_run.bat` uses `set raddebuggerExe=%FLD_APPS%\Raddebugger\raddbg.exe` and **never** looks in `PATH`. The OdinRAG mirror follows the same logic, then falls back to `where raddbg.exe` for users who installed Raddebugger elsewhere. If both fail, the task still exits 0 and prints the binary path so you can attach manually.

## `presentation.clear: true` on the `[BUILD_PVG03]` tasks

```jsonc
"presentation": { "reveal": "always", "panel": "shared", "clear": true }
```

`clear: true` forces VS Code to wipe the terminal panel before each run. Without it, the panel keeps the previous build's output and the status bar can stay on "task is running" after the task has actually finished (because the output never drained properly after the PowerShell wrapper closed its pipe).

## Adding a new sub-project

Suppose you add `code/projects/PVG02_Raylib/`.

1. **Duplicate the 4 `[BUILD_PVG03]` tasks** in `.vscode/tasks.json` (search for `BUILD_PVG03` and replace `PVG03_RPG` by `PVG02_Raylib`). Keep `type: "process"` and the same args/options structure (just path adjustments).
2. **Duplicate the 6 launches** in `.vscode/launch.json` (search for `PVG03_RPG` and replace). For the Raddebugger config, also edit the `preLaunchTask` label to point at the new `[BUILD_PVG02] build_and_run (Raddebugger)` task.
3. **Zed does not need changes** - the `Odin: ...` tasks auto-detect the project from `$ZED_FILE` via `odin_task.ps1`.
4. Update `_tools/build_and_run_OdinRAG.bat`: change `defaultProject=PVG03_RPG` to `PVG02_Raylib` (or add a `--project` flag if you want both). The `childToolsDir` resolution is relative to `defaultProject`, so it works out.
5. If you want full project-local fidelity, also copy `code/projects/PVG03_RPG/_tools/build_and_run.bat` (and the `project.raddbg_*` files) into `code/projects/PVG02_Raylib/_tools/`.

There is no `pickString` to update - we learned to keep the prompt out of `launch.json`.

## If "Waiting for preLaunchTask ..." comes back

Diagnose in this order:

1. Open `Ctrl+Shift+P > Developer: Reload Window`. Stale caches from previous edits cause spurious hangs.
2. Check the task you triggered really is one of the `[BUILD_PVG03]` `type: "process"` tasks (or `[BUILD_PVG03] build_and_run (Raddebugger)`). Open `.vscode/launch.json`, find the config name, read its `preLaunchTask` value.
3. Run the task standalone via `Ctrl+Shift+P > Run Task > <name>`. If it exits 0 in the panel and you see the expected log, the task itself is fine - the hang is launch-side. Confirm `request: "launch"` and `type: "cppvsdbg"` (or `type: "cppvsdbg" + noDebug: true`) are set.
4. If the task still hangs standalone, the pipe is leaking. Switch the task back to a direct `odin` invocation (no `powershell`, no `cmd /c` wrapper). The `.bat` is the only allowed exception because it ends with `start ""` to detach the long-lived process.
5. If `raddbg.exe` is being launched but does not honor the project file, verify that `build/project.raddbg_project` exists. The `.bat` copies it from `code/projects/PVG03_RPG/_tools/project.raddbg_project` on first run, but if you wiped `build/` it copies again. If the file is missing at the source, the `.bat` warns and continues without it (raddbg then has no breakpoint on `main.odin:1`).
