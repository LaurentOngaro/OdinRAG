"""_Helpers/scripts/lib/private_paths.py - Single source of truth for private/paywalled path rules.

Loads `_Helpers/config/private_paths.jsonc` and merges `"scope": "private"` entries
from `_Helpers/links.jsonc`. Python stdlib-only so CI runners work without pip installs.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from .user_config import load_jsonc_file

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONFIG_PATH = REPO_ROOT / "_Helpers" / "config" / "private_paths.jsonc"


@dataclass(frozen=True)
class PrivatePathsConfig:
    """Resolved private path rules shared by publish and audit scripts."""

    strip_rules: tuple[str, ...]
    forbidden_patterns: tuple[tuple[str, str], ...]
    any_depth_segments: tuple[tuple[str, str], ...]
    allowed_readmes: frozenset[str]


def load_private_paths(config_path: Path = DEFAULT_CONFIG_PATH, repo_root: Path = REPO_ROOT) -> PrivatePathsConfig:
    """Load private path rules from JSONC config and linked private projects."""
    raw = load_jsonc_file(config_path)
    if not raw:
        raise FileNotFoundError(f"Missing or empty private paths config: {config_path}")

    strip_rules: list[str] = []
    forbidden: list[tuple[str, str]] = []
    seen_rules: set[str] = set()

    def _add_prefix(raw_path: str, reason: str) -> None:
        clean = raw_path.strip().strip("/")
        if not clean or clean in seen_rules:
            return
        seen_rules.add(clean)
        strip_rules.append(clean)
        forbidden.append((f"{clean}/", reason))

    for entry in raw.get("prefixes", []):
        if isinstance(entry, dict):
            _add_prefix(str(entry.get("path", "")), str(entry.get("reason", "Private path")))

    if raw.get("include_private_links", False):
        links_rel = str(raw.get("links_manifest", "_Helpers/links.jsonc")).strip()
        link_reason = str(raw.get("private_link_reason", "Personal project (never push)"))
        links_data = load_jsonc_file(repo_root / links_rel)
        for link_entry in links_data.get("links", []):
            if isinstance(link_entry, dict) and link_entry.get("scope") == "private":
                _add_prefix(str(link_entry.get("link", "")), link_reason)

    any_depth: list[tuple[str, str]] = []
    for seg_entry in raw.get("any_depth_segments", []):
        if isinstance(seg_entry, dict):
            seg = str(seg_entry.get("segment", "")).strip().strip("/")
            reason = str(seg_entry.get("reason", f"Nested {seg}/ directory is private"))
            if seg:
                any_depth.append((seg, reason))

    allowed = frozenset(
        str(p).replace("\\", "/").strip("/")
        for p in raw.get("allowed_readmes", [])
        if str(p).strip()
    )

    return PrivatePathsConfig(
        strip_rules=tuple(strip_rules),
        forbidden_patterns=tuple(forbidden),
        any_depth_segments=tuple(any_depth),
        allowed_readmes=allowed,
    )


def match_violation_reason(path: str, config: PrivatePathsConfig, *, respect_allowed_readmes: bool = True) -> str | None:
    """Return the violation reason if `path` is private/forbidden, else `None`."""
    normalized = path.replace("\\", "/").lstrip("/")
    if not normalized:
        return None
    if respect_allowed_readmes and normalized in config.allowed_readmes:
        return None

    for prefix, reason in config.forbidden_patterns:
        bare = prefix.rstrip("/")
        if normalized == bare or normalized.startswith(prefix):
            return reason

    parts = normalized.split("/")
    for seg, reason in config.any_depth_segments:
        if seg in parts:
            return reason

    return None


def find_violations(paths: Iterable[str], config: PrivatePathsConfig, *, respect_allowed_readmes: bool = True) -> list[tuple[str, str]]:
    """Return `(path, reason)` pairs for every forbidden path in `paths`."""
    violations: list[tuple[str, str]] = []
    for path in paths:
        reason = match_violation_reason(path, config, respect_allowed_readmes=respect_allowed_readmes)
        if reason is not None:
            violations.append((path, reason))
    return violations
