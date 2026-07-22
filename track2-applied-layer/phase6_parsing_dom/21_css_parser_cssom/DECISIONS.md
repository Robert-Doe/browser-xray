# Module 21: css_parser_cssom — DECISIONS.md

## A character-scanning parser with explicit quote-tracking, not a regex
**(c) Convention, forced in part by (a) a real grammar property.**
CSS values can legitimately contain `;`, `{`, `}` as literal characters
inside a quoted string (`content: "a;b{c}";` is completely valid CSS).
A regex-based "split on semicolons" approach would incorrectly treat
those characters as syntax. Tracking whether we're currently inside a
quoted string, character by character, is the only correct way to
know when `;`/`{`/`}` are real syntax versus literal text — this is
forced by the actual grammar, not a style preference.

## Stripping comments in a single pre-pass, before any other parsing logic runs
**(c) Convention.** CSS comments can appear almost anywhere and never
nest — handling them once, up front, means every other part of the
parser (selector reading, declaration reading) never has to think
about comments interrupting a token, which would otherwise complicate
every other piece of logic.

## Selectors captured as raw, comma-split TEXT, not parsed into a selector AST
**(c) Convention — a deliberate, named scope boundary.** Real selector
parsing (combinators like `>` and `+`, pseudo-classes, specificity
calculation) is Module 22's concern, once the CSSOM needs to be MATCHED
against the DOM. This module's job stops at "here is a valid rule with
these selector strings and these declarations" — parsing what a
selector strings actually MEANS is a separate, later step.

## `@`-rules skipped as balanced blocks or up to `;`, never parsed
**(c) Convention — a deliberate, named scope boundary, matching real
CSS's own forward-compatibility design.** The real CSS specification is
explicitly designed so that an unrecognized construct (a newer at-rule
a parser doesn't understand yet) can be safely skipped without
corrupting the rest of the stylesheet — this is a deliberate,
future-proofing design decision by the CSS spec authors, not an
accident. This module reproduces that skip-safely behavior without
implementing what's actually inside a `@media` or `@import` block,
which is real, additional complexity out of this module's scope.

## A malformed declaration (no `:`) being silently skipped, with parsing continuing
**(b) External contract.** This is real, specified CSS parsing
behavior, not an invented leniency: browsers are required to recover
from a malformed declaration by discarding just that one declaration,
never the whole rule or stylesheet. We surface the skipped text via
`skipped_declarations` specifically so this module's demo can show the
recovery happening, rather than the malformed content just silently
vanishing with no visible evidence at all.

## `_IMPORTANT_RE` as a small, narrowly-scoped regex, despite avoiding regex for the main parse
**(c) Convention.** Detecting `!important` (optionally with whitespace
before "important") is a small, well-bounded, un-ambiguous pattern at
the END of an already-extracted value string — using a tiny, precise
regex here is a reasonable, proportionate tool, unlike using regex for
the main brace/quote-aware scanning, where the actual grammar requires
character-by-character state tracking a regex cannot correctly express.

---

## Decisions We Made

| Decision | Category | Could it have gone another way? |
|---|---|---|
| Character-scanning parser with quote-tracking | (a)/(c) Forced by real grammar (string literals) | No, for correctness |
| Comments stripped in one pre-pass | (c) Convention (simplifies everything downstream) | Yes, inline comment handling also works, more complex |
| Selectors as raw text, not an AST | (c) Convention (deferred to Module 22) | Yes — a fuller selector parser is a natural extension |
| `@`-rules skipped, not parsed | (c) Convention (matches real CSS's own forward-compat design) | Yes — parsing `@media` internals is a natural but out-of-scope extension |
| Malformed declarations skipped, not fatal | (b) Forced — real, specified CSS behavior | No |
| Small regex for `!important` only | (c) Convention (proportionate tool for a narrow, bounded pattern) | Yes |

## What We Proved

Running eight real, illustrative stylesheets through the parser
produced correct CSSOM structures in every case, including:

1. **Ordinary rules and comma-separated selectors** parsed correctly.
2. **`!important`**, with and without a space before "important,"
   correctly normalized.
3. **A string value containing `;`, `{`, `}`** — real syntax characters
   as literal text — was preserved intact rather than being
   misinterpreted as declaration/rule boundaries.
4. **A comment containing what looks like an entire valid rule** was
   stripped completely, proving comments are removed before any
   structural parsing occurs, not interleaved with it.
5. **A malformed declaration in the middle of a valid rule** was
   discarded while both surrounding valid declarations were correctly
   kept — real, observable CSS error recovery.
6. **An `@media` block and an `@import` statement** were both safely
   skipped as balanced units, with parsing correctly continuing on the
   rules that followed them.

This is direct, run-and-observed confirmation that CSS parsing produces
a real, independent object model (the CSSOM) via a genuine
grammar-aware parser — one that correctly distinguishes syntax from
literal text inside strings, and recovers from malformed input by
specification, not by accident.
