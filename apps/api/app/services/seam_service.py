"""Service for seam allowance operations using Clipper2."""

from __future__ import annotations

import sys
from pathlib import Path

# Add pattern-engine to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / "packages" / "pattern-engine" / "src"))

from clipper_ops import offset_polygon  # noqa: E402


def apply_seam_allowance(panels: list, distance_mm: float) -> list:
    """Apply seam allowance offset to selected panels."""
    updated = []
    for panel in panels:
        polygon = panel.get("polygon", [])
        if polygon:
            new_polygon = offset_polygon(polygon, distance_mm)
            panel = dict(panel)
            panel["polygon"] = new_polygon
            # Update centroid and bounding box
            xs = [p[0] for p in new_polygon]
            ys = [p[1] for p in new_polygon]
            panel["centroid"] = [sum(xs) / len(xs), sum(ys) / len(ys)]
            panel["bounding_box"] = {
                "min": [min(xs), min(ys)],
                "max": [max(xs), max(ys)],
            }
            panel["area_mm2"] = abs(
                sum(
                    new_polygon[i][0] * new_polygon[(i + 1) % len(new_polygon)][1]
                    - new_polygon[(i + 1) % len(new_polygon)][0] * new_polygon[i][1]
                    for i in range(len(new_polygon))
                )
                / 2
            )
        updated.append(panel)
    return updated
