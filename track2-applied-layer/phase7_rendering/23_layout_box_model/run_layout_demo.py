"""
Module 23: layout_box_model -- demonstration runner.

Builds a real DOM + CSSOM + computed styles (Modules 19-22), then runs
this module's own recursive block-layout algorithm, printing real box
geometry for every element -- proving layout is a genuine, recursive
geometry computation, not something implied by styles alone.
"""

from css_parser import parse_css
from dom_nodes import Document, Element
from html_tokenizer import tokenize
from layout import layout_block, render_layout
from style_computation import compute_styles
from tree_constructor import build_tree

HTML = '<div id="container"><div id="a">A</div><div id="b">B</div></div>'

CSS = """
#container { width: 400px; padding: 10px; }
#a { height: 50px; margin: 5px; }
#b { height: 80px; }
"""

VIEWPORT_WIDTH = 1000


def main() -> None:
    print("HTML:", HTML)
    print("CSS:", CSS.strip())
    print()

    dom = build_tree(tokenize(HTML))
    rules = parse_css(CSS)
    compute_styles(dom, rules)

    container = next(child for child in dom.children if isinstance(child, Element))
    box = layout_block(container, x=0, y=0, available_width=VIEWPORT_WIDTH)

    print(render_layout(box))
    print()
    print(f"container: explicit width 400px + 10px padding each side = {box.width:g}px total")
    print(f"           auto height = sum of both children's heights + padding = {box.height:g}px")
    print(f"#a:        margin: 5px shrinks its available width to 400 - 10 = {box.children[0].width:g}px")
    print(f"#b:        no margin -- takes the FULL 400px content width: {box.children[1].width:g}px")
    print(f"#b's y ({box.children[1].y:g}) = #a's y ({box.children[0].y:g}) + #a's height ({box.children[0].height:g}) "
          f"-- real block-flow stacking")


if __name__ == "__main__":
    main()
