#!/usr/bin/env python3
"""
_Helpers/scrape_skool.py - Skool Course Scraper (programvideogames)

Extracts every lesson of the Skool "programvideogames" group (courses ->
modules -> lessons) and exports them as structured Markdown with frontmatter
metadata (title, duration, associated YouTube video). Optionally downloads
the YouTube videos and/or the support files (ZIP) attached to the lessons.

Usage:
python _Helpers/scrape_skool.py [options]

Options:
--download-video, -dv              Also download the lessons' YouTube videos via yt-dlp.
--download-video-folder PATH       Target folder for YouTube videos. Default: DEFAULT_DOWNLOAD_VIDEO_FOLDER.
--download-support-files, -ds      Also download the attached files (ZIP, images, etc.) declared in metadata.resources. Placed in <course>/Support Files/<NNN-slug>/<file>.
                                    Idempotent: does not re-download already-present files.
                                    Strategy: parse metadata.resources (JSON), resolve the signed URL
                                    via POST https://api2.skool.com/files/<file_id>/download-url (auth via skool-cli cookies). Fallback: scan .zip links in the already-exported Markdown.
--overwrite-existing-lessons, -f   Force the re-download and re-write of already-exported lessons (default: idempotent skip).
--lesson, -l PATTERN               Filter the lessons to process (fuzzy case-insensitive substring on the normalised title). The normalisation replaces every non-alphanumeric character by a space, so
                                    --lesson "editor-side-panel" matches the title "2.41 - Editor Side Panel (ImGui) (10:53)".
                                    Ex: --lesson "entities state physics" only processes the lesson whose title contains those words.
                                    Without --lesson: all the lessons of the course are exported.
--skip-until INDEX                 Skip the first INDEX lessons (global counter across all courses) and start processing from lesson INDEX+1. Useful to resume a long scrape after an interruption.
                                    Ex: --skip-until 50 skips lessons 1..50 and processes from the 51st.
                                    Without --skip-until: no lesson is skipped by this mechanism (--lesson remains priority for filtering).
--add-index                        Add a numeric index prefix to the downloaded videos
                                    ({i+1:03d}-{slug}.mp4 instead of {slug}.mp4). By default
                                    (False), videos use a stable name based on the slug only - avoids name collisions between runs
                                    when --lesson is used (the index changes with the filtered list). Markdown lessons always keep their index prefix for reading order.
--add-duration                     Keep the duration suffix (MM:SS or H:MM:SS) of the Skool title in the filename -> the slug ends with the duration digits (ex: ...editor-side-panel-imgui-1053).
                                    By default (False), this suffix is removed -> shorter name (ex: ...editor-side-panel-imgui). The duration stays visible in the Markdown frontmatter.

Prerequisites:
- Windows: DEFENDER FIREWALL DISABLED (OTHERWISE PLAYWRIGHT CHROMIUM -> ERR_NETWORK_ACCESS_DENIED)
- Python 3.10+
- Node.js + npm:  npm install -g skool-cli  then  npx playwright install chromium
- For --download-video: yt-dlp (PATH or YT_DLP_EXE); ffmpeg recommended
- skool-cli patches applied in %AppData%/npm/node_modules/skool-cli/dist/core/
    browser-manager.js: blocks *.awssaf.com (AWS WAF challenge.js)
    page-ops.js        : goto retries with waitUntil:"commit" on timeout

Credentials (priority order):
1. Env vars SKOOL_EMAIL / SKOOL_PASSWORD  (CI, containers)
2. File .private/skool_credentials.txt        (gitignored, local)
3. Interactive prompt (password masked via getpass)

YouTube cookies (optional but recommended to avoid the rate-limit):
- Env var YOUTUBE_COOKIES_FILE=/path/cookies.txt (Netscape format)
"""

import argparse
import shutil
import subprocess
import json
import os
import re
import sys
import time
import html
from pathlib import Path
from datetime import datetime
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

# Helpers réutilisables (lib/ + _Helpers/)
sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib.text_clean import repair_mojibake  # noqa: E402
from odin_format import format_path_if_odin  # noqa: E402


# get root directory
ROOT_DIR = Path(__file__).resolve().parent.parent

# ─── CREDENTIALS ────────────────────────────────────────────────────────────────
SKOOL_EMAIL: str = ""
SKOOL_PASSWORD: str = ""
# Priorité de chargement :
#   1. Variables d'env SKOOL_EMAIL / SKOOL_PASSWORD  (CI, conteneurs)
#   2. KEY=VALUE file at .private/skool-credentials.txt  (gitignored, local use)
#   3. Prompt interactif (mot de passe masqué via getpass)
CREDENTIALS_FILE = ROOT_DIR /"_Helpers" / ".private" / "skool_credentials.txt"
# YouTube cookies (optional but recommended to avoid the rate-limit):
#   1. Install the browser extension "Get cookies.txt LOCALLY"
#   2. Visit youtube.com (signed in to your account)
#   3. Export to a .txt file (Netscape format)
#   4. Set YOUTUBE_COOKIES_FILE=/path/to/cookies.txt (env var) or fill in here:
YOUTUBE_COOKIES_FILE: str | Path | None = ROOT_DIR /"_Helpers" / ".private" / "cookies.txt"


# ─── CONFIG ───────────────────────────────────────────────────────────────────
SKOOL_GROUP     = "programvideogames"  # nom du groupe Skool
OUTPUT_DIR     = ROOT_DIR / "odin-knowledge-base" / "courses" / "programvideogames"
DELAY_BETWEEN  = 1.0   # secondes entre chaque appel Skool (politesse)

# yt-dlp: read in this order - env var YT_DLP_EXE > user_config.json paths.yt_dlp_exe > empty string
from _Helpers.lib.user_config import env_or_config
YT_DLP_EXE     = env_or_config("paths.yt_dlp_exe", "YT_DLP_EXE")

# Video download
VIDEO_DELAY_BETWEEN = 8.0   # seconds between each YouTube download

# Support files download (ZIP attached to lessons)
SUPPORT_FILES_DELAY = 1.0   # seconds between each support download

# Retry limit for YouTube video download (yt-dlp) and Skool API calls (get-lesson, download-url)
MAX_VIDEO_RETRIES = 3

# ZIPs are referenced via metadata.resources (JSON-encoded) in the get-lesson
# response. URL resolution goes through the Skool API:
# Cookies are stored by skool-cli on connection.
SKOOL_AUTH_STATE = Path.home() / ".skool-cli" / "auth-state.json"
SKOOL_API_BASE   = "https://api2.skool.com"

# stderr markers that indicate a YouTube rate-limit / anti-bot
ANTI_BOT_MARKERS: tuple[str, ...] = (
    "Sign in to confirm",
    "not a bot",
    "HTTP Error 429",
    "HTTP Error 403",
)

# Default YouTube videos download folder
DEFAULT_DOWNLOAD_VIDEO_FOLDER = (
    "M:/Elearning_EnCours/Game Dev Autres/Odin"
    "/Dylan Falconer - Program Video Game"
)

# Pattern de durée en fin de titre Skool : "(10:53)" ou "(1:23:45)".
# Capturé en suffixe des titres de leçons, supprimé par défaut du slug
# (--add-duration option to keep it).
_DURATION_RE = re.compile(
    r"\s*\(\s*\d+(?::\d{1,2}){0,2}\s*(?:min)?\s*\)\s*$"
)


def slugify(text: str, keep_duration: bool = False) -> str:
    """Convert a title into a safe filename or folder name.

    If ``keep_duration`` is False (default), the trailing ``(MM:SS)`` or
    ``(H:MM:SS)`` suffix is stripped before slugging, so the filename has
    no duration digits at the end. If True, the suffix is preserved and
    the slug ends with those digits (e.g. ``...imgui-1053``).
    """
    if not keep_duration:
        text = _DURATION_RE.sub("", text)
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    text = re.sub(r"^-+|-+$", "", text)
    return text or "untitled"

# Lesson-number pattern at the start of the title: "2.06 - ", "1.5 - ", etc.
# Utilisé par ``lesson_filename_from_title`` pour produire un préfixe naturel
# type "206-" (sans point) avant le titre réel.
_LESSON_NUM_RE = re.compile(r"^(\d+)\.(\d+)\s*[-–-]\s*")

# Caractères interdits par Windows (et Linux en pratique) pour les noms de
# files. Spaces, commas, parentheses are PRESERVED (readable names).
_WIN_FORBIDDEN = re.compile(r'[<>:"/\\|?*\x00-\x1f]')

