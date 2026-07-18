"""Pattern analysis engine for car seat cover DXF files."""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any

from shapely.geometry import LineString, Point, Polygon
from shapely.ops import polygonize, unary_union

# Import from the dxf-parser package
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "dxf-parser" / "src"))
from parser import DXFDocument, DXFEntity, parse_dxf  # noqa: E402


@dataclass
class Panel:
    id: str
    area_mm2: float
    cut_length_mm: float
    bounding_box: dict[str, list[float]]
    centroid: list[float]
    polygon: list[list[float]]
    labels: list[str] = field(default_factory=list)


@dataclass
class Hole:
    center: list[float]
    radius_mm: float
    diameter_mm: float
    classification: str
    layer: str = "0"
    inside_panel_id: str | None = None


@dataclass
class Label:
    text: str
    position: list[float]
    height: float | None
    layer: str
    label_type: str
    linked_panel_id: str | None = None


@dataclass
class Pattern:
    source_file: str
    dxf_version: str
    panels: list[Panel] = field(default_factory=list)
    holes: list[Hole] = field(default_factory=list)
    labels: list[Label] = field(default_factory=list)
    layers: list[str] = field(default_factory=list)
    bounding_box: dict[str, list[float]] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_file": self.source_file,
            "dxf_version": self.dxf_version,
            "panels": [asdict(p) for p in self.panels],
            "holes": [asdict(h) for h in self.holes],
            "labels": [asdict(l) for l in self.labels],
            "layers": self.layers,
            "bounding_box": self.bounding_box,
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, default=str)


def _snap_value(value: float, tolerance: float) -> float:
    return round(value / tolerance) * tolerance


def _snap_segments(segments: list[LineString], tolerance: float = 0.05) -> list[LineString]:
    if not segments:
        return segments

    endpoint_map: dict[tuple[float, float], list[tuple[float, float]]] = {}
    for seg in segments:
        coords = list(seg.coords)
        for pt in (coords[0], coords[-1]):
            key = (_snap_value(pt[0], tolerance), _snap_value(pt[1], tolerance))
            endpoint_map.setdefault(key, []).append(pt)

    cluster_center = {
        key: (sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts))
        for key, pts in endpoint_map.items()
    }

    snapped: list[LineString] = []
    for seg in segments:
        coords = list(seg.coords)
        for i in (0, -1):
            pt = coords[i]
            key = (_snap_value(pt[0], tolerance), _snap_value(pt[1], tolerance))
            coords[i] = cluster_center[key]
        try:
            snapped.append(LineString(coords))
        except Exception:
            pass
    return snapped


def _entity_to_linestring(entity: DXFEntity) -> LineString | None:
    dxftype = entity.type
    if dxftype == "LINE":
        return LineString([tuple(entity.geometry["start"]), tuple(entity.geometry["end"])])
    if dxftype == "ARC":
        center = entity.geometry["center"]
        radius = entity.geometry["radius"]
        start = math.radians(entity.geometry["start_angle"])
        end = math.radians(entity.geometry["end_angle"])
        if end < start:
            end += 2 * math.pi
        steps = max(8, int((end - start) / (math.pi / 16)))
        pts = []
        for i in range(steps + 1):
            angle = start + (end - start) * i / steps
            pts.append((center[0] + radius * math.cos(angle), center[1] + radius * math.sin(angle)))
        return LineString(pts)
    if dxftype in ("LWPOLYLINE", "POLYLINE"):
        pts = [tuple(p) for p in entity.geometry["points"]]
        if entity.geometry["closed"]:
            return Polygon(pts).boundary
        return LineString(pts)
    return None


def analyze_pattern(path: Path) -> Pattern:
    """Parse a DXF and extract panels, holes, and labels."""
    doc = parse_dxf(path)
    result = Pattern(
        source_file=doc.file_path,
        dxf_version=doc.dxf_version,
        layers=[layer.name for layer in doc.layers],
        bounding_box=doc.bounding_box,
    )

    segments: list[LineString] = []
    for entity in doc.entities:
        geom = _entity_to_linestring(entity)
        if geom:
            segments.append(geom)

        if entity.type == "CIRCLE":
            radius = entity.geometry["radius"]
            classification = "notch" if radius < 15 else "grommet" if radius < 50 else "hole"
            result.holes.append(
                Hole(
                    center=entity.geometry["center"],
                    radius_mm=radius,
                    diameter_mm=radius * 2,
                    classification=classification,
                    layer=entity.layer,
                )
            )
        elif entity.type in ("TEXT", "MTEXT") and entity.text:
            label_type = "part_number" if "PART" in entity.layer.upper() else "panel_number" if "PANEL" in entity.layer.upper() else "text"
            result.labels.append(
                Label(
                    text=entity.text,
                    position=entity.position or [0, 0],
                    height=entity.text_height,
                    layer=entity.layer,
                    label_type=label_type,
                )
            )

    # Detect closed panels
    if segments:
        snapped = _snap_segments(segments, tolerance=0.05)
        merged = unary_union(snapped)
        polys = list(polygonize(merged))

        for i, poly in enumerate(polys):
            if poly.area < 500:
                continue
            bounds = poly.bounds
            centroid = poly.centroid
            panel_id = f"PANEL_{i + 1}"
            result.panels.append(
                Panel(
                    id=panel_id,
                    area_mm2=round(poly.area, 2),
                    cut_length_mm=round(poly.boundary.length, 2),
                    bounding_box={"min": [bounds[0], bounds[1]], "max": [bounds[2], bounds[3]]},
                    centroid=[centroid.x, centroid.y],
                    polygon=[[p[0], p[1]] for p in poly.exterior.coords],
                )
            )

    # Match holes to panels
    for hole in result.holes:
        pt = Point(hole.center[0], hole.center[1])
        for panel in result.panels:
            poly = Polygon(panel.polygon)
            if poly.contains(pt) or poly.touches(pt):
                hole.inside_panel_id = panel.id
                break

    # Match labels to panels (nearest centroid)
    for label in result.labels:
        best_panel = None
        best_dist = float("inf")
        for panel in result.panels:
            dist = math.sqrt((panel.centroid[0] - label.position[0]) ** 2 + (panel.centroid[1] - label.position[1]) ** 2)
            if dist < best_dist and dist <= 300:
                best_dist = dist
                best_panel = panel
        if best_panel:
            label.linked_panel_id = best_panel.id
            best_panel.labels.append(label.text)

    return result
