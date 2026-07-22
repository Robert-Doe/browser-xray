"""
Module 21: css_parser_cssom -- demonstration runner.

Feeds real, illustrative and deliberately malformed CSS through the
parser, printing the resulting CSSOM -- proving CSS becomes its own
independent object model, parsed with real, spec-accurate error
recovery, entirely separately from any HTML or DOM.
"""

from css_parser import CSSParser
from cssom import render_cssom

CASES = [
    ("basic rule with multiple declarations",
     "div { color: red; font-size: 12px; }"),
    ("comma-separated selectors sharing one rule's declarations",
     "h1, h2, .title { margin: 0; }"),
    ("!important, with and without a space before 'important'",
     "p { color: blue !important; width: 10px ! important; }"),
    ("a string value containing ';', '{', '}' as literal text, not syntax",
     'p::before { content: "a;b{c}"; color: red; }'),
    ("a comment stripped, INCLUDING one that looks like a whole rule",
     "/* div { color: green; } */ p { color: red; }"),
    ("a malformed declaration in the middle -- real CSS error recovery",
     "div { color: red; this is garbage; font-size: 12px; }"),
    ("an @media block skipped as a balanced unit, without breaking later rules",
     "@media (max-width: 600px) { p { color: green; } } div { color: red; }"),
    ("an @import skipped without breaking later rules",
     '@import url("foo.css"); p { color: red; }'),
]


def main() -> None:
    for label, css in CASES:
        print(f"=== {label} ===")
        print(f"input: {css!r}\n")
        parser = CSSParser(css)
        rules = parser.parse()
        print(render_cssom(rules))
        if parser.skipped_declarations:
            print(f"(recovered from malformed declaration(s): {parser.skipped_declarations})")
        print()


if __name__ == "__main__":
    main()
