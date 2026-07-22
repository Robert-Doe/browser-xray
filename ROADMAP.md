# ROADMAP.md
## Course: *The Browser Architecture — An X-Ray View for the Security Researcher*

This course builds a real, working, toy browser stack from the OS floor up,
one small module at a time, so that every security claim you later make
about browsers ("Site Isolation stops X," "sandboxing prevents Y," "CSP
mitigates Z") is grounded in something you personally built, ran, and broke.

It is structured as two tracks, mirroring how a real browser is actually two
things stacked on top of each other: an **OS-mediated process substrate**
(what Chromium's security model is *built on top of*) and an **applied
browser engine** (parsing, rendering, JS execution, and the web-facing
security policies). You cannot reason correctly about Site Isolation,
sandbox escapes, or Spectre-class leaks without Track 1 — that's why it
comes first and why Track 2 cites it constantly.

---

## TRACK 1 — Core Engine: OS & Process Substrate

*"Kernel" role. Everything a browser's security model ultimately rests on:
address spaces, processes, IPC, sandboxing primitives, and exploit
mitigations. No browser code yet — this is the ground the browser stands on.*

### Phase 1: Bare Metal Foundation

| # | Module | What it proves | Directory | Status |
|---|--------|-----------------|-----------|--------|
| 1 | `mem_addressing` | Proves a process's virtual address space is a translated illusion, not physical memory — the same virtual address in two processes maps to different physical RAM | `track1-core-engine/phase1_bare_metal/01_mem_addressing/` | Not started |
| 2 | `privilege_rings` | Proves user-mode code physically cannot execute a privileged instruction without trapping into the kernel | `track1-core-engine/phase1_bare_metal/02_privilege_rings/` | Not started |
| 3 | `syscall_boundary` | Proves every "browser action" (open a file, open a socket) is a request that crosses into kernel code, traceable and interceptable | `track1-core-engine/phase1_bare_metal/03_syscall_boundary/` | Not started |
| 4 | `process_anatomy` | Proves a process is a kernel-held data structure plus an address space plus threads — not "a running .exe" | `track1-core-engine/phase1_bare_metal/04_process_anatomy/` | Not started |

### Phase 2: Process & IPC Substrate

| # | Module | What it proves | Directory | Status |
|---|--------|-----------------|-----------|--------|
| 5 | `process_creation` | Proves spawning a child process creates a genuinely distinct address space — writing to "the same" variable address in parent and child never collide | `track1-core-engine/phase2_process_ipc/05_process_creation/` | Not started |
| 6 | `pipes_and_sockets` | Proves two isolated processes can only exchange data through a kernel-mediated channel that must be explicitly set up — nothing crosses by accident | `track1-core-engine/phase2_process_ipc/06_pipes_and_sockets/` | Not started |
| 7 | `shared_memory` | Proves the one deliberate exception to process isolation is explicit shared memory, and that it must be opted into by both sides | `track1-core-engine/phase2_process_ipc/07_shared_memory/` | Not started |
| 8 | `toy_browser_shell` | Proves a "browser" can be correctly modeled as one Browser Process plus N Renderer Processes exchanging structured IPC messages — this is the seed of your toy browser | `track1-core-engine/phase2_process_ipc/08_toy_browser_shell/` | Not started |

### Phase 3: Isolation & Sandboxing

| # | Module | What it proves | Directory | Status |
|---|--------|-----------------|-----------|--------|
| 9 | `least_privilege_tokens` | Proves a process's OS-level permissions can be stripped after spawn, so a renderer literally cannot open a file its parent can | `track1-core-engine/phase3_sandboxing/09_least_privilege_tokens/` | Not started |
| 10 | `syscall_filtering` | Proves a process can be blocked from making certain syscalls at all, even if compromised code inside it tries | `track1-core-engine/phase3_sandboxing/10_syscall_filtering/` | Not started |
| 11 | `site_isolation_model` | Proves putting two different origins in two different sandboxed OS processes makes cross-origin memory reads impossible without going through IPC | `track1-core-engine/phase3_sandboxing/11_site_isolation_model/` | Not started |

### Phase 4: Memory Safety & Exploit Mitigations

| # | Module | What it proves | Directory | Status |
|---|--------|-----------------|-----------|--------|
| 12 | `aslr_and_leaks` | Proves ASLR only raises exploit cost by randomizing addresses — it proves nothing once a single info-leak exists | `track1-core-engine/phase4_mitigations/12_aslr_and_leaks/` | Not started |
| 13 | `dep_nx_w_xor_x` | Proves W^X blocks code written into data memory from ever executing, by triggering the fault and then showing the sanctioned alternative | `track1-core-engine/phase4_mitigations/13_dep_nx_w_xor_x/` | Not started |
| 14 | `stack_canaries_cfi` | Proves canaries/CFI catch control-flow hijacks only at specific checkpoints, not universally — shows a naive smash caught, and why a smarter one wouldn't be | `track1-core-engine/phase4_mitigations/14_stack_canaries_cfi/` | Not started |

---

## TRACK 2 — Applied Layer: Browser Engine & Web Security

*"Userland browser" role. Parsing, rendering, JS execution, and the
policies (SOP/CORS/CSP/cookies) that only make sense once you know what
process boundary they're riding on top of.*

| # | Module | What it proves | Directory | Depends on (Track 1) | Status |
|---|--------|-----------------|-----------|------------------------|--------|
| 15 | `dns_tcp_tls_handshake` | Proves what "loading a URL" costs before a single byte of HTML arrives | `track2-applied-layer/phase5_networking/15_dns_tcp_tls_handshake/` | 6 (sockets), 8 (toy browser shell) | Not started |
| 16 | `http_parsing` | Proves an HTTP response is structured text over a socket, hand-parseable with no framework magic | `track2-applied-layer/phase5_networking/16_http_parsing/` | 6 | Not started |
| 17 | `origin_model_sop` | Proves the *browser*, not the server, is what enforces that script from origin A cannot read a response from origin B | `track2-applied-layer/phase5_networking/17_origin_model_sop/` | 8, 11 | Not started |
| 18 | `cors_preflight` | Proves CORS is an opt-in relaxation of SOP via an extra validated round trip, not an independent security mechanism | `track2-applied-layer/phase5_networking/18_cors_preflight/` | 17 | Not started |
| 19 | `html_tokenizer` | Proves HTML parsing is a state machine with defined recovery behavior, not "reading tags" | `track2-applied-layer/phase6_parsing_dom/19_html_tokenizer/` | 8 | Not started |
| 20 | `dom_tree_builder` | Proves the DOM is built incrementally from tokens under insertion-mode rules, not assembled all at once | `track2-applied-layer/phase6_parsing_dom/20_dom_tree_builder/` | 19 | Not started |
| 21 | `css_parser_cssom` | Proves CSS becomes a separate object tree (CSSOM), parsed independently of the DOM and merged later | `track2-applied-layer/phase6_parsing_dom/21_css_parser_cssom/` | 19 | Not started |
| 22 | `style_computation` | Proves every DOM node gets one fully resolved computed style via cascade + specificity before any pixel exists | `track2-applied-layer/phase7_rendering/22_style_computation/` | 20, 21 | Not started |
| 23 | `layout_box_model` | Proves layout is a recursive geometry pass that produces real x/y/width/height boxes from styled nodes | `track2-applied-layer/phase7_rendering/23_layout_box_model/` | 22 | Not started |
| 24 | `paint_and_composite` | Proves paint (pixels) and composite (layers) are separate stages — and why a compositor-only style change skips layout and paint entirely | `track2-applied-layer/phase7_rendering/24_paint_and_composite/` | 23 | Not started |
| 25 | `js_lexer_parser` | Proves JS source becomes an AST before a single line executes | `track2-applied-layer/phase8_js_engine/25_js_lexer_parser/` | 8 | Not started |
| 26 | `tree_walking_interpreter` | Proves the naive way to "run" JS is direct AST evaluation, and measures why that's slow | `track2-applied-layer/phase8_js_engine/26_tree_walking_interpreter/` | 25 | Not started |
| 27 | `bytecode_vm` | Proves a bytecode VM is a deliberate engineering response to interpreter overhead, measured against Module 26 | `track2-applied-layer/phase8_js_engine/27_bytecode_vm/` | 26 | Not started |
| 28 | `event_loop_microtasks` | Proves JS concurrency is single-threaded cooperative scheduling via task/microtask queues, not real parallelism | `track2-applied-layer/phase8_js_engine/28_event_loop_microtasks/` | 27 | Not started |
| 29 | `cookies_samesite` | Proves SameSite is an origin-*adjacent* boundary enforced by the browser on outgoing requests, set by a server-controlled flag | `track2-applied-layer/phase9_policy_layer/29_cookies_samesite/` | 17 | Not started |
| 30 | `csp_enforcement` | Proves CSP is a browser-side allowlist checked before script/resource execution, not a server-side filter | `track2-applied-layer/phase9_policy_layer/30_csp_enforcement/` | 20, 25 | Not started |
| 31 | `mixed_content_hsts` | Proves HSTS and mixed-content blocking exist specifically to prevent silent HTTPS→HTTP downgrade | `track2-applied-layer/phase9_policy_layer/31_mixed_content_hsts/` | 15 | Not started |
| 32 | `xss_csrf_on_toy_browser` | Proves a real XSS/CSRF payload succeeds against your own toy browser until the specific policy module is wired in, then fails after | `track2-applied-layer/phase10_attack_surface/32_xss_csrf_on_toy_browser/` | 17, 29, 30 | Not started |
| 33 | `clickjacking_uxss` | Proves clickjacking exploits the compositor/paint model and UXSS exploits a site-isolation gap — demonstrated against your own stack | `track2-applied-layer/phase10_attack_surface/33_clickjacking_uxss/` | 11, 24 | Not started |
| 34 | `side_channel_timing` | Proves a non-weaponized timing side-channel can leak cross-origin data even when SOP and site isolation block *direct* reads — the reason Site Isolation targets process boundaries, not just script checks | `track2-applied-layer/phase10_attack_surface/34_side_channel_timing/` | 11, 17 | Not started |
| 35 | `sandbox_escape_chain` | Proves a full browser compromise requires defeating multiple independently-built layers together (a mitigation bypass *and* a syscall-filter bypass), tying both tracks into one attacker's-eye chain | `track2-applied-layer/phase10_attack_surface/35_sandbox_escape_chain/` | 10, 13, 14 | Not started |

---

## Recommended Stopping Points

| Your goal | Stop at module |
|---|---|
| OS/process fundamentals for general pwn/CTF work | **14** (end of Track 1) |
| Browser sandboxing & exploit-mitigation research specifically | **14** |
| Full web-app security research (XSS/CSRF/CORS/CSP/cookies) | **31** |
| Rendering-engine or JS-engine internals / engine-bug research | **28** |
| Complete attacker's-eye view spanning OS through browser | **35** (full course) |

---

## Tools / Architecture Target

- **Primary language:** Python 3 — fast to build and *inspect* (introspection matters more than raw speed for this course). Used for IPC, toy HTTP/DOM/CSS/JS-engine modules, and policy layers.
- **Secondary language:** C, used *only* where a primitive must be shown at the metal with no runtime cushioning it (e.g. `VirtualProtect`/`mprotect`, a raw shellcode-in-buffer demo for W^X).
- **Platform:** Windows 11 native APIs as the primary target (Job Objects, restricted tokens, integrity levels, `VirtualProtect`) since that's this environment — this is also a legitimate real-world sandbox model, since Chromium ships a real Windows sandbox built on exactly these primitives. WSL2/Linux is used as a *named comparison track* for seccomp-bpf and namespaces, since most public Chromium sandbox-escape research is Linux/Android-based — divergences between the two will be called out explicitly, never silently substituted.
- **Networking:** real sockets/TLS via Python's `socket`/`ssl` stdlib — no fabricated protocol behavior; every packet-level claim will be captured, not asserted.
- **Verification method:** logs, hex dumps, and printed state — no GUI is built. A handful of small HTML diagrams exist only inside the tutorials, not as part of the toy browser's output.
- **Explicitly out of scope:** a spec-complete rendering engine, GPU compositing, a real V8-compatible JIT/optimizing compiler, a real cryptographic implementation (TLS is via stdlib, not reimplemented), mobile-browser specifics, weaponized/production exploit code, and any modification of actual Chromium source.

---

## Open questions before I start Phase 1

1. **35 modules is the full count** — comfortable, or do you want a trimmed first pass (e.g. stop the initial build at Module 14 or 31 and revisit Track 2's back half later)?
2. Any objection to the **Python-primary / C-for-the-metal-only** split, or would you rather more of Track 1 be in C to stay closer to how real exploit-mitigation research is usually read?
3. Windows-native sandbox primitives as primary, WSL2 as comparison — confirm that split works for you, since it affects Modules 9, 10, 13, 35 directly.

I will not start Phase 1 (prerequisites) or any module code until you confirm the module list/count above.
