# Module 24: paint_and_composite — DECISIONS.md

## Splitting paint and composite into two genuinely separate functions/stages, not one combined step
**(c) Convention — the module's entire point.** It would be simpler
code to paint directly into final on-screen positions in one pass.
Keeping them separate — paint producing records in local box
coordinates, composite assigning those records to layers with their
own offsets — is what makes it possible to update ONLY the composite
stage later without re-running paint at all, which is the real
architectural reason this split exists in actual browsers.

## `needs_own_layer()` checking for the presence of `transform` (or `will-change: transform`)
**(b) External contract.** These are real, well-known triggers for
compositor layer promotion in actual browser engines — not arbitrary
properties we picked. Real engines use a broader set of triggers
(3D transforms, `opacity` animations, `will-change`, `<video>`/`<canvas>`
elements, and more), but `transform` is the most commonly cited,
clearest example, making it the right one to model explicitly.

## Instrumenting the pipeline with plain call counters, rather than real wall-clock timing
**(c) Convention.** This module's claim is about WHICH stages run, not
about how much time each one takes — real timing would depend heavily
on this specific machine and Python's overhead, and would risk implying
a performance claim this toy pipeline was never built to substantiate
accurately. A count of "did this stage's function get called again"
is a precise, honest, and sufficient way to demonstrate the skip.

## `change_compositor_only_property()` directly mutating an existing layer's offset, rather than re-running `composite()` from scratch
**(c) Convention — this IS the point.** A real compositor doesn't
re-walk the entire box tree to move one already-promoted layer; it
just updates that layer's transform and lets the GPU composite the
existing bitmaps at the new position. Directly adjusting
`layer.offset_x`/`offset_y` on the already-existing `Layer` object
mirrors that real behavior far more accurately than calling
`composite()` again would — the latter would still "work" but would
misrepresent what real compositors actually do.

## A real, caught bug: the compositor-only path initially forgot to increment `composite_runs`
**(c) Convention — kept here as an honest, verified account.** The
first version of `change_compositor_only_property()` correctly updated
the layer's offset but never incremented `self.composite_runs`,
making the demo's own counters misleadingly claim composite hadn't run
at all for that update. Running the demo and reading the printed
counts directly (rather than assuming the code was correct) caught
this immediately — the fix was one added line. Left documented here
because it's a good, real example of exactly the "verify before
trusting your own instrumentation" habit this course tries to model
throughout.

---

## Decisions We Made

| Decision | Category | Could it have gone another way? |
|---|---|---|
| Paint and composite as separate stages/functions | (c) Convention (the module's entire point) | N/A |
| `transform`/`will-change` as layer-promotion triggers | (b) Forced — real, well-known browser behavior | No, for the clearest, most commonly cited example |
| Call-count instrumentation over wall-clock timing | (c) Convention (precise claim, avoids an unsubstantiated perf claim) | Yes, real timing is possible but risks over-claiming |
| Direct layer-offset mutation for compositor-only updates | (c) Convention (mirrors real compositor behavior) | Yes, technically re-running composite() also "works" |
| Composite counter bug, caught and fixed | (c) Convention (honest account of a real, caught bug) | N/A |

## What We Proved

Running one real page through the instrumented pipeline, then applying
two different kinds of updates, produced exactly the claimed contrast:

1. **Initial render**: style, layout, paint, and composite each ran
   exactly once, producing a base layer and one dedicated layer for the
   element with `transform` set.
2. **Changing `#box`'s `width`** (a layout-affecting property):
   layout, paint, AND composite counts all incremented — real,
   necessary work, since the geometry itself changed.
3. **Changing `#mover`'s `transform`** (a compositor-only property):
   ONLY the composite count incremented. Layout and paint counts
   stayed exactly where they were after step 2 — direct, captured
   proof that this update never touched either stage.

This is direct, run-and-observed confirmation that paint and composite
are genuinely separate pipeline stages, and that specific CSS
properties (`transform`, `opacity` in real engines) are singled out in
browser performance guidance precisely because changing them can skip
layout and paint entirely, not merely because they're described that
way in documentation.
