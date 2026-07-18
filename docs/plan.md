# Zervi Pattern Platform — Implementation Plan

## Guiding Rule

This is a **design intelligence platform**, not a migration tool or CAD replacement. We build one focused capability at a time and validate with real files before moving on.

**Important architectural note:** We use existing open-source CAD libraries instead of building custom geometry code. No custom polygonization, no custom booleans, no custom endpoint snapping.

---

## Current Status (as of 2026-07-18)

### What Works

| Feature | Status | Notes |
|---------|--------|-------|
| DXF parsing | ✅ Working | `packages/dxf-parser` — LINE, ARC, CIRCLE, LWPOLYLINE, POLYLINE, TEXT, MTEXT |
| Panel detection | ✅ Working | `packages/pattern-engine` — currently uses shapely, being refactored to Clipper2 |
| API ingestion | ✅ Working | `POST /api/v1/patterns/ingest` |
| Web viewer | ✅ Working | SvelteKit + Canvas, zoom/pan, layer toggles, panel selection |
| Layer filtering | ✅ Working | Checkbox controls visibility |
| Hole/label filtering | ✅ Working | Right sidebar shows only selected panel’s data |
| CAD-style UI | ✅ Working | Menu bar, ribbon tabs, file tabs, status bar, toolbox, block library |
| Multi-select | ✅ Working | Click, Ctrl+click, rubber-band |
| Panel editing | ✅ Working | Rename panel |
| Export DXF | ✅ Working | Export selected panels as DXF |
| Move panels | ✅ Working | Drag to reposition |
| Draw lines | ✅ Working | Click two points |
| Add notches | ✅ Working | Click to place |
| Touch support | ✅ Working | Pinch zoom, drag pan |

### Tested Files

- `STARIA WITH PART NUMBERS.dxf` — 25 panels, 6 holes, 20 labels
- `SR-DS-001-CGA10APH70 STARIA 3 RD ROW.dxf` — 766 panels, 74 holes, 1064 labels

---

## Architecture Decision: Use Existing CAD Libraries

**Do not build custom geometry code.** Use these libraries:

| Library | Purpose | Why |
|---------|---------|-----|
| **Clipper2** | 2D booleans, offsets, polygon operations | Fast, robust, widely used |
| **ezdxf** | DXF read/write | Already using it, works well |
| **libredwg** | DWG import | Only real open-source DWG reader |
| **PlaneGCS / libslvs** | Constraint solving | For future parametric sketches |
| **LibreCAD source** | CAD operation reference | Move, rotate, scale, mirror, trim, fillet |

### What We Are Refactoring

- **Remove:** Custom shapely polygonization
- **Remove:** Custom endpoint snapping
- **Remove:** Custom point-in-polygon
- **Add:** Clipper2 for all 2D geometry operations
- **Add:** libredwg for DWG import
- **Keep:** Current UI, canvas, and editing features

---

## Phase 1: DXF Viewer + Pattern Storage (DONE)

**Goal:** Open one Zervi DXF in the browser, see it rendered with layers/text, and store its structure.

**Deliverables:**
- [x] `packages/dxf-parser`
- [x] `packages/pattern-engine`
- [x] `apps/api` ingestion endpoint
- [x] `apps/web` viewer with canvas
- [x] Layer tree, panel list, properties sidebar
- [x] Zoom/pan/fit controls
- [x] Y-flip coordinate fix
- [x] Layer visibility filtering
- [x] Hole/label filtering by panel
- [x] CAD-style UI (menu bar, ribbon, file tabs, status bar, toolbox, block library)

---

## Phase 2: File Management + Basic Editing (DONE)

**Goal:** Engineers can manage multiple open patterns and make small, safe edits.

**Deliverables:**
- [x] File tabs manage multiple open patterns
- [x] Switch between files, close files
- [x] Dirty state indicator
- [x] Rename panel
- [x] Export selected panel(s) as DXF
- [x] Multi-select (click, Ctrl+click, rubber band)

---

## Phase 3: CAD Editing (DONE)

**Goal:** Basic CAD editing features.

