"""_Helpers/scripts/dev/normalize_eol.py - Normalisation des fins de ligne (LF).

Objectif : un fichier doit avoir les memes octets sur tous les OS. Le depot
stocke du LF, la copie de travail est en LF, et un fichier dont seuls les fins
de ligne ont change n'est jamais signale comme modifie par Git.

Ce script normalise la COPIE DE TRAVAIL (les octets presents sur le disque) :
il remplace les sequences CRLF par LF dans les fichiers texte dont la
directive `eol` vaut `lf`. Les scripts Windows (.bat, .cmd, .ps1) sont
respectes : leur directive vaut `crlf`, ils restent en CRLF. Les fichiers
binaires (NUL detecte, ou attribut `-text`) ne sont jamais touches.

Pourquoi la copie de travail d'abord ? Parce que `git add --renormalize` ne
repare pas les blobs "mixed" deja stockes : git refuse de normaliser un
fichier dont la version dans l'index contient des CRLF (il le considere
binaire pour le calcul des fins de ligne). La sequence qui fonctionne est :
reecrire le fichier en LF, puis `git add` (le filtre clean de git reencodera
de toute facon en LF, et l'index ne contiendra plus qu'un seul style).

Utilisation :
    python _Helpers/scripts/dev/normalize_eol.py --check   # rapport, exit 1 si derives
    python _Helpers/scripts/dev/normalize_eol.py --apply   # reecrit la copie de travail
    python _Helpers/scripts/dev/normalize_eol.py --stage   # normalise puis `git add -f` les fichiers touches

Codes de sortie :
    0  toutes les fins de ligne sont conformes
    1  au moins un fichier derive (mode --check)
    2  erreur bloquante (pas un depot git, etc.)
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
except Exception:
    pass

REPO_ROOT = Path(__file__).resolve().parents[3]

# Taille maximale lue pour detecter la presence de CRLF (les fichiers volumineux
# sont traites par lecture par blocs, mais on evite de charger 1 Go en memoire).
CHUNK_SIZE = 1024 * 1024


def _log(level: str, message: str) -> None:
    """Affiche une ligne de log avec un prefixe stable."""
    print(f"[{level}] {message}")


def _git(*args: str) -> str:
    """Execute une commande git dans la racine du depot et retourne sa sortie."""
    result = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} a echoue : {result.stderr.strip()}")
    return result.stdout


def list_tracked_attrs() -> list[tuple[str, str]]:
    """Retourne la liste (chemin, attributs git) des fichiers suivis.

    Les chemins sont separes par un caractere nul, ce qui evite tout probleme
    avec les espaces et les caracteres accentues.
    """
    raw = _git("ls-files", "--eol", "-z")
    entries: list[tuple[str, str]] = []
    for record in raw.split("\0"):
        if not record.strip():
            continue
        head, _, path = record.partition("\t")
        if not path:
            continue
        # L'en-tete a la forme "i/<eol> w/<eol> attr/<attributs> ...".
        # Les attributs peuvent contenir plusieurs directives ("text eol=crlf").
        parts = head.split(None, 2)
        attrs = parts[2] if len(parts) > 2 else ""
        entries.append((path, attrs))
    return entries


def wants_lf(attrs: str) -> bool:
    """Vrai quand la directive git du fichier impose LF (et non CRLF)."""
    if "eol=crlf" in attrs:
        return False
    if "-text" in attrs:
        return False
    return "text" in attrs


def has_crlf(path: Path) -> bool:
    """Vrai si le fichier contient au moins une sequence CRLF."""
    try:
        with open(path, "rb") as handle:
            previous = b""
            while True:
                chunk = handle.read(CHUNK_SIZE)
                if not chunk:
                    return False
                if b"\r\n" in previous + chunk:
                    return True
                previous = chunk[-1:]
    except OSError:
        return False


def is_binary(path: Path) -> bool:
    """Vrai si le fichier contient un octet NUL (heuristique binaire de git)."""
    try:
        with open(path, "rb") as handle:
            while True:
                chunk = handle.read(CHUNK_SIZE)
                if not chunk:
                    return False
                if b"\0" in chunk:
                    return True
    except OSError:
        return True


def normalize_file(path: Path) -> bool:
    """Reecrit le fichier en LF (CRLF -> LF). Retourne True si modifie."""
    try:
        data = path.read_bytes()
    except OSError:
        return False
    if b"\r\n" not in data:
        return False
    path.write_bytes(data.replace(b"\r\n", b"\n"))
    return True


def find_eol_only_changes() -> list[str]:
    """Liste les fichiers signales modifies alors que seul le style de fin de ligne change.

    Git compare la copie de travail a l'index en passant par le filtre clean :
    un fichier sauvegarde en CRLF par un editeur peut donc etre signale modifie
    alors que le diff est vide. `git update-index --refresh` leve le faux
    positif (le cache de stat est simplement perime).
    """
    modified = set(_git("diff", "--name-only").splitlines())
    if not modified:
        return []
    real = set(_git("diff", "--ignore-cr-at-eol", "--name-only").splitlines())
    return sorted(modified - real)


def main(argv: list[str] | None = None) -> int:
    """Point d'entree. Retourne le code de sortie du processus."""
    parser = argparse.ArgumentParser(description="Normalise les fins de ligne de la copie de travail en LF.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="rapport seul, ne modifie rien (defaut)")
    mode.add_argument("--apply", action="store_true", help="reecrit les fichiers concernés en LF")
    mode.add_argument("--stage", action="store_true", help="normalise puis `git add -f` les fichiers touchés")
    args = parser.parse_args(argv)

    try:
        entries = list_tracked_attrs()
    except RuntimeError as exc:
        _log("x", str(exc))
        return 2

    if not entries:
        _log("i", "aucun fichier suivi dans ce depot")
        return 0

    candidates: list[str] = []
    skipped_crlf = 0
    for path, attrs in entries:
        if not wants_lf(attrs):
            if "eol=crlf" in attrs:
                skipped_crlf += 1
            continue
        absolute = REPO_ROOT / path
        if not absolute.is_file() or absolute.is_symlink():
            continue
        if is_binary(absolute):
            continue
        if has_crlf(absolute):
            candidates.append(path)

    if not candidates:
        _log("+", "toutes les fins de ligne sont conformes (LF)")
        _log("i", "%d script(s) Windows laissés en CRLF" % skipped_crlf)
    else:
        _log("i", "%d fichier(s) à normaliser, %d script(s) Windows laissés en CRLF" % (len(candidates), skipped_crlf))

    # Faux positifs : modifies pour cause de fin de ligne uniquement.
    try:
        eol_only = find_eol_only_changes()
    except RuntimeError:
        eol_only = []
    if eol_only:
        _log("!", "%d fichier(s) signalé(s) modifiés alors que seul le style de fin de ligne change" % len(eol_only))
        for path in eol_only:
            _log("i", "faux positif : %s" % path)
        _log("i", "lever avec : git update-index --refresh")

    if not candidates:
        return 0

    if args.check:
        for path in candidates:
            _log("i", "dérive : %s" % path)
        _log("i", "lancer --apply (ou --stage) pour corriger")
        return 1

    changed: list[str] = []
    for path in candidates:
        if normalize_file(REPO_ROOT / path):
            changed.append(path)

    for path in changed:
        _log("+", "normalisé : %s" % path)
    _log("+", "%d fichier(s) normalisé(s)" % len(changed))

    if args.stage and changed:
        # `-f` : certains chemins sont volontairement exclus via .git/info/exclude
        # (contenu personnel suivi avec `git add -f`, cf. doc 007).
        _git("add", "-f", "--", *changed)
        _log("+", "%d fichier(s) ajouté(s) à l'index" % len(changed))

    return 0


if __name__ == "__main__":
    sys.exit(main())
