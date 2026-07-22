# Module 5: process_creation — SAFETY_NOTES.md

**Status: no notable concerns.**

## Primitives used
- `VirtualAlloc` with an explicit, fixed `lpAddress`, committing memory
  at a specific virtual address.
- `subprocess.run` to spawn a same-user, same-privilege child process
  running a fixed, hardcoded script from this module's own directory.

## Why this is safe as built
- All memory operations affect **only each process's own address
  space**. No cross-process memory access, no `WriteProcessMemory`, no
  `ReadProcessMemory` against another process, no handles opened to
  another process at all in this module.
- The child process runs a fixed, known script
  (`child_writes_same_address.py`) — there is no dynamic code
  generation, no arbitrary command construction, no user-controllable
  input reaching `subprocess.run`.
- The pinned address (32 TB) is chosen specifically to avoid colliding
  with anything meaningful; writing to it has no effect beyond this
  module's own scratch memory.

## Risk if extended
- None identified specific to this module. The general pattern (fixed
  address requests via `VirtualAlloc`) is ordinary, unremarkable systems
  programming — it does not, on its own, constitute a memory-corruption
  or injection primitive the way Module 2's RWX-execute pattern did.

## Action needed
- None to proceed with Module 6.
