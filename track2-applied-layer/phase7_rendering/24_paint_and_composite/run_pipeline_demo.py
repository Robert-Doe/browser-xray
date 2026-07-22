"""
Module 24: paint_and_composite -- demonstration runner.
"""

from composite import render_layers
from dom_nodes import Element
from pipeline import InstrumentedPipeline

HTML = '<div id="page"><div id="box">content</div><div id="mover">slides</div></div>'

CSS = """
#page { width: 500px; padding: 10px; }
#box { height: 100px; background-color: lightblue; }
#mover { height: 50px; background-color: orange; transform: translate(0px, 0px); }
"""


def find_by_id(node, target_id):
    if isinstance(node, Element):
        if node.element_id() == target_id:
            return node
        for child in node.children:
            found = find_by_id(child, target_id)
            if found:
                return found
    else:
        for child in getattr(node, "children", []):
            found = find_by_id(child, target_id)
            if found:
                return found
    return None


def main() -> None:
    pipeline = InstrumentedPipeline(HTML, CSS)

    print("=== Initial render ===")
    print(render_layers(pipeline.layers))
    print(f"stage run counts: {pipeline.counts()}\n")

    box = find_by_id(pipeline.dom, "box")
    mover = find_by_id(pipeline.dom, "mover")

    print("=== Change #box's WIDTH (a layout-affecting property) ===")
    pipeline.change_layout_affecting_property(box, "width", "200px")
    print(f"stage run counts: {pipeline.counts()}")
    print("  -> layout, paint, AND composite all ran again\n")

    print("=== Change #mover's TRANSFORM (a compositor-only property) ===")
    pipeline.change_compositor_only_property(mover, dx=30, dy=0)
    print(f"stage run counts: {pipeline.counts()}")
    print("  -> ONLY composite ran again -- layout and paint counts are unchanged\n")

    print(render_layers(pipeline.layers))


if __name__ == "__main__":
    main()
