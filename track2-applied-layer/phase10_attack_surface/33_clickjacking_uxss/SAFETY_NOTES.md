# Module 33: clickjacking_uxss — SAFETY_NOTES.md

**Status: contained, educational demonstration of two real
vulnerability classes (clickjacking, UXSS) against this course's own
toy models. Consistent with Module 32's pattern. Safe as built.**

## Primitives used
- A toy compositor layer/hit-testing model (extending Module 24's real
  paint/composite concepts).
- A toy multi-window model with a deliberately togglable origin-check
  flag.

## Why this is safe as built
- **No real rendering, no real browser, no real network activity
  anywhere.** All "layers," "windows," and "documents" are plain Python
  objects with fixed, hardcoded demo data (a fake bank button label, a
  fake auth token string) defined entirely within this module's own
  scripts.
- **The UXSS "vulnerability" is a deliberately exposed toggle
  (`enforce_origin_check`), not a disguised real engine bug.** This
  module does not attempt to find, reproduce, or exploit any bug in a
  real browser engine — it demonstrates the CONSEQUENCE such a bug
  class has, using a flag that makes the before/after comparison
  explicit and honest.
- **The clickjacking demo never renders anything visually** — it's a
  pure coordinate/z-index calculation proving which layer WOULD receive
  a click, with no actual UI, no actual user interaction capture, and
  no real target website referenced by real domain name.

## Risk if extended
- Same category of note as Module 32: this module is a natural point
  where a request to build a REAL clickjacking overlay page (an actual
  HTML/CSS page with a real invisible iframe) or to search for a real,
  currently-unpatched UXSS bug in a real browser might arise. Both
  would be fundamentally different, unauthorized, and out of this
  course's explicit scope (per the root `ROADMAP.md`). Nothing in this
  module's code is structured toward either extension.

## Action needed
- None to proceed with Module 34.
