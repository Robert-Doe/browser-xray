# Module 18: cors_preflight — DECISIONS.md

## Using a real `PUT` with a custom header, rather than a plain `GET`, as the demonstrated request
**(b) External contract.** The real CORS specification defines exactly
which requests are "simple" (GET/HEAD/POST with only a small allowlist
of headers) and therefore skip preflight entirely. A `PUT` with a
custom `X-Custom-Auth` header is guaranteed, by the spec itself, to
require a preflight — choosing this specific combination wasn't
arbitrary, it's what makes `_needs_preflight()` actually trigger and
therefore what makes this module's core mechanism (the OPTIONS
round trip) observable at all.

## The server checking `Origin` and deciding per-request, rather than a static, always-on `Access-Control-Allow-Origin: *`
**(c) Convention.** A wildcard `*` origin is common in real APIs, but
it would make Part A and Part B of this module's demo produce the
identical (allowed) result, proving nothing about origin-specific
policy. Checking the actual `Origin` header against one specific
allowed value is what makes the module able to show both a real grant
and a real denial from the same server, same code path, same request
shape.

## The server always processing the ACTUAL request (not just the preflight) regardless of origin, and only conditionally adding `Access-Control-Allow-Origin`
**(b) External contract — this is real CORS behavior, not our
invention.** A CORS-compliant server's ordinary request handling is not
supposed to refuse to process a request just because of a disallowed
origin — the response is computed normally, and the ONLY difference is
whether the `Access-Control-Allow-Origin` header is included. It is the
BROWSER's job to withhold that already-computed response from script if
the header is missing or wrong — this module's client-side
`cors_enforced_fetch()` implements exactly that responsibility, mirroring
Module 17's core lesson at a more advanced layer.

## Requiring the preflight grant AND a matching header on the actual response (not treating preflight approval as final)
**(b) External contract.** This is a real, sometimes-missed subtlety
of the actual CORS specification: a successful preflight only means
the browser is PERMITTED to send the real request — it does not, by
itself, guarantee the real response will be exposed. The real response
must independently carry a matching `Access-Control-Allow-Origin`.
Implementing only the preflight check would model CORS incorrectly by
omission.

## `_needs_preflight()` as a simple two-condition check, not the full real "simple request" rule set
**(c) Convention — a deliberate, named simplification.** The real spec's
definition of a "simple request" has more nuance (specific allowed
Content-Type values, exact casing rules for allowed headers, etc.).
This module's simplified check ("non-GET/HEAD/POST, or any custom
header at all triggers preflight") captures the load-bearing shape of
the real rule without reproducing every edge case, which is out of
scope for what this module needs to prove.

---

## Decisions We Made

| Decision | Category | Could it have gone another way? |
|---|---|---|
| `PUT` + custom header as the demo request | (b) Forced — guarantees a real preflight per spec | No, for this module's specific point |
| Origin-specific server policy (not wildcard) | (c) Convention (need both a grant and a denial to demonstrate) | Yes, `*` also matches real-world APIs, wrong choice for this demo |
| Server processes actual requests regardless of origin | (b) Forced — real CORS servers behave this way | No |
| Both preflight AND actual-response checks required | (b) Forced — real spec behavior, a common omission elsewhere | No |
| Simplified `_needs_preflight()` | (c) Convention (captures the shape, not every edge case) | Yes, a fuller implementation is possible but out of scope |

## What We Proved

1. **Part A**: a non-simple cross-origin request from the server's one
   allowed partner origin correctly triggered a real OPTIONS preflight,
   received a real grant, and the subsequent real PUT's response was
   correctly exposed to the caller.
2. **Part B**: the byte-for-byte identical request, differing only in
   the `Origin` header value, was blocked at the preflight stage —
   real, captured evidence that CORS is a per-origin, server-decided
   policy, checked by the client before any risky request is sent.
3. **Part C**: a same-origin request bypassed all CORS machinery
   entirely, confirming CORS is specifically a cross-origin concern,
   irrelevant when the origins already match.

Together, this is direct, run-and-observed confirmation that CORS is
an explicit, server-controlled, per-origin RELAXATION of the
Same-Origin Policy's default — enacted through a real, extra
round trip (the preflight) precisely so a browser can ask permission
before sending a request that could have a real side effect, rather
than discovering the answer only after the fact.
