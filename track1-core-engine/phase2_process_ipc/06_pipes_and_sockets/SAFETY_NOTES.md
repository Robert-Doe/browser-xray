# Module 6: pipes_and_sockets — SAFETY_NOTES.md

**Status: no notable concerns.**

## Primitives used
- A Windows named pipe (`\\.\pipe\module6_demo_pipe`), local to this
  machine, server and client both spawned by this module's own scripts.
- A TCP socket bound to `127.0.0.1` (loopback only — never binds to a
  non-loopback interface or `0.0.0.0`).

## Why this is safe as built
- The TCP server binds explicitly to `127.0.0.1`, not a wildcard
  address, so it is never reachable from the network — only from this
  same machine.
- The named pipe name is a fixed, non-sensitive string with no
  collision risk with real system pipes.
- No data exchanged is anything other than a hardcoded demo string; no
  file paths, credentials, or user-controllable input are transmitted.
- Both servers accept exactly one connection and exit — no long-running
  listening service is left behind after the demo scripts finish.

## Risk if extended
- None specific to this module. Loopback-only sockets and named pipes
  between same-machine, same-user processes are standard, unremarkable
  IPC — this is the same mechanism class as Module 8's toy browser
  shell will build on, at which point the "who can connect to this
  channel" question becomes more relevant (addressed there).

## Action needed
- None to proceed with Module 7.
