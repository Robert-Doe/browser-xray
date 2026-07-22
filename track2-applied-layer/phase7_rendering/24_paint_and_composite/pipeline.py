"""
Module 24: paint_and_composite -- the actual proof.

An instrumented, full pipeline (style -> layout -> paint -> composite)
that counts how many times each stage actually RUNS. Two kinds of
updates are then applied to the SAME already-rendered page:

  - A layout-affecting property change (width) -- must re-run layout,
    paint, AND composite, because the geometry itself changed.
  - A compositor-only property change (transform) -- must re-run
    ONLY composite. Layout and paint are never touched, because the
    already-painted pixels for that layer are still perfectly valid;
    only the layer's on-screen OFFSET needs to change.

This is the real, practical reason browser performance guidance
consistently recommends animating `transform`/`opacity` over properties
like `width`/`top`/`left`.
"""

from composite import composite
from css_parser import parse_css
from dom_nodes import Document, Element
from html_tokenizer import tokenize
from layout import layout_block
from paint import paint
from style_computation import compute_styles
from tree_constructor import build_tree

VIEWPORT_WIDTH = 1000


class InstrumentedPipeline:
    def __init__(self, html: str, css: str):
        self.style_runs = 0
        self.layout_runs = 0
        self.paint_runs = 0
        self.composite_runs = 0

        self.dom = build_tree(tokenize(html))
        self.rules = parse_css(css)
        self.root_element = next(c for c in self.dom.children if isinstance(c, Element))

        self._run_style()
        self._run_layout()
        self._run_paint()
        self._run_composite()

    def _run_style(self) -> None:
        compute_styles(self.dom, self.rules)
        self.style_runs += 1

    def _run_layout(self) -> None:
        self.root_box = layout_block(self.root_element, x=0, y=0, available_width=VIEWPORT_WIDTH)
        self.layout_runs += 1

    def _run_paint(self) -> None:
        self.paint_records = paint(self.root_box)
        self.paint_runs += 1

    def _run_composite(self) -> None:
        self.layers = composite(self.root_box, self.paint_records)
        self.composite_runs += 1

    def change_layout_affecting_property(self, element: Element, property_name: str, value: str) -> None:
        """A property like `width` changes actual geometry -- there is
        no shortcut: layout must be redone, which invalidates the old
        paint records, which invalidates the old layer assignment."""
        element.computed_style[property_name] = value
        self._run_layout()
        self._run_paint()
        self._run_composite()

    def change_compositor_only_property(self, element: Element, dx: float, dy: float) -> None:
        """`transform: translate(...)` changes nothing about the
        element's LAYOUT geometry or its own pixels -- only where its
        already-painted layer is displayed. Real compositors handle
        this with the GPU, without asking layout or paint to run again
        at all."""
        for layer in self.layers:
            if any(record.box.element is element for record in layer.paint_records):
                layer.offset_x += dx
                layer.offset_y += dy
                self.composite_runs += 1  # composite work happened; layout/paint did not
                return
        raise ValueError("element has no dedicated layer -- add 'transform' to its style first")

    def counts(self) -> dict:
        return {
            "style": self.style_runs,
            "layout": self.layout_runs,
            "paint": self.paint_runs,
            "composite": self.composite_runs,
        }