# ─── LOG ──────────────────────────────────────────────────────────────────────
# Log level: ERROR | INFO | WARNING | DEBUG (default INFO).
#   INFO    -> errors + results (per lesson / video / support).
#   WARNING -> adds yt-dlp and skool-cli warnings.
#   DEBUG   -> adds API/skool-cli/yt-dlp calls (verbose).
# Override via env : SKOOL_LOG_LEVEL=DEBUG  (ou WARNING, INFO, ERROR).
LOG_LEVEL = os.environ.get("SKOOL_LOG_LEVEL", "INFO").upper()
LOG_FILE = Path(__file__).resolve().parent / "logs" / f"{Path(__file__).stem}.log"
_LOG_LEVELS = {"ERROR": 1, "INFO": 2, "WARNING": 3, "DEBUG": 4}
_LOG_LEVEL_NUM = _LOG_LEVELS.get(LOG_LEVEL, 2)
_LOG_ENABLED = False


def _init_log(reset: bool = False) -> None:
    """Initialise the log file (cumulative by default, opt-in reset).
    By default the log is APPEND-only: each run appends its lines after
    With ``reset=True`` (--log-reset flag), the file is fully overwritten
    before writing the new header.
    """
    global _LOG_ENABLED
    try:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        mode = "w" if reset else "a"
        with LOG_FILE.open(mode, encoding="utf-8") as f:
            f.write(
                f"\n{'=' * 70}\n"
                f"=== RUN START - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n"
                f"=== Script : {Path(__file__).name}\n"
                f"=== Log level : {LOG_LEVEL}\n"
                f"=== Groupe    : {SKOOL_GROUP}\n"
                f"=== Output    : {OUTPUT_DIR}\n"
                + "=" * 70 + "\n"
            )
        _LOG_ENABLED = True
        action = "reset" if reset else "append"
        print(f"[*] Log → {LOG_FILE} (niveau {LOG_LEVEL}, mode {action})")
    except OSError as e:
        print(f"[WARN] Log désactivé ({LOG_FILE}): {e}")
        _LOG_ENABLED = False


def _log(level: str, message: str) -> None:
    """Append une ligne horodatée au log. No-op si niveau trop verbeux."""
    if not _LOG_ENABLED:
        return
    if _LOG_LEVELS.get(level, 0) > _LOG_LEVEL_NUM:
        return
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with LOG_FILE.open("a", encoding="utf-8") as f:
            f.write(f"[{ts}] [{level:<7}] {message}\n")
    except OSError:
        pass


def _parse_credentials_file(path: Path) -> dict[str, str]:
    """Read a KEY=VALUE file, ignore blanks/comments, unquote the values."""
    credentials: dict[str, str] = {}
    if not path.exists():
        return credentials
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as e:
        print(f"[!] Impossible de lire {path}: {e}")
        return credentials

    SKOOL_EMAIL=lines[0].strip()
    SKOOL_PASSWORD=lines[1].strip()
    credentials["SKOOL_EMAIL"] = SKOOL_EMAIL
    credentials["SKOOL_PASSWORD"] = SKOOL_PASSWORD
    # for raw in lines:
    #     line = raw.strip()
    #     if not line or line.startswith("#"):
    #         continue
    #     if "=" not in line:
    #         continue
    #     key, _, value = line.partition("=")
    #     credentials[key.strip().upper()] = value.strip().strip('"').strip("'")
    return credentials


def setup_credentials() -> None:
    """Initialise SKOOL_EMAIL/SKOOL_PASSWORD (env > user_config.json > file > prompt).

    Priority order:
    1. Environment variables SKOOL_EMAIL / SKOOL_PASSWORD (CI, containers)
    2. skool.email field of _Helpers/.private/user_config.json
    3. File .private/skool_credentials.txt
    4. Interactive prompt (password masked via getpass)
    """
    global SKOOL_EMAIL, SKOOL_PASSWORD

    credentials = _parse_credentials_file(CREDENTIALS_FILE)
    # Priority 1: environment variables
    credentials["SKOOL_EMAIL"] = os.environ.get("SKOOL_EMAIL", credentials.get("SKOOL_EMAIL", ""))
    credentials["SKOOL_PASSWORD"] = os.environ.get("SKOOL_PASSWORD", credentials.get("SKOOL_PASSWORD", ""))
    # Priority 2: _Helpers/.private/user_config.json (skool.email only - password stays env/file/prompt)
    try:
        from _Helpers.lib.user_config import SKOOL as _SKOOL
        if not credentials["SKOOL_EMAIL"]:
            credentials["SKOOL_EMAIL"] = _SKOOL.get("email", "")
    except (ImportError, OSError):
        pass

    SKOOL_EMAIL = credentials["SKOOL_EMAIL"].strip()
    SKOOL_PASSWORD = credentials["SKOOL_PASSWORD"]


def lesson_filename_from_title(title: str, idx: int | None = None, keep_duration: bool = False) -> str:
    """Build a readable video filename from the Skool title.

    The lesson number at the start (``2.06 - ...``) becomes a prefix
    ``206-`` (without the dot). If the title has NO lesson number
    (``Introduction to Odin and Raylib (3min)``) and ``idx`` is provided,
    a positional prefix ``{idx+1:03d}-`` is used as a fallback.
    The rest of the title is preserved as-is (spaces, commas,
    ampersands) after sanitising only the Windows-forbidden characters
    (``<>:"/\\|?*``).

    Examples:
        ``"2.06 - Events, Entity Update, Debug Draw (15:04)"`` (idx=40)
            → ``"206-Events, Entity Update, Debug Draw"``        (default)
            → ``"206-Events, Entity Update, Debug Draw (15-04)"`` (--add-duration)
        ``"1.05 - Deep Dive into the Compiler (1:23:45)"``
            → ``"105-Deep Dive into the Compiler"``
        ``"Introduction to Odin and Raylib (3min)"`` (idx=0)
            → ``"001-Introduction to Odin and Raylib"``
        ``"Bonus Q&A"`` (pas de numéro, idx=None)
            → ``"Bonus Q&A"``
    """
    # 1. Extract and remove the lesson number at the start (natural prefix).
    #    Positional fallback if no number and idx provided.
    prefix = ""
    m = _LESSON_NUM_RE.match(title)
    if m:
        major, minor = m.groups()
        prefix = f"{major}{int(minor):02d}-"
        title = title[m.end():]
    elif idx is not None:
        prefix = f"{idx+1:03d}-"

    # 2. Duration suffix (optional). If kept, ":" -> "-" for
    #    la compatibilité Windows (les `:` sont interdits dans les noms).
    if keep_duration:
        title = title.replace(":", "-")
    else:
        title = _DURATION_RE.sub("", title)

    # 3. Nettoyer les séparateurs autour du titre restant
    title = title.strip(" -–-")

    # 4. Sanitise for Windows (keep spaces, commas, `()`, apostrophes, etc.)
    safe = _WIN_FORBIDDEN.sub("_", title)
    safe = re.sub(r"_+", "_", safe).strip(". ")

    return (prefix + safe).strip() or "video"


# ╔═══════════════════════════════════════════════════════════════════════════════╗
# ║  ONE-SHOT CLEANUP - REMOVE AFTER USE                                         ║
# ╚═══════════════════════════════════════════════════════════════════════════════╝
#
# Retire la durée ``(MM:SS)`` / ``(H:MM:SS)`` / ``(Nmin)`` du titre H1
# (``# {title}``) of the markdown files already generated by previous runs
# previous runs - BEFORE ``lesson_to_markdown`` starts processing
# supprimer automatiquement (déploiement progressif).
#
# Strategy: for each ``*.md`` under ``OUTPUT_DIR``, locate the line
# ``# <title>`` et applique ``_DURATION_RE.sub("", title)`` au titre.
# The rest of the file is untouched. Idempotent.
#
# WARNING: Modifies ALL .md under OUTPUT_DIR. Backup recommended before use.
ONE_SHOT_CLEANUP_MD_TITLES = True  # ← Mettre à False (ou supprimer) après usage


