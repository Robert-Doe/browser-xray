"""
Module 19: html_tokenizer -- demonstration runner.

Feeds the tokenizer well-formed HTML and several genuinely malformed
inputs, printing the resulting token stream for each -- proving HTML
tokenization is a defined, recoverable state machine, not a "well-formed
input only" parser that throws on anything unexpected.
"""

from html_tokenizer import tokenize

CASES = [
    ("well-formed nested tags",
     '<div class="box" id=main>Hello <b>world</b>!</div>'),
    ("unquoted attribute value",
     '<a href=foo.html>link</a>'),
    ("unclosed tag at EOF",
     '<div>text with no closing tag'),
    ("stray '<' that is not a tag (real text, not an error)",
     '1 < 2 and 3 > 1'),
    ("'<?xml ...?>' becomes a BOGUS COMMENT, not special XML syntax",
     '<?xml version="1.0"?><p>after</p>'),
    ("invalid end tag name -- ordering across a bogus comment",
     'a</1>b'),
    ("tag name case-folding (<DIV> same as <div>)",
     '<DIV ID="X">hi</DIV>'),
    ("real comment",
     '<!-- a comment --><p>after comment</p>'),
    ("unterminated comment at EOF",
     '<!-- never closes'),
    ("DOCTYPE is recognized and skipped",
     '<!DOCTYPE html><p>hi</p>'),
    ("self-closing void element",
     '<img src="a.png"/>after'),
]


def main() -> None:
    for label, html in CASES:
        print(f"--- {label} ---")
        print(f"input: {html!r}")
        for token in tokenize(html):
            print(f"    {token}")
        print()


if __name__ == "__main__":
    main()
