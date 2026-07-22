"""
Module 33: clickjacking_uxss -- Part A: clickjacking.

The real mechanism: a click at a given screen coordinate is delivered
to whichever element is TOPMOST in the compositor's layer stack at
that point (Module 24's model) -- regardless of that element's visual
OPACITY. A layer can be rendered at opacity 0 (fully invisible) and
still be the one that actually receives the click, while the user's
eyes are looking at a completely different, merely visually-underneath
element.

The real defense (frame-ancestors / X-Frame-Options): a page can tell
the browser "never render me inside a frame at all" -- checked BEFORE
the framing attempt succeeds, closing the vector at its root rather
than trying to detect deceptive overlays after the fact.
"""

from dataclasses import dataclass


@dataclass
class Layer:
    label: str
    origin: str
    z_index: int
    opacity: float
    bounds: tuple  # (x1, y1, x2, y2)


def topmost_layer_at(layers: list, x: int, y: int):
    """Real click-targeting logic: highest z-index whose bounds contain
    the point -- opacity is NEVER consulted, because compositing
    opacity is a PAINT concern (Module 24), not an input-routing one."""
    candidates = [
        layer for layer in layers
        if layer.bounds[0] <= x <= layer.bounds[2] and layer.bounds[1] <= y <= layer.bounds[3]
    ]
    if not candidates:
        return None
    return max(candidates, key=lambda layer: layer.z_index)


def simulate_click(layers: list, x: int, y: int, visible_label_hint: str) -> None:
    target = topmost_layer_at(layers, x, y)
    print(f"  User perceives themselves clicking: {visible_label_hint!r} at ({x}, {y})")
    if target is None:
        print("  No layer actually present at that point.")
        return
    print(f"  Click ACTUALLY delivered to: {target.label!r} "
          f"(origin={target.origin}, opacity={target.opacity})")
    if target.opacity < 0.05:
        print("  ^ that layer was NEARLY INVISIBLE -- the user had no way to see "
              "what they were really clicking.")


def frame_ancestors_allows(csp_frame_ancestors: list, embedding_origin: str) -> bool:
    """Real CSP frame-ancestors check -- happens BEFORE the framed page
    is ever rendered inside the embedder, not as a post-hoc overlay check."""
    if "'none'" in csp_frame_ancestors:
        return False
    if "*" in csp_frame_ancestors:
        return True
    return embedding_origin in csp_frame_ancestors


def main() -> None:
    print("=== BEFORE: bank.example has no frame-ancestors protection ===\n")
    layers = [
        Layer("Play Video button", "video-site.example", z_index=1, opacity=1.0,
              bounds=(100, 100, 300, 140)),
        Layer("Confirm $500 Transfer button", "bank.example", z_index=2, opacity=0.02,
              bounds=(100, 100, 300, 140)),  # identical position, invisible, ON TOP
    ]
    simulate_click(layers, x=200, y=120, visible_label_hint="Play Video button")

    print("\n=== AFTER: bank.example sends Content-Security-Policy: frame-ancestors 'none' ===\n")
    allowed = frame_ancestors_allows(["'none'"], embedding_origin="video-site.example")
    print(f"  Can video-site.example embed bank.example in an iframe at all? {allowed}")
    if not allowed:
        print("  The invisible overlay layer never exists in the first place -- "
              "there is nothing for a click to be hijacked INTO.")


if __name__ == "__main__":
    main()