def _clean_md_titles(root: Path) -> tuple[int, int]:
    """Strip the duration from the H1 of the markdown files under ``root``.

    Retourne ``(fichiers_modifiés, fichiers_scannés)``.
    """
    if not ONE_SHOT_CLEANUP_MD_TITLES:
        return 0, 0

    cleaned = scanned = 0
    h1_re = re.compile(r"^#\s+(.+)$")
    for md_path in root.rglob("*.md"):
        # Ignore les index de cours (README.md) : on ne touche que les leçons.
        if md_path.name.lower() == "readme.md":
            scanned += 1
            continue
        scanned += 1
        try:
            content = md_path.read_text(encoding="utf-8")
        except OSError:
            continue

        new_lines = []
        modified = False
        for line in content.splitlines():
            m = h1_re.match(line)
            if m and not _DURATION_RE.search(m.group(1)) is False:
                # Plus simple : juste tester si la ligne H1 contient # un pattern de durée, et si oui, le retirer.
                pass
            stripped_line = line.strip()
            if stripped_line.startswith("# ") and not stripped_line.startswith("## "):
                # This is an H1 (not H2+). Strip the duration from the title.
                title_part = stripped_line[2:].strip()
                new_title = _DURATION_RE.sub("", title_part).strip()
                if new_title != title_part:
                    new_line = f"# {new_title}"
                    # Preserve the original indentation if any
                    indent = line[:len(line) - len(line.lstrip())]
                    new_line = indent + new_line
                    new_lines.append(new_line)
                    modified = True
                    continue
            new_lines.append(line)

        if modified:
            try:
                md_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
                cleaned += 1
                _log("INFO", f"  [md-cleanup] H1 nettoyé : {md_path}")
            except OSError as e:
                _log("ERROR", f"  [md-cleanup FAIL] {md_path}: {e}")
    return cleaned, scanned


def _normalize_for_match(s: str) -> str:
    """Normalise une chaîne pour le matching fuzzy du filtre --lesson.

    Remplace tout caractère non-alphanumérique par un espace et collapse les espaces. Permet à ``--lesson editor-side-panel`` de matcher
    ``"2.41 - Editor Side Panel (ImGui) (10:53)"`` (hyphens vs espaces).
    """
    return re.sub(r"[^\w]+", " ", s, flags=re.UNICODE).strip()


def run_skool(args: list[str], retries: int = 3) -> dict | list | None:
    """Run a skool-cli command and return the parsed JSON output."""
    cmd = ["skool.cmd"] + args + ["--json"]
    _log("DEBUG", f"run_skool: {' '.join(cmd)}")
    for attempt in range(retries):
        result = None
        try:
            result = subprocess.run(
                cmd,
                capture_output=True, text=True, check=True, timeout=120
            )
            raw = result.stdout.strip()
            if not raw:
                _log("DEBUG", f"run_skool OK (empty body) : {' '.join(cmd)}")
                return None
            data = json.loads(raw)
            _log("DEBUG", f"run_skool OK ({len(raw)} chars): {' '.join(cmd)}")
            return data
        except subprocess.CalledProcessError as e:
            print(f"  [ERR] Command failed (attempt {attempt+1}/{retries}): {' '.join(cmd)}")
            print(f"        stderr: {e.stderr.strip()[:200]}")
            _log("ERROR", f"run_skool FAIL (attempt {attempt+1}/{retries}): {' '.join(cmd)} | stderr={e.stderr.strip()[:160]}")
            if attempt < retries - 1:
                time.sleep(3)
        except json.JSONDecodeError as e:
            print(f"  [ERR] Invalid JSON: {e}")
            if result is not None:
                print(f"        stdout: {result.stdout[:200]}")
            return None
    return None


def login() -> bool:
    """Authentification via skool-cli (stocke la session dans ~/.skool-cli/)."""
    auth_state = Path.home() / ".skool-cli" / "auth-state.json"
    if auth_state.exists():
        print(f"[*] Session déjà active ({auth_state}), skip login.")
        return True

    print(f"[*] Connexion en tant que {SKOOL_EMAIL}...")
    try:
        subprocess.run(
            ["skool.cmd", "login", "--email", SKOOL_EMAIL, "--password", SKOOL_PASSWORD],
            check=True, capture_output=True, text=True, timeout=120
        )
        print("[+] Connecté.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERR] Login échoué: {e.stderr}")
        return False


def get_courses() -> list[dict]:
    """Liste tous les cours du groupe."""
    print(f"[*] Fetching courses from '{SKOOL_GROUP}'...")
    data = run_skool(["list-courses", "-g", SKOOL_GROUP])
    if not data:
        return []
    # skool-cli returns {"courses": [...]} or directly a list
    courses = data.get("courses", data) if isinstance(data, dict) else data
    print(f"[+] {len(courses)} cours trouvés.")
    return courses


def get_lessons(course_name: str) -> list[dict]:
    """Flat list of lessons (folders + root lessons) with id, folder, href."""
    data = run_skool(["list-lessons", "-g", SKOOL_GROUP, "--course", course_name])
    if not data:
        return []
    flat: list[dict] = []
    for item in data:
        if item.get("type") == "folder":
            folder_name = item.get("name", "")
            for child in item.get("children", []):
                flat.append({
                    "title":  child.get("name", "Sans titre"),
                    "id":     child.get("id", ""),
                    "folder": folder_name,
                    "href":   child.get("href", ""),
                })
        else:
            flat.append({
                "title":  item.get("name", "Sans titre"),
                "id":     item.get("id", ""),
                "folder": None,
                "href":   item.get("href", ""),
            })
    return flat


def _count_total_lessons(courses: list[dict], lesson_filter: str | None) -> int:
    """Compte le nombre total de leçons à traiter dans ce run (après --lesson).

    Coûte 1 appel skool-cli ``list-lessons`` par cours (le même appel
    is redone later in ``export_course``, but this double-call
    displays the progress "lesson N/TOTAL analysis" as soon as
    la première leçon).
    """
    total = 0
    for course in courses:
        course_name = course.get("title", course.get("name", "unknown"))
        lessons = get_lessons(course_name)
        if not lessons:
            continue
        if lesson_filter:
            norm_pattern = _normalize_for_match(lesson_filter)
            norm_re = re.compile(re.escape(norm_pattern), re.IGNORECASE)
            lessons = [
                ls for ls in lessons
                if norm_re.search(_normalize_for_match(ls.get("title", "")))
            ]
        total += len(lessons)
    return total


def fetch_lesson_content(lesson: dict) -> dict:
    """Fetch the full content (HTML, video) via `get-lesson --url`."""
    href = lesson.get("href", "")
    if not href:
        return {}
    url = href if href.startswith("http") else f"https://www.skool.com{href}"
    result = run_skool(["get-lesson", "--url", url])
    return result if isinstance(result, dict) else {}


