"""_Helpers/lib/user_config.py - Personal user config loader.

The config file is gitignored (in `_Helpers/.private/user_config.json`).
If absent, scripts fall back to environment variables, then to empty
strings.

To create your local config:

    cp _Helpers/docs/user_config.example.json _Helpers/.private/user_config.json

Then edit the copy and fill in your paths / credentials.

Scripts that depend on the user config:

    - _Helpers/odin_format.py       (ODINFMT_EXE)
    - _Helpers/scrape_skool.py      (yt-dlp path, Skool credentials)
    - _Helpers/book_html_to_md.py   (path to Karl book HTML)
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

CONFIG_PATH = Path(
    os.environ.get("ODINRAG_CONFIG")
    or (Path(__file__).resolve().parent.parent / ".private" / "user_config.json")
)

EXAMPLE_PATH = (
    Path(__file__).resolve().parent.parent / "docs" / "user_config.example.json"
)

DEFAULTS: dict[str, Any] = {
    "paths": {
        "odinfmt_exe": "",
        "odinfmt_config_system": "",
        "yt_dlp_exe": "",
        "odin_compiler": "",
        "python_exe": "",
        "karl_book_html": "",
        "karl_book_out": "",
        "project_root": "",
        "external_odin_projects_dir": "",
        "temp_dir": "",
    },
    "skool": {
        "email": "",
    },
    "scraper": {
        "youtube_cookies_file": "",
    },
    "kb": {
        "expected_lessons_skool": 0,
        "expected_files_karl_book": 0,
        "expected_articles_zylinski": 0,
        "expected_official_docs": 0,
    },
}


def _strip_dunder_keys(d: dict) -> dict:
    """Strip keys '_comment', '_xxx_env' etc. (metadata, not config)."""
    return {k: v for k, v in d.items() if not k.startswith("_")}


def _deep_merge(base: dict, override: dict) -> dict:
    """Deep-merge `override` into `base` (override wins). Ignore '_'-prefixed keys."""
    out = json.loads(json.dumps(base))  # deep copy
    for k, v in override.items():
        if k.startswith("_"):
            continue
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def load_config() -> dict:
    """Load the user config, merging with the DEFAULTS."""
    if not CONFIG_PATH.is_file():
        return json.loads(json.dumps(DEFAULTS))
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            user_data = json.load(f)
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return json.loads(json.dumps(DEFAULTS))
    return _deep_merge(DEFAULTS, user_data)


_config = load_config()

# Flat view of common sections for ergonomic access (`PATHS.odinfmt_exe` etc.)
PATHS = _config.get("paths", {})
SKOOL = _config.get("skool", {})
SCRAPER = _config.get("scraper", {})
KB = _config.get("kb", {})


def get(key_path: str, default: Any = "") -> Any:
    """Acces par chemin pointé. Exemple: get('paths.odinfmt_exe')."""
    cur: Any = _config
    for part in key_path.split("."):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        else:
            return default
    return cur


def env_or_config(key_path: str, env_var: str, default: str = "") -> str:
    """Environment variable takes priority, then config, then default."""
    env_val = os.environ.get(env_var, "").strip()
    if env_val:
        return env_val
    cfg_val = str(get(key_path, default) or default).strip()
    return cfg_val


# Flat view for common usages
def where_to_create() -> str:
    """Path where the user_config.json file should be created (displayed if absent)."""
    return str(CONFIG_PATH)


__all__ = [
    "CONFIG_PATH",
    "EXAMPLE_PATH",
    "DEFAULTS",
    "load_config",
    "get",
    "env_or_config",
    "PATHS",
    "SKOOL",
    "SCRAPER",
    "KB",
    "where_to_create",
]
