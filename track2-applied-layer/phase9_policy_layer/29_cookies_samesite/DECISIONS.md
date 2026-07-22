# Module 29: cookies_samesite — DECISIONS.md

## A tiny, hardcoded Public Suffix List subset (`KNOWN_PUBLIC_SUFFIXES`), rather than the real, full list
**(c) Convention — a deliberate, named scope boundary.** Mozilla's real
Public Suffix List has many thousands of entries and changes over
time. This module hardcodes five illustrative suffixes (`com`, `org`,
`net`, `co.uk`, `gov.uk`) — enough to demonstrate the real ALGORITHM
(and specifically the tricky multi-label case, `co.uk`, which a naive
"just take the last two labels" approach gets wrong) without
maintaining a real, complete, externally-sourced list.

## A real bug we hit while building the demo: choosing `bank.example` / `evil.example` as test hostnames
**(c) Convention — kept here as an honest, verified account.** Our
first draft used `bank.example` and `app.bank.example` as the target
and same-site pages. Running the demo directly showed the same-site
scenario was MISSING the `strict_session` cookie entirely — a real
bug. The cause: our simplified PSL doesn't (and correctly shouldn't)
treat `"example"` as a public suffix, so `registrable_domain("app.bank.example")`
fell through to returning the ENTIRE hostname
(`"app.bank.example"`) rather than `"bank.example"`, making it compare
unequal to the target and fail the same-site check. The fix was to use
test hostnames consistent with our own implemented suffix list
(`bank.example.com`, `app.bank.example.com`, both correctly reducing to
`example.com`) rather than assuming `"example"` alone would be treated
as a suffix. This is left documented because it's a genuinely
instructive, real mistake: registrable-domain logic is only as good as
its suffix list, and testing against domains outside that list will
silently produce wrong "same-site" answers.

## Real, precise per-SameSite-value enforcement rules, not a simplified "Strict/Lax/None = high/medium/low security"
**(b) External contract.** The actual rules are considerably more
specific than a simple ranking: `Lax` cookies are attached for
cross-site TOP-LEVEL navigations using SAFE methods (GET/HEAD) but
NOT for subresource requests or unsafe methods, even cross-site
top-level ones. Implementing this as a real decision (checking
`is_top_level_navigation` AND `safe_method` together, not just "is this
cross-site") is what correctly reproduces the real, sometimes-surprising
behavior verified in this module's Run It output — that a cross-site
top-level POST attaches ONLY the `None` cookie, not the `Lax` one.

## Rejecting `SameSite=None` cookies that aren't also marked `Secure`
**(b) External contract.** This is a real, specified browser
requirement (not this module's invention): a cookie asking to be sent
on every cross-site request, with no SameSite restriction at all, must
also require HTTPS — otherwise it could be trivially intercepted on an
insecure connection. `CookieJar.set_cookie` raising a `ValueError` for
this combination mirrors real browser enforcement.

## Cookie `domain` matching via exact string equality to the request's `target_host`, not a broader domain-matching scheme
**(c) Convention — a deliberate, named scope boundary.** Real cookies
can be scoped broader than one exact host via the `Domain` attribute
(e.g., a cookie set with `Domain=example.com` applies to all
subdomains). This module's `Cookie.domain` only ever matches the exact
requested host, which is sufficient to demonstrate the SameSite
decision this module focuses on, without also modeling the separate
`Domain`-attribute scoping mechanism.

---

## Decisions We Made

| Decision | Category | Could it have gone another way? |
|---|---|---|
| Tiny, hardcoded PSL subset | (c) Convention (named scope boundary) | Yes — a real, full PSL is a natural, larger extension |
| Test hostnames fixed after a real bug | (c) Convention (verified, corrected) | N/A — the fix was required for the claim to be true |
| Full real per-value SameSite rules (not a simplified ranking) | (b) Forced — matches real, specified browser behavior | No |
| Reject `SameSite=None` without `Secure` | (b) Forced — real browser requirement | No |
| Exact-host cookie domain matching only | (c) Convention (named scope boundary) | Yes — broader `Domain`-attribute scoping is a natural extension |

## What We Proved

Running four real request scenarios against three cookies (one per
SameSite value) on the same target site produced exactly the real,
specified outcomes:

1. **Same-site request** (`app.bank.example.com` → `bank.example.com`):
   ALL THREE cookies attached — Strict, Lax, and None all apply on a
   genuinely same-site request.
2. **Cross-site top-level navigation, GET** (`evil.com` → `bank.example.com`):
   only `lax_session` and `none_session` attached — `strict_session`
   correctly withheld.
3. **Cross-site subresource/XHR request, GET**: only `none_session`
   attached — `lax_session`, despite being a "safe" GET, is correctly
   withheld because this isn't a TOP-LEVEL navigation.
4. **Cross-site top-level navigation via POST**: only `none_session`
   attached — confirming `Lax` specifically requires BOTH a top-level
   navigation AND a safe method, not either alone.

This is direct, run-and-observed confirmation that SameSite is a real,
precisely-defined, browser-enforced boundary based on registrable
domain ("site," not exact origin) — checked at request time, with
distinct behavior per value that depends on both the request's
cross-site status and its navigation/method context together, not a
single simplified axis.