def html_to_markdown(raw_html: str) -> str:
    """Convertit le HTML Skool (TipTap) en Markdown lisible."""
    if not raw_html:
        return ""
    import textwrap

    s = raw_html

    s = re.sub(r"(?i)<br\s*/?>", "\n", s)
    s = re.sub(r"(?is)<pre>\s*<code[^>]*class=\"language-([^\"]*)\"[^>]*>(.*?)</code>\s*</pre>",
                lambda m: f"\n\n```{m.group(1)}\n{m.group(2).strip()}\n```\n\n", s)
    s = re.sub(r"(?is)<pre>\s*<code[^>]*>(.*?)</code>\s*</pre>",
                lambda m: f"\n\n```odin\n{m.group(1).strip()}\n```\n\n", s)
    s = re.sub(r"(?is)<pre>(.*?)</pre>",
                lambda m: f"\n\n```odin\n{m.group(1).strip()}\n```\n\n", s)

    s = re.sub(r"(?is)<img\s+[^>]*src=\"([^\"]+)\"[^>]*alt=\"([^\"]*)\"[^>]*/?>",
                lambda m: f"\n\n![{m.group(2)}]({m.group(1)})\n\n", s)
    s = re.sub(r"(?is)<img\s+[^>]*src=\"([^\"]+)\"[^>]*/?>",
                lambda m: f"\n\n![]({m.group(1)})\n\n", s)

    s = re.sub(r"(?is)<a\s+[^>]*href=\"([^\"]+)\"[^>]*>(.*?)</a>",
                lambda m: f"[{re.sub(r'<[^>]+>', '', m.group(2)).strip()}]({m.group(1)})", s)

    s = re.sub(r"(?is)<strong[^>]*>(.*?)</strong>", r"**\1**", s)
    s = re.sub(r"(?is)<b[^>]*>(.*?)</b>", r"**\1**", s)
    s = re.sub(r"(?is)<em[^>]*>(.*?)</em>", r"*\1*", s)
    s = re.sub(r"(?is)<i[^>]*>(.*?)</i>", r"*\1*", s)
    s = re.sub(r"(?is)<u[^>]*>(.*?)</u>", r"__\1__", s)
    s = re.sub(r"(?is)<code[^>]*>(.*?)</code>", r"`\1`", s)

    def _heading(m):
        level = int(m.group(1))
        inner = m.group(2)
        inner = re.sub(r"<[^>]+>", "", inner)
        inner = html.unescape(inner).strip()
        return f"\n\n{'#' * level} {inner}\n\n"

    s = re.sub(r"(?is)<h([1-6])[^>]*>(.*?)</h\1>", _heading, s)

    def _list(m):
        tag = m.group(1).lower()
        body = m.group(2)
        items = re.findall(r"(?is)<li[^>]*>(.*?)</li>", body)
        out_list = []
        for idx, item in enumerate(items, start=1):
            text = re.sub(r"<[^>]+>", "", item)
            text = html.unescape(text).strip()
            text = re.sub(r"\s+", " ", text)
            if tag == "ol":
                out_list.append(f"{idx}. {text}")
            else:
                out_list.append(f"- {text}")
        return "\n\n" + "\n".join(out_list) + "\n\n"

    s = re.sub(r"(?is)<(ul|ol)[^>]*>(.*?)</\1>", _list, s)

    s = re.sub(r"(?is)</?p[^>]*>", "\n\n", s)
    s = re.sub(r"(?is)</?div[^>]*>", "\n", s)
    s = re.sub(r"(?is)</?span[^>]*>", "", s)

    def _blockquote(m):
        inner = m.group(1)
        inner = re.sub(r"(?is)</?p[^>]*>", " ", inner)
        inner = re.sub(r"<[^>]+>", "", inner)
        inner = html.unescape(inner).strip()
        inner = re.sub(r"[ \t]+", " ", inner)
        inner = re.sub(r" *\n *", "\n", inner)
        quoted = "\n".join("> " + ln if ln.strip() else ">" for ln in inner.splitlines())
        return f"\n\n{quoted}\n\n"

    s = re.sub(r"(?is)<blockquote[^>]*>(.*?)</blockquote>", _blockquote, s)

    s = re.sub(r"<[^>]+>", "", s)

    # Répare le mojibake 'UTF-8 lu comme Latin-1' : box-drawing cassé # (├ ─ │ └ ...), typographie curly (’ “ ” – - … €), accents # français (é è à ç ...), NBSP double-encodé (Â ). Voir # ``_Helpers/text_clean.py`` pour la table complète.
    s = repair_mojibake(s)

    s = html.unescape(s)

    s = re.sub(r"\x1b\[[0-9;]*m", "", s)
    s = re.sub(r"\*\*(?=\*\*)", "** ", s)
    s = re.sub(r"(?<= )\*\*(?=\w)", "**", s)
    s = re.sub(r"(?<=\w)\*\*(?= )", "**", s)

    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r" *\n *", "\n", s)
    s = re.sub(r"\n{3,}", "\n\n", s)

    out: list[str] = []
    in_code = False
    for line in s.split("\n"):
        if line.startswith("```"):
            in_code = not in_code
            out.append(line)
            continue
        if in_code or not line.strip():
            out.append(line)
            continue
        if re.match(r"^#{1,6} ", line) or re.match(r"^> ", line) or re.match(r"^[-*] ", line) or re.match(r"^\d+\. ", line):
            out.append(line)
            continue
        out.append(textwrap.fill(line, width=100, break_long_words=False, break_on_hyphens=False))

    return "\n".join(out).strip()


def lesson_to_markdown(lesson: dict, course_name: str, folder: str | None, content: dict) -> str:
    """Generate the full Markdown of a lesson."""
    title     = lesson.get("title", "Sans titre")
    lesson_id = lesson.get("id", "")
    metadata  = content.get("metadata", {}) or {}
    video_url  = metadata.get("videoLink")  or content.get("videoLink", "")
    thumb_url  = metadata.get("videoThumbnail", "")
    duration_ms = metadata.get("videoLenMs", 0)
    duration_min = round(duration_ms / 60000, 1) if duration_ms else 0
    body      = content.get("html", "")

    lines = [
        "---",
        f"Cours: \"{course_name}\"",
    ]
    if folder:
        lines.append(f"Module: \"{folder}\"")
    if lesson_id:
        lines.append(f"ID: \"{lesson_id}\"")
    if duration_min:
        lines.append(f"Durée: {duration_min} min")
    lines += ["---", ""]

    # H1 : strip la durée du titre (cohérent avec le naming des fichiers).
    # La durée reste visible dans le frontmatter ci-dessus ("Durée: 10.9 min").
    title_for_md = _DURATION_RE.sub("", title).strip()
    lines.append("")
    lines.append(f"# {title_for_md}")
    lines.append("")
    if video_url:
        lines.append("## 🎬 Vidéo")
        lines.append("")
        if thumb_url:
            lines.append(f"[![Vidéo]({thumb_url})]({video_url})")
            lines.append("")
        lines.append(f"- **Lien** : [{video_url}]({video_url})")
        if duration_min:
            lines.append(f"- **Durée** : {duration_min} min")
        lines.append("")

    if body:
        md_body = html_to_markdown(body)
        if md_body:
            lines += ["## 📝 Contenu", "", md_body, ""]
        else:
            lines += ["## 📝 Content", "", "_Empty content._", ""]
    else:
        lines += ["## 📝 Contenu", "", "_Contenu non récupéré._", ""]

    return "\n".join(lines)


def _is_anti_bot(stderr: str) -> bool:
    """Detect a YouTube rate-limit / anti-bot in stderr."""
    return any(marker in stderr for marker in ANTI_BOT_MARKERS)


