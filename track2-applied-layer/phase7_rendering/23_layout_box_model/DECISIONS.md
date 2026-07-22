# Module 23: layout_box_model — DECISIONS.md

## Block-flow only: every child stacks vertically, filling parent width by default
**(c) Convention — a deliberate, named scope boundary.** Real CSS
layout includes inline layout (text wrapping into line boxes), flexbox,
grid, floats, and positioned layout, each with substantially different
algorithms. Block flow is the original, foundational CSS layout mode
and the one every other mode is usually explained as a variation
FROM — making it the correct, minimal starting point for proving
"layout is a recursive geometry computation" without the scope of a
full layout engine.

## Explicit `width`/`height` treated as CONTENT-box dimensions (not including padding)
**(b) External contract — this matches CSS's own DEFAULT sizing
model.** CSS's default `box-sizing: content-box` means a declared
`width`/`height` describes the content area only; padding and border
are added on top, which is exactly this module's own
`total_width = content_width + 2 * padding` calculation. This isn't a
simplification we introduced — it's a direct match to the real,
default CSS box model (the alternative, `box-sizing: border-box`,
where declared width INCLUDES padding, is a real, common,
deliberately-opted-into alternative this module does not implement).

## Auto width computed as `available_width - 2*margin - 2*padding`
**(b) External contract.** This is the real default block-layout
behavior: an element with no explicit width fills its containing
block's available width, with its own margin and padding subtracted
from what's left for its content. We verified this directly (see
`06 Run It`): sibling `#a` (with a 5px margin) and `#b` (with no
margin) received different actual content widths from the identical
400px container, purely because of each box's own margin — exactly the
real behavior, not something asserted without checking.

## Ignoring `Text` node children entirely for height/geometry purposes
**(c) Convention — a deliberate, named scope boundary.** Real inline
layout would measure actual glyph widths and wrap text into line boxes
with real heights, which requires font metrics this course has no
reason to implement. This module's boxes are sized entirely by
explicit `height`/CSS values or by summing child ELEMENT boxes — text
content is real in the tree (Module 20) but contributes no computed
geometry here, which is an honest, stated limitation rather than a
silent gap.

## `parse_px` supporting only bare `px` values, returning `None` (treated as "auto") for anything else
**(c) Convention.** Real CSS supports percentages, `em`/`rem`,
`auto`, `calc()`, and more for these properties. Restricting to `px`
keeps the arithmetic in this module simple and unambiguous while still
demonstrating the real recursive geometry computation faithfully —
adding unit conversion is a natural, separate extension, not something
this module's core claim depends on.

---

## Decisions We Made

| Decision | Category | Could it have gone another way? |
|---|---|---|
| Block-flow layout only | (c) Convention (named scope boundary) | Yes — inline/flex/grid are natural, larger extensions |
| Explicit width/height as content-box | (b) Forced — matches CSS's actual default sizing model | No, for the default (unset `box-sizing`) case |
| Auto width fills container minus own margin/padding | (b) Forced — real default block layout behavior, verified directly | No |
| Text nodes contribute no geometry | (c) Convention (avoids needing real font metrics) | Yes, at the cost of true inline layout |
| Only bare `px` units parsed | (c) Convention (keeps arithmetic simple, no ambiguity) | Yes — unit conversion is a natural extension |

## What We Proved

Running one real, deliberately constructed HTML+CSS example through
this module's recursive `layout_block()` produced exactly the
hand-computable expected geometry:

1. **The container** (`width: 400px; padding: 10px;`) resolved to a
   total box width of `420px` (400 content + 10px padding × 2) and an
   auto height of `150px` — exactly the sum of both children's heights
   plus its own padding.
2. **`#a`** (`margin: 5px`, no explicit width) received a content width
   of `390px` — the container's `400px` minus `#a`'s own `5px` margin
   on each side.
3. **`#b`** (no margin, no explicit width) received the FULL `400px`
   content width — proving auto-width depends on each box's OWN
   margin, not a sibling's.
4. **`#b`'s y-coordinate (`60`)** equaled exactly `#a`'s y (`10`) plus
   `#a`'s height (`50`) — real, observable block-flow vertical
   stacking, not an assumed or hardcoded relationship.

This is direct, run-and-observed confirmation that layout is a genuine
recursive geometry computation — every box's position and size is
mechanically derived from its parent's available space, its own CSS
box-model properties, and its children's own computed geometry, in
that specific top-down-then-bottom-up order.
