"""
Module 30: csp_enforcement -- parsing a real Content-Security-Policy
header into a directive -> allowed-sources mapping.

A CSP header is plain, semicolon-separated text: each directive name
(script-src, style-src, ...) followed by a space-separated list of
sources it allows. Nothing here is exotic -- it's the same "split on a
delimiter, trim whitespace" shape as every other header this course
has parsed (Module 16).
"""


def parse_csp(header: str) -> dict:
    directives = {}
    for raw_directive in header.split(";"):
        raw_directive = raw_directive.strip()
        if not raw_directive:
            continue
        parts = raw_directive.split()
        name = parts[0].lower()
        sources = parts[1:]
        directives[name] = sources
    return directives
