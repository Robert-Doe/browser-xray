"""
Module 20: dom_tree_builder -- demonstration runner.

Feeds real, illustrative HTML through Module 19's tokenizer and this
module's tree constructor, printing the resulting tree -- proving the
DOM is assembled incrementally via a stack of open elements, with
real, specific auto-closing rules independent of the tokenizer itself.
"""

from dom_nodes import render_tree
from html_tokenizer import tokenize
from tree_constructor import build_tree

CASES = [
    ("auto-close <p>: a new <p> implicitly closes the previous one",
     "<p>1<p>2"),
    ("auto-close <li>: a new <li> implicitly closes the previous one",
     "<ul><li>a<li>b</li></ul>"),
    ("an ancestor's end tag implicitly closes a still-open descendant",
     "<div><span>text</div>after"),
    ("an end tag with no matching open element is simply ignored",
     "<p>hello</span></p>"),
    ("ordinary well-formed nesting",
     "<div><p>Hello <b>world</b>!</p></div>"),
]


def main() -> None:
    for label, html in CASES:
        print(f"=== {label} ===")
        print(f"input: {html!r}\n")
        tree = build_tree(tokenize(html))
        print(render_tree(tree))
        print()


if __name__ == "__main__":
    main()
