"""
Module 29: cookies_samesite -- the "site" half of same-site, computed
via a (deliberately tiny) Public Suffix List.

"Same-origin" (Module 17) requires scheme+host+port to match EXACTLY.
"Same-site" is looser: it only compares the REGISTRABLE DOMAIN -- the
part of a hostname a random person could actually register themselves
-- which requires knowing which suffixes (like "co.uk") are NOT
registrable on their own. Real browsers use Mozilla's actual, large
Public Suffix List for this; this module hardcodes a tiny, illustrative
subset, explicitly scoped (see DECISIONS.md).
"""

# A deliberately small, illustrative subset of the real Public Suffix
# List -- entries here are suffixes that are NOT themselves
# registrable; a registrable domain is exactly one label plus one of
# these suffixes.
KNOWN_PUBLIC_SUFFIXES = {"com", "org", "net", "co.uk", "gov.uk"}


def registrable_domain(hostname: str) -> str:
    labels = hostname.lower().split(".")
    for i in range(len(labels)):
        candidate_suffix = ".".join(labels[i + 1 :])
        if candidate_suffix in KNOWN_PUBLIC_SUFFIXES:
            return ".".join(labels[i:])
    # No known public suffix matched -- fall back to the whole hostname
    # (a real PSL implementation has broader coverage; see DECISIONS.md).
    return hostname.lower()


def is_same_site(host_a: str, host_b: str) -> bool:
    return registrable_domain(host_a) == registrable_domain(host_b)
