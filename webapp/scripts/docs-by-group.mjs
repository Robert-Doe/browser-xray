/**
 * Curated, verified doc links shared across every module in a phase group
 * (43 unique per-module doc sets wasn't tractable; every link below was
 * fetched and confirmed live during authoring).
 */
export const DOCS_BY_GROUP = {
  'bare-metal': [
    { title: 'Virtual memory (Wikipedia)', description: 'How an OS translates virtual addresses to physical RAM per-process — the mechanism Module 1 proves by example.', url: 'https://en.wikipedia.org/wiki/Virtual_memory' },
    { title: 'Protection ring (Wikipedia)', description: 'The CPL 0-3 hardware privilege model Module 2 demonstrates faulting on.', url: 'https://en.wikipedia.org/wiki/Protection_ring' },
    { title: 'System call (Wikipedia)', description: 'What actually happens when user-mode code asks the kernel to do something — Module 3’s subject.', url: 'https://en.wikipedia.org/wiki/System_call' },
  ],
  'process-ipc': [
    { title: 'Inter-process communication (Wikipedia)', description: 'The channel types (pipes, sockets, shared memory) this phase builds and compares.', url: 'https://en.wikipedia.org/wiki/Inter-process_communication' },
    { title: 'Access Tokens (Microsoft Learn)', description: 'The real Windows primitive behind least-privilege process tokens.', url: 'https://learn.microsoft.com/en-us/windows/win32/secauthz/access-tokens' },
  ],
  sandboxing: [
    { title: 'Chromium Site Isolation', description: 'The real, shipped feature Module 11 models: putting different origins in different sandboxed OS processes.', url: 'https://www.chromium.org/Home/chromium-security/site-isolation/' },
    { title: 'Job Objects (Microsoft Learn)', description: 'The Windows primitive for constraining a group of processes as a unit — the OS mechanism syscall/resource sandboxing builds on.', url: 'https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects' },
    { title: 'Access Tokens (Microsoft Learn)', description: 'Restricted tokens — stripping a process’s permissions after spawn, Module 9’s subject.', url: 'https://learn.microsoft.com/en-us/windows/win32/secauthz/access-tokens' },
  ],
  mitigations: [
    { title: 'Spectre (security vulnerability) (Wikipedia)', description: 'Why address randomization alone (ASLR) isn’t enough once a side-channel or info-leak exists.', url: 'https://en.wikipedia.org/wiki/Spectre_(security_vulnerability)' },
    { title: 'Virtual memory (Wikipedia)', description: 'Background for how DEP/NX and page permissions (W^X) are enforced at the same MMU layer as address translation.', url: 'https://en.wikipedia.org/wiki/Virtual_memory' },
  ],
  networking: [
    { title: 'Populating the page: how browsers work (MDN)', description: 'DNS lookup, the TCP handshake, and TLS negotiation — the real round-trip cost before a byte of HTML arrives.', url: 'https://developer.mozilla.org/en-US/docs/Web/Performance/Guides/How_browsers_work' },
    { title: 'Transport Layer Security (Wikipedia)', description: 'The real TLS handshake steps Module 15 walks through.', url: 'https://en.wikipedia.org/wiki/Transport_Layer_Security' },
    { title: 'Same-origin policy (MDN)', description: 'The browser-enforced boundary Module 17 proves is a client-side, not server-side, control.', url: 'https://developer.mozilla.org/en-US/docs/Web/Security/Defenses/Same-origin_policy' },
    { title: 'CORS (MDN)', description: 'The opt-in relaxation of SOP, including exactly which requests trigger a preflight — Module 18’s subject.', url: 'https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CORS' },
  ],
  'parsing-dom': [
    { title: 'WHATWG HTML — Tokenization', description: 'The real, 84-state HTML tokenizer state machine this course’s scoped-down Module 19 tokenizer mirrors the shape of.', url: 'https://html.spec.whatwg.org/multipage/parsing.html#tokenization' },
    { title: 'WHATWG DOM Standard', description: 'The tree/node model Module 20’s tree constructor builds a simplified version of.', url: 'https://dom.spec.whatwg.org/' },
    { title: 'CSSOM (W3C/CSSWG)', description: 'The separate object tree CSS becomes, parsed independently of the DOM — Module 21’s subject.', url: 'https://drafts.csswg.org/cssom/' },
  ],
  rendering: [
    { title: 'Rendering performance (web.dev)', description: 'The real pipeline — Style, Layout, Paint, Composite — and why a compositor-only change can skip stages entirely.', url: 'https://web.dev/articles/rendering-performance' },
  ],
  'js-engine': [
    { title: 'JavaScript execution model (MDN)', description: 'The event loop, tasks, and microtasks — why JS concurrency is cooperative scheduling, not real parallelism.', url: 'https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Execution_model' },
  ],
  policy: [
    { title: 'HTTP Cookies (MDN)', description: 'The Set-Cookie SameSite attribute (Strict/Lax/None) Module 29 is built around.', url: 'https://developer.mozilla.org/en-US/docs/Web/HTTP/Cookies' },
    { title: 'Content-Security-Policy (MDN)', description: 'The browser-side allowlist checked before script execution — Module 30’s subject.', url: 'https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CSP' },
    { title: 'Strict-Transport-Security (MDN)', description: 'HSTS — the header that prevents silent HTTPS→HTTP downgrade, Module 31’s subject.', url: 'https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Strict-Transport-Security' },
  ],
  'attack-surface': [
    { title: 'OWASP CSRF Prevention Cheat Sheet', description: 'The real defense patterns (synchronizer tokens, SameSite, Fetch Metadata) Module 32 tests against the toy browser.', url: 'https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html' },
    { title: 'Clickjacking (MDN)', description: 'The compositor/iframe-overlay attack Module 33 demonstrates, and its real defenses (frame-ancestors, X-Frame-Options).', url: 'https://developer.mozilla.org/en-US/docs/Web/Security/Attacks/Clickjacking' },
    { title: 'Spectre (security vulnerability) (Wikipedia)', description: 'The canonical timing side-channel class Module 34 builds a non-weaponized demonstration of.', url: 'https://en.wikipedia.org/wiki/Spectre_(security_vulnerability)' },
    { title: 'Chromium Site Isolation', description: 'What Module 35’s sandbox-escape chain has to defeat: process-boundary isolation, not just script-level checks.', url: 'https://www.chromium.org/Home/chromium-security/site-isolation/' },
  ],
};
