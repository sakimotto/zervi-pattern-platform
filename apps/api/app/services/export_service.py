"""Service for exporting pattern data to DXF."""

from __future__ import annotations

import tempfile
from pathlib import Path

import ezdxf
from fastapi.responses import FileResponse


def export_panels_to_dxf(panels: list, holes: list, labels: list, filename: str) -> FileResponse:
    """Create a DXF file from multiple panels and return it as a download."""
    doc = ezdxf.new("R2010")
    msp = doc.modelspace()

    # Add standard layers
    for layer_name in ["CUT", "NOTCH", "TEXT", "DIMS"]:
        doc.layers.add(layer_name)

    panel_ids = {p.get("id") for p in panels}

    # Add each panel boundary as closed polyline
    for panel in panels:
        polygon = panel.get("polygon", [])
        if polygon:
            points = [(p[0], p[1]) for p in polygon]
            msp.add_lwpolyline(points, close=True, dxfattribs={"layer": "CUT"})

    # Add holes as circles
    for hole in holes:
        if hole.get("inside_panel_id") in panel_ids:
            center = hole.get("center", [0, 0])
            radius = hole.get("radius_mm", 0)
            if radius > 0:
                layer = "NOTCH" if hole.get("classification") == "notch" else "CUT"
                msp.add_circle(center, radius, dxfattribs={"layer": layer})

    # Add labels
    for label in labels:
        if label.get("linked_panel_id") in panel_ids:
            text = label.get("text", "")
            position = label.get("position", [0, 0])
            height = label.get("height") or 10
            layer = "DIMS" if "x" in text.lower() and "mm" in text.lower() else "TEXT"
            msp.add_text(
                text,
                dxfattribs={
                    "layer": layer,
                    "height": height,
                    "insert": position,
                },
            )

    # Save to temp file
    safe_name = filename.replace(" ", "_").replace("/", "_")
    tmp_dir = Path(tempfile.gettempdir())
    out_path = tmp_dir / f"{safe_name}.dxf"
    doc.saveas(out_path)

    return FileResponse(
        path=out_path,
        filename=f"{safe_name}.dxf",
        media_type="application/dxf",
    )