**Deliverables:**
- [x] Move panels (drag to reposition)
- [x] Draw lines (click two points)
- [x] Add notches (click to place)
- [x] Edit mode toolbar
- [x] Touch support (pinch, drag)

---

## Phase 4: Geometry Engine Refactor (IN PROGRESS)

**Goal:** Replace custom geometry code with proper CAD libraries.

### Tasks
1. [ ] Install Clipper2 Python bindings (`pyclipper` or `clipper2`)
2. [ ] Refactor `packages/pattern-engine` to use Clipper2
   - Panel detection via boolean operations
   - Offset for seam allowance
   - Union/intersection for complex shapes
3. [ ] Add libredwg support for DWG import
   - Convert DWG to DXF before parsing
   - Or direct DWG parsing via libredwg bindings
4. [ ] Reference LibreCAD source for CAD operations
   - Move, rotate, scale, mirror
   - Trim, fillet, offset
5. [ ] Update API to handle both DXF and DWG

### Success Criteria
- Same test files produce same results
- DWG files can be imported
- Seam allowance uses Clipper2 offset

---

## Phase 5: Advanced CAD Editing (NEXT)

**Goal:** Full CAD editing capabilities using LibreCAD concepts.

### Tasks
1. [ ] Rotate panels
2. [ ] Scale panels
3. [ ] Mirror panels
4. [ ] Trim/extend lines
5. [ ] Fillet corners
6. [ ] Offset entities
7. [ ] Undo/redo stack

### Success Criteria
- All basic CAD operations work
- Edits can be undone/redone
- Operations match LibreCAD behavior

---

## Phase 6: Multi-Level BOM (NEXT)

**Goal:** Group panels into assemblies and generate BOMs.

### Tasks
1. [ ] Add `assemblies` and `assembly_panels` tables
2. [ ] Hierarchy Builder Agent
3. [ ] Hierarchy editor UI
4. [ ] BOM Generator Agent
5. [ ] BOM viewer/editor

---

## Phase 7: Block Library (FUTURE)

**Goal:** Store and insert reusable blocks with real CAD previews.

### Tasks
1. [ ] Store blocks in database
2. [ ] Render real CAD previews from geometry
3. [ ] Insert blocks into pattern
4. [ ] Block usage tracking

---

## Phase 8: Agent-Driven Major Operations (FUTURE)

**Goal:** Use AI agents for complex geometry changes.

### Tasks
1. [ ] Seam Extension Agent (uses Clipper2 offset)
2. [ ] Panel Splitting Agent
3. [ ] Mirror Agent
4. [ ] Approval workflow

---

## Phase 9: Odoo Integration (FUTURE)

**Goal:** Sync BOMs and products to Odoo.

### Tasks
1. [ ] Odoo bridge
2. [ ] Sync agent
3. [ ] Sync dashboard

---

## Technical Debt / Known Issues

| Issue | Priority | Fix |
|-------|----------|-----|
| Dev server times out after 10 min | High | Use `npm run dev -- --host 0.0.0.0` or a process manager |
| Block previews are placeholder icons | Medium | Render from actual geometry |
| No database storage yet | High | Add PostgreSQL persistence |
| No authentication | Medium | Add API key or OAuth |
| No error handling in API | High | Add try/catch and user feedback |
| No tests | Medium | Add pytest + vitest |
| Custom geometry code | High | Replace with Clipper2 |

---

## Immediate Next Steps

1. **Install Clipper2** and refactor pattern-engine
2. **Add libredwg** for DWG import
3. **Reference LibreCAD** for CAD operations
4. **Build advanced editing** (rotate, scale, mirror)
5. **Build multi-level BOM**

---

## How to Resume After Crash

1. Read `README.md`
2. Read `docs/architecture.md`
3. Read `docs/plan.md` (this file)
4. Check `git log` for latest commits
5. Start dev servers:
   ```bash
   cd apps/api && ../../.venv/Scripts/python.exe -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
   cd apps/web && npm run dev
   ```
6. Open http://localhost:5173/viewer
