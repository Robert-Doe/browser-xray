# Module 22: style_computation — DECISIONS.md

## Adding a `parent` reference to DOM nodes (absent in Module 20)
**(c) Convention, forced by a new real need.** Module 20's tree
constructor never needed to look upward — it only ever needed "where
am I inserting right now." Descendant-combinator selector matching
(`div p`) genuinely requires walking UP from an element toward the
root, checking each ancestor. Rather than retrofit Module 20's file,
this module's local copy of `tree_constructor.py` adds the one field
needed for its own actual purpose.

## Selector scope: type/class/ID/universal + descendant combinator only
**(c) Convention — a deliberate, named scope boundary.** Real CSS
selectors include child (`>`), sibling (`+`, `~`), attribute
(`[href]`), and pseudo-class/element selectors (`:hover`,
`::before`), each with their own matching AND specificity rules. This
module implements enough to demonstrate genuine, real cascade behavior
(specificity comparison, source-order tiebreaking, `!important`
override, and ancestor-dependent matching) without reproducing the
entire selector grammar, which is substantially larger in scope.

## Specificity as a real `(ids, classes, types)` tuple, summed across the WHOLE selector
**(b) External contract.** This is exactly how real CSS specificity is
defined and compared — not our invention. Comparing specificity as
tuples (Python's native tuple comparison does exactly the right
lexicographic ordering: IDs matter more than classes, which matter
more than types) is a direct, correct implementation of the real rule,
not an approximation.

## Sorting candidates ascending by `(important, specificity, source_order)` and letting later writes overwrite earlier ones per property
**(c) Convention — an implementation technique chosen to directly
mirror the real cascade's actual decision process.** Rather than
writing separate comparison logic for "which of these two candidates
wins," sorting once by the exact real priority order and then
iterating in that order (so the last write for any given property is
automatically the correct cascade winner) makes the WINNING candidate
for each property a direct consequence of Python's own stable sort,
not a separately-maintained comparison function that could drift out
of sync with the sort order.

## Resolving the cascade PER PROPERTY, not per matching rule/declaration-block
**(b) External contract.** This is how real CSS actually works — two
different rules can each contribute different WINNING properties to
the same element's final computed style (as this module's own test
shows: the `<div>` gets `color` from one rule and `background` from a
different one). Treating an element's final style as "pick one whole
winning rule" would be a fundamentally incorrect model of the cascade.

## Deliberately NOT implementing property inheritance (e.g. `color` cascading from parent to child when unset)
**(c) Convention — a deliberate, named scope boundary.** The ROADMAP
scopes this module specifically to "cascade + specificity." Real CSS
also has a separate, additional mechanism where certain properties
inherit their computed value from a parent element when no rule sets
them explicitly — genuinely useful and real, but a distinct mechanism
from the cascade itself, and left out of this module's scope
deliberately rather than blurred into the cascade logic.

---

## Decisions We Made

| Decision | Category | Could it have gone another way? |
|---|---|---|
| Added `parent` reference to DOM nodes | (c) Convention (forced by descendant-matching's real need) | No, for this specific capability |
| Selector scope limited to type/class/ID/universal + descendant | (c) Convention (named scope boundary) | Yes — a fuller selector engine is a natural extension |
| Specificity as a real, summed `(ids, classes, types)` tuple | (b) Forced — matches real CSS specificity definition | No |
| Ascending sort + overwrite for cascade resolution | (c) Convention (mirrors the real decision process directly) | Yes, an explicit comparator function also works |
| Per-property (not per-rule) cascade resolution | (b) Forced — matches real CSS behavior | No |
| No property inheritance | (c) Convention (named scope boundary, separate from cascade) | Yes — inheritance is a natural, separate extension |

## What We Proved

Running one real HTML document and one real, deliberately-crafted
stylesheet through tokenizer → tree constructor → CSS parser → cascade
resolution produced exactly the real, specified cascade outcome:

1. **`<div id="header" class="title">`** resolved `color: blue` — the
   ID selector (`#header`) outranked the class selector (`.title`)
   despite `.title`'s rule appearing FIRST in the stylesheet, directly
   confirming specificity beats source order.
2. **Both `<p>` elements** resolved `color: green` — the `!important`
   declaration on the lowest-specificity matching rule (`p`) beat
   every higher-specificity rule that lacked `!important`, directly
   confirming `!important` overrides specificity entirely.
3. **Only the `<p>` nested inside the `<div>`** resolved
   `font-weight: bold` — the top-level `<p>` correctly did NOT match
   the descendant-combinator selector `div p`, confirming ancestor-
   dependent matching works correctly using the newly-added parent
   references.

This is direct, run-and-observed confirmation that every DOM node
gets one fully resolved computed style via a real, correctly-ordered
cascade — before a single pixel of layout or paint exists anywhere in
this course's pipeline.
