# Module 15: dns_tcp_tls_handshake — DECISIONS.md

## Using Python's `ssl` module rather than hand-parsing/constructing raw TLS records
**(c) Convention — a deliberate scope boundary.** Hand-constructing a
real TLS 1.3 ClientHello (key exchange groups, cipher suite lists,
extensions, the full cryptographic handshake) is a substantial
undertaking on its own — implementing it correctly would be a
different course. This module's actual claim is about the layered
COST and SEQUENCE of DNS → TCP → TLS, not about re-implementing TLS
itself. Python's `ssl` module performs a real, correct, standards-compliant
handshake against a real server (backed by OpenSSL) — we verify and
report its real results, we don't fabricate or simulate them.

## `example.com` as the target host
**(c) Convention.** A stable, well-known, low-risk, widely-used
testing domain — explicitly reserved by IANA for documentation and
testing purposes, meaning hitting it repeatedly for a course exercise
is exactly the kind of use it exists for, unlike targeting an arbitrary
production website.

## `socket.getaddrinfo()` rather than `socket.gethostbyname()`
**(c) Convention.** `gethostbyname()` is an older, IPv4-only API that
returns a single address. `getaddrinfo()` is the modern, protocol-agnostic
API and — as our own captured output shows — a single hostname can
resolve to multiple real addresses (in this run, two, both Cloudflare
edge IPs). Using the API that reveals this multiplicity is a more
honest demonstration of what DNS resolution for a real production
domain actually returns.

## `HEAD` instead of `GET` for the HTTP request
**(c) Convention.** A `HEAD` request gets a real server to respond with
real headers and a real status line, without transferring a page body
— which lets this module's final line make a precise, true claim ("not
one byte of an actual HTML page has arrived") without needing to
discard or ignore a body we didn't ask for in the first place.

## Hex-dumping the DECRYPTED response bytes, with an explicit note about what an eavesdropper would see
**(c) Convention.** We cannot, without additional tooling (raw packet
capture, which needs elevated privileges/npcap on Windows and is out
of this module's scope), show the actual ciphertext crossing the wire.
Showing the decrypted plaintext bytes, with an explicit, honest caveat
that this readability exists only because TLS already did its job for
us, keeps the claim accurate without overstating what was actually
captured.

## Timing each phase separately with `time.perf_counter()`
**(c) Convention.** `perf_counter()` is Python's documented choice for
measuring short elapsed intervals (monotonic, highest available
resolution) — using `time.time()` instead would be vulnerable to
system clock adjustments during measurement, a real (if usually small)
source of inaccuracy for exactly this kind of before/after timing.

---

## Decisions We Made

| Decision | Category | Could it have gone another way? |
|---|---|---|
| `ssl` module over hand-rolled TLS | (c) Convention (deliberate scope boundary) | Yes — building TLS by hand is a different, much larger project |
| `example.com` as target | (c) Convention (safe, intended-for-this-purpose domain) | Yes, any HTTPS host works |
| `getaddrinfo` over `gethostbyname` | (c) Convention (more honest, more modern) | Yes |
| `HEAD` over `GET` | (c) Convention (precise, true final claim) | Yes, `GET` + discarding the body also works, less cleanly |
| Hex-dump decrypted bytes with an eavesdropper caveat | (c) Convention (accuracy given tooling limits) | Yes, with raw packet capture tooling (out of scope here) |
| `perf_counter()` for timing | (c) Convention (documented best practice for this exact case) | Yes, `time.time()` is strictly worse here |

## What We Proved

A single real run against a real server produced:

1. **DNS**: two real IP addresses for `example.com`, resolved in
   ~9–30 ms across runs.
2. **TCP**: a real three-way handshake completing in ~25 ms, with a
   real OS-assigned ephemeral local port confirmed via `getsockname()`.
3. **TLS**: a real TLS 1.3 handshake in ~34–41 ms, negotiating
   `TLS_AES_256_GCM_SHA384`, against a real certificate (subject
   `example.com`, issued by Cloudflare's issuing CA, with a real
   expiration date).
4. **HTTP**: a real `200 OK` response over the encrypted channel, with
   real header bytes captured and hex-dumped, arriving *after* every
   one of the above steps had already completed.

This is direct, run-and-observed evidence that "loading a URL" is not
one action but a strict sequence of independently measurable costs —
and that every byte of that sequence completes *before* anything
resembling the actual requested content exists anywhere in the browser.
