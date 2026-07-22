# Module 18: cors_preflight — SAFETY_NOTES.md

**Status: no notable concerns.**

## Primitives used
- One loopback-only local server implementing a real, working
  origin-based CORS policy.
- A client-side CORS enforcement layer performing real OPTIONS
  preflight requests and real conditional requests.

## Why this is safe as built
- The server binds to `127.0.0.1` only, never network-reachable.
- All data involved (the served body, the allowed origin, the custom
  header value) is hardcoded, non-sensitive demo content defined by
  this module's own scripts.
- Both the "allowed" and "disallowed" requesting origins are fixed
  local port numbers this module itself defines — no real third-party
  origin is impersonated or targeted.

## Risk if extended
- None specific to this module. This module models a real, standard,
  defensive web mechanism (CORS) faithfully; there is no natural
  "more dangerous" extension of a working CORS policy checker.

## Action needed
- None to proceed with Module 19 (which begins Track 2's parsing
  phase — HTML tokenization).
