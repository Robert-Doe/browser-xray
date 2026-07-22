# Module 19: html_tokenizer — DECISIONS.md

## An explicit state machine (named states, one handler method each), not a regex or "find `<...>`" approach
**(c) Convention — the module's entire point.** Regex-based or
naive-substring HTML "parsing" is a well-known, real source of bugs and
security issues precisely because HTML's actual grammar isn't regular
— it has context-dependent recovery rules (see the bogus-comment and
stray-`<` cases below) that no regex can express correctly. An explicit
state machine, one character at a time, is what the real WHATWG spec
itself is defined as, and it's the only approach that gets these
recovery cases right by construction rather than by accumulating
special-case patches.

## State names matching the real WHATWG spec's own names (`TAG_OPEN`, `BEFORE_ATTRIBUTE_NAME`, `BOGUS_COMMENT`, etc.)
**(b) External contract.** These aren't our invented names — using the
spec's actual terminology means anything learned here transfers
directly to reading the real specification or a real browser engine's
source code later.

## Coalescing consecutive characters into one `Character` token, rather than one token per character
**(c) Convention.** The literal spec defines character tokens one
character at a time; virtually every real implementation buffers and
coalesces runs of character data for efficiency and usability, and the
resulting stream is behaviorally equivalent for anything downstream
(Module 20's tree builder). Buffering here is a legitimate,
practical implementation choice — not a deviation from what the token
STREAM should ultimately represent.

## `<?xml...?>` and other unexpected `<!`-prefixed sequences becoming `Comment` tokens (bogus comment state)
**(b) External contract, deliberately preserved as-is even though it
looks surprising.** This is genuinely how the real HTML5 tokenization
spec behaves — HTML has no special handling for XML processing
instructions or "smart" recognition of malformed declarations; anything
after `<?` or an unrecognized `<!...` is swallowed into a comment token.
Keeping this exact, spec-accurate (if initially counter-intuitive)
behavior, rather than "fixing" it to do something more sensible-looking,
is precisely the point of this module.

## A stray `<` not followed by a letter, `/`, `!`, or `?` producing a literal `<` character, not an error
**(b) External contract.** This is a real, deliberate part of the
spec's design — HTML predates strict validation-based parsing and was
designed to be maximally recoverable from "text that merely happens to
contain a less-than sign." Treating this as a hard error would make
this tokenizer non-compliant with real browser behavior on completely
ordinary text like "1 < 2".

## The `_emit()` unification, and the real bug it fixes
**(c) Convention — adopted after catching a genuine ordering bug
during testing.** An earlier version called `_flush_char_buffer()`
manually at several specific call sites believed to precede a new
token. Testing the exact input `"a</1>b"` (an invalid end-tag name,
recovered via the bogus-comment path) surfaced a real bug: the
`Character('a')` token was emitted AFTER `Comment('1')` in the output,
even though 'a' appears first in the source — because the code path
taken for `</1>` never happened to call the flush function before
`</1>`'s comment token was appended, while 'b' (typed afterward) got
appended to the SAME still-open character buffer, silently merging into
`Character('ab')` positioned incorrectly after the comment. Refactoring
so that **every** non-character token is emitted through one shared
`_emit()` method — which flushes the character buffer first, always —
fixed this by construction: it is no longer possible to add a new state
transition that accidentally forgets to flush, since flushing is no
longer something individual state handlers need to remember to do at
all.

## DOCTYPE recognized and then discarded (no `Doctype` token type)
**(c) Convention — a deliberate, named scope simplification.** Real
HTML5 tokenizers emit a distinct DOCTYPE token, which the tree
constructor uses to decide "quirks mode" vs. standards-mode rendering.
This course's tokenizer only needs to demonstrate the tokenization
state-machine shape and its recovery behavior; DOCTYPE's rendering-mode
implications are out of scope, so consuming and discarding it (rather
than building a sixth token type solely to immediately ignore its
content everywhere else) was the simpler, honest choice.

---

## Decisions We Made

| Decision | Category | Could it have gone another way? |
|---|---|---|
| Explicit named-state machine | (c) Convention (the module's entire point) | N/A |
| Spec-matching state names | (b) Forced — enables direct transfer to real spec/source | No |
| Coalesced character tokens | (c) Convention (practical, behaviorally equivalent) | Yes, one-token-per-char also works, less usable |
| Bogus-comment swallowing `<?...?>` | (b) Forced — real, documented spec behavior | No |
| Stray `<` as literal text | (b) Forced — real, documented spec behavior | No |
| Unified `_emit()` flush point | (c) Convention, adopted after catching a real bug | Yes, manual per-site flushing also works if done perfectly everywhere — which is exactly the failure mode this fixes |
| DOCTYPE recognized-then-discarded | (c) Convention (named scope simplification) | Yes, a full Doctype token type is a natural extension |

## What We Proved

Running the tokenizer against eleven real, distinct inputs (see
`run_tokenizer_demo.py`) produced correct, spec-matching token streams
for every case, including:

1. **Ordinary nested tags with attributes** — parsed correctly, exactly
   as expected.
2. **Unquoted attribute values** — handled without requiring quotes,
   per spec.
3. **An unclosed tag at EOF** — degraded gracefully, emitting the
   partial, real content rather than crashing or losing data.
4. **A stray `<` in plain text ("1 < 2 and 3 > 1")** — correctly
   remained literal text, not misparsed as a tag.
5. **`<?xml version="1.0"?>`** — correctly became a single `Comment`
   token, matching real (if surprising) spec-defined behavior.
6. **An invalid end tag (`</1>`) sitting between two character runs** —
   correctly preserved source order across the recovery path, after we
   caught and fixed a real ordering bug during testing.
7. **Case-insensitive tag names (`<DIV>` → `div`)**, **real comments**,
   **unterminated comments at EOF**, **DOCTYPE**, and **self-closing
   void elements** — all handled correctly.

This is direct, run-and-observed confirmation that HTML tokenization is
a well-defined, deterministic state machine with precise, specified
recovery behavior for malformed input — not a "well-formed documents
only" process that fails outside the happy path, and not something a
regular expression could faithfully reproduce.
