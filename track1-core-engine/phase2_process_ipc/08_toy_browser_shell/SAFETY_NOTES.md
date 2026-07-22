# Module 8: toy_browser_shell — SAFETY_NOTES.md

**Status: no notable concerns. Flagged for forward-reference since
this module is the foundation later, more sensitive modules build on.**

## Primitives used
- TCP sockets bound to `127.0.0.1` only (loopback, never network-reachable).
- `subprocess.Popen` spawning a fixed, known script
  (`renderer_process.py`) with no dynamic/user-controllable command
  construction.
- A custom length-prefixed JSON message protocol (no use of `pickle`,
  `eval`, or any other deserialization mechanism capable of executing
  arbitrary code from message content — `json.loads` only ever produces
  plain data).

## Why this is safe as built
- No real network exposure: the listening socket is loopback-only.
- No arbitrary code execution risk in the protocol: JSON deserialization
  cannot construct or execute code, unlike `pickle` or similar.
- The "renderer" does no real file, network, or system access on the
  URLs it receives — it only formats a string. There is no actual
  content fetching, parsing, or execution happening yet at this stage
  of the course.
- Renderer processes are spawned with the same privilege level as the
  Browser Process (no sandboxing has been applied yet — that is
  Module 9's explicit, later addition, not an oversight here).

## Risk if extended
- **This is the load-bearing note for this module.** Every later
  Track 2 module that touches HTML/CSS/JS parsing (Modules 19–28) or
  security policy (Modules 29–35) builds its "renderer" logic on top of
  this same shell. As soon as a future module makes the renderer parse
  *real, externally-sourced* content (an actual HTML file, a real
  fetched URL), that module needs its own fresh safety review — the
  "no real content processing happens yet" safety property this note
  relies on will no longer hold, by design, at that point.

## Action needed
- None to proceed with Module 9. Revisit this note explicitly once
  Track 2 begins feeding real external content into a renderer built on
  this shell (starting around Module 19).