def download_video(video_url: str, target_dir: Path, lesson_slug: str) -> Path | None:
    """Download a YouTube video with yt-dlp into target_dir.

    Returns the path of the downloaded file, or None on failure.

    Optimised strategy in 3 cycles per family:
    - Cycle 1 : ``android_vr`` **sans cookies** - marche pour 99% des vidéos (publiques + unlisted) en 1 tentative. Seul client qui déverrouille les formats élevés ; mais skippé par yt-dlp dès qu'un mode cookies est actif (peu importe --cookies ou --add-header).
    - Cycle 2 (rate-limit): ``web`` + ``--cookies`` - different client/IP, so not yet rate-limited. Covers the videos where android_vr hasté bloqué par anti-bot.
    - Cycle 3 (persistent rate-limit): ``ios`` + ``--cookies`` - third bucket. If even this fails, accept the failure.
    Chaque cycle essaie 3 formats (137+140, 136+140, 18) sauf si anti-bot détecté dès l'attempt 1 (early-exit → backoff immédiat).

    Anti-bot : backoff exponentiel 90s → 180s → 360s entre cycles.
    Cookies : voir YOUTUBE_COOKIES_FILE (utilisé cycles 2-3).
    """
    target_dir.mkdir(parents=True, exist_ok=True)
    output_template = str(target_dir / f"{lesson_slug}.%(ext)s")

    yt_exe = YT_DLP_EXE if (YT_DLP_EXE and Path(YT_DLP_EXE).exists()) else (
        shutil.which("yt-dlp") or shutil.which("yt-dlp.exe") or "yt-dlp"
    )
    has_ffmpeg = bool(shutil.which("ffmpeg") or shutil.which("ffmpeg.exe"))

    # Cookies: config OR env variable, normalised as Path.
    cookies_path: Path | None = None
    cookies_src = YOUTUBE_COOKIES_FILE or os.environ.get("YOUTUBE_COOKIES_FILE")
    if cookies_src:
        cookies_path = Path(cookies_src).expanduser()
        if not cookies_path.exists():
            print(f"  [WARN] Fichier cookies introuvable : {cookies_path} (ignoré)")
            cookies_path = None

    # Formats par qualité (mp4 m4a muxés si ffmpeg, sinon combiné 18).
    if has_ffmpeg:
        fmts: list[tuple[str, bool]] = [
            ("137+140", True),   # 1080p vidéo + audio m4a
            ("136+140", True),   # 720p
            ("18",     False),   # 360p combiné (fallback si ffmeg ou rate-limit)
        ]
    else:
        fmts = [("18", False)]
        print("  [i] ffmpeg missing -> reduced quality (360p combined)")

    # 3 cycles × 1 famille × 3 formats. Chaque cycle est homogène (même client).
    # On change de famille uniquement entre cycles (backoff anti-bot).
    cycle_families: list[tuple[str, bool]] = [
        ("android_vr", False),  # Cycle 1 : default, formats élevés
        ("web",        True),   # Cycle 2 : rate-limit fallback
        ("ios",        True),   # Cycle 3: last resort
    ]

    def make_cmd(client: str, fmt: str, needs_merge: bool, use_cookies: bool) -> list[str]:
        args = [yt_exe, "--extractor-args", f"youtube:player_client={client}"]
        if use_cookies and cookies_path:
            args += ["--cookies", str(cookies_path)]
        args += ["-f", fmt]
        if needs_merge:
            args += ["--merge-output-format", "mp4"]
        args += [
            "--no-progress",
            "--sleep-interval", "3",
            "--max-sleep-interval", "8",
            "-o", output_template,
            video_url,
        ]
        return args

    def _report_success() -> Path | None:
        mp4_path = target_dir / f"{lesson_slug}.mp4"
        if mp4_path.exists():
            print(f"  [✓] Video downloaded: {mp4_path.name}")
            _log("INFO", f"  [video OK] {mp4_path.name} ({mp4_path.stat().st_size // (1024*1024)} MB)")
            return mp4_path
        candidates = [
            p for p in target_dir.glob(f"{lesson_slug}.*")
            if not p.name.endswith(".part")
        ]
        if candidates:
            print(f"  [✓] Video downloaded: {candidates[0].name}")
            _log("INFO", f"  [video OK] {candidates[0].name} ({candidates[0].stat().st_size // (1024*1024)} MB)")
            return candidates[0]
        return None

    def _cleanup_partial() -> None:
        for pattern in (f"{lesson_slug}.*.part",
                        f"{lesson_slug}.f*.mp4",
                        f"{lesson_slug}.f*.m4a"):
            for f in target_dir.glob(pattern):
                f.unlink(missing_ok=True)

    # Pad/truncate le nombre de cycles si MAX_VIDEO_RETRIES est plus petit.
    cycles_to_run = cycle_families[:MAX_VIDEO_RETRIES]
    _log("DEBUG", f"yt-dlp start: {video_url} (cycles={len(cycles_to_run)})")

    for cycle_idx, (client, use_cookies) in enumerate(cycles_to_run):
        cycle = cycle_idx + 1
        cycle_stderr = ""
        cookie_tag = "+cookies" if use_cookies else ""
        for n, (fmt, needs_merge) in enumerate(fmts, 1):
            tag = (f"cycle {cycle}/{len(cycles_to_run)}, "
                f"tentative {n}/{len(fmts)} ({client}{cookie_tag}, {fmt})")
            print(f"  [↓] yt-dlp ({tag}) → {target_dir.name}/{lesson_slug}")
            cmd = make_cmd(client, fmt, needs_merge, use_cookies)
            _log("DEBUG", f"yt-dlp {tag}: {' '.join(cmd[:4])}…")
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            except subprocess.TimeoutExpired:
                print(f"  [ERR] yt-dlp timeout après 600s pour {video_url}")
                _log("ERROR", f"  [video FAIL] {video_url} | timeout 600s")
                return None
            except FileNotFoundError:
                print(f"  [ERR] yt-dlp introuvable (essayé: {yt_exe}). "
                "Check YT_DLP_EXE or the system PATH.")
                _log("ERROR", f"  [video FAIL] yt-dlp introuvable: {yt_exe}")
                return None

            if result.returncode == 0:
                got = _report_success()
                if got is not None:
                    return got
                return None

            _cleanup_partial()

            err_text = result.stderr or result.stdout or ""
            cycle_stderr += err_text
            err_lines = err_text.strip().splitlines()
            diagnostic = next(
                (ln for ln in err_lines if "ERROR" in ln or "WARNING" in ln), ""
            )
            print(f"  [WARN] {tag} failed (code {result.returncode})"
            + (f" : {diagnostic[:160]}" if diagnostic else ""))
            _log("DEBUG", f"yt-dlp FAIL {tag} code={result.returncode} | {diagnostic[:120]}")

            # Early-exit : si anti-bot détecté, ne pas gaspiller les formats
            # restants dans ce cycle → passer au backoff + cycle suivant.
            if _is_anti_bot(err_text):
                print(f"  [!!] Anti-bot détecté → arrêt du cycle {cycle}, "
                "passage au suivant après backoff.")
                _log("WARNING", f"  [video anti-bot] cycle {cycle} ({client}{cookie_tag})")
                break

        # All the strategies of the cycle failed. Anti-bot -> backoff + retry.
        if _is_anti_bot(cycle_stderr) and cycle < len(cycles_to_run):
            cooldown = 90 * (2 ** (cycle - 1))   # 90, 180
            print(f"  [!!] Anti-bot YouTube confirmé → pause {cooldown}s "
            f"avant cycle {cycle + 1}/{len(cycles_to_run)}...")
            time.sleep(cooldown)
            continue

        # Final failure (format not found, private video, etc.)
        print(f"  [ERR] all the strategies failed for {video_url}")
        _log("ERROR", f"  [video FAIL] {video_url} (all strategies)")
        return None

    return None


def find_zip_urls_in_markdown(md_text: str) -> list[tuple[str, str]]:
    """Trouve les liens .zip dans un Markdown déjà converti.

    The converter preserves URLs in [text](url) tags, so we scan this syntax (more reliable than re-parsing the raw HTML that would have been normalised). Deduplicates and unescapes HTML entities. Query strings are preserved in the download URL but excluded from the filename.

    Returns [(url, filename)] where ``filename`` is derived from the last path segment of the URL (without query/fragment).
    """
    if not md_text:
        return []
    pattern = re.compile(r'\[([^\]]*)\]\(([^)]+)\)')
    seen: set[str] = set()
    zips: list[tuple[str, str]] = []
    for m in pattern.finditer(md_text):
        raw_url = html.unescape(m.group(2)).strip()
        # Filtre extension .zip sur la partie path
        path = raw_url.split('?', 1)[0].split('#', 1)[0]
        if not re.search(r'\.zip$', path, re.IGNORECASE):
            continue
        if raw_url in seen:
            continue
        seen.add(raw_url)
        fname = Path(path).name or "support.zip"
        zips.append((raw_url, fname))
    return zips


def download_support_file(url: str, target_dir: Path, filename: str) -> Path | None:
    """Download a support file (ZIP) to ``target_dir/filename``.

    Idempotent: if the file exists and is non-empty, skip. Otherwise stream-download with urllib (stdlib, no external dependency), and clean up partial files on failure.

    Returns the final path of the file, or None on failure.
    """
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / filename

    if target.exists() and target.stat().st_size > 0:
        print(f"  [=] Support already present: Support Files/{target_dir.name}/{filename}")
        _log("INFO", f"  [support skip] Support Files/{target_dir.name}/{filename} (already present)")
        return target

    # Nettoyage préventif d'un .part résiduel
    part = target.with_suffix(target.suffix + ".part")
    if part.exists():
        part.unlink(missing_ok=True)

    print(f"  [↓] Support -> Support Files/{target_dir.name}/{filename}")
    _log("DEBUG", f"GET {url} -> Support Files/{target_dir.name}/{filename}")
    req = Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible; OdinRAG/1.0)"})
    try:
        with urlopen(req, timeout=120) as resp:
            with open(part, 'wb') as f:
                while True:
                    chunk = resp.read(65536)
                    if not chunk:
                        break
                    f.write(chunk)
        # Download OK -> rename .part to final file
        part.replace(target)
        size = target.stat().st_size
        print(f"  [✓] Support downloaded: {filename} ({size} bytes)")
        _log("INFO", f"  [support OK] Support Files/{target_dir.name}/{filename} ({size} bytes)")
        return target
    except (URLError, HTTPError, OSError, TimeoutError) as e:
        print(f"  [ERR] Download failure {url}: {e}")
        _log("ERROR", f"  [support FAIL] Support Files/{target_dir.name}/{filename} | {e}")
        if part.exists():
            part.unlink(missing_ok=True)
        return None


def load_skool_cookies() -> str | None:
    """Lit les cookies d'auth Skool depuis auth-state.json (sauvegardé par skool-cli).

    Retourne une chaîne Cookie: "...", ou None si indisponible.
    """
    if not SKOOL_AUTH_STATE.exists():
        return None
    try:
        state = json.loads(SKOOL_AUTH_STATE.read_text(encoding="utf-8"))
        cookies = state.get("cookies", [])
        return "; ".join(f"{c['name']}={c['value']}" for c in cookies)
    except (OSError, json.JSONDecodeError, KeyError, TypeError) as e:
        print(f"  [WARN] Lecture {SKOOL_AUTH_STATE} échouée: {e}")
        return None


