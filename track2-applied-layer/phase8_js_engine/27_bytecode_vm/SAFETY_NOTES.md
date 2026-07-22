# Module 27: bytecode_vm — SAFETY_NOTES.md

**Status: contained, executes compiled bytecode. Same category of
concern as Module 26; safe for the same reasons.**

## Primitives used
- A real compiler (AST -> bytecode) and a real VM that executes that
  bytecode.

## Why this is safe as built
- Identical scope boundary to Module 26: no built-in reaches the
  filesystem, network, environment, or host Python capabilities from
  within the interpreted language. The instruction set
  (`LOAD_CONST`/`LOAD_VAR`/`STORE_VAR`/`BINARY_OP`/`UNARY_OP`/`JUMP`/
  `JUMP_IF_FALSE`/`CALL`/`RETURN`/`POP`) has no instruction capable of
  touching anything outside the VM's own value stack and locals dict.
- All executed programs are fixed, hardcoded source strings defined in
  this module's own demo script.

## Risk if extended
- Same note as Module 26: adding any built-in function that reaches
  outside the VM's own sandboxed instruction set, or executing
  genuinely untrusted/external source through this compiler+VM, would
  need its own fresh review.

## Action needed
- None to proceed with Module 28.
