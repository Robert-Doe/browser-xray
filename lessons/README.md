# lessons/ — Cross-Module Concept Clusters

Some ideas in this course don't belong entirely to any single module —
they recur, in genuinely different forms, across several. Splitting
them out here (rather than repeating a partial explanation inside each
module that touches them) is what lets each cluster get the fuller
treatment its cross-cutting nature actually deserves: history, real-world
alternative implementations, security implications, and performance
tradeoffs that would be out of scope for any one module's own build.

## Clusters

### [01_ipc_across_the_stack](01_ipc_across_the_stack/01_explainer.html)
**Relates to:** Module 6 (pipes_and_sockets), Module 7 (shared_memory),
Module 8 (toy_browser_shell), Module 15 (dns_tcp_tls_handshake),
Module 16 (http_parsing).

**Why it lives here, not in one module:** Modules 6 and 7 build the
raw OS-level IPC *primitives*. Module 8 builds a custom
*application-level protocol* on top of one of them. Modules 15 and 16
apply the same underlying mechanism (sockets) to real, standardized,
internet-facing communication. No single module's own scope covers
*why* you'd choose one mechanism over another, or how they relate as a
family — that comparison only makes sense once all five exist to
compare.

### [02_browser_policy_stack](02_browser_policy_stack/01_explainer.html)
**Relates to:** Module 17 (origin_model_sop), Module 18
(cors_preflight), Module 29 (cookies_samesite), Module 30
(csp_enforcement), Module 31 (mixed_content_hsts).

**Why it lives here, not in one module:** Each of these five modules
proves ONE policy mechanism in isolation, which is the right scope for
learning each one correctly. But a real page load runs through ALL
FIVE, in a specific real order, each catching a different class of
risk — and the single most common real confusion practitioners have
("which of these five stops which kind of attack?") only gets resolved
by looking at all five side by side, which is exactly what this
cluster does.

## Vocabulary Webs

Vocabulary webs (Phase 4 — see each module's own folder) live inside
the specific module where a tightly-related, easily-conflated group of
terms first comes fully together, rather than here — they're module-
scoped by design, unlike these clusters. Current vocabulary webs:

- **PID vs. Handle vs. Token vs. SID** — in
  [track1-core-engine/phase1_bare_metal/04_process_anatomy/](../track1-core-engine/phase1_bare_metal/04_process_anatomy/concept_how_they_connect.html)
- **SOP vs. CORS vs. SameSite vs. CSP vs. HSTS** — in
  [track2-applied-layer/phase9_policy_layer/31_mixed_content_hsts/](../track2-applied-layer/phase9_policy_layer/31_mixed_content_hsts/concept_how_they_connect.html)
