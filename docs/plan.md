# Zervi Pattern Platform — Implementation Plan

## Guiding Rule

This is a **design intelligence platform**, not a migration tool or CAD replacement. We build one focused capability at a time and validate with real files before moving on.

---

## Current Status (as of 2026-07-18)

### What Works

| Feature | Status | Notes |
|---------|--------|-------|
| DXF parsing | ✅ Working | `packages/dxf-parser` — LINE, ARC, CIRCLE, LWPOLYLINE, POLYLINE, TEXT, MTEXT |
| Panel detection | ✅ Working | `packages/pattern-engine` — endpoint snapping, closed-loop detection, label matching |
| API ingestion | ✅ Working | `POST /api/v1/patterns/ingest` |
| Web viewer | ✅ Working | SvelteKit + Canvas, zoom/pan, layer toggles, panel selection |
| Layer filtering | ✅ Working | Checkbox controls visibility |
| Hole/label filtering | ✅ Working | Right sidebar shows only selected panel’s data |
| CAD-style UI | ✅ Working | Menu bar, ribbon tabs, file tabs, status bar, toolbox, block library panel |

### Tested Files

- `STARIA WITH PART NUMBERS.dxf` — 25 panels, 6 holes, 20 labels
- `SR-DS-001-CGA10APH70 STARIA 3 RD ROW.dxf` — 766 panels (includes title block), 74 holes, 1064 labels

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

## Phase 2: File Management + Basic Editing (IN PROGRESS)

**Goal:** Engineers can manage multiple open patterns and make small, safe edits.

### Tasks
1. [ ] File tabs actually manage multiple open patterns
   - Switch between files
   - Close files
   - Dirty state indicator
2. [ ] Save pattern back to DXF
   - `POST /api/v1/patterns/{id}/export`
   - Download modified DXF
3. [ ] Basic editing
   - Double-click panel to rename
   - Move label position
   - Resize hole radius
   - Undo/redo stack
4. [ ] Keyboard shortcuts
   - Ctrl+S save
   - Ctrl+Z undo
   - Ctrl+Y redo
   - F fit view

### Success Criteria
- Open two DXFs in tabs, switch between them
- Rename THSBS204 → new name, export DXF, open in progeCAD
- Undo a rename

---

## Phase 3: Export DXF (NEXT)

**Goal:** Export selected panels or whole patterns as clean DXF files for CNC/nesting.

### Tasks
1. [ ] Export selected panel as individual DXF
2. [ ] Export whole pattern with edits applied
3. [ ] Export with Zervi template layers preserved
4. [ ] Batch export multiple panels

### Success Criteria
- Export THSBS204 as `THSBS204.dxf` and it opens in progeCAD/LibreCAD

---

## Phase 4: Multi-Level BOM (NEXT)

**Goal:** Group panels into assemblies and generate BOMs.

### Tasks
1. [ ] Add `assemblies` and `assembly_panels` tables
2. [ ] Hierarchy Builder Agent
   - Suggest grouping from panel names (RB, RC, HR, etc.)
   - Manual override in UI
3. [ ] Hierarchy editor UI
   - Tree view of assemblies
   - Drag-and-drop panels into groups
4. [ ] BOM Generator Agent
   - Compute BOM per assembly
   - Include material, quantity, cut length, area
5. [ ] BOM viewer/editor
   - Tree view
   - Editable quantities

### Success Criteria
- Group STARIA 3rd row into driver/passenger/cushion/seatback
- Generate multi-level BOM

---

## Phase 5: Block Library (FUTURE)

**Goal:** Store and insert reusable blocks with real CAD previews.

### Tasks
1. [ ] Store blocks in database
2. [ ] Render real CAD previews from geometry
3. [ ] Insert blocks into pattern
4. [ ] Block usage tracking

---

## Phase 6: Agent-Driven Major Operations (FUTURE)

**Goal:** Use AI agents for complex geometry changes.

### Tasks
1. [ ] Seam Extension Agent
2. [ ] Panel Splitting Agent
3. [ ] Mirror Agent
4. [ ] Approval workflow

---

## Phase 7: Odoo Integration (FUTURE)

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

---

## Immediate Next Steps

1. **Update docs** (this file + architecture.md)
2. **Commit current state**
3. **Build file management** (Phase 2)
4. **Build basic editing** (Phase 2)
5. **Build export DXF** (Phase 3)

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
