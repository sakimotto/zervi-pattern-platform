"""Clipper2-based geometry operations for Zervi Pattern Platform."""

from __future__ import annotations

import pyclipper


def offset_polygon(points: list[list[float]], distance: float) -> list[list[float]]:
    """Offset a polygon by distance using Clipper2.

    Positive distance expands, negative shrinks.
    """
    if not points or len(points) < 3:
        return points

    # Clipper2 uses integer coordinates; scale to preserve precision
    scale = 1000
    path = [(int(p[0] * scale), int(p[1] * scale)) for p in points]

    pco = pyclipper.PyclipperOffset()
    pco.AddPath(path, pyclipper.JT_ROUND, pyclipper.ET_CLOSEDPOLYGON)
    solution = pco.Execute(distance * scale)

    if not solution:
        return points

    # Return the largest resulting polygon
    largest = max(solution, key=lambda p: abs(pyclipper.Area(p)))
    return [[p[0] / scale, p[1] / scale] for p in largest]


def polygon_area(points: list[list[float]]) -> float:
    """Compute polygon area using Clipper2."""
    scale = 1000
    path = [(int(p[0] * scale), int(p[1] * scale)) for p in points]
    return abs(pyclipper.Area(path)) / (scale * scale)


def union_polygons(polygons: list[list[list[float]]]) -> list[list[list[float]]]:
    """Union multiple polygons using Clipper2."""
    scale = 1000
    clip = pyclipper.Pyclipper()
    for poly in polygons:
        path = [(int(p[0] * scale), int(p[1] * scale)) for p in poly]
        clip.AddPath(path, pyclipper.PT_SUBJECT, True)

    solution = clip.Execute(pyclipper.CT_UNION, pyclipper.PFT_NONZERO, pyclipper.PFT_NONZERO)
    return [[[p[0] / scale, p[1] / scale] for p in poly] for poly in solution]
