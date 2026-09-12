"""Re-exports the Pillow text-rendering helpers already written for
instagram_bot (RTL-aware Persian layout, font loading) instead of forking
them -- both projects burn text onto video/image frames the same way, and
the fonts/ directory (large .ttf files) already lives under instagram_bot/.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "instagram_bot"))

from text_overlay import (  # noqa: E402  (import must follow sys.path tweak)
    draw_wrapped_px,
    draw_wrapped_rtl,
    load_font,
    rounded_panel,
    vazirmatn,
    wrap_lines_px,
)

__all__ = [
    "draw_wrapped_px",
    "draw_wrapped_rtl",
    "load_font",
    "rounded_panel",
    "vazirmatn",
    "wrap_lines_px",
]
