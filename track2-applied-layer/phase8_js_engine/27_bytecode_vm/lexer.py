"""
Module 25: js_lexer_parser -- a real lexer for a JS subset.

Turns raw source text into a flat stream of tokens: numbers, strings,
identifiers/keywords, and operators/punctuation -- exactly the same
first stage every real JS engine (V8, SpiderMonkey, JavaScriptCore)
performs before anything resembling "running the code" begins.
"""

from dataclasses import dataclass

KEYWORDS = {
    "var", "let", "const", "function", "return", "if", "else",
    "while", "true", "false", "null",
}

# Longest-match-first matters: '===' must be checked before '==' before '='.
MULTI_CHAR_OPS = [
    "===", "!==", "**", "&&", "||",
    "==", "!=", "<=", ">=", "+=", "-=", "*=", "/=",
]
SINGLE_CHAR_OPS = set("+-*/%=<>!(){}[];,.")


@dataclass
class Token:
    type: str  # 'NUMBER' | 'STRING' | 'IDENT' | 'KEYWORD' | 'OP' | 'EOF'
    value: str


class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.pos = 0

    def _current(self):
        return self.source[self.pos] if self.pos < len(self.source) else None

    def _skip_whitespace_and_comments(self) -> None:
        while self.pos < len(self.source):
            c = self._current()
            if c in " \t\n\r":
                self.pos += 1
            elif self.source[self.pos : self.pos + 2] == "//":
                while self.pos < len(self.source) and self.source[self.pos] != "\n":
                    self.pos += 1
            elif self.source[self.pos : self.pos + 2] == "/*":
                end = self.source.find("*/", self.pos + 2)
                self.pos = len(self.source) if end == -1 else end + 2
            else:
                break

    def tokenize(self) -> list:
        tokens = []
        while True:
            self._skip_whitespace_and_comments()
            c = self._current()
            if c is None:
                tokens.append(Token("EOF", ""))
                break

            if c.isdigit():
                tokens.append(self._read_number())
            elif c in ('"', "'"):
                tokens.append(self._read_string())
            elif c.isalpha() or c == "_":
                tokens.append(self._read_ident_or_keyword())
            else:
                tokens.append(self._read_operator())
        return tokens

    def _read_number(self) -> Token:
        start = self.pos
        while self._current() is not None and (self._current().isdigit() or self._current() == "."):
            self.pos += 1
        return Token("NUMBER", self.source[start : self.pos])

    def _read_string(self) -> Token:
        quote = self._current()
        self.pos += 1
        start = self.pos
        while self._current() is not None and self._current() != quote:
            self.pos += 1
        value = self.source[start : self.pos]
        self.pos += 1  # consume closing quote
        return Token("STRING", value)

    def _read_ident_or_keyword(self) -> Token:
        start = self.pos
        while self._current() is not None and (self._current().isalnum() or self._current() == "_"):
            self.pos += 1
        word = self.source[start : self.pos]
        return Token("KEYWORD" if word in KEYWORDS else "IDENT", word)

    def _read_operator(self) -> Token:
        for op in MULTI_CHAR_OPS:
            if self.source[self.pos : self.pos + len(op)] == op:
                self.pos += len(op)
                return Token("OP", op)
        c = self._current()
        if c in SINGLE_CHAR_OPS:
            self.pos += 1
            return Token("OP", c)
        raise SyntaxError(f"Unexpected character {c!r} at position {self.pos}")


def tokenize(source: str) -> list:
    return Lexer(source).tokenize()
