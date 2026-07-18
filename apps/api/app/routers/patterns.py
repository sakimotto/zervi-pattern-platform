"""Pattern ingestion and management endpoints."""

from fastapi import APIRouter, File, UploadFile, HTTPException

from app.services.pattern_service import ingest_dxf

router = APIRouter()


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


@router.get("/{pattern_id}")
async def get_pattern(pattern_id: int):
    """Get a single pattern by ID."""
    return {"pattern_id": pattern_id}
