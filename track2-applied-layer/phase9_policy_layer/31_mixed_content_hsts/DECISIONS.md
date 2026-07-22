# Module 31: mixed_content_hsts — DECISIONS.md

## `HstsStore.enforce()` rewrites the URL BEFORE any network call would happen
**(c) Convention — the module's entire point.** HSTS's real security
value depends specifically on this ordering: the rewrite has to happen
client-side, before a single packet leaves the machine, or the
downgrade attack it defends against (an attacker intercepting a
plaintext first request) is still possible. This module's `enforce()`
takes a URL and returns a (possibly rewritten) URL — it never
simulates sending the original `http://` request first and redirecting
afterward, because that would misrepresent the actual mechanism.

## `max-age=0` clearing a stored HSTS record, rather than being ignored
**(b) External contract.** This is real, specified `Strict-Transport-Security`
behavior — a site can deliberately opt OUT of HSTS by sending
`max-age=0`, and browsers are required to honor that by forgetting the
previous record. Implementing this (rather than only ever adding
records) reflects the real, complete specified behavior, not just the
common case.

## `is_hsts_host()` checking ancestor domains by LABEL, not by string suffix
**(b) External contract — this avoids a real, easy security bug.** A
naive check like `hostname.endswith("example.com")` would incorrectly
treat `not-example.com` or `evil-example.com` as subdomains of
`example.com`, because those strings genuinely end with that
substring. Splitting on `.` and comparing whole labels (`"com"`,
`"example.com"`, etc.) as this module does is what correctly
distinguishes a real subdomain relationship from a coincidentally
similar-looking, completely unrelated domain — verified directly in
this module's own test case (`not-example.com` correctly does NOT
match `example.com`'s HSTS record).

## Splitting mixed content into PASSIVE (auto-upgrade) vs. ACTIVE (block outright) categories
**(b) External contract.** This distinction, and which real HTML
elements fall into each category, is not this module's invention — it
matches real, modern (post-~2019) browser behavior specifically: mixed
passive content (images, audio, video) is auto-upgraded to HTTPS and
only blocked if that upgrade itself fails; mixed active content
(scripts, stylesheets, frames) has always been blocked outright, with
no auto-upgrade attempt, because the risk of allowing a network
attacker to inject or tamper with ACTIVE content is categorically
higher than merely swapping a displayed image.

## `check_subresource()` returning a result OBJECT (action + final_url + reason), not just a boolean
**(c) Convention.** A plain allowed/blocked boolean would lose real
information — an "upgraded" resource is neither simply allowed (its
URL changed) nor blocked (it still loads). Representing three distinct
real outcomes (`allowed`, `upgraded`, `blocked`) is what lets the demo
accurately show the auto-upgrade behavior as its own, distinct case
rather than collapsing it into "allowed."

---

## Decisions We Made

| Decision | Category | Could it have gone another way? |
|---|---|---|
| URL rewritten before any network call | (c) Convention (the module's entire point) | N/A |
| `max-age=0` clears a stored record | (b) Forced — real, specified HSTS behavior | No |
| Label-based (not string-suffix) subdomain matching | (b) Forced — avoids a real security bug class | No |
| Passive-upgrade vs. active-block categorization | (b) Forced — matches real, modern browser behavior | No |
| Three-outcome result object, not a boolean | (c) Convention (preserves real information) | Yes, a simpler boolean loses the "upgraded" case |

## What We Proved

1. **HSTS**: after recording one real `Strict-Transport-Security`
   header for `example.com` with `includeSubDomains`, a subsequent
   `http://example.com/login` request was rewritten to
   `https://...` before ever reaching a network call, and so was
   `http://sub.example.com/page` (a real subdomain) — while
   `http://not-example.com/page` (a similar-LOOKING but unrelated
   domain) was correctly left completely unchanged, confirming
   label-based matching avoids a real false-positive security bug.
2. **Mixed content**: on an HTTPS page, an `<img>` and a `<video>`
   requesting plain-HTTP resources were both auto-UPGRADED to HTTPS,
   while a `<script>` and a `<link>` requesting plain-HTTP resources
   were both BLOCKED outright — confirming the real, modern
   passive-vs-active distinction browsers actually enforce.

This is direct, run-and-observed confirmation that HSTS and
mixed-content handling both exist specifically to prevent a silent,
attacker-exploitable downgrade from HTTPS to HTTP — one by rewriting
requests before they're ever sent, the other by treating different
resource types according to the real severity of what a network
attacker could do with each.