def get_file_signed_url(file_id: str, cookie_header: str) -> str | None:
    """Ask the Skool API for a signed URL to download a file.

    Endpoint : POST {SKOOL_API_BASE}/files/<file_id>/download-url?expire=28800
    Response: signed URL (raw text) on files.skool.com, valid 8h.
    The download via this URL needs no additional auth.

    Note : GET /files?ids=<id> retourne bien le metadata.store_key mais aucun read_url public - Skool signe l'URL à la demande via ce POST.
    """
    url = f"{SKOOL_API_BASE}/files/{file_id}/download-url?expire=28800"
    headers = {
        "Cookie": cookie_header,
        "Accept": "*/*",
        "User-Agent": "Mozilla/5.0 (compatible; OdinRAG/1.0)",
        "Origin": "https://www.skool.com",
        "Referer": "https://www.skool.com/",
        "Content-Length": "0",
    }
    _log("DEBUG", f"POST {url} (file_id={file_id[:12]}…)")
    try:
        req = Request(url, method="POST", headers=headers)
        with urlopen(req, timeout=30) as resp:
            signed = resp.read().decode("utf-8").strip().strip('"')
            _log("DEBUG", f"POST OK status={resp.status} signed_url_len={len(signed)}")
            return signed
    except (URLError, HTTPError, OSError, TimeoutError) as e:
        print(f"  [WARN] POST /files/{file_id[:12]}…/download-url: {e}")
        _log("WARNING", f"POST /files/{file_id[:12]}…/download-url: {e}")
        return None


def parse_resources_field(resources_str: str | None) -> list[dict]:
    """Parse le champ ``metadata.resources`` (JSON-encoded string) en liste de dicts.

    Format observed on Program Video Games:
    [{"title": "metroidvania_2.5.zip",
        "file_id": "2378b3e0d01147d49d642cbfe54bd0ad",
        "file_name": "metroidvania_2.5.zip",
        "file_content_type": "application/zip"}]
    Format skool-cli (création de leçon) :
    [{"title": "...", "link": "https://..."}]
    On retourne la liste telle quelle - le code appelant gère les deux schémas.
    """
    if not resources_str:
        return []
    try:
        parsed = json.loads(resources_str)
    except (json.JSONDecodeError, TypeError):
        return []
    return parsed if isinstance(parsed, list) else []


def sanitize_filename(name: str) -> str:
    """Sanitise a filename for Windows (forbidden <>:"/\\|?*)."""
    cleaned = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '_', name)
    cleaned = re.sub(r'_+', '_', cleaned).strip('. ')
    return cleaned or "support.zip"


