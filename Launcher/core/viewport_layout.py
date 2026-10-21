"""Display-only layout policy for the CP1 environment doctor.

The game/runtime state is intentionally independent of window dimensions.
"""

MIN_WINDOW_SIZE = (800, 600)
COMPACT_LAYOUT_BELOW = 1120


def is_compact_layout(window_width: int) -> bool:
    """Stack diagnosis panes when side-by-side columns would clip text."""
    return window_width < COMPACT_LAYOUT_BELOW
