"""Pattern ingestion and management endpoints."""

from fastapi import APIRouter, File, UploadFile, HTTPException
from pydantic import BaseModel

from app.services.pattern_service import ingest_dxf
from app.services.export_service import export_panels_to_dxf
from app.services.seam_service import apply_seam_allowance

router = APIRouter()


class ExportPanelsRequest(BaseModel):
    panels: list
    holes: list
    labels: list
    filename: str


class SeamAllowanceRequest(BaseModel):
    panels: list
    distance_mm: float


@router.get("/")
async def list_patterns():
    """List imported patterns."""
    return {"patterns": []}


@router.post("/ingest")
async def ingest_pattern(file: UploadFile = File(...)):
    """Ingest a DXF file using the Zervi template."""
    if not file.filename or not file.filename.lower().endswith(".dxf"):
        raise HTTPException(status_code=400, detail="Only DXF files are supported")

    try:
        return await ingest_dxf(file)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse DXF: {str(e)}")


@router.post("/export-panels")
async def export_panels(request: ExportPanelsRequest):
    """Export multiple panels as DXF."""
    try:
        return export_panels_to_dxf(request.panels, request.holes, request.labels, request.filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export DXF: {str(e)}")


@router.post("/seam-allowance")
async def seam_allowance(request: SeamAllowanceRequest):
    """Apply seam allowance offset to panels using Clipper2."""
    try:
        updated = apply_seam_allowance(request.panels, request.distance_mm)
        return {"panels": updated}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to apply seam allowance: {str(e)}")


@router.get("/{pattern_id}")
async def get_pattern(pattern_id: int):
    """Get a single pattern by ID."""
    return {"pattern_id": pattern_id}
