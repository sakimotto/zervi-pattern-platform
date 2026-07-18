"""Pattern ingestion and management endpoints."""

from fastapi import APIRouter, File, UploadFile

router = APIRouter()


@router.get("/")
async def list_patterns():
    """List imported patterns."""
    return {"patterns": []}


@router.post("/ingest")
async def ingest_pattern(file: UploadFile = File(...)):
    """Ingest a DXF file using the Zervi template."""
    return {
        "filename": file.filename,
        "status": "queued",
        "message": "Ingestion not yet implemented",
    }


@router.get("/{pattern_id}")
async def get_pattern(pattern_id: int):
    """Get a single pattern by ID."""
    return {"pattern_id": pattern_id}
