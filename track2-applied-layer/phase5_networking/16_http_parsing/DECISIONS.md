# Module 16: http_parsing — DECISIONS.md

## No `http.client`, no `requests` — a hand-rolled parser
**(c) Convention — the module's entire point.** Using a real HTTP
library would prove nothing about what an HTTP response actually looks
like; it would just prove the library works. Splitting on `\r\n\r\n`,
splitting header lines on `:`, and manually reversing chunked encoding
is the whole demonstration.

## Handling BOTH Content-Length and chunked framing, not just one
**(b) External contract, and a real, live discovery.** We initially
expected to demonstrate Content-Length framing against a live fetch
(`example.com`) and chunked framing only against our own local test
server. Running the live fetch for real revealed that `example.com`
(served via Cloudflare) actually uses **chunked** encoding by default
— not Content-Length. This is not a bug in our parser or our
expectations being "wrong" in a bad way — it's a real, useful fact
about how production CDN-fronted sites commonly serve content, learned
by testing rather than assumed. We kept the module honest about this:
`part_a_content_length()` was renamed in spirit (see its updated
comments) to report whatever framing the server *actually* used,
rather than asserting Content-Length was guaranteed.

## Adding a synthetic self-test (`self_test_synthetic_cases`) rather than relying on live fetches alone
**(c) Convention, adopted specifically because of the discovery
above.** Since no live server we tried happened to exercise the
Content-Length path, we added a deterministic, hand-built synthetic
test for it directly in the module's own run script — so the claim
"this parser handles Content-Length framing" is verified by something
that will pass consistently on every future run, not dependent on a
third party's current server configuration.

## A local server (`local_chunked_server.py`) for the chunked demonstration, rather than depending only on a live third party
**(c) Convention.** We initially tried a real public chunked-encoding
test endpoint (`httpbin.org`); it returned `503 Service Temporarily
Unavailable` when we tested it directly — a real illustration of why
depending on a specific third-party service's current uptime for a
repeatable course exercise is fragile. A small local server, sending a
genuinely real, wire-format-correct chunked response over a genuine
socket, gives the same teaching value with no dependency on any
external service's availability.

## Normalizing header names to lowercase during parsing
**(b) External contract.** HTTP header field names are explicitly
case-insensitive per the HTTP specification — a server may send
`Content-Length`, `content-length`, or `CONTENT-LENGTH` and all are
equally valid. Normalizing to lowercase on parse is what makes
`headers["content-length"]` a reliable lookup regardless of how a
specific server happened to capitalize it.

## The `raw.index(b'\\r\\n\\r\\n')` escaping bug we actually hit
**(c) Convention — kept here as a real, honest account.** An early
draft of the orchestrator's f-string used a doubled backslash
(`b'\\r\\n\\r\\n'`) inside an f-string expression, which Python parses
as the literal 8-character sequence `\r\n\r\n` (backslash-r-backslash-n...)
rather than four actual CR/LF bytes — causing a real
`ValueError: subsection not found` when run. The fix was to compute the
split point in a plain statement before the f-string
(`header_end = raw.index(b"\r\n\r\n")`) rather than embedding an
escaping-prone byte literal inside the f-string expression itself —
also simply better style, avoiding nested-quote fragility entirely.

---

## Decisions We Made

| Decision | Category | Could it have gone another way? |
|---|---|---|
| Hand-rolled parser, no HTTP library | (c) Convention (the module's entire point) | N/A |
| Handle both Content-Length and chunked | (b) Forced — real-world servers use both | No |
| Add a synthetic self-test | (c) Convention, adopted after a live-fetch surprise | Yes, but the Content-Length claim would otherwise go unverified |
| Local server for the chunked demo | (c) Convention (reliability over live third-party dependency) | Yes — a live chunked endpoint also works, when available |
| Lowercase header normalization | (b) Forced — HTTP header names are case-insensitive by spec | No |
| Avoid embedded byte literals inside f-strings | (c) Convention (fixed after a real bug) | Yes |

## What We Proved

1. **Synthetic self-test**: our parser correctly reconstructs
   `b"hello world"` from both a hand-built Content-Length response and
   a hand-built chunked response — deterministic, repeatable proof of
   both code paths.
2. **Part A (live fetch)**: a real request to `example.com` was parsed
   correctly — including discovering, by inspecting the real response
   rather than assuming, that Cloudflare serves it with chunked
   encoding rather than Content-Length.
3. **Part B (local chunked server)**: a real, from-scratch server
   emitted a genuinely chunked HTTP response over a real socket, which
   our parser correctly dechunked back into the original message,
   `b"The quick brown fox jumps."`

Together, this is direct, run-and-observed confirmation that an HTTP
response is exactly as much "magic" as roughly sixty lines of
straightforward text-splitting logic — nothing about parsing it
requires a framework, and the two real body-framing mechanisms in
common use are both fully within reach of a plain reading of the spec.