def export_course(course: dict, download_videos: bool = False,
            video_download_dir: Path | None = None,
            overwrite_existing_lessons: bool = False,
            download_support_files: bool = False,
            lesson_filter: str | None = None,
            add_index: bool = False,
            add_duration: bool = False,
            skip_until: int | None = None,
            lesson_counter: int = 0,
            total_lessons_run: int = 0) -> tuple[int, int]:
    """Exporte toutes les leçons d'un cours vers des fichiers Markdown.

    Affiche en début de chaque leçon :
        ``analyse leçon <cpt>/<total dans le PROCESSUS actuel> : <title>``
    où ``<cpt>`` est le compteur global incrémenté par leçon (cumul sur
    tous les cours) et ``<total>`` est ``total_lessons_run`` (calculé
    upfront dans ``main()`` via ``_count_total_lessons``).

    Le compteur ``lesson_counter`` est global (cumulé sur tous les cours
    par l'appelant). Pour chaque leçon rencontrée, on l'incrémente AVANT
    de tester ``skip_until``. Si ``skip_until`` est défini et que le
    compteur est strictement inférieur, la leçon est sautée entièrement
    (pas de fetch, pas d'écriture, pas de vidéo/support). Retourne
    ``(lesson_count_exportées, lesson_counter_final)``.

    Si ``overwrite_existing_lessons`` est False (défaut), les leçons déjà
    présentes sur disque sont réutilisées (idempotence) : aucun appel Skool,
    aucune réécriture. Le compteur ``lesson_count`` et l'index sont tout de
    même mis à jour. Les vidéos éventuelles sont laissées intactes (leur
    propre garde ``video_path.exists()`` reste actif pour le run en cours).

    Si ``lesson_filter`` est fourni, seules les leçons dont le titre matche
    (case-insensitive, re.search) sont traitées. Les autres sont skippées
    silencieusement (aucun appel Skool pour elles).

    Si ``download_support_files`` est True, lit le champ
    ``metadata.resources`` du contenu de chaque leçon (JSON-encoded list de
    ``{title, file_id, file_name, ...}``) and downloads the files
    manquants dans ``<course_dir>/Support Files/<lesson_slug>/<file>``.

    Si ``add_index`` est True, un préfixe positionnel ``{i+1:03d}-`` est
    ajouté au nom naturel de la vidéo (rarement utile : le numéro de
    leçon extrait du titre est déjà un identifiant stable). Par défaut
    (False), pas de préfixe positionnel.

    Si ``add_duration`` est True, le suffixe de durée ``(MM:SS)`` du titre
    is kept (with ``:`` -> ``-`` for Windows-safety). By default
    (False), ce suffixe est retiré. La durée reste dans le frontmatter MD.

    Les vidéos sont placées dans ``<course_video_dir>/<module?>/<name>.mp4``
    où ``<module>`` est le dossier Skool de la leçon (slugifié) - réplique
    la structure des markdown (``metroidvania/``, ``rpg/``, etc.).
    """
    course_name  = course.get("title", course.get("name", "unknown"))
    course_slug  = slugify(course_name)
    course_dir   = OUTPUT_DIR / course_slug
    course_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n[*] Cours : '{course_name}' → {course_dir}")
    _log("INFO", f"Cours: {course_name} → {course_slug}")

    # Dossier vidéos dédié à ce cours (un sous-dossier par cours)
    course_video_dir: Path | None = None
    if download_videos:
        course_video_dir = (
            (video_download_dir / course_slug) if video_download_dir
            else course_dir / "videos"
        )
        assert course_video_dir is not None  # narrow for type-checker
        course_video_dir.mkdir(parents=True, exist_ok=True)
        print(f"  [i] Videos -> {course_video_dir}")

    lessons = get_lessons(course_name)
    if not lessons:
        print(f"  [!] No lesson found (restricted access or empty course).")
        _log("WARNING", f"Cours {course_name}: aucune leçon (accès restreint?)")
        # Early return: we have not yet incremented lesson_counter (the loop
        # hasn't started), so we return the value received as parameter
        # pour ne pas casser le compteur global du caller.
        return 0, lesson_counter

    # ─── Filtre --lesson : sous-chaîne fuzzy (normalisée) sur le titre ───
    if lesson_filter:
        # Normalisation fuzzy : pattern et titre passent par _normalize_for_match
        # → "editor-side-panel" matche "Editor Side Panel (ImGui)..." (espaces vs tirets).
        norm_pattern = _normalize_for_match(lesson_filter)
        norm_re = re.compile(re.escape(norm_pattern), re.IGNORECASE)
        matched = [
            ls for ls in lessons
            if norm_re.search(_normalize_for_match(ls.get("title", "")))
        ]
        print(f"  [+] {len(lessons)} leçons trouvées, "
            f"{len(matched)} retenue(s) par --lesson '{lesson_filter}' "
            f"(normalisé: '{norm_pattern}').")
        _log("INFO", f"  Filtre '{lesson_filter}' (norm='{norm_pattern}'): "
            f"{len(matched)}/{len(lessons)} leçons retenues")
        if not matched:
            print(f"  [!] No lesson matches the pattern.")
            _log("WARNING", f"  Filtre '{lesson_filter}': 0 match")
            # Idem early return : lesson_counter pas encore incrémenté.
            return 0, lesson_counter
        lessons = matched
    else:
        print(f"  [+] {len(lessons)} leçons trouvées.")
        _log("INFO", f"  {len(lessons)} leçons trouvées")

    index_lines = [
        f"# Index - {course_name}",
        f"\nExporté le {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
    ]

    current_folder = None
    lesson_count = 0

    for i, lesson in enumerate(lessons):
        folder  = lesson.get("folder")
        title   = lesson.get("title", f"Leçon {i+1}")

        # ─── Compteur global (skip-until + progress) ──────────────────────
        # Incrémenté AVANT tout traitement pour que la 1ère leçon = 1.
        # Skip "first N" : avec --skip-until N, on saute les N premières leçons
        # (compteur 1..N) et on commence à traiter à la leçon N+1.
        lesson_counter += 1
        if skip_until is not None and lesson_counter <= skip_until:
            print(f"  [⏭] #{lesson_counter}/{skip_until} skip --skip-until : {title}")
            _log("INFO", f"  [skip-until] #{lesson_counter} <= {skip_until} : {title}")
            continue

        # Compteur de progression (toujours affiché, sauf si --skip-until
        # vient de skipper cette leçon).
        progress = f"{lesson_counter}/{total_lessons_run}" if total_lessons_run else f"{lesson_counter}/?"
        print(f"  [analysis] lesson {progress} : {title}")

        # Nom de fichier unifié pour cette leçon : .md, .mp4, et le dossier
        # Support Files/<lesson_name>/ partagent ce même basename (titre
        # sanitised natural). The lesson number ("2.06") becomes the prefix "206-".
        lesson_name = lesson_filename_from_title(
            title, idx=i, keep_duration=add_duration,
        )
        # --add-index ajoute un préfixe positionnel `NNN-` par-dessus (legacy).
        if add_index:
            lesson_name = f"{i+1:03d}-{lesson_name}"

        if folder and folder != current_folder:
            current_folder = folder
            folder_dir = course_dir / slugify(folder)
            folder_dir.mkdir(exist_ok=True)
            index_lines.append(f"\n## {folder}\n")
            print(f"  [>] Module : {folder}")

        base_dir = course_dir / slugify(folder) if folder else course_dir
        base_dir.mkdir(exist_ok=True)
        filename = f"{lesson_name}.md"
        filepath = base_dir / filename

        rel_path = filepath.relative_to(OUTPUT_DIR)
        index_lines.append(f"- [{title}]({rel_path})")

        # ─── Leçon : skip idempotent OU fetch+write ────────────────────────
        skip_lesson = filepath.exists() and not overwrite_existing_lessons
        content: dict | None = None
        if skip_lesson:
            print(f"  [=] Leçon déjà exportée : {filename}")
            _log("INFO", f"  [skip] {filename}")
            # Silent re-fetch if we have to check the videos and/or support files
            # (even for a skipped lesson, we want to be able to discover / download
            # les ressources manquantes sans réécrire le .md).
            if download_videos or download_support_files:
                content = fetch_lesson_content(lesson)
        else:
            content = fetch_lesson_content(lesson)
            md_content = lesson_to_markdown(lesson, course_name, folder, content)
            # Filet de sécurité : ``html_to_markdown`` appelle déjà
            # ``repair_mojibake`` sur le corps, mais on repassele résultat
            # complet au cas où le titre / front-matter contiendrait des
            # séquences cassées (caractères Latin-1 ailleurs dans la leçon).
            md_content = repair_mojibake(md_content)
            filepath.write_text(md_content, encoding="utf-8")
            # Passe les blocs ```odin ... ``` du Markdown dans odinfmt.
            format_path_if_odin(filepath, silent=True)
            print(f"  [+] {filename}")
            _log("INFO", f"  [write] {filename}")
        lesson_count += 1

        # ─── YouTube Video ───────────────────────────────────────────────────
        # Vérifiée même pour les leçons déjà exportées (skip_lesson=True) tant
        # --download-video is active. Idempotent: does not re-download if
        # le fichier .mp4 existe déjà, sauf si --overwrite-existing-lessons.
        if download_videos and content is not None:
            assert course_video_dir is not None  # narrowed by line 472 guard
            meta = (content.get("metadata") or {})
            video_url = meta.get("videoLink") or content.get("videoLink", "")
            if video_url:
                # Sous-dossier par module (réplique la structure des markdown).
                if folder:
                    video_subdir = course_video_dir / slugify(folder)
                else:
                    video_subdir = course_video_dir
                video_subdir.mkdir(parents=True, exist_ok=True)

                video_path = video_subdir / f"{lesson_name}.mp4"
                # Overwrite: delete the existing file before re-downloading
                if overwrite_existing_lessons and video_path.exists():
                    video_path.unlink(missing_ok=True)
                    for part in video_subdir.glob(f"{lesson_name}.*.part"):
                        part.unlink(missing_ok=True)
                    _log("DEBUG", f"video overwrite: {video_path.name} supprimée")

                if not video_path.exists():
                    download_video(video_url, video_subdir, lesson_name)
                else:
                    print(f"  [=] Video already present: {video_path.name}")
                    _log("INFO", f"  [video skip] {video_path.name} (déjà présent)")
                # Anti-rate-limit pause between each YouTube download
                time.sleep(VIDEO_DELAY_BETWEEN)

        # ─── Fichiers de support (ZIP) : via metadata.resources ───────────
        if download_support_files and content is not None:
            resources = parse_resources_field(
                (content.get("metadata") or {}).get("resources", "")
            )
            # Fallback : si metadata.resources absent, scanner le .md
            if not resources:
                md_for_scan = filepath.read_text(encoding="utf-8")
                resources = [
                    {"file_name": fname, "read_url": url}
                    for url, fname in find_zip_urls_in_markdown(md_for_scan)
                ]

            if resources:
                cookie_header = load_skool_cookies()
                if not cookie_header:
                    print(f"  [WARN] Skool cookies missing -> cannot download the support files")
                    _log("WARNING", f"  [support FAIL] cookies absents (course={course_slug})")
                else:
                    # Support Files/<module?>/<lesson_name>/<file>.zip
                    # (réplique la structure des .md et .mp4 pour cohérence).
                    support_root = course_dir / "Support Files"
                    if folder:
                        support_dir = support_root / slugify(folder) / lesson_name
                    else:
                        support_dir = support_root / lesson_name
                    support_dir.mkdir(parents=True, exist_ok=True)
                    for res in resources:
                        raw_name = res.get("file_name") or res.get("title") or "support.zip"
                        file_name = sanitize_filename(raw_name)
                        target = support_dir / file_name

                        # Overwrite: delete the existing file before re-downloading
                        if (overwrite_existing_lessons
                                and target.exists() and target.stat().st_size > 0):
                            target.unlink(missing_ok=True)
                            for part in support_dir.glob(f"{file_name}.part"):
                                part.unlink(missing_ok=True)
                            _log("DEBUG", f"support overwrite: {file_name} supprimé")

                        if target.exists() and target.stat().st_size > 0:
                            print(f"  [=] Support déjà présent : Support Files/{lesson_name}/{file_name}")
                            continue

                        # Résolution URL : read_url/link direct, sinon POST API signed
                        read_url = res.get("read_url") or res.get("link")
                        if not read_url:
                            file_id = res.get("file_id")
                            if file_id:
                                read_url = get_file_signed_url(file_id, cookie_header)
                        if not read_url:
                            print(f"  [WARN] URL introuvable pour {file_name} "
                                f"(file_id={res.get('file_id', '?')[:12]}…)")
                            _log("WARNING", f"  [support FAIL] URL introuvable: {file_name} (file_id={res.get('file_id', '?')[:12]}…)")
                            continue

                        download_support_file(read_url, support_dir, file_name)
                        time.sleep(SUPPORT_FILES_DELAY)
            else:
                print(f"  [·] Aucun fichier de support détecté pour {filename}")
                _log("DEBUG", f"  [no support] {filename}")

        time.sleep(DELAY_BETWEEN)

    index_path = course_dir / "README.md"
    index_path.write_text("\n".join(index_lines), encoding="utf-8")
    print(f"  [+] Index créé : {index_path}")
    _log("INFO", f"  Cours {course_name} terminé: {lesson_count} leçons exportées")

    return lesson_count, lesson_counter


def write_global_index(courses: list[dict], total: int):
    """Generate a global README for the whole knowledge base."""
    lines = [
        "# Odin Game Dev Knowledge Base - programvideogames",
        f"\nExporté le {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"Total : {total} leçons exportées",
        "",
        "## Cours disponibles",
        "",
    ]
    for course in courses:
        name = course.get("title", course.get("name", "unknown"))
        slug = slugify(name)
        lines.append(f"- [{name}](./{slug}/README.md)")

    readme = OUTPUT_DIR / "README.md"
    readme.write_text("\n".join(lines), encoding="utf-8")
    print(f"\n[+] Index global : {readme}")


