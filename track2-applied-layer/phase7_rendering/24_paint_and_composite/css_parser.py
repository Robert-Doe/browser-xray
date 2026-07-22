"""
Module 21: css_parser_cssom -- a real, hand-written CSS parser.

Like Module 19's HTML tokenizer, this is a genuine character-by-
character scanner respecting CSS's actual grammar shape -- not a
regex. It specifically handles three real, easy-to-get-wrong cases:
quoted string values that may contain ';', '{', or '}' as literal text
(not syntax), a malformed declaration that must be skipped without
aborting the whole stylesheet (CSS's forward-compatible error recovery
model), and at-rules (e.g. @media) being skipped as balanced blocks
rather than breaking the parser.

SCOPE (see DECISIONS.md): selectors are captured as raw, comma-split
text, not parsed into a selector AST (combinators, specificity, etc. --
Module 22's concern). At-rule bodies are skipped entirely, not parsed.
"""

import re

from cssom import CSSRule, Declaration

_IMPORTANT_RE = re.compile(r"!\s*important\s*$", re.IGNORECASE)


def strip_comments(css: str) -> str:
    """CSS comments (/* ... */) never nest and can appear almost
    anywhere; stripping them up front keeps every other part of the
    parser from needing to think about them at all."""
    result = []
    i = 0
    while i < len(css):
        if css[i : i + 2] == "/*":
            end = css.find("*/", i + 2)
            i = len(css) if end == -1 else end + 2
        else:
            result.append(css[i])
            i += 1
    return "".join(result)


class CSSParser:
    def __init__(self, css: str):
        self.css = strip_comments(css)
        self.pos = 0
        self.skipped_declarations: list[str] = []  # for demonstrating recovery

    def parse(self) -> list[CSSRule]:
        rules = []
        while True:
            self._skip_whitespace()
            if self.pos >= len(self.css):
                break
            if self.css[self.pos] == "@":
                self._skip_at_rule()
                continue
            rule = self._parse_rule()
            if rule is not None:
                rules.append(rule)
        return rules

    def _skip_whitespace(self) -> None:
        while self.pos < len(self.css) and self.css[self.pos] in " \t\n\r\f":
            self.pos += 1

    def _read_until(self, stop_chars: str) -> str:
        """Reads characters up to (not including) one of stop_chars at
        the top level -- but characters inside a quoted string are
        NEVER treated as stop characters, matching real CSS syntax."""
        buf = []
        in_string = None
        while self.pos < len(self.css):
            c = self.css[self.pos]
            if in_string:
                buf.append(c)
                if c == in_string:
                    in_string = None
                self.pos += 1
                continue
            if c in ('"', "'"):
                in_string = c
                buf.append(c)
                self.pos += 1
                continue
            if c in stop_chars:
                break
            buf.append(c)
            self.pos += 1
        return "".join(buf)

    def _skip_at_rule(self) -> None:
        """@import ...; and @media ... { ... } both start with '@' --
        neither is parsed here, only safely skipped so the rest of the
        stylesheet still parses correctly."""
        text = self._read_until("{;")
        if self.pos < len(self.css) and self.css[self.pos] == ";":
            self.pos += 1
        elif self.pos < len(self.css) and self.css[self.pos] == "{":
            self.pos += 1
            self._skip_balanced_block()

    def _skip_balanced_block(self) -> None:
        depth = 1
        while self.pos < len(self.css) and depth > 0:
            c = self.css[self.pos]
            if c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
            self.pos += 1

    def _parse_rule(self):
        selector_text = self._read_until("{")
        if self.pos >= len(self.css):
            return None  # malformed: selector with no block at all -- nothing to recover into

        self.pos += 1  # consume '{'
        selectors = [s.strip() for s in selector_text.split(",") if s.strip()]
        if not selectors:
            self._skip_balanced_block()
            return None

        declarations = self._parse_declarations()
        return CSSRule(selectors=selectors, declarations=declarations)

    def _parse_declarations(self) -> list[Declaration]:
        declarations = []
        while True:
            self._skip_whitespace()
            if self.pos >= len(self.css):
                break
            if self.css[self.pos] == "}":
                self.pos += 1
                break

            decl_text = self._read_until(";}")
            terminator = self.css[self.pos] if self.pos < len(self.css) else None
            if terminator == ";":
                self.pos += 1

            decl = self._parse_one_declaration(decl_text)
            if decl is not None:
                declarations.append(decl)

            if terminator is None:
                break
        return declarations

    def _parse_one_declaration(self, text: str):
        text = text.strip()
        if not text:
            return None
        if ":" not in text:
            # Real CSS behavior: a malformed declaration (no colon) does
            # NOT abort the stylesheet -- it's simply discarded, and
            # parsing continues with whatever comes next.
            self.skipped_declarations.append(text)
            return None

        prop, _, value = text.partition(":")
        prop = prop.strip().lower()
        value = value.strip()

        important = bool(_IMPORTANT_RE.search(value))
        if important:
            value = _IMPORTANT_RE.sub("", value).strip()

        if not prop:
            self.skipped_declarations.append(text)
            return None

        return Declaration(property=prop, value=value, important=important)


def parse_css(css: str) -> list[CSSRule]:
    return CSSParser(css).parse()
