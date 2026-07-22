# Module 1: mem_addressing — SAFETY_NOTES.md

**Status: no notable concerns. Documented for completeness / pattern consistency.**

## Primitives used
- `ctypes` call into the real Win32 `VirtualQuery` function.
- `id()` on live CPython objects to obtain a virtual address.

## Why this is safe as built
- `VirtualQuery` is a **read-only introspection** API — it reports
  metadata about a memory region, it does not modify memory, change
  permissions, or execute anything.
- Every address queried belongs to **the calling process's own address
  space**. No other process, no kernel memory, no cross-process access
  is attempted anywhere in this module.
- No network activity, no file writes outside the repo, no elevation,
  no persistence.

## Risk if extended
- None identified. This module has no natural "more dangerous" version
  — it's a pure information-gathering demo about one's own process.

## Action needed
- None. No external tools, downloads, or user review required.
