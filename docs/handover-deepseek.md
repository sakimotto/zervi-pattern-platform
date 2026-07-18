# Handover — Zervi Pattern Platform to DeepSeek

**Date:** 2026-07-18  
**From:** Kimi Code CLI  
**To:** DeepSeek (CAD Engine Developer)  
**Project:** Zervi Pattern Platform  
**Repo:** https://github.com/sakimotto/zervi-pattern-platform

---

## 1. Project Overview

The Zervi Pattern Platform is a web-based design intelligence system for car seat cover manufacturing. Engineers use existing 2D CAD tools (progeCAD, LibreCAD, AutoCAD) to draw patterns. This platform imports their DXF files, structures the data, and provides a web-based viewer, editor, and BOM generator.

**Important:** This is NOT a CAD replacement. It is a companion tool for pattern analysis, hierarchy management, and manufacturing intelligence.

---

## 2. What Works (Do Not Break)

### 2.1 DXF Parsing and Pattern Detection

- **`packages/dxf-parser/src/parser.py`** — Parses DXF into JSON entities (LINE, ARC, CIRCLE, LWPOLYLINE, POLYLINE, TEXT, MTEXT)
- **`packages/pattern-engine/src/engine.py`** — Detects panels using shapely polygonization with endpoint snapping
- **`packages/pattern-engine/src/clipper_ops.py`** — Clipper2 integration for offsets and booleans

**Test files:**
- `D:\OneDrive\OneDrive - Zervi Asia Co., Ltd\Documents\LBRECAD-TEST\STARIA WITH PART NUMBERS.dxf`
- `D:\OneDrive\OneDrive - Zervi Asia Co., Ltd\Documents\LBRECAD-TEST\SR-DS-001-CGA10APH70 STARIA 3 RD ROW.dxf`

### 2.2 API

- **`apps/api/app/routers/patterns.py`** — FastAPI endpoints
  - `POST /api/v1/patterns/ingest` — Upload DXF
  - `POST /api/v1/patterns/export-panels` — Export selected panels as DXF
  - `POST /api/v1/patterns/seam-allowance` — Apply seam allowance (Clipper2)

### 2.3 Web Viewer (Raw Canvas Version)

The raw canvas version works and is in the git history before the Fabric.js refactor.

**Key files:**
- `apps/web/src/lib/canvas.js` — Canvas rendering with Y-flip, zoom, pan
- `apps/web/src/routes/viewer/+page.svelte` — Viewer with selection, move, draw line, add notch

**Features that work:**
- Multi-select (click, Ctrl+click, rubber band)
- Move panels (drag to reposition)
- Draw lines (click two points)
- Add notches (click to place)
- Panel rename
- Export DXF (single or multiple panels)
- Layer filtering
- File tabs

### 2.4 CAD-Style UI

- **`apps/web/src/lib/components/MenuBar.svelte`** — File, Edit, View, Tools, Help
- **`apps/web/src/lib/components/RibbonTabs.svelte`** — Home, View, Panels, BOM, Agents, Output
- **`apps/web/src/lib/components/FileTabs.svelte`** — Multiple open patterns
- **`apps/web/src/lib/components/StatusBar.svelte`** — Coordinates, scale, selection
- **`apps/web/src/lib/components/Toolbox.svelte`** — Vertical toolbar
- **`apps/web/src/lib/components/BlockLibrary.svelte`** — Block categories, thumbnails, insert options

---

## 3. What Does NOT Work (Needs CAD Engine)

### 3.1 Fabric.js Refactor (Wrong Approach)

The current `main` branch has a Fabric.js-based viewer that is **wrong for CAD**. Fabric.js is a vector drawing app, not a CAD tool. It scales objects with handles, which is not how CAD works.

**Do not use the Fabric.js version.** Revert to the raw canvas version from git history.

### 3.2 Missing CAD Foundation