def check_prerequisites():
    """Verify that skool-cli is installed."""
    try:
        subprocess.run(["skool.cmd", "--version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("[ERR] skool.cmd (de skool-cli) introuvable. Installez-le d'abord :")
        print("  npm install -g skool-cli")
        print("  npx playwright install chromium")
        return False


def main():
    print("=" * 60)
    print("  Skool Course Scraper - Odin Knowledge Base")
    print("=" * 60)

    parser = argparse.ArgumentParser(
        description="Scrape les leçons Skool et exporte en Markdown."
    )
    parser.add_argument(
        "--download-video", "-dv",
        action="store_true",
        help="Download the YouTube videos present in the lessons via yt-dlp.",
    )
    parser.add_argument(
        "--download-video-folder",
        default=DEFAULT_DOWNLOAD_VIDEO_FOLDER,
        help=f"Target folder for the YouTube videos download. Default: {DEFAULT_DOWNLOAD_VIDEO_FOLDER}",
    )
    parser.add_argument(
        "--download-support-files", "-ds",
        action="store_true",
        help="Also download the support files (.zip) linked in each lesson. Placed in <course>/Support Files/<NNN-slug>/<file>.zipip. Idempotent : ne télécharge pas les fichiers déjà présents (non vides).",
    )
    parser.add_argument(
        "--overwrite-existing-lessons", "-f",
        action="store_true",
        help="Rewrite the Markdown files of already exported lessons (re-download from Skool). By default, lessons already present aret réutilisées (idempotence : aucun appel Skool, aucune réécriture).",
    )
    parser.add_argument(
        "--lesson", "-l",
        metavar="PATTERN",
        help="Filtre les leçons à traiter (substring fuzzy case-insensitive sur le "
            "titre normalisé). La normalisation remplace tout caractère non-"
            "alphanumérique par un espace, donc --lesson 'editor-side-panel' "
            "matche '2.41 - Editor Side Panel (ImGui) (10:53)' (tirets vs "
            "espaces). Le pattern est un substring (re.search), pas une regex. "
            "Ex: --lesson 'entities state physics' ne traite que la leçon dont "
            "le titre contient ces mots. Sans --lesson : toutes les leçons.",
    )
    parser.add_argument(
        "--skip-until",
        type=int,
        metavar="INDEX",
        default=None,
        help="Saute les INDEX premières leçons (tous cours confondus) et "
            "commence à traiter à partir de la leçon INDEX+1. Le compteur "
            "s'incrémente par leçon (pas par cours, pas par vidéo), ce qui "
            "useful to resume a long scrape after an interruption. "
            "Ex: --skip-until 50 saute les leçons 1..50 et traite à partir "
            "de la 51e. Sans --skip-until : aucune leçon n'est sautée par ce "
            "mécanisme (--lesson reste prioritaire pour filtrer).",
    )
    parser.add_argument(
        "--add-index",
        action="store_true",
        help="Add a numeric index prefix to the downloaded videos: "
            "{i+1:03d}-{slug}.mp4 au lieu de {slug}.mp4. Par défaut (False), "
            "les vidéos utilisent un nom stable basé uniquement sur le slug, "
            "ce qui évite les collisions quand --lesson est utilisé (l'index "
            "changes with the filtered list). Markdown lessons always keep "
            "toujours leur préfixe d'index pour l'ordre de lecture.",
    )
    parser.add_argument(
        "--add-duration",
        action="store_true",
        help="Keep the duration suffix (MM:SS or H:MM:SS) of the Skool title "
            "dans le nom de fichier → le slug se termine par les chiffres de "
            "durée (ex: ``...editor-side-panel-imgui-1053``). Par défaut "
            "(False), ce suffixe est retiré → ``...editor-side-panel-imgui`` "
            "(nom plus court, durée déjà présente dans le frontmatter du MD).",
    )
    parser.add_argument(
        "--log-reset",
        action="store_true",
        help="Écrase (reset) le fichier de log au démarrage du run au lieu "
            "de l'append. Par défaut (False), les runs successifs ajoutent "
            "leurs lignes (séparées par un marqueur '=== RUN START ===') ce "
            "that allows keeping the download errors of previous runs "
            "précédents. Sans --log-reset : comportement cumulatif.",
    )
    args = parser.parse_args()
    _init_log(reset=args.log_reset)
    _log("INFO", "Démarrage du scrape")

    download_videos = args.download_video
    video_download_dir: Path | None = None
    if download_videos:
        video_download_dir = Path(args.download_video_folder).expanduser()
        print(f"[*] Video download enabled -> {video_download_dir}")
        _log("INFO", f"--download-video activé → {video_download_dir}")

    if args.download_support_files:
        print("[*] --download-support-files -> download ZIPs attached to lessons")
        _log("INFO", "--download-support-files activé")

    if args.overwrite_existing_lessons:
        print("[*] --overwrite-existing-lessons → réécriture forcée des leçons existantes")
        _log("INFO", "--overwrite-existing-lessons activé")

    if args.lesson:
        print(f"[*] --lesson '{args.lesson}' → filtre sur le titre (case-insensitive)")
        _log("INFO", f"--lesson '{args.lesson}' (filtre titre)")

    if args.add_index:
        print("[*] --add-index → vidéos nommées avec préfixe d'index (NNN-slug.mp4)")
        _log("INFO", "--add-index activé")

    if args.add_duration:
        print("[*] --add-duration → suffixe de durée conservé dans le slug")
        _log("INFO", "--add-duration activé")

    _log("DEBUG", f"args={vars(args)}")

    if not check_prerequisites():
        _log("ERROR", "Prérequis skool-cli manquants")
        sys.exit(1)

    # Credentials depuis env vars > fichier .private/ > prompt interactif
    setup_credentials()

    if not login():
        _log("ERROR", "Authentification Skool échouée")
        sys.exit(1)
    _log("INFO", "Authentification Skool OK")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    courses = get_courses()
    if not courses:
        print("[ERR] No course found. Check the group name.")
        _log("ERROR", f"Aucun cours trouvé pour le groupe '{SKOOL_GROUP}'")
        sys.exit(1)
    _log("INFO", f"{len(courses)} cours trouvés dans '{SKOOL_GROUP}'")

    if args.skip_until is not None:
        print(f"[*] --skip-until {args.skip_until} → saute les {args.skip_until} premières leçons (compteur global tous cours)")
        _log("INFO", f"--skip-until {args.skip_until} activé")

    # Compteur total upfront (1 appel list-lessons par cours, en plus de
    # celui dans export_course). Sert à afficher la progression "N/TOTAL".
    total_lessons_run = _count_total_lessons(courses, args.lesson)
    print(f"[*] Total leçons à traiter dans ce run : {total_lessons_run}")
    _log("INFO", f"Total leçons à traiter (run) : {total_lessons_run}")

    total_lessons = 0
    lesson_counter = 0  # Compteur global tous cours confondus (pour --skip-until)
    for course in courses:
        n, lesson_counter = export_course(
            course,
            download_videos=download_videos,
            video_download_dir=video_download_dir,
            overwrite_existing_lessons=args.overwrite_existing_lessons,
            download_support_files=args.download_support_files,
            lesson_filter=args.lesson,
            add_index=args.add_index,
            add_duration=args.add_duration,
            skip_until=args.skip_until,
            lesson_counter=lesson_counter,
            total_lessons_run=total_lessons_run,
        )
        total_lessons += n

    if args.skip_until is not None:
        print(f"[*] Compteur final : {lesson_counter} leçons vues, {total_lessons} traitées")
        _log("INFO", f"Compteur final : {lesson_counter} leçons vues, {total_lessons} traitées")

    # ─── ONE-SHOT CLEANUP - strip durée du H1 dans les .md legacy ────────
    if ONE_SHOT_CLEANUP_MD_TITLES:
        print(f"[*] Cleanup H1 titres (one-shot) : {_clean_md_titles.__doc__.splitlines()[0].strip() if _clean_md_titles.__doc__ else ''}")
    n_cleaned, n_scanned = _clean_md_titles(OUTPUT_DIR)
    if n_scanned:
        print(f"[*] Cleanup H1 : {n_cleaned}/{n_scanned} .md modifiés")
        _log("INFO", f"Cleanup H1 titres : {n_cleaned}/{n_scanned} .md modifiés")

    write_global_index(courses, total_lessons)

    print("\n" + "=" * 60)
    print(f"  ✓ Export terminé : {total_lessons} leçons dans {OUTPUT_DIR}")
    print(f"  → Indexe dans RAGnarōk : Topic 'programvideogames'")
    print("=" * 60)
    _log("INFO", f"Terminé : {total_lessons} leçons exportées dans {OUTPUT_DIR}")
    _log("INFO", f"Log finalisé dans {LOG_FILE}")
    # End-of-run marker to clearly delimit the next run
    try:
        ts_end = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with LOG_FILE.open("a", encoding="utf-8") as _f:
            _f.write(f"{'=' * 70}\n=== RUN END   - {ts_end} ===\n{'=' * 70}\n")
    except OSError:
        pass


if __name__ == "__main__":
    main()
