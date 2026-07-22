# Module 3: syscall_boundary — SAFETY_NOTES.md

**Status: low risk, documented for pattern consistency.**

## Primitives used
- Direct calls into `ntdll.dll`'s NT native API (`NtCreateFile`,
  `NtReadFile`, `NtClose`), bypassing the documented Win32 API layer.
- Hand-declared structs (`UNICODE_STRING`, `OBJECT_ATTRIBUTES`,
  `IO_STATUS_BLOCK`) matching an interface Microsoft treats as
  semi-private (used internally by Win32 and by driver code, not
  officially documented for application use, though extremely
  well-understood publicly).

## Why this is safe as built
- All operations target **files this module itself creates in its own
  working directory** (`proof_file.txt`) and cleans up after itself, or
  a deliberately nonexistent filename used only to test the failure
  path. No access to arbitrary user files, no path traversal, no
  operation on anything outside this module's own scratch file.
- Read-only and single-file-create/delete operations only — no
  destructive filesystem operations, no registry access, no process or
  memory manipulation of other processes.
- Calling undocumented-but-well-known NT native APIs is a completely
  standard technique in security research, systems programming, and
  EDR/AV product development itself — it is not, on its own, an evasive
  or offensive technique. It becomes relevant to defensive/offensive
  tooling only in *how* it's used (e.g., to bypass a specific userland
  hook placed on the Win32 layer) — this module doesn't do that; it
  uses the native layer purely to demonstrate the layering itself.

## Risk if extended
- The technique shown here (calling ntdll directly instead of
  kernel32) is the same technique used by some malware and by some
  EDR-evasion tooling specifically *to avoid* userland API hooks placed
  on the Win32 layer by security products. This module does not employ
  it for that purpose and involves no hooking, no injection, and no
  attempt to evade any monitoring. Worth flagging explicitly given this
  module will be a natural reference point if later, more adversarial
  modules (Track 2, Phase 10) discuss detection evasion — this course's
  scope explicitly excludes evasion techniques (see root ROADMAP.md,
  "Explicitly out of scope").

## Action needed
- None to proceed with Module 4. Keep this note in mind if any later
  module is tempted to build a general-purpose "call ntdll directly to
  avoid X" utility — that would need fresh, explicit scoping.
