"""DXF parsing and normalization for the Zervi Pattern Platform."""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any

import ezdxf
from ezdxf import bbox


@dataclass
class DXFLayer:
    name: str
    color: int = 7
    linetype: str = "CONTINUOUS"
    locked: bool = False
    frozen: bool = False


@dataclass
class DXFEntity:
    type: str
    layer: str
    handle: str
    color: int = 256
    geometry: dict[str, Any] = field(default_factory=dict)
    text: str | None = None
    text_height: float | None = None
    position: list[float] | None = None


@dataclass
class DXFDocument:
    file_path: str
    dxf_version: str
    layers: list[DXFLayer] = field(default_factory=list)
    entities: list[DXFEntity] = field(default_factory=list)
    bounding_box: dict[str, list[float]] | None = None
    unsupported: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "file_path": self.file_path,
            "dxf_version": self.dxf_version,
            "layers": [asdict(layer) for layer in self.layers],
            "entities": [asdict(entity) for entity in self.entities],
            "bounding_box": self.bounding_box,
            "unsupported": self.unsupported,
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, default=str)


def parse_dxf(path: Path) -> DXFDocument:
    """Parse a DXF file into a normalized document."""
    doc = ezdxf.readfile(path)
    msp = doc.modelspace()

    result = DXFDocument(
        file_path=str(path),
        dxf_version=doc.dxfversion,
    )

    # Layers
    for layer in doc.layers:
        result.layers.append(
            DXFLayer(
                name=layer.dxf.name,
                color=layer.dxf.color,
                linetype=layer.dxf.linetype,
                locked=layer.is_locked,
                frozen=layer.is_frozen,
            )
        )

    # Bounding box
    extents = bbox.extents(msp, fast=True)
    if extents.has_data:
        result.bounding_box = {
            "min": [extents.extmin.x, extents.extmin.y, extents.extmin.z],
            "max": [extents.extmax.x, extents.extmax.y, extents.extmax.z],
        }

    # Entities
    for entity in msp:
        dxftype = entity.dxftype()
        layer = entity.dxf.layer
        handle = entity.dxf.handle
        color = entity.dxf.color if entity.dxf.hasattr("color") else 256

        if dxftype == "LINE":
            result.entities.append(
                DXFEntity(
                    type="LINE",
                    layer=layer,
                    handle=handle,
                    color=color,
                    geometry={
                        "start": [entity.dxf.start.x, entity.dxf.start.y],
                        "end": [entity.dxf.end.x, entity.dxf.end.y],
                    },
                )
            )
        elif dxftype == "ARC":
            result.entities.append(
                DXFEntity(
                    type="ARC",
                    layer=layer,
                    handle=handle,
                    color=color,
                    geometry={
                        "center": [entity.dxf.center.x, entity.dxf.center.y],
                        "radius": entity.dxf.radius,
                        "start_angle": entity.dxf.start_angle,
                        "end_angle": entity.dxf.end_angle,
                    },
                )
            )
        elif dxftype == "CIRCLE":
            result.entities.append(
                DXFEntity(
                    type="CIRCLE",
                    layer=layer,
                    handle=handle,
                    color=color,
                    geometry={
                        "center": [entity.dxf.center.x, entity.dxf.center.y],
                        "radius": entity.dxf.radius,
                    },
                )
            )
        elif dxftype == "LWPOLYLINE":
            pts = [(p.x, p.y) for p in entity.vertices_in_wcs()]
            closed = entity.closed
            result.entities.append(
                DXFEntity(
                    type="LWPOLYLINE",
                    layer=layer,
                    handle=handle,
                    color=color,
                    geometry={
                        "points": pts,
                        "closed": closed,
                    },
                )
            )
        elif dxftype == "POLYLINE":
            pts = [(v.dxf.location.x, v.dxf.location.y) for v in entity.vertices]
            closed = entity.is_closed
            result.entities.append(
                DXFEntity(
                    type="POLYLINE",
                    layer=layer,
                    handle=handle,
                    color=color,
                    geometry={
                        "points": pts,
                        "closed": closed,
                    },
                )
            )
        elif dxftype == "TEXT":
            text = entity.dxf.text
            result.entities.append(
                DXFEntity(
                    type="TEXT",
                    layer=layer,
                    handle=handle,
                    color=color,
                    text=text,
                    text_height=entity.dxf.height,
                    position=[entity.dxf.insert.x, entity.dxf.insert.y],
                    geometry={
                        "rotation": entity.dxf.rotation if entity.dxf.hasattr("rotation") else 0,
                    },
                )
            )
        elif dxftype == "MTEXT":
            text = entity.plain_text()
            result.entities.append(
                DXFEntity(
                    type="MTEXT",
                    layer=layer,
                    handle=handle,
                    color=color,
                    text=text,
                    text_height=entity.dxf.char_height if entity.dxf.hasattr("char_height") else None,
                    position=[entity.dxf.insert.x, entity.dxf.insert.y],
                )
            )
        elif dxftype == "SPLINE":
            result.unsupported.append(f"SPLINE (handle={handle}, layer={layer})")
        elif dxftype == "INSERT":
            result.unsupported.append(f"INSERT (handle={handle}, layer={layer}, name={entity.dxf.name})")
        elif dxftype == "HATCH":
            result.unsupported.append(f"HATCH (handle={handle}, layer={layer})")
        elif dxftype == "DIMENSION":
            result.unsupported.append(f"DIMENSION (handle={handle}, layer={layer})")
        elif dxftype == "ELLIPSE":
            result.unsupported.append(f"ELLIPSE (handle={handle}, layer={layer})")
        elif dxftype == "POINT":
            result.unsupported.append(f"POINT (handle={handle}, layer={layer})")
        else:
            result.unsupported.append(f"{dxftype} (handle={handle}, layer={layer})")

    return result
