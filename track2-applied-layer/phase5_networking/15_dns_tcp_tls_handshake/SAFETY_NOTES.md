# Module 15: dns_tcp_tls_handshake — SAFETY_NOTES.md

**Status: no notable concerns — first module in the course making a
real outbound network connection.**

## Primitives used
- Real DNS resolution, a real TCP connection, and a real TLS handshake
  against a live, real-world server (`example.com`, port 443).
- A single real `HEAD` HTTP request over that connection.

## Why this is safe as built
- `example.com` is IANA's own domain, explicitly reserved and
  documented as safe for exactly this kind of testing and
  documentation use — not a production service the traffic could
  meaningfully burden.
- The module makes exactly one lightweight `HEAD` request per run — no
  loops, no repeated hammering, no body download.
- Standard TLS certificate verification is left enabled (Python's
  `ssl.create_default_context()` default) — the connection is
  genuinely authenticated, not weakened for convenience.
- No credentials, cookies, or any user data are sent — the request
  carries only a descriptive `User-Agent` identifying it as course
  material.

## Risk if extended
- None specific to this module. This is the first module to reach
  outside the local machine; later modules (17–35) build on this same
  pattern (real or loopback-only HTTP/TLS traffic) for origin/policy
  demonstrations — each gets its own safety note as built.

## Action needed
- None to proceed with Module 16.
