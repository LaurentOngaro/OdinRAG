# tools folder

This folder stores tools like setup or install scripts for the project. There are some scripts and some config files.

The scripts (.ps1, .bat and .sh files) MUST BE MANUALLY REVIEWED before launch, mainly to change the path used in variables for folders and exectutables.

## Scripts

| Script                 | Platform      | Role                                                                                                                                            |
| ---------------------- | ------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| `install_full_env.ps1` | Windows       | Downloads Odin + Portable Build Tools, then extends `devcmd.bat`.                                                                               |
| `create_junctions.ps1` | Windows       | Creates the NTFS junctions in `_refs/` so `ols.json` can resolve the `core`, `examples` and `vendor` collections.                               |
| `create_junctions.sh`  | Linux / macOS | Same role as the `.ps1` above, using POSIX symlinks. Replaces the junctions left over from a Windows run so they do not appear as broken links. |
| `build_and_run.bat`    | Windows       | Generic build + run + RadDebugger launcher.                                                                                                     |
| `build_and_run.sh`     | Linux / macOS | Same CLI as the `.bat` above, written in bash. Invoked by the `linux` blocks in `.vscode/tasks.json`.                                           |
| `check_and_format.bat` | Windows       | Formatting and vetting pipeline for CI.                                                                                                         |

## Creating the `_refs/` links on Linux

`ols.json` resolves its collections through `_refs/`, which must point at the local Odin SDK. On Linux, the junctions created on Windows do not survive the filesystem, so the links have to be recreated:

```bash
cd <project>/_tools
./create_junctions.sh
```

The script auto-detects the Odin SDK root, in order: `$ODIN_ROOT`, `odin root`, `$FLD_OLS_DIST`, `/opt/odin`, `$ODIN_INSTALL_DIR`, `~/.odin`, `/usr/share/odin`. To force a specific location, use `ODIN_ROOT=/path/to/odin ./create_junctions.sh`.

Re-running the script is safe: a link that already resolves to the right place is left untouched, a stale or broken one is recreated. Use `--force` to recreate everything unconditionally.

| Exit code | Meaning                                                           |
| --------- | ----------------------------------------------------------------- |
| 0         | Success.                                                          |
| 1         | Wrong platform, or a real directory is in the way of a link.      |
| 2         | The Odin SDK root could not be found, or `$ODIN_ROOT` is invalid. |
| 3         | The `_refs/` folder is missing. Create it first.                  |
