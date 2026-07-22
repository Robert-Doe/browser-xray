"""
Module 19: html_tokenizer -- a real state-machine HTML tokenizer.

This is a genuine (if scoped-down) implementation of the shape of the
WHATWG HTML5 tokenization algorithm: an explicit state machine, one
character consumed at a time, with named states matching the real
spec's own state names. It is NOT a regex hack, and it is NOT "find
things between < and >" -- both of those approaches fail on exactly
the malformed-input cases this module deliberately tests, which real
browsers are specified to recover from in precise, defined ways.

Scope: covers start/end tags, attributes (quoted and unquoted),
comments, and the two "bogus comment" recovery paths real HTML5
parsing defines for `<?...>` and invalid tag-open sequences. DOCTYPE
is recognized and skipped (not emitted as its own token type) --
noted explicitly as a scope simplification in DECISIONS.md.
"""

from tokens import Character, Comment, EndOfFile, EndTag, StartTag

WHITESPACE = " \t\n\r\f"


class HtmlTokenizer:
    def __init__(self, html: str):
        self.html = html
        self.pos = 0
        self.state = "DATA"
        self.tokens: list = []
        self._char_buffer = ""
        self._tag: StartTag | EndTag | None = None
        self._attr_name = ""
        self._attr_value = ""
        self._comment_data = ""

    # --- low-level cursor helpers ---
    def _current(self) -> str | None:
        return self.html[self.pos] if self.pos < len(self.html) else None

    def _advance(self) -> None:
        self.pos += 1

    def _flush_char_buffer(self) -> None:
        if self._char_buffer:
            self.tokens.append(Character(self._char_buffer))
            self._char_buffer = ""

    def _emit(self, token) -> None:
        """The ONE place any non-Character token enters the stream.
        Flushing the pending character buffer here -- rather than at
        scattered call sites -- is what guarantees correct ordering
        regardless of which state path produced the token: a Comment
        or tag is never allowed to appear before text that preceded it
        in the source, even though the character buffer is built up
        incrementally across many DATA-state steps."""
        self._flush_char_buffer()
        self.tokens.append(token)

    def _emit_tag(self) -> None:
        self._finalize_attribute()
        self._emit(self._tag)
        self._tag = None

    def _finalize_attribute(self) -> None:
        if self._attr_name and isinstance(self._tag, StartTag):
            self._tag.attributes.setdefault(self._attr_name, self._attr_value)
        self._attr_name = ""
        self._attr_value = ""

    def tokenize(self) -> list:
        while self.state != "EOF":
            handler = getattr(self, f"_state_{self.state.lower()}")
            handler()
        self._flush_char_buffer()
        self.tokens.append(EndOfFile())
        return self.tokens

    # --- states ---

    def _state_data(self) -> None:
        c = self._current()
        if c is None:
            self.state = "EOF"
        elif c == "<":
            self._advance()
            self.state = "TAG_OPEN"
        else:
            self._char_buffer += c
            self._advance()

    def _state_tag_open(self) -> None:
        c = self._current()
        if c is not None and c.isalpha():
            self._tag = StartTag(name="")
            self.state = "TAG_NAME"
        elif c == "/":
            self._advance()
            self.state = "END_TAG_OPEN"
        elif c == "!":
            self._advance()
            self.state = "MARKUP_DECLARATION_OPEN"
        elif c == "?":
            # Real spec behavior: invalid first character after '<' that
            # isn't a letter, '/', or '!' -- treated as a BOGUS COMMENT,
            # not a syntax error that aborts parsing.
            self._comment_data = ""
            self.state = "BOGUS_COMMENT"
        else:
            # Real spec behavior: '<' not followed by anything tag-like
            # is not an error at all -- it's just a literal '<' character
            # in the data. ("1 < 2" is valid HTML text.)
            self._char_buffer += "<"
            self.state = "DATA"  # reconsume c in DATA

    def _state_end_tag_open(self) -> None:
        c = self._current()
        if c is not None and c.isalpha():
            self._tag = EndTag(name="")
            self.state = "TAG_NAME"
        elif c == ">":
            self._advance()
            self.state = "DATA"  # malformed "</>" -- spec: parse error, emit nothing
        elif c is None:
            self._char_buffer += "</"
            self.state = "EOF"
        else:
            self._comment_data = ""
            self.state = "BOGUS_COMMENT"  # reconsume c

    def _state_tag_name(self) -> None:
        c = self._current()
        if c is None:
            self.state = "EOF"  # truncated tag at EOF -- dropped, like real browsers do for this case
        elif c in WHITESPACE:
            self._advance()
            self.state = "BEFORE_ATTRIBUTE_NAME"
        elif c == "/":
            self._advance()
            self.state = "SELF_CLOSING_START_TAG"
        elif c == ">":
            self._advance()
            self._emit_tag()
            self.state = "DATA"
        else:
            # Tag names are ASCII case-INSENSITIVE -- <DIV> and <div>
            # are the same tag. Lowercasing here is that normalization.
            self._tag.name += c.lower()
            self._advance()

    def _state_before_attribute_name(self) -> None:
        c = self._current()
        if c in WHITESPACE:
            self._advance()
        elif c in (">", "/") or c is None:
            self.state = "AFTER_ATTRIBUTE_NAME"  # reconsume
        else:
            self._attr_name = ""
            self._attr_value = ""
            self.state = "ATTRIBUTE_NAME"  # reconsume

    def _state_attribute_name(self) -> None:
        c = self._current()
        if c is None or c in WHITESPACE or c in (">", "/"):
            self.state = "AFTER_ATTRIBUTE_NAME"  # reconsume
        elif c == "=":
            self._advance()
            self.state = "BEFORE_ATTRIBUTE_VALUE"
        else:
            self._attr_name += c.lower()
            self._advance()

    def _state_after_attribute_name(self) -> None:
        c = self._current()
        if c is None:
            self.state = "EOF"
        elif c in WHITESPACE:
            self._advance()
        elif c == "/":
            self._advance()
            self.state = "SELF_CLOSING_START_TAG"
        elif c == "=":
            self._advance()
            self.state = "BEFORE_ATTRIBUTE_VALUE"
        elif c == ">":
            self._advance()
            self._emit_tag()
            self.state = "DATA"
        else:
            self._finalize_attribute()
            self.state = "BEFORE_ATTRIBUTE_NAME"  # reconsume

    def _state_before_attribute_value(self) -> None:
        c = self._current()
        if c in WHITESPACE:
            self._advance()
        elif c == '"':
            self._advance()
            self.state = "ATTRIBUTE_VALUE_DOUBLE_QUOTED"
        elif c == "'":
            self._advance()
            self.state = "ATTRIBUTE_VALUE_SINGLE_QUOTED"
        else:
            self.state = "ATTRIBUTE_VALUE_UNQUOTED"  # reconsume, no quotes at all

    def _state_attribute_value_double_quoted(self) -> None:
        c = self._current()
        if c == '"':
            self._advance()
            self._finalize_attribute()
            self.state = "AFTER_ATTRIBUTE_VALUE_QUOTED"
        elif c is None:
            self.state = "EOF"
        else:
            self._attr_value += c
            self._advance()

    def _state_attribute_value_single_quoted(self) -> None:
        c = self._current()
        if c == "'":
            self._advance()
            self._finalize_attribute()
            self.state = "AFTER_ATTRIBUTE_VALUE_QUOTED"
        elif c is None:
            self.state = "EOF"
        else:
            self._attr_value += c
            self._advance()

    def _state_attribute_value_unquoted(self) -> None:
        c = self._current()
        if c is None:
            self.state = "EOF"
        elif c in WHITESPACE:
            self._advance()
            self._finalize_attribute()
            self.state = "BEFORE_ATTRIBUTE_NAME"
        elif c == ">":
            self._advance()
            self._finalize_attribute()
            self._emit_tag()
            self.state = "DATA"
        else:
            self._attr_value += c
            self._advance()

    def _state_after_attribute_value_quoted(self) -> None:
        c = self._current()
        if c in WHITESPACE:
            self._advance()
            self.state = "BEFORE_ATTRIBUTE_NAME"
        elif c == "/":
            self._advance()
            self.state = "SELF_CLOSING_START_TAG"
        elif c == ">":
            self._advance()
            self._emit_tag()
            self.state = "DATA"
        elif c is None:
            self.state = "EOF"
        else:
            self.state = "BEFORE_ATTRIBUTE_NAME"  # reconsume; missing-whitespace recovery

    def _state_self_closing_start_tag(self) -> None:
        c = self._current()
        if c == ">":
            self._advance()
            if isinstance(self._tag, StartTag):
                self._tag.self_closing = True
            self._emit_tag()
            self.state = "DATA"
        elif c is None:
            self.state = "EOF"
        else:
            self.state = "BEFORE_ATTRIBUTE_NAME"  # reconsume; unexpected-solidus recovery

    def _state_markup_declaration_open(self) -> None:
        if self.html[self.pos : self.pos + 2] == "--":
            self.pos += 2
            self._comment_data = ""
            self.state = "COMMENT"
        elif self.html[self.pos : self.pos + 7].upper() == "DOCTYPE":
            self.pos += 7
            self.state = "DOCTYPE_SKIP"
        else:
            self._comment_data = ""
            self.state = "BOGUS_COMMENT"

    def _state_doctype_skip(self) -> None:
        # Scope simplification: we don't build a DOCTYPE token type,
        # we just consume up to '>' and discard it -- noted in
        # DECISIONS.md. Real browsers use a DOCTYPE token to decide
        # quirks-mode rendering, out of scope for this tokenizer.
        c = self._current()
        if c is None:
            self.state = "EOF"
        elif c == ">":
            self._advance()
            self.state = "DATA"
        else:
            self._advance()

    def _state_comment(self) -> None:
        if self.html[self.pos : self.pos + 3] == "-->":
            self.pos += 3
            self._emit(Comment(self._comment_data))
            self.state = "DATA"
        elif self._current() is None:
            self._emit(Comment(self._comment_data))  # unterminated comment: emit what we have
            self.state = "EOF"
        else:
            self._comment_data += self._current()
            self._advance()

    def _state_bogus_comment(self) -> None:
        c = self._current()
        if c == ">":
            self._advance()
            self._emit(Comment(self._comment_data))
            self.state = "DATA"
        elif c is None:
            self._emit(Comment(self._comment_data))
            self.state = "EOF"
        else:
            self._comment_data += c
            self._advance()


def tokenize(html: str) -> list:
    return HtmlTokenizer(html).tokenize()
