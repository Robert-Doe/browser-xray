"""
Module 17: origin_model_sop -- the actual proof.

Two toy origins run locally (Module 17's own servers -- see
toy_servers.py). A "page" is modeled as just a URL string standing in
for "the origin script is currently running on."

Part A: naive_fetch() -- no origin awareness anywhere -- lets a
"script on origin A" read origin B's private data outright. This is
what the web would look like with NO Same-Origin Policy.

Part B: sop_enforced_fetch() performs the identical cross-origin
request and is refused -- but the exception message makes clear the
network request itself still happened.

Part C: sop_enforced_fetch() succeeds normally for a SAME-origin
request -- proving the policy isn't "block everything," only
"block cross-origin script access."
"""

import time

from fetch_layer import BlockedBySameOriginPolicy, naive_fetch, sop_enforced_fetch
from toy_servers import start_origin_servers


def main() -> None:
    origin_a_url, origin_b_url = start_origin_servers()
    time.sleep(0.3)  # let both server threads reach accept()

    print(f"Origin A (the 'requesting page'): {origin_a_url}")
    print(f"Origin B (holds private data):    {origin_b_url}\n")

    print("=== Part A: naive_fetch -- NO origin check at all ===")
    leaked = naive_fetch(origin_b_url)
    print(f"  script on origin A read origin B's response directly: {leaked!r}")
    print("  (this is what the web looks like with no Same-Origin Policy at all)\n")

    print("=== Part B: sop_enforced_fetch -- cross-origin, from origin A to origin B ===")
    try:
        sop_enforced_fetch(requesting_page_url=origin_a_url, target_url=origin_b_url)
        print("  UNEXPECTED: cross-origin read was not blocked")
    except BlockedBySameOriginPolicy as e:
        print(f"  BLOCKED, as expected: {e}\n")

    print("=== Part C: sop_enforced_fetch -- SAME origin (A fetching from A) ===")
    same_origin_body = sop_enforced_fetch(requesting_page_url=origin_a_url, target_url=origin_a_url)
    print(f"  ALLOWED, as expected: {same_origin_body!r}\n")

    print(
        "[analysis] The exact same network request reached origin B in both "
        "Part A and Part B -- origin B's server has no idea whether a browser "
        "enforces SOP or not, and did not need to. The policy is enforced "
        "entirely on OUR side, deciding whether to hand the response to the "
        "calling script -- never by refusing to make the request in the "
        "first place."
    )


if __name__ == "__main__":
    main()
