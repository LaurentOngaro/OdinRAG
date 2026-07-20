---
title: "Tasks and launch wiring (root workspace)"
date: "2026-07-20"
tags: [OdinRAG, reference, vscode, zed, tasks, launch, odin, raddebugger]
type: reference
status: active
version: 2.4.0
lastUpdated: "2026-07-20"
updatedBy: "Kilo Code (resolved Family B cwd propagation via ${input:pvProjectDir} pickString; documented why command input was abandoned; cleaned up after the wrapper-script detour)"
---

# 008_tasks_and_launch_wiring

> **Why this document exists.** The root workspace has TWO parallel wiring systems for Odin tasks: VS Code (`.vscode/launch.json` + `.vscode/tasks.json`) and Zed (`.zed/tasks.json`). Each handles the project in a different way. The VS Code system also has TWO sub-families of tasks with very different semantics (`[BUILD_PVG03]` process tasks vs `[BUILD]/[RUN]/[DEV]` shell+PowerShell tasks). The rules below are what keep them stable and what they actually do today. Read this before touching any `tasks.json`, `launch.json`, or adding a new Odin sub-project under `code/projects/`.

## TL;DR

- F5 from the OdinRAG root workspace builds and runs `code/projects/PVG03_RPG` via **8 launch configurations** (4 generic + 4 project-specific, plus the `[BUILD] odin_task (Debug + Raddebugger)` detached entry).
- The launches all use the **PowerShell wrapper** `[BUILD] / [DEV] odin_task *` tasks (`type: "process"` + `command: "powershell"`). They were also `type: "shell"` historically but are now `type: "process"` with the shell kept as the process - this still lets us detect the project from `${file}` while avoiding the "Waiting for preLaunchTask..." pipe-tracking hang that motivated the original split.
- The Raddebugger flow stays generic (no `.bat` involved - `odin_task.ps1` builds then launches `raddbg.exe` directly).
- **Sub-project mode**: when `odin_task.ps1` is invoked from a project-specific launch config (its `cwd` is inside `code/projects/<X>/`), it detects the sub-project's `_tools\build_and_run.bat` and delegates to it for build-debug / build-release / run-debug / run-release. The `check` mode is always generic. This preserves the pipeline used by the standalone workspace without duplicating tasks in the root `.vscode/tasks.json`.
- **Binary convention**: outputs go to `build/<mode>/<Project>.exe` (or `.dll`) — `build/debug/PVG03_RPG.exe`, `build/release/PVG03_RPG.exe`, `build/dll/PVG03_RPG.dll`. **No** `_debug` / `_release` suffixes on the file names — the sub-folder disambiguates. Matches the convention from Karl Zylinski's hot-reload template (`OUT_DIR=build/debug`).
- **Zed** has its own `tasks.json` mirroring the PowerShell wrapper tasks (key use: `Odin: Run Debug`).
- To add a new sub-project, add 3 project-specific launch configs (see [Adding a new sub-project](#adding-a-new-sub-project)). `tasks.json` is NOT touched.

## The hang we fixed (historical context, still relevant)

When a `preLaunchTask` invokes `powershell.exe -File ...odin_task.ps1 ...`, three processes get spawned in series (`cmd.exe` → `powershell.exe` → `odin`). When the wrapper task is `type: "shell"`, VS Code tracks the foreground `cmd.exe` PID but does not always observe early termination of the inner PowerShell pipe, so it stays on "Waiting for preLaunchTask ..." indefinitely even though the build actually succeeded and the binary was launched.

The fix that stuck:

1. **All F5 launches use `type: "process"` + `command: "powershell"`** for every `odin_task.ps1` invocation, with the script args passed as a real array (no more `command: "powershell -NoProfile ..."` monolithic strings that VS Code would mis-resolve as a path). VS Code tracks the process directly, no pipe ambiguity.
2. **The Raddebugger launch uses `cmd.exe /c exit 0` as a no-op `program`** so VS Code clears the preLaunchTask state without attaching a second debugger that would conflict with `raddbg.exe`. `odin_task.ps1` itself launches `raddbg.exe` detached, so the preLaunchTask exits in ~50 ms.

Other hang sources we removed:

- `${input:odinProject}` (pickString) inside a `program` field combined with a `preLaunchTask`. The pickString prompt can resolve after the task starts in some VS Code versions, blocking the launch loop. We hardcoded `PVG03_RPG` everywhere to keep both task and program resolution deterministic. Note: a `pickString` in a `command` INPUT is fine (used at launch.json load time, before preLaunchTask); the hang only applies when the prompt is resolved _during_ preLaunchTask execution.
- `preLaunchTask` that itself launched the binary. VS Code waits for the task to exit; if the task holds the binary open, the wait never completes. Note: `_Helpers/scripts/dev/odin_task.ps1 -Mode run-debug` STILL does `odin build` then `& $exePath`. It is therefore **not** used as a `preLaunchTask`. It is wired as `Ctrl+Shift+P > Run Task > [RUN] Run with odin_task (Debug)` only.

## File map

| Path                                                                            | Role                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| ------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `.vscode/tasks.json`                                                            | 15 tasks total: 6 PowerShell-wrapper Odin tasks (`[BUILD]`, `[BUILD+RUN]`, `[DEV]`), 1 `[SCRAPE]`, 3 `[DIAG]`, 3 `[PUBLISH]`, 2 misc. All `type: "process"`. F5 launch configs reference the `[BUILD]` / `[BUILD+RUN]` / `[DEV]` tasks.                                                                                                                                                                                                  |
| `.vscode/launch.json`                                                           | 8 debug configurations (all `type: "cppvsdbg"`). 4 generic (project auto-detected from `${file}`) + 4 project-specific (`[PVG03] *` with hardcoded `cwd`). Each config's `preLaunchTask` references a `odin_task.ps1` task by label.                                                                                                                                                                                                     |
| `.zed/tasks.json`                                                               | Mirror of a subset of the PowerShell-wrapper tasks (build-debug, build-release, build-dll, run-debug, check, format). Variables: `$ZED_WORKTREE_ROOT`, `$ZED_FILE`.                                                                                                                                                                                                                                                                      |
| `code/projects/PVG03_RPG/_tools/build_and_run.bat`                              | The sub-project's canonical build pipeline. Invoked by `odin_task.ps1` when its `cwd` is inside the project (via the `[PVG03] *` launch configs). Pipeline: `odin build` → optional `--exec` to run.                                                                                                                                                                                                                                     |
| `code/projects/PVG03_RPG/.vscode/launch.json`                                   | Standalone-project mirror of the root `.vscode/launch.json`. Uses **legacy** `[BUILD] *` / `build_and_run *` naming instead of the PowerShell-wrapper `[BUILD] odin_task *` naming - see [Child project naming](#child-project-naming-codeprojectspvg03_rpgvscode).                                                                                                                                                                      |
| `code/projects/PVG03_RPG/_tools/project.raddbg_project` / `project.raddbg_user` | Source of truth for the raddbg project/user files. Used by the sub-project's `.bat` on first run.                                                                                                                                                                                                                                                                                                                                        |
| `_Helpers/scripts/dev/odin_task.ps1`                                            | PowerShell wrapper used by all `[BUILD]` / `[BUILD+RUN]` / `[DEV]` VS Code tasks AND by all Zed tasks. Detects the project from `${file}` / `$ZED_FILE` via regex `^code[\\/]projects[\\/]([^\\/]+)`. If invoked with `cwd` inside the project, delegates build/run to the project's `_tools/build_and_run.bat`. Uses a `src/`-prefers-`source/` tie-breaker per mode. Writes outputs to `build/debug/`, `build/release/`, `build/dll/`. |

## The PowerShell-wrapper tasks used by F5

All F5-reachable tasks are `type: "process"` and invoke `powershell.exe` as a process (not as a shell wrapper) with explicit args. They live in `.vscode/tasks.json`. They are the **only** tasks referenced by `launch.json`.

| Label                                           | Command      | Mode arg         | Key args                                                                                                                                   | Output                                                                                                  |
| ----------------------------------------------- | ------------ | ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------- |
| `[BUILD] odin_task (debug)`                     | `powershell` | `build-debug`    | `-NoProfile -ExecutionPolicy Bypass -File _Helpers/scripts/dev/odin_task.ps1 -WorkspaceFolder ... -ActiveFile ... -Mode build-debug -Exec` | `build/debug/<Project>.exe` (e.g. `code/projects/PVG03_RPG/build/debug/PVG03_RPG.exe`); launched at end |
| `[BUILD] odin_task (release)`                   | `powershell` | `build-release`  | (same wrapper + `-Exec`)                                                                                                                   | `build/release/<Project>.exe`; launched at end                                                          |
| `[BUILD] Hot Reload with odin_task (Build DLL)` | `powershell` | `build-dll`      | (same wrapper, no `-Exec`)                                                                                                                 | `build/dll/<Project>.dll`                                                                               |
| `[BUILD] odin_task (Debug + Raddebugger)`       | `powershell` | `build-raddebug` | (same wrapper, no `-Exec`)                                                                                                                 | `build/debug/<Project>.exe` then launches `raddbg.exe`                                                  |
| `[BUILD+RUN] odin_task (debug)`                 | `powershell` | `run-debug`      | (same wrapper)                                                                                                                             | `build/debug/<Project>.exe` then runs it (build + run in one task)                                      |
| `[BUILD+RUN] odin_task (release)`               | `powershell` | `run-release`    | (same wrapper)                                                                                                                             | `build/release/<Project>.exe` then runs it                                                              |
| `[DEV] odin_task Check Source folder`           | `powershell` | `check`          | (same wrapper, no `-Exec`)                                                                                                                 | no output - `odin check -vet -strict-style`                                                             |

- `odin_task.ps1` is `type: process` from VS Code's perspective: the `command: "powershell"` field is the executable, the wrapper args are passed as an explicit array. This avoids the "Path to shell executable ... does not exist" error that hit when the full command line was inlined in a single string with spaces.
- `odin_task.ps1` ensures `build/debug/`, `build/release/`, `build/dll/` exist before invoking Odin (creates them on first run).
- The `-Exec` flag is added to the `[BUILD] *` tasks (NOT to `[BUILD] odin_task (Debug + Raddebugger)` which manages its own binary lifecycle through `raddbg.exe`, NOT to `[BUILD+RUN] *` which already run the binary via `& $exePath`, NOT to `[DEV] Check` which produces no binary, NOT to `[BUILD] Hot Reload (Build DLL)` which produces a DLL).
- **Sub-project routing**: when `odin_task.ps1` is invoked with `cwd` inside `code/projects/<X>/` (the `[PVG03] *` launch configs hardcode this), the script delegates build/run operations to `<X>/_tools/build_and_run.bat`. This preserves the canonical pipeline used by the standalone workspace without duplicating the tasks in `tasks.json`. `check` mode stays generic.

## The launch configurations

All in `.vscode/launch.json`, all `type: "cppvsdbg"`, all `request: "launch"`. Two families:

### Family A — generic (4 configs)

Project is auto-detected from `${file}` by `odin_task.ps1`. `cwd` is `${workspaceFolder}` (no hardcoded project). You need an editor tab inside the project for these to work.

| Name                                          | preLaunchTask                             | `program`           | `noDebug` | Behavior                                                                                                                                                                               |
| --------------------------------------------- | ----------------------------------------- | ------------------- | --------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `[BUILD] odin_task (debug)`                   | `[BUILD] odin_task (debug)`               | `cmd.exe /c exit 0` | `false`   | The preLaunchTask runs `odin_task.ps1` which builds the binary (and launches it via `-Exec`). The launch itself is a no-op so VS Code does not block waiting for a debugger to attach. |
| `[BUILD] odin_task (release)`                 | `[BUILD] odin_task (release)`             | `cmd.exe /c exit 0` | `false`   | Same, release mode.                                                                                                                                                                    |
| `[BUILD] odin_task (Debug + Raddebugger)`     | `[BUILD] odin_task (Debug + Raddebugger)` | `cmd.exe /c exit 0` | `false`   | Builds then launches `raddbg.exe` detached. The launch is a no-op so VS Code does not attach a second debugger that would conflict with raddbg.                                        |
| `[DIAG] Odin: Check (vet only) - then attach` | `[DEV] odin_task Check Source folder`     | `cmd.exe /c exit 0` | `false`   | Runs `odin check -vet -strict-style`. Smoke test before launching.                                                                                                                     |

### Family B — project-specific (3 configs per project)

`cwd` is HARDCODED to the sub-project folder. This makes the build work even if the active editor tab is not under that project. `odin_task.ps1` detects the `cwd` and delegates to the project's `_tools/build_and_run.bat`. You duplicate these 3 entries per sub-project.

| Name                      | preLaunchTask                         | `cwd`                                        | `program`           | `noDebug` |
| ------------------------- | ------------------------------------- | -------------------------------------------- | ------------------- | --------- |
| `[PVG03] build (debug)`   | `[BUILD] odin_task (debug)`           | `${workspaceFolder}/code/projects/PVG03_RPG` | `cmd.exe /c exit 0` | `false`   |
| `[PVG03] build (release)` | `[BUILD] odin_task (release)`         | `${workspaceFolder}/code/projects/PVG03_RPG` | `cmd.exe /c exit 0` | `false`   |
| `[PVG03] build (check)`   | `[DEV] odin_task Check Source folder` | `${workspaceFolder}/code/projects/PVG03_RPG` | `cmd.exe /c exit 0` | `false`   |

### Why `cmd.exe /c exit 0` as the `program`?

VS Code requires `program` to be set for `type: "cppvsdbg"`. We do NOT want to re-launch the binary from VS Code because the `[BUILD] odin_task (debug|release)` preLaunchTask already builds + launches it (via `-Exec`). Re-launching would create a second instance. Using `cmd.exe /c exit 0` is a deterministic no-op that satisfies the schema without spawning anything.

The Raddebugger launch uses the same pattern (with `internalConsoleOptions: "neverOpen"` to suppress the no-op terminal).

## PowerShell-wrapper tasks (menu use)

All Odin-related VS Code tasks go through the PowerShell wrapper, including the ones referenced by `launch.json`. The ones listed here are also surfaced in `Ctrl+Shift+P > Run Task > <label>` for menu workflows:

| Label                                           | Mode arg         | Purpose                                                                                                                                                              | group             |
| ----------------------------------------------- | ---------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------- |
| `[BUILD] odin_task (debug)`                     | `build-debug`    | Debug build of the project containing `${file}`. Marked `isDefault: true` for the `build` group.                                                                     | `build` (default) |
| `[BUILD] odin_task (release)`                   | `build-release`  | Release build (`-o:speed`).                                                                                                                                          | `build`           |
| `[BUILD] Hot Reload with odin_task (Build DLL)` | `build-dll`      | Builds the hot-reload DLL (`-build-mode:dll`). For this mode the script prefers `source/` over `src/`.                                                               | `build`           |
| `[BUILD] odin_task (Debug + Raddebugger)`       | `build-raddebug` | Builds the debug binary and launches `raddbg.exe` (via the `.bat`).                                                                                                  | `build`           |
| `[BUILD+RUN] odin_task (debug)`                 | `run-debug`      | Builds then runs the debug binary. The `odin_task.ps1 -Mode run-debug` script does `odin build` and then `& $exePath` - so it must NOT be used as a `preLaunchTask`. | `test` (default)  |
| `[BUILD+RUN] odin_task (release)`               | `run-release`    | Same as `run-debug` but in release mode.                                                                                                                             | `test`            |
| `[DEV] odin_task Check Source folder`           | `check`          | `odin check -vet -strict-style` on the project containing `${file}`.                                                                                                 | `build`           |

All 7 Odin tasks above also pass `-Cwd ${input:pvProjectDir}`. The input is declared at the top of `tasks.json`:

| Input id       | Type         | Options                                                                                      | Default                   |
| -------------- | ------------ | -------------------------------------------------------------------------------------------- | ------------------------- |
| `pvProjectDir` | `pickString` | `code/projects/PVG03_RPG`, `code/projects/PVG02_Metroidvania`, `code/projects/Odin_Skeleton` | `code/projects/PVG03_RPG` |

The list is **HARDCODED** - to add a new sub-project, append it to `options` (and optionally to `default`). VS Code on this machine refuses to spawn any executable from a `command` input (PATH not inherited, `${workspaceFolder}` not resolved in the `command` field), so we cannot auto-discover `code/projects/*` at runtime. The pickString is safe because it is resolved at launch.json load time, before any preLaunchTask runs.

### `odin_task.ps1` - source-folder detection

The script computes `src` from two candidates under the detected project (`code/projects/<proj>/`):

- `build-dll` mode → prefers `source/` over `src/`.
- All other modes → prefers `src/` over `source/`.

For the current PVG03_RPG layout (only `source/` exists), the tie-breaker is a no-op - every mode resolves to `source/`. The `src/` branch only triggers when a project actually has both folders (legacy migration case).

### Why shell tasks exist at all

The `type: "shell"` + PowerShell wrapper combo has one feature the `type: "process"` `[BUILD_PVG03]` tasks don't: **auto-detection of the project from `${file}`**. So `Ctrl+Shift+P > Run Task > [RUN] Run with odin_task (Debug)` works regardless of which `code/projects/*/source/main.odin` you have open. They are useful for menu workflows where you are not committing to a single project.

They are also the only path that gives you `[BUILD] Hot Reload with odin_task (Build DLL)` and `[RUN] Run with odin_task (Debug)` (one-shot build + run) without writing a new VS Code launch.

## Diagnostic / utility tasks

Also in `.vscode/tasks.json`, all `type: "process"`, all `python ...` with explicit args. Not used by F5.

| Label                                                        | Script                                                                             |
| ------------------------------------------------------------ | ---------------------------------------------------------------------------------- |
| `[DIAG] Audit Consistency READMEs`                           | `_Helpers/scripts/diagnostic/auditReadmeCoherence.py`                              |
| `[DIAG] Vault Diagnostic`                                    | `_Helpers/scripts/diagnostic/vaultDiagnostic.py`                                   |
| `[DIAG] Validate Frontmatter`                                | `_Helpers/scripts/diagnostic/validateFrontmatter.py --fail-on-error`               |
| `[DIAG] Audit with code_auditor (single file prompt)`        | `_Helpers/scripts/diagnostic/code_auditor/code_auditor.py` (prompts for file/path) |
| `[PUBLISH] publish_public --check (dry-run)`                 | `_Helpers/scripts/diagnostic/publish_public.py --check`                            |
| `[PUBLISH] publish_public --full (private + regen + public)` | `_Helpers/scripts/diagnostic/publish_public.py`                                    |
| `[PUBLISH] publish_public --skip-private`                    | `_Helpers/scripts/diagnostic/publish_public.py --skip-private`                     |
| `[SCRAPE] Run all scrapers (interactive)`                    | `_Helpers/scripts/scrapers/run_all_scrapers.py`                                    |

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

### F5 - `[BUILD_PVG03] build_and_run Source (debug)`

```
VS Code (F5)
  |
  preLaunchTask: [BUILD] odin_task (debug)
    -> powershell -NoProfile -ExecutionPolicy Bypass -File _Helpers/scripts/dev/odin_task.ps1 -WorkspaceFolder ... -ActiveFile ... -Mode build-debug
         -> Resolve-ProjectContext: detects project name (PVG03_RPG), picks source/ vs src/
         -> mkdir build\debug (creates if missing)
         -> odin build source -out:build/debug/PVG03_RPG.exe -debug -vet -strict-style -use-separate-modules
         -> exit 0
  |
  request: "launch", type: "cppvsdbg", program = .../code/projects/PVG03_RPG/build/debug/PVG03_RPG.exe
    -> VS Code (Windows debugger) attaches and runs the binary
```

### F5 - `[BUILD_PVG03] Build + open Raddebugger (debug)`

```
VS Code (F5)
  |
  preLaunchTask: [BUILD] odin_task (Debug + Raddebugger)
    -> powershell ... -Mode build-raddebug
         -> odin build source -out:build/debug/PVG03_RPG.exe -debug -vet -strict-style
         -> if raddbg.exe in PATH: & raddbg.exe -g build/debug/PVG03_RPG.exe --PID 0  (detached, task exits ~50 ms)
         -> else: prints "binary ready: build/debug/PVG03_RPG.exe"
    -> task done, "Waiting for preLaunchTask ..." status cleared
  |
  request: "launch", type: "cppvsdbg", noDebug: true
    -> VS Code marks the launch as complete (no debugger attached)
```

The arg order `--user:` then `--project:` then target exe (used in the child project's `.bat`) is required by RAD Debugger.

### `Ctrl+Shift+P > Run Task > [BUILD+RUN] odin_task (debug)`

```
VS Code (menu picker)
  |
  Task: [BUILD+RUN] odin_task (debug)
    -> powershell -File _Helpers/scripts/dev/odin_task.ps1 -WorkspaceFolder ... -ActiveFile ${file} -Mode run-debug
         -> Resolve-ProjectContext: detects project name from ${file} (regex ^code[\\/]projects[\\/]([^\\/]+))
         -> picks source/ or src/ (src preferred here)
         -> mkdir build\debug
         -> odin build <src> -out:build/debug/<proj>.exe -debug -vet -strict-style
         -> if OK: & "build/debug/<proj>.exe"
    -> the binary blocks the task until exit
```

## Child project naming (`code/projects/PVG03_RPG/.vscode/`)

The standalone project uses a **legacy naming** for its tasks/launches (`[BUILD] *` prefix / `build_and_run Source/Src *`) instead of the root's PowerShell-wrapper `[BUILD] odin_task *` naming. That is **intentional**:

- Naming was already that way before the root workspace was consolidated around the PowerShell wrapper.
- Anyone opening `code/projects/PVG03_RPG/project.code-workspace` standalone should not have to relearn muscle memory.
- Both families call the same Odin + same `_tools/build_and_run.bat`, so behavior is identical.

### Inventory of the child project's launches

7 configs (vs the 4 at the root). The extras are a `Src` mirror for when the project grows a `src/` folder, plus the standalone variants of every build mode:

| Name                                          | preLaunchTask                         | Notes                                                                       |
| --------------------------------------------- | ------------------------------------- | --------------------------------------------------------------------------- |
| `Build Source using Odin (debug)`             | `Build Source using Odin (debug)`     | Same as root `[BUILD] odin_task (debug)` + attach.                          |
| `Build Src using Odin (debug)`                | `Build Src using Odin (debug)`        | Mirror for the (future) `src/` folder.                                      |
| `build_and_run Source (debug)`                | `build_and_run Source (debug)`        | Same as root `[BUILD] odin_task (debug)` via `.bat`.                        |
| `build_and_run Source (release)`              | `build_and_run Source (release)`      | Same as root `[BUILD] odin_task (release)`.                                 |
| `build_and_run Src (debug)`                   | `build_and_run Src (debug)`           | Mirror for `src/`.                                                          |
| `build_and_run Source (Raddebug)`             | `build_and_run Source (Raddebug)`     | Same as root `[BUILD] odin_task (Debug + Raddebugger)` (detached, noDebug). |
| `[DIAG] Odin: Check (vet only) - then attach` | `[DEV] Check Source folder with odin` | Vet-only attach - mirrors root `[DIAG]` config.                             |

## Why `raddbg.exe` resolution uses `%FLD_APPS%` first

The sub-project's `build_and_run.bat` uses `set raddebuggerExe=%FLD_APPS%\Raddebugger\raddbg.exe` and **never** looks in `PATH`. `odin_task.ps1` follows the same logic when invoked from the sub-project, then falls back to `where raddbg.exe` for users who installed Raddebugger elsewhere. If both fail, the task still exits 0 and prints the binary path so you can attach manually.

## `presentation.clear: true` on the build tasks

```jsonc
"presentation": { "reveal": "always", "panel": "shared", "clear": true }
```

`clear: true` forces VS Code to wipe the terminal panel before each run. Without it, the panel keeps the previous build's output and the status bar can stay on "task is running" after the task has actually finished (because the output never drained properly after the PowerShell wrapper closed its pipe).

## Adding a new sub-project

Suppose you add `code/projects/PVG02_Raylib/`.

1. **`.vscode/tasks.json`**: nothing to add. The PowerShell-wrapper tasks auto-detect the project from `${file}` (Family A) and from `cwd` (Family B), so no per-project task is needed.
2. **`.vscode/launch.json`**: duplicate the 3 Family B entries (`[PVG03] build (debug|release|check)`) under `[PVG02_Raylib] build (debug|release|check)`. Replace `PVG03_RPG` by `PVG02_Raylib` in the `cwd` and the `name`. Keep the same `preLaunchTask` labels (`[BUILD] odin_task (debug)`, etc.) - they are project-agnostic.
3. **Zed does not need changes** - the `Odin: ...` tasks auto-detect the project from `$ZED_FILE` via `odin_task.ps1`.
4. If you want full project-local fidelity, copy `code/projects/PVG03_RPG/_tools/build_and_run.bat` (and the `project.raddbg_*` files) into `code/projects/PVG02_Raylib/_tools/`. This is what makes Family B work for the new project.

There is **no `pickString` inside a launch config's `program` field** - we learned to keep interactive prompts out of `launch.json`. There IS a `pickString` input at the workspace level (`pvProjectDir` in `tasks.json`) which is safe: it's resolved at launch.json load time, well before any preLaunchTask runs, and the user just presses Enter to accept the default.

## If "Waiting for preLaunchTask ..." comes back

Diagnose in this order:

1. Open `Ctrl+Shift+P > Developer: Reload Window`. Stale caches from previous edits cause spurious hangs.
2. Check the task you triggered really is one of the PowerShell-wrapper tasks (`[BUILD] / [BUILD+RUN] / [DEV] odin_task *`) and that the wrapper is invoked as `type: "process"` + `command: "powershell"` (NOT `type: "shell"` with the full command line inlined). Open `.vscode/launch.json`, find the config name, read its `preLaunchTask` value.
3. Run the task standalone via `Ctrl+Shift+P > Run Task > <name>`. If it exits 0 in the panel and you see the expected log, the task itself is fine - the hang is launch-side. Confirm `request: "launch"` and `type: "cppvsdbg"` (or `type: "cppvsdbg" + noDebug: true`) are set.
4. If the task still hangs standalone, the pipe is leaking. Switch the task back to a direct `odin` invocation (no `powershell`, no `cmd /c` wrapper). The `.bat` is the only allowed exception because it ends with `start ""` to detach the long-lived process.
5. If `raddbg.exe` is being launched but does not honor the project file, verify that `build/debug/project.raddbg_project` exists (the `.bat` copies it from `code/projects/PVG03_RPG/_tools/project.raddbg_project` on first run; if you wiped `build/` it copies again). If the file is missing at the source, the `.bat` warns and continues without it (raddbg then has no breakpoint on `main.odin:1`).
