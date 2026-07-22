# Module 20: dom_tree_builder — DECISIONS.md

## Reusing Module 19's tokenizer unchanged, as a local copy
**(c) Convention, consistent with this course's per-module
self-containment.** `tokens.py` and `html_tokenizer.py` are copied
verbatim from Module 19 — this module's actual subject is what happens
AFTER tokenization, and reusing the exact, already-verified tokenizer
rather than reimplementing or importing across module directories
keeps this module runnable on its own while making clear the tree
constructor is a genuinely separate stage operating on the token
stream, not something bundled into the tokenizer itself.

## A "stack of open elements" as the core data structure
**(b) External contract.** This is not our design choice — it is
exactly the data structure the real HTML5 tree construction algorithm
is specified around. The stack's top is always "where new content
currently gets inserted," and popping/pushing it is what "closing" and
"opening" an element concretely means at the implementation level.

## Checking only the IMMEDIATE top of the stack for auto-close rules, rather than the real spec's full "scope" algorithm
**(c) Convention — a deliberate, named scope simplification.** The real
spec's auto-close logic (e.g., for `<p>`) walks the stack looking for a
"button scope" boundary, not just the immediate parent — this handles
more deeply nested edge cases correctly. This module's simplified,
immediate-top-only check correctly reproduces the well-known, most
commonly cited real behavior (`<p>1<p>2` producing sibling paragraphs;
`<li>` chains not nesting) without implementing the full scope-tracking
algorithm, which is a substantially larger undertaking out of this
module's scope.

## Void/self-closing elements appended as children but never pushed onto the stack
**(b) External contract.** `<img>`, `<br>`, and similar void elements
are defined by the HTML spec as unable to have children or a matching
end tag at all — pushing one onto the open-elements stack would be
incorrect, since nothing should ever be "inside" it. Skipping the push
for these is required correctness, not a convenience.

## An unmatched end tag scanning the WHOLE stack, and being silently ignored if no match exists
**(b) External contract.** Both the "closes every open descendant back
to the match" behavior and the "no match anywhere → ignored entirely"
behavior are real, specified HTML5 parsing outcomes — not
simplifications we introduced. We verified both directly:
`<div><span>text</div>` correctly closes the still-open `<span>`
too, and `</span>` in `<p>hello</span></p>` (with no `<span>` ever
opened) is correctly ignored, leaving `<p>` open and correctly closed
by the following `</p>`.

## A simple `render_tree()` pretty-printer, not a real DOM API surface
**(c) Convention.** A real DOM implements `Node.childNodes`,
`Node.parentNode`, `getElementsByTagName`, and much more. This module's
only job is to prove the TREE SHAPE is built correctly via the stack
mechanism — a plain, readable text rendering of that shape is
sufficient evidence, and building a fuller DOM API surface is out of
scope here.

---

## Decisions We Made

| Decision | Category | Could it have gone another way? |
|---|---|---|
| Reuse Module 19's tokenizer as a local copy | (c) Convention (self-containment) | Yes — cross-directory import also works, less consistent |
| Stack of open elements as the core structure | (b) Forced — matches the real spec's own algorithm shape | No |
| Immediate-top-only auto-close check | (c) Convention (named simplification of full scope algorithm) | Yes, at the cost of some deeply-nested edge cases |
| Void elements never pushed onto the stack | (b) Forced — void elements cannot have children by spec | No |
| Unmatched end tags ignored entirely | (b) Forced — real, specified behavior, verified directly | No |
| Plain-text `render_tree()` over a full DOM API | (c) Convention (sufficient for this module's claim) | Yes, a fuller API is a natural but out-of-scope extension |

## What We Proved

Running five real, illustrative inputs through the tokenizer and this
module's tree constructor produced trees matching real browser
behavior in every case:

1. **`<p>1<p>2`** produced two SIBLING `<p>` elements, not nested —
   confirming the real, well-known `<p>` auto-close rule.
2. **`<ul><li>a<li>b</li></ul>`** produced two sibling `<li>` elements
   under one `<ul>` — confirming the analogous `<li>` auto-close rule.
3. **`<div><span>text</div>after`** correctly closed BOTH the
   still-open `<span>` and the `<div>` when `</div>` was encountered,
   with `"after"` correctly landing as a sibling of `<div>`, not inside
   it — confirming the "ancestor's end tag closes open descendants too"
   rule.
4. **`<p>hello</span></p>`** correctly ignored the unmatched `</span>`
   entirely, leaving `<p>` open to be closed correctly by the following
   `</p>`.
5. **Ordinary well-formed nesting** produced the exact expected tree
   shape, confirming the mechanism doesn't misbehave on the happy path.

This is direct, run-and-observed confirmation that a DOM tree is built
incrementally, one token at a time, via a stack that tracks the current
insertion point — and that several specific, real, and initially
counter-intuitive HTML behaviors (implicit tag closing, implicit
closing of descendants, silent ignoring of orphaned end tags) are exact
consequences of that one mechanism, not separate special cases bolted
on top of it.
