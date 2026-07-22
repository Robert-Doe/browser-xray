# Module 17: origin_model_sop — DECISIONS.md

## Two local servers on different PORTS, rather than different hostnames
**(c) Convention.** Port is a full, equal member of the origin tuple
(Prerequisite 8) — using two ports on `127.0.0.1` is a completely valid
way to create two genuinely different origins, without needing to
provision fake DNS names, a hosts-file edit, or certificates. This
keeps the module self-contained and reliable while still exercising a
real (if minimal) axis of the origin comparison.

## `naive_fetch()` and `sop_enforced_fetch()` sharing the identical underlying `_raw_get()` network call
**(c) Convention — the module's central, deliberate design choice.**
The whole point is to show that SOP enforcement is a decision made
*after* the network layer has already done its job, not a
network-level restriction. Giving both functions their own separate
network code would risk implying (even unintentionally) that SOP works
by altering what gets sent over the wire — it doesn't. Both call the
exact same `_raw_get()`.

## Raising `BlockedBySameOriginPolicy` only AFTER the real request completes
**(c) Convention.** This ordering is not an implementation detail —
it's the whole teaching point. The exception is raised once we already
have a real, complete response in hand, specifically to make it
undeniable in the code's own control flow that the network round trip
already happened before the origin check ever ran.

## A minimal, Content-Length-only `http_helpers.py`, duplicated (not imported) from Module 16
**(c) Convention, consistent with this course's per-module
self-containment.** This module's own toy servers always respond with
`Content-Length` (see `toy_servers.py`), so the fuller parser's
chunked-decoding logic is genuinely unnecessary here — a smaller,
scoped-down local copy is more honest about what this specific module
actually needs than importing the fuller Module 16 parser across
directories would be.

## `Origin` as a frozen dataclass, `same_origin()` as a free function comparing a 3-tuple
**(c) Convention.** A frozen (immutable) dataclass makes an `Origin`
usable as a value that can't be accidentally mutated after construction
— appropriate for something meant to represent a fixed identity.
Comparing via an explicit 3-tuple equality (`(a.scheme, a.host, a.port)
== (b.scheme, b.host, b.port)`) makes the ENTIRE Same-Origin Policy
comparison visible in one line, rather than spread across multiple
`and`-chained conditions that could be individually mis-edited later.

---

## Decisions We Made

| Decision | Category | Could it have gone another way? |
|---|---|---|
| Two ports instead of two hostnames | (c) Convention (self-contained, still a real origin-tuple axis) | Yes — fake hostnames via a hosts-file edit also work, with more setup |
| Shared `_raw_get()` between naive and enforced fetch | (c) Convention (the module's core teaching move) | N/A |
| Exception raised only after the real request completes | (c) Convention (makes the ordering undeniable in code) | N/A |
| Local, Content-Length-only parser copy | (c) Convention (per-module self-containment, scoped to actual need) | Yes — importing Module 16's fuller parser also works |
| `Origin` as frozen dataclass, tuple-equality comparison | (c) Convention (immutability + one-line clarity) | Yes |

## What We Proved

1. **Part A**: with no origin awareness anywhere in the fetch code, a
   "script on origin A" read origin B's private data directly and
   completely — real, captured evidence of what the web would look
   like with no Same-Origin Policy: any page could read any other
   site's response bodies at will.
2. **Part B**: the identical cross-origin request, made through the
   SOP-enforcing wrapper, was refused — but only after the real network
   round trip to origin B had already completed, confirmed by the
   exception's own message and the code's control flow.
3. **Part C**: the identical enforcing wrapper allowed a same-origin
   request through normally — confirming the policy specifically
   targets cross-origin script access, not network requests in general.

This is direct, run-and-observed confirmation of the module's central
claim: the Same-Origin Policy is enforced by the browser, on the
response side, after the request has already gone out — never by the
server, and never by preventing the request itself.
