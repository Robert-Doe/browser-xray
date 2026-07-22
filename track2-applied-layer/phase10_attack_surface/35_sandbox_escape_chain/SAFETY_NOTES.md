# Module 35: sandbox_escape_chain — SAFETY_NOTES.md

**Status: contained. Combines two already-reviewed, real, restrictive
(never escalating) mechanisms from Modules 9 and 10. This is the
course's final module and the clearest expression of its actual
purpose: showing defenses working and failing in combination, for
defensive understanding. Safe as built.**

## Primitives used
- Windows Job Objects (Module 10's real mechanism), applied only
  restrictively.
- Least-privilege integrity-lowered tokens (Module 9's real mechanism),
  applied only restrictively (always lowering, never raising —
  structurally incapable of doing otherwise, per Module 9's own
  `DECISIONS.md`).
- A "compromised renderer" probe that attempts exactly two fixed,
  bounded actions (spawn a hardcoded trivial process; append a fixed
  string to a file this module itself created).

## Why this is safe as built
- **Every restriction demonstrated here is a real, working DEFENSE,
  never a bypass.** No scenario in this module shows a way to escape a
  restriction that was actually applied — all four scenarios simply
  vary which of two real, restrictive mechanisms are active, and
  observe the (always correctly restrictive, when active) result. There
  is no "Scenario E" showing either defense being defeated.
- **The "sensitive file" is created, tampered with, and deleted
  entirely within this module's own script**, containing only a fixed
  demo string — not real Browser Process data, not anything from a real
  application.
- **The "spawned process" in every scenario is a trivial, fixed,
  harmless command** (`python -c "print(...)"`) — never anything
  capable of further action itself.
- This module's own explicit conclusion is that COMBINING real
  defenses is necessary — reinforcing, not undermining, this course's
  defensive framing throughout.

## Risk if extended
- None beyond what Modules 9 and 10 already flagged in their own
  `SAFETY_NOTES.md` files for these same underlying mechanisms — this
  module adds no new primitive, only a new combination of two already-
  reviewed ones.

## Action needed
- None. This is the final module of the course.