| Feature | Status | Notes |
|---------|--------|-------|
| Undo/redo | ❌ Missing | Critical for production use |
| Entity editing | ❌ Missing | Only panels can be edited, not individual lines/arcs |
| Snap | ❌ Missing | No endpoint, midpoint, center snap |
| Trim/extend | ❌ Missing | |
| Fillet/chamfer | ❌ Missing | |
| Rotate/scale/mirror | ❌ Missing | |
| Dimensioning | ❌ Missing | |
| Constraint solving | ❌ Missing | |

---

## 4. What DeepSeek Should Build

### 4.1 Immediate (Foundation)

1. **Revert to raw canvas version** from git history (before Fabric.js)
2. **Undo/redo system** — Command pattern with history stack
3. **Entity editing** — Select and edit individual lines, arcs, circles
4. **Snap system** — Endpoint, midpoint, center, intersection
5. **Basic CAD operations** — Move, rotate, scale, mirror, delete, copy

### 4.2 Short Term (CAD Operations)

6. **Trim/extend** — Trim lines to cutting edge
7. **Fillet/chamfer** — Round or bevel corners
8. **Offset** — Parallel lines with distance
9. **Drawing tools** — Line, circle, arc, rectangle, polyline
10. **Dimensioning** — Linear, angular, radial dimensions

### 4.3 Medium Term (Advanced)

11. **Constraint solver** — PlaneGCS or libslvs
12. **Blocks** — Create, insert, manage blocks
13. **Hatching** — Fill patterns
14. **Text styles** — Fonts, sizes, alignments

---

## 5. Key Decisions to Respect

1. **Use existing libraries** — Do not build custom geometry code
   - **Clipper2** for booleans and offsets
   - **ezdxf** for DXF I/O
   - **libredwg** for DWG import
   - **PlaneGCS/libslvs** for constraints

2. **CAD is line-by-line, not handle-based** — No drag-to-scale, no bounding boxes. Click entity, edit properties.

3. **Snap is critical** — Engineers expect endpoint, midpoint, center snap.

4. **Undo/redo is mandatory** — Every edit must be reversible.

5. **No seat-cover-specific features yet** — Build general 2D CAD first, customize later.

---

## 6. Reference Code

### 6.1 LibreCAD Source

Local copy: `C:\Users\Arthur Mitrou\zervi\repos\librecad-src`

Use as reference for:
- CAD operations (move, rotate, trim, fillet)
- Mouse handling
- Entity selection
- Undo/redo patterns

### 6.2 Zervi CAD Assistant (Previous Project)

Local copy: `C:\Users\Arthur Mitrou\zervi\repos\zervi-cad-assistant`

Contains working DXF cleanup scripts that can be adapted.

---

## 7. How to Run

```bash
# Clone
git clone https://github.com/sakimotto/zervi-pattern-platform.git
cd zervi-pattern-platform

# Python deps
python -m venv .venv
.venv/Scripts/pip install fastapi uvicorn[standard] pydantic pydantic-settings ezdxf shapely python-multipart python-dotenv httpx pyclipper

# Node deps
cd apps/web
npm install

# Run API
cd apps/api
../../.venv/Scripts/python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000

# Run Web (another terminal)
cd apps/web
npm run dev

# Open http://localhost:5173/viewer
```

---

## 8. Git History Guidance

The git history has both working and broken versions:

- **Working raw canvas:** Commits before `3806162` (Fabric.js refactor)
- **Broken Fabric.js:** Commits after `3806162`

To revert to the working version:
```bash
git checkout 84d7e5a -- apps/web/src/routes/viewer/+page.svelte apps/web/src/lib/canvas.js
```

---

## 9. Contact

- **UI/UX questions:** Bring back Kimi Code CLI
- **CAD engine questions:** DeepSeek
- **Project owner:** Arthur Mitrou

---

## 10. Final Notes

This project has a working viewer, API, and UI. The missing piece is a proper 2D CAD editing engine. Build that with Clipper2, ezdxf, and LibreCAD as reference. Do not reinvent CAD — use existing libraries and patterns.

The user (Arthur) is frustrated with shortcuts. Build the foundation properly, even if it takes longer. No Fabric.js, no drag-to-scale, no handle-based editing. Real CAD: line-by-line, snap, precise operations, undo/redo.
