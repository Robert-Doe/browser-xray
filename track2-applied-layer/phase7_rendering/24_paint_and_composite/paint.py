"""
Module 24: paint_and_composite -- the PAINT stage.

Turns real box geometry (Module 23) into "paint records" -- the
pixels-to-be, in effect. Painting reads the computed style's visual
(not geometric) properties and records what color goes where, in the
box's own local coordinates. Nothing about compositing (layering,
transforms) happens here -- that's a genuinely separate stage.
"""

from dataclasses import dataclass

from layout import Box


@dataclass
class PaintRecord:
    box: Box
    background_color: str


def paint(box: Box) -> list:
    """Real, actual painting: reads computed style, produces a flat
    list of paint records in back-to-front order (parents painted
    before their children, matching real painter's-algorithm order)."""
    records = []
    background = box.element.computed_style.get("background-color") or box.element.computed_style.get("background")
    if background:
        records.append(PaintRecord(box=box, background_color=background))
    for child in box.children:
        records.extend(paint(child))
    return records
