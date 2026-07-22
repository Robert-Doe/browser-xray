"""
Module 24: paint_and_composite -- the COMPOSITE stage.

Takes already-painted records and arranges them into LAYERS -- real
browsers give certain elements (those with `transform`, `opacity`
animations, `will-change`, etc.) their own compositor layer
specifically so that layer can be moved, scaled, or faded by the GPU
without re-running paint (or layout) at all. This is the real,
practical reason those specific CSS properties are singled out as
"compositor-only" / "cheap to animate" in browser performance guidance.
"""

from dataclasses import dataclass, field


def needs_own_layer(box) -> bool:
    style = box.element.computed_style
    return "transform" in style or style.get("will-change") == "transform"


@dataclass
class Layer:
    name: str
    paint_records: list = field(default_factory=list)
    offset_x: float = 0.0
    offset_y: float = 0.0


def composite(root_box, all_paint_records: list) -> list:
    """Walks the box tree once, assigning each paint record to either
    the shared base layer or a NEW, dedicated layer for any box that
    needs one -- exactly the real reason some elements get "promoted"
    to their own compositor layer."""
    base_layer = Layer(name="base")
    layers = [base_layer]

    def assign(box, current_layer):
        record = next((r for r in all_paint_records if r.box is box), None)
        if needs_own_layer(box):
            layer_id = box.element.element_id() or box.element.tag
            new_layer = Layer(name=f"layer:{layer_id}")
            if record:
                new_layer.paint_records.append(record)
            layers.append(new_layer)
            for child in box.children:
                assign(child, new_layer)
        else:
            if record:
                current_layer.paint_records.append(record)
            for child in box.children:
                assign(child, current_layer)

    assign(root_box, base_layer)
    return layers


def render_layers(layers: list) -> str:
    lines = []
    for layer in layers:
        lines.append(f"{layer.name}  (offset {layer.offset_x:g}, {layer.offset_y:g})")
        for record in layer.paint_records:
            b = record.box
            lines.append(
                f"    <{b.element.tag}> background={record.background_color!r} "
                f"at x={b.x:g} y={b.y:g} w={b.width:g} h={b.height:g}"
            )
    return "\n".join(lines)
