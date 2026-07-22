"""
Module 23: layout_box_model -- a real, recursive block-layout
algorithm.

Turns computed styles (Module 22 -- "color: blue" style facts with no
geometry at all) into actual boxes: real x, y, width, height numbers,
for every element, computed recursively.

SCOPE (see DECISIONS.md): block-flow layout only -- every child stacks
vertically, one after another, filling its parent's width by default.
No inline layout (text wrapping/line boxes), no flexbox, no grid, no
floats. Box model properties supported: margin, padding, explicit
width/height (all single px values, no percentages/auto keyword
parsing beyond "absent = auto").
"""

import re
from dataclasses import dataclass, field

from dom_nodes import Element

_PX_RE = re.compile(r"^(-?\d+(?:\.\d+)?)px$")


@dataclass
class Box:
    element: Element
    x: float
    y: float
    width: float
    height: float
    children: list = field(default_factory=list)


def parse_px(value, default=None):
    if value is None:
        return default
    match = _PX_RE.match(value.strip())
    if not match:
        return default
    return float(match.group(1))


def layout_block(element: Element, x: float, y: float, available_width: float) -> Box:
    style = element.computed_style

    margin = parse_px(style.get("margin"), 0.0)
    padding = parse_px(style.get("padding"), 0.0)
    explicit_width = parse_px(style.get("width"), None)
    explicit_height = parse_px(style.get("height"), None)

    # A block box's default ("auto") width FILLS its containing block's
    # available width, minus its own margin -- this is real CSS block
    # layout behavior, not a simplification unique to this module.
    content_width = explicit_width if explicit_width is not None else available_width - 2 * margin - 2 * padding

    box_x = x + margin
    box_y = y
    content_x = box_x + padding
    content_y = box_y + padding

    cursor_y = content_y
    child_boxes = []
    for child in element.children:
        if isinstance(child, Element):
            child_box = layout_block(child, content_x, cursor_y, content_width)
            child_boxes.append(child_box)
            cursor_y += child_box.height  # BLOCK FLOW: each child stacks directly below the previous one

    auto_content_height = cursor_y - content_y
    content_height = explicit_height if explicit_height is not None else auto_content_height

    total_width = content_width + 2 * padding
    total_height = content_height + 2 * padding

    return Box(
        element=element, x=box_x, y=box_y,
        width=total_width, height=total_height,
        children=child_boxes,
    )


def render_layout(box: Box, indent: int = 0) -> str:
    pad = "  " * indent
    line = (
        f"{pad}<{box.element.tag}> "
        f"x={box.x:g} y={box.y:g} width={box.width:g} height={box.height:g}"
    )
    lines = [line]
    for child in box.children:
        lines.append(render_layout(child, indent + 1))
    return "\n".join(lines)
