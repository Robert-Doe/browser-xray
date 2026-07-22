# Module 8: toy_browser_shell — DECISIONS.md

## `ipc_protocol.py`

### Length-prefixed JSON over the header format `"!I"`
**(c) Convention, with a (a) forced component.** Choosing JSON as the
message format, and choosing to prefix each message with its length,
is our design — a real system might use protobuf, Cap'n Proto, or
Mojo's own binary format instead. But the *reason* a length prefix is
needed at all is forced: TCP is a byte stream with no built-in message
boundaries (unlike Module 6's message-mode named pipe), so without
some framing scheme, `recv()` cannot know where one JSON object ends
and the next begins. The `"!"` in the format string forcing
**network byte order (big-endian)** is a convention we chose to follow
— not because TCP requires it structurally, but because it's the
long-standing convention essentially all wire protocols use (see
Prerequisite 6), and deviating from it for no reason would be a needless
inconsistency with every real protocol Module 15 examines later.

### `_recv_exact()` looping instead of a single `recv()` call
**(a) Forced by how TCP sockets actually behave.** A single `recv(n)`
call is documented to return *up to* n bytes, not necessarily exactly
n — even if the sender transmitted exactly n bytes in one `send()`
call, the OS is free to deliver them across multiple smaller reads.
Assuming one `recv()` call yields one complete message is a common,
real bug; looping until the exact byte count is satisfied is not
optional correctness here, it's required by TCP's own contract.

## `renderer_process.py`

### Simulated "rendering" (`f"(toy render of {url})"`) instead of a real parser
**(c) Convention — an explicit, acknowledged scope boundary.** This
module's entire claim is about the *process and IPC shape* of a
browser, not about rendering correctness — which hasn't been built yet
at this point in the course (Track 2, Phases 6–8 build it, piece by
piece, starting several modules later). Faking the render step here
lets this module's actual claim be tested in isolation, without a
false dependency on machinery that doesn't exist yet. The
tutorial and this file are both explicit that this is a stand-in, not
an oversight.

### An unbounded `while True` loop servicing messages until `"shutdown"`
**(c) Convention.** A real renderer process handles many command types
over its lifetime; this module only needs two (`load_url`,
`shutdown`) to prove its point, so the loop is deliberately minimal
rather than built out as a general command dispatcher other modules
would need to modify.

## `browser_process.py`

### Spawning renderers one at a time, in a loop (`Popen` then blocking
`accept()`), rather than spawning all N first and accepting after
**(c) Convention.** A production browser can spawn many renderers
concurrently and doesn't need to serialize accept() one-by-one. This
module serializes it specifically to keep the parent/child pairing
unambiguous in the printed output for teaching purposes — with N
concurrent connections racing to `accept()`, matching each accepted
socket back to the specific renderer that made it would need extra
bookkeeping this module doesn't need to teach yet.

### A single, fixed `PORT = 51900` rather than an OS-assigned ephemeral port
**(c) Convention.** Letting the OS pick a free port (by binding to port
`0`) is generally better production practice — it avoids collisions
with anything else already using a fixed port. A fixed port was chosen
here purely for the reader's convenience: the exact port number is
visible and stable in the tutorial's captured output without needing
an extra step to discover which port the OS actually chose.

### The `Tab` class holding `proc`, `conn`, and `renderer_pid` together
**(c) Convention.** Nothing in this module strictly requires bundling
these three into one object rather than three parallel lists — it was
chosen because later Track 2 modules (which reuse this exact file) will
need to look up "the renderer for tab N" repeatedly, and a small,
explicit object is clearer to extend than parallel-list bookkeeping.

---

## Decisions We Made

| Decision | Category | Could it have gone another way? |
|---|---|---|
| JSON + length prefix as the wire format | (c) Convention | Yes — many real formats would work |
| Big-endian (`"!"`) length header | (c) Convention (follows universal protocol norm) | Yes, but would break convention with every real protocol studied later |
| Looping `_recv_exact()` | (a) Forced by TCP's own byte-stream contract | No |
| Simulated rendering in the renderer | (c) Convention (explicit scope boundary) | N/A — real rendering doesn't exist yet in the course |
| Serialized spawn-then-accept, one renderer at a time | (c) Convention (unambiguous teaching output) | Yes — concurrent spawning is more realistic |
| Fixed port `51900` | (c) Convention (reader convenience) | Yes — OS-assigned port is more production-correct |
| `Tab` class bundling process/socket/pid | (c) Convention (anticipates reuse by later modules) | Yes — parallel lists would also work |

## What We Proved

Running `browser_process.py` produced real, captured evidence of every
piece of the claimed architecture:

1. **One Browser Process** (a specific PID) spawned **three genuinely
   separate Renderer Processes** (three different PIDs, each confirmed
   `!= browser_pid`) — one per requested tab.
2. Each Renderer Process connected back over its own dedicated IPC
   channel and correctly identified itself by PID in its `"hello"`
   message.
3. The Browser Process sent each renderer a structured `"load_url"`
   command and received back a structured `"loaded"` response,
   correctly attributed to the matching renderer's own PID — proving
   the message routing genuinely reaches the intended process, not just
   "some process."
4. Every renderer shut down cleanly on an explicit `"shutdown"` command
   and acknowledgment, rather than being killed — modeling orderly tab
   closure.

This directly confirms the module's claim: "one Browser Process, N
Renderer Processes, structured IPC" is not just a diagram — it is a
real, runnable shape, built entirely from primitives (process creation,
socket IPC, message framing) this course already independently proved
in Modules 5, 6, and the prerequisites.
