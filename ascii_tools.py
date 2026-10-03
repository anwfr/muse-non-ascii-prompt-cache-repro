"""The workaround: tool definitions whose `description` strings are folded to ASCII.

Every non-ASCII character of a `description` (the tool's, and those of the properties of its input schema) becomes
an ASCII equivalent: an em dash becomes "-", an arrow "->", and so on. Names, types, enums, patterns and the shape
of the schemas are left untouched, so the model still gets complete tools. Used by replay.py (variant ascii-tools)
and by claude-code-compare.py (option --ascii-tools).
"""
import re, unicodedata

FOLD = {"—": "-", "–": "-", "→": "->", "←": "<-", "…": "...", "≤": "<=", "≥": ">=",
        "×": "x", "‘": "'", "’": "'", "“": '"', "”": '"', " ": " ", "•": "*"}


def to_ascii(text):
    def one(m):
        c = m.group(0)
        return FOLD.get(c) or unicodedata.normalize("NFKD", c).encode("ascii", "ignore").decode() or "?"
    return re.sub(r"[^\x00-\x7f]", one, text)


def fold_descriptions(node):
    """Tool definitions with every `description` string in ASCII; everything else unchanged."""
    if isinstance(node, dict):
        return {k: (to_ascii(v) if k == "description" and isinstance(v, str) else fold_descriptions(v))
                for k, v in node.items()}
    if isinstance(node, list):
        return [fold_descriptions(v) for v in node]
    return node
