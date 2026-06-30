"""Text cleaning helpers (used by the scrapers).

Exposes `repair_mojibake()` which fixes the "double-encoded UTF-8 -> Latin-1"
artefact produced when a UTF-8 string is decoded as Latin-1/cp1252.

Typical symptoms (to fix):
â”œ â”€ â”‚ â”” â”Œ â”˜ â”¤ â”¬ â”´ â”¼   (broken box-drawing)
â€™ â€œ â€¦ â€“ â€” â‚¬ â„¢ â€¢           (curly typography)
Ã© Ã¨ Ã Ãª Ã« Ã® Ã¯ Ã´ Ã¹ Ã» Ã§   (French accents - lowercase)
Ã‰ Ãˆ Ã€ ÃŠ Ã‹ ÃŽ Ã› Ã‡ Ã”         (French accents - uppercase)
Â (followed by a Latin-1 character)   (double-encoded NBSP = "Â ")

No character below U+0080 is touched: the round-trip is safe for any text
that isn't itself raw Latin-1 (very rare for Skool content).
"""

from __future__ import annotations

import re


_MOJIBAKE_REPLACEMENTS: dict[str, str] = {
    # Box-drawing (UTF-8 E2 94 xx)
    "â”€": "─", "â”‚": "│", "â”œ": "├", "â””": "└",
    "â”Œ": "┌", "â”˜": "┘", "â”¤": "┤", "â”¬": "┬",
    "â”´": "┴", "â”¼": "┼",
    # Arrows (UTF-8 E2 86/87/9x)
    "â†’": "→", "â†": "←", "â†‘": "↑", "â†“": "↓",
    "â†”": "↔", "â‡’": "⇒", "â‡": "⇐",
    # Curly typography & dashes (UTF-8 E2 80 xx)
    "â€™": "’", "â€œ": "“", "â€": "”",
    "â€¦": "…", "â€“": "–", "â€”": "-",
    "â‚¬": "€", "â„¢": "™", "â€¢": "•", "Â·": "·",
    # Double-encoded NBSP (UTF-8 C2 A0 -> "Â ")
    "Â ": " ",
    # Lowercase French accents (UTF-8 C3 xx)
    "Ã©": "é", "Ã¨": "è", "Ã ": "à", "Ã¢": "â",
    "Ãª": "ê", "Ã«": "ë", "Ã®": "î", "Ã¯": "ï",
    "Ã´": "ô", "Ã¹": "ù", "Ã»": "û", "Ã§": "ç",
    "Ã¦": "æ", "Å“": "œ",
    # Uppercase French accents (UTF-8 C3 xx)
    "Ã‰": "É", "Ãˆ": "È", "Ã€": "À", "Ã‚": "Â",
    "ÃŠ": "Ê", "Ã‹": "Ë", "ÃŽ": "Î", "Ã": "Ï",
    "Ã”": "Ô", "Ã™": "Ù", "Ã›": "Û", "Ã‡": "Ç",
    # Latin-1 supplement punctuation
    "Â«": "«", "Â»": "»", "Â¡": "¡", "Â¢": "¢",
    "Â£": "£", "Â¤": "¤", "Â¥": "¥", "Â¦": "¦",
    "Â§": "§", "Â¨": "¨", "Â©": "©", "Â®": "®",
    "Â¯": "¯", "Â°": "°", "Â±": "±", "Â²": "²",
    "Â³": "³", "Â´": "´", "Âµ": "µ", "Â¶": "¶",
    "Â¸": "¸", "Â¹": "¹", "Âº": "º", "Â¼": "¼",
    "Â½": "½", "Â¾": "¾", "Â¿": "¿",
}

# Sort by descending length to avoid partial replacements
# (e.g. "â€" must not be replaced by "â€\"" before "â€\"" can match).
_MOJIBAKE_ORDER: tuple[str, ...] = tuple(
    sorted(_MOJIBAKE_REPLACEMENTS.keys(), key=len, reverse=True)
)


def repair_mojibake(text: str) -> str:
    """Fix 'UTF-8 read as Latin-1' mojibake in a Python string.

    Two-pass strategy:
      1. Replace known MOJIBAKE_REPLACEMENTS sequences (zero false
         positives: none of them makes sense in real Latin-1 for French/English
         educational content).
      2. For the remainder (rarer accents or symbols not listed),
         try the round-trip ``text.encode('latin-1').decode('utf-8')``.
         Silently abandoned if the string already contains real Latin-1
         (UnicodeEncodeError / UnicodeDecodeError).

    Returns ``text`` unchanged if no marker (``â`` / ``Â`` / ``Ã``) is
    detected.
    """
    if not text:
        return text

    if not any(marker in text for marker in ("â", "Â", "Ã")):
        return text

    # Pass 1: explicit sequences (most common, zero risk).
    for bad in _MOJIBAKE_ORDER:
        if bad in text:
            text = text.replace(bad, _MOJIBAKE_REPLACEMENTS[bad])

    # Pass 2: round-trip fallback (isolated accents not listed, etc.).
    # Includes "Â" because "Â<0x80-0xBF>" is typically Latin-1 that
    # re-decodes as UTF-8 (e.g. "Â\xa0" -> NBSP). The try/except ensures
    # an isolated real Latin-1 character (invalid encode) stays untouched.
    if "Ã" in text or "â" in text or "Â" in text:
        try:
            text = text.encode("latin-1").decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            pass

    # Pass 3: typographic normalisation consistent with the Skool
    # scraper (NBSP = plain space, used by Skool to glue words in
    # French/English). Harmless: NBSP inside a code block is rendered
    # as a space anyway.
    text = text.replace("\u00a0", " ")

    # Pass 4: removal of stranded markers (Â, Ã, â) that survive the
    # previous passes when the round-trip raises UnicodeDecodeError
    # (typically: an Â or Ã at end of line, or followed by an ASCII
    # character). Conservative: we only touch when followed by
    # whitespace, punctuation, quotes/backticks, or end-of-line/string.
    # So real French words like ``Âge`` / ``Aîné`` are NOT affected
    # (Â followed by a letter = preserved).
    _stray_pattern = re.compile(
        r"[\u00c2\u00c3\u00e2]"
        r"(?=[\s\.,;:!?\"'\u00b6\u00ab\u00bb\)\]\}\-\*_`\u2013\u2014\u2026\n]|$)"
    )
    text = _stray_pattern.sub("", text)

    return text


__all__ = ["repair_mojibake"]
