"""Service layer for pattern ingestion and retrieval."""

from __future__ import annotations

import shutil
import sys
import uuid
from pathlib import Path

from fastapi import UploadFile

# Add pattern-engine to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / "packages" / "pattern-engine" / "src"))

from engine import analyze_pattern  # noqa: E402

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


async def ingest_dxf(file: UploadFile) -> dict:
    """Save uploaded DXF and analyze it."""
    # Save file
    file_id = str(uuid.uuid4())
    file_ext = Path(file.filename or "pattern.dxf").suffix
    saved_path = UPLOAD_DIR / f"{file_id}{file_ext}"

    with saved_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Analyze
    pattern = analyze_pattern(saved_path)
    data = pattern.to_dict()
    data["file_id"] = file_id
    data["filename"] = file.filename

    return data
