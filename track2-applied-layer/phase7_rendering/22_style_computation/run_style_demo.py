"""
Module 22: style_computation -- demonstration runner.

Builds a real DOM (Module 20) and a real CSSOM (Module 21) from
scratch, then computes final styles for every element -- proving the
cascade's real, exact priority order: !important beats specificity,
specificity beats source order, source order is the final tiebreaker.
"""

from css_parser import parse_css
from dom_nodes import Document, Element
from html_tokenizer import tokenize
from style_computation import compute_styles
from tree_constructor import build_tree

HTML = '<div id="header" class="title"><p>inside div</p></div><p>outside div</p>'

CSS = """
.title { color: red; }
#header { color: blue; }
p { color: green !important; }
div p { font-weight: bold; }
.title { background: yellow; }
"""


def find_all(node, tag=None) -> list:
    results = []
    if isinstance(node, Element):
        if tag is None or node.tag == tag:
            results.append(node)
        for child in node.children:
            results.extend(find_all(child, tag))
    elif isinstance(node, Document):
        for child in node.children:
            results.extend(find_all(child, tag))
    return results


def parent_tag(element: Element) -> str:
    return element.parent.tag if isinstance(element.parent, Element) else "#document"


def main() -> None:
    print("HTML:", HTML)
    print("CSS:", CSS.strip())
    print()

    dom = build_tree(tokenize(HTML))
    rules = parse_css(CSS)
    compute_styles(dom, rules)

    header = find_all(dom, tag="div")[0]
    print(f"<div id=header class=title> computed style: {header.computed_style}")
    print("  -> color: blue, because #header (1 ID) outranks .title (1 class),")
    print("     regardless of which rule appeared first in the stylesheet")
    print("  -> background: yellow, since only .title sets it at all\n")

    for p in find_all(dom, tag="p"):
        print(f"<p> (parent={parent_tag(p)}) computed style: {p.computed_style}")
    print("  -> BOTH <p> elements get color: green, because !important overrides")
    print("     specificity entirely, even though 'p' alone has the LOWEST")
    print("     specificity of any rule that matches either paragraph")
    print("  -> only the <p> INSIDE the div gets font-weight: bold, because")
    print("     'div p' is a descendant-combinator selector that the top-level")
    print("     <p> genuinely does not match")


if __name__ == "__main__":
    main()
