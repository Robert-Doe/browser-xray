# Module 6: pipes_and_sockets — DECISIONS.md

## Building both a named pipe demo AND a TCP socket demo
**(c) Convention.** The module's claim ("a channel must be explicitly,
mutually established") is mechanism-independent, but proving it with
only one mechanism would leave "maybe this is just a named-pipe quirk"
on the table. Building both a Windows-specific mechanism (named pipes)
and a general, cross-platform one (TCP sockets over loopback) shows the
same property holding for two IPC mechanisms with very different
addressing schemes (a string name vs. a host+port pair).

## `pipe_server.py` / `pipe_client.py`

### `PIPE_TYPE_MESSAGE | PIPE_READMODE_MESSAGE`
**(c) Convention.** Named pipes can operate in byte-stream mode (like a
socket) or message mode (each `WriteFile` call is a discrete unit a
matching `ReadFile` call receives whole). We chose message mode because
it makes the demo's send/receive correspondence exact and simple to
reason about — byte-stream mode would work too, but would require the
reader to handle partial reads, which isn't this module's point.

### `win32pipe.ConnectNamedPipe(pipe, None)` blocking with no overlapped I/O
**(c) Convention.** A production named-pipe server typically uses
overlapped (asynchronous) I/O to serve multiple clients concurrently.
This module serves exactly one client and exits — blocking,
synchronous I/O keeps the code's causality (create → wait → connect →
exchange → close) visible in a straight line, which matters more here
than throughput.

### `time.sleep(0.5)` before launching the client in the orchestrator
**(c) Convention — a real timing dependency, handled pragmatically.**
`ConnectNamedPipe` must be listening before the client's `CreateFile`
call arrives, or the client's connection attempt fails. A fixed sleep
is not the most robust solution (a readiness-signaling approach would
be more correct in production code) but keeps the demo simple; the
same tradeoff was made explicitly in Module 4's child-process timing.

## `socket_server.py` / `socket_client.py` / `run_socket_demo.py`

### `SO_REUSEADDR` on the server socket
**(c) Convention.** Without it, re-running this demo shortly after a
previous run can fail to bind with "address already in use," because
the OS holds a just-closed TCP port in a brief `TIME_WAIT` state.
Setting this option is standard, safe practice for a short-lived local
demo server — it would be a more consequential choice for a long-lived
production service, where `TIME_WAIT` exists specifically to avoid
delivering a stray, delayed packet from an old connection to a new one.

### Catching both `ConnectionRefusedError` AND `TimeoutError` in Part B
**(b) External contract — a real behavior we discovered, not assumed.**
We initially only handled `ConnectionRefusedError`, expecting the
loopback stack to answer a SYN to an unused port with an immediate TCP
RST. Running it for real produced a `TimeoutError` instead (see
`06 Run It`) — on this machine, something in the local network stack
(most plausibly Windows Defender Firewall's loopback handling) is
silently dropping the SYN rather than answering with RST. Both outcomes
equally support the module's actual claim ("no channel was
established, so no data crossed") — so the fix was to treat both as
valid confirmations rather than to force one specific mechanism, and to
say plainly in the tutorial that this specific behavior (refused vs.
timed out) is environment-dependent.

### Port `51837` / `51838` as fixed constants
**(c) Convention.** Any high, unassigned port pair works; these were
picked arbitrarily and verified free at test time.

---

## Decisions We Made

| Decision | Category | Could it have gone another way? |
|---|---|---|
| Demonstrate both named pipes and TCP sockets | (c) Convention (breadth of proof) | Yes — either alone would show a narrower claim |
| Message-mode named pipe | (c) Convention (clarity over realism) | Yes — byte-stream mode also works |
| Synchronous, single-client pipe server | (c) Convention (linear readability) | Yes — overlapped I/O is more production-realistic |
| `SO_REUSEADDR` on the TCP server | (c) Convention (safe for a short-lived demo) | Yes, with caveats for long-lived services |
| Handle both refused AND timed-out as "no channel" | (b) Forced by observed real environment behavior | No — this machine's actual behavior dictated it |

## What We Proved

1. **`run_pipe_demo.py`, Part A**: a message sent by a client process
   through a specifically-named pipe was received, acknowledged, and
   replied to by a completely separate server process — a real,
   deliberately established channel working exactly as designed.
2. **`run_pipe_demo.py`, Part B**: attempting to open a pipe name no
   server had ever created failed immediately with a real Win32 error
   (`winerror=2`, "The system cannot find the file specified") —
   confirming that simply *knowing the correct-looking address* is not
   enough; the other side has to have actually built the channel.
3. **`run_socket_demo.py`, Part A**: the same shape of real,
   bidirectional exchange, addressed by `(host, port)` instead of a
   pipe name — showing the claim isn't specific to one IPC mechanism.
4. **`run_socket_demo.py`, Part B**: an attempt to reach a port nothing
   was listening on failed — as a timeout rather than the initially
   expected immediate refusal, a real, captured environment detail that
   still confirms the same underlying claim: no channel, no data.
