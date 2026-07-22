"""
Module 31: mixed_content_hsts -- mixed-content handling.

A page loaded over HTTPS makes a real, specific promise: everything on
it was delivered privately and authentically. Loading a SUBRESOURCE
over plain HTTP on that page breaks that promise for whatever that
resource can see or do -- but real browsers treat this differently
depending on how DANGEROUS that specific broken promise is:

  - PASSIVE content (images, audio, video): a network attacker could
    only swap out what's displayed/played -- serious, but bounded.
    Modern browsers auto-UPGRADE these to HTTPS and only block them if
    the upgrade fails outright.
  - ACTIVE content (scripts, stylesheets, iframes): a network attacker
    who can inject ANY of these gets to run/control code or layout on
    an otherwise-secure page -- browsers BLOCK these outright, no
    auto-upgrade attempt.
"""

PASSIVE_CONTENT_TAGS = {"img", "audio", "video"}
ACTIVE_CONTENT_TAGS = {"script", "link", "iframe", "frame"}


class MixedContentResult:
    def __init__(self, action: str, final_url: str, reason: str):
        self.action = action  # 'allowed' | 'upgraded' | 'blocked'
        self.final_url = final_url
        self.reason = reason

    def __repr__(self):
        return f"MixedContentResult(action={self.action!r}, final_url={self.final_url!r})"


def check_subresource(page_url: str, tag: str, resource_url: str) -> MixedContentResult:
    page_is_https = page_url.startswith("https://")
    resource_is_http = resource_url.startswith("http://")

    if not page_is_https or not resource_is_http:
        return MixedContentResult("allowed", resource_url, "no mixed-content concern")

    if tag in PASSIVE_CONTENT_TAGS:
        upgraded = "https://" + resource_url[len("http://"):]
        return MixedContentResult(
            "upgraded", upgraded,
            f"<{tag}> is passive content -- auto-upgraded to HTTPS rather than blocked",
        )

    if tag in ACTIVE_CONTENT_TAGS:
        return MixedContentResult(
            "blocked", resource_url,
            f"<{tag}> is active content -- blocked outright, never auto-upgraded",
        )

    return MixedContentResult("blocked", resource_url, f"unknown tag {tag!r} -- blocked to be safe")
