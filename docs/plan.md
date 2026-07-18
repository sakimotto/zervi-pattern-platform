# Zervi Pattern Platform — Implementation Plan

## Guiding Rule

This is a **design intelligence platform**, not a migration tool or CAD replacement. We build one focused capability at a time and validate with real files before moving on.

---

## Phase 1: DXF Viewer + Pattern Storage (Weeks 1–3)

### Goal
Open one Zervi DXF in the browser, see it rendered with layers/text, and store its structure in PostgreSQL.

### Tasks
1. Build `packages/dxf-parser`
   - Parse DXF into JSON entities
   - Extract layers, lines, arcs, circles, polylines, text
   - Flag unsupported entities (splines, hatches, blocks)
2. Build `packages/pattern-engine`
   - Endpoint snapping
   - Closed-loop panel detection
   - Label extraction
   - Hole classification
3. Build `apps/api`
   - `POST /api/v1/patterns` — ingest DXF
   - `GET /api/v1/patterns` — list patterns
   - `GET /api/v1/patterns/{id}` — get pattern with panels/labels
4. Build `apps/web`
   - Upload page
   - Pattern viewer page (canvas + layer tree + panel list)
   - Basic navigation
5. Database migration: core tables (patterns, panels, labels, holes)

### Success Criteria
- Upload `STARIA WITH PART NUMBERS.dxf` and see it rendered
- Upload `SR-DS-001-CGA10APH70 STARIA 3 RD ROW.dxf` and see layers/text
- Panels and labels extracted to PostgreSQL

---

## Phase 2: Hierarchy Builder + Multi-Level BOM (Weeks 4–6)

### Goal
Group panels into driver/passenger/cushion/seatback/headrest assemblies and generate multi-level BOMs.

### Tasks
1. Add `assemblies` and `assembly_panels` tables
2. Build Hierarchy Builder Agent
   - Suggest grouping from panel names (RB, RC, HR, etc.)
   - Allow manual override in UI
3. Build hierarchy editor UI
   - Tree view of assemblies
   - Drag-and-drop panels into groups
   - Rename assemblies
4. Build BOM Generator Agent
   - Compute BOM per assembly
   - Include material, quantity, cut length, area
5. Build BOM viewer/editor
   - Tree view of BOM
   - Editable quantities and materials

### Success Criteria
- Can group STARIA 3rd row into driver/passenger/cushion/seatback
- Generate multi-level BOM matching actual seat structure

---

## Phase 3: Basic Editing (Weeks 7–8)

### Goal
Allow small, safe edits to patterns without breaking geometry.

### Tasks
1. Label editing
   - Rename panel
   - Change part number
   - Move label position
2. Hole editing
   - Resize notch radius
   - Move hole position
3. Panel naming rules
   - Enforce Zervi naming conventions
   - Suggest standard names
4. Undo/redo for edits
5. Save edits back to DXF (export)

### Success Criteria
- Engineer can rename THSBS204 → correct name
- Export updated DXF that still opens in progeCAD

---

## Phase 4: Agent-Driven Major Operations (Weeks 9–11)

### Goal
Use AI agents to perform complex geometry changes safely.

### Tasks
1. Seam Extension Agent
   - Extend seam allowance by X mm
   - Apply to selected panels or assemblies
   - Preview before apply
2. Panel Splitting Agent
   - Split a large panel into sub-panels
   - Maintain naming and BOM links
3. Mirror Agent
   - Mirror driver side to passenger side
   - Update panel numbers
4. Approval workflow
   - Agent proposes changes
   - User reviews and approves
   - Changes logged

### Success Criteria
- Extend seam allowance on all cushion covers by 10mm
- Mirror driver side to passenger side automatically

---

## Phase 5: Odoo Integration (Weeks 12–13)

### Goal
Sync multi-level BOMs and products to Odoo.

### Tasks
1. Build `packages/odoo-bridge`
   - Auth client
   - Product CRUD
   - BOM CRUD
2. Odoo Sync Agent
   - Map assemblies to Odoo BOMs
   - Map materials to Odoo products
   - Handle conflicts
3. Sync dashboard UI
   - Connection status
   - Sync history
   - Error log

### Success Criteria
- Push STARIA 3rd row BOM to Odoo
- See products and BOM lines in Odoo

---

## Phase 6: Part Matching & Reuse (Weeks 14–15)

### Goal
Find similar panels across patterns and suggest reusable blocks.

### Tasks
1. Compute panel embeddings (pgvector)
2. Part Matching Agent
   - Find similar panels
   - Suggest block candidates
3. Block library UI
   - Browse blocks
   - See usage across patterns
   - Insert block into pattern

### Success Criteria
- Find all panels similar to THSBS204
- Suggest creating a “standard hook tab” block

---

## Technology Stack

| Layer | Choice | Why |
|-------|--------|-----|
| Frontend | SvelteKit + Tailwind | Fast, clean, good DX |
| 2D Canvas | Fabric.js | Easy selection, layers, export |
| Backend | FastAPI | Python ecosystem for geometry |
| Agents | Simple Python runtime | No LangGraph complexity |
| LLM | DeepSeek / Kimi | Strong math, cost-effective |
| Database | PostgreSQL + pgvector | Already running for Saki AI |
| DXF parsing | dxf-parser + custom | Works in browser and server |

---

## What We Are Not Building

- Full CAD editing (no drawing new geometry)
- Batch migration of 10,000 files (import on demand)
- LangGraph or complex agent orchestration
- 3D modeling
- Nesting optimization
- Mobile UI

---

## Success Metrics

- Engineer can upload and view a pattern in under 2 minutes
- 80% of panels correctly classified by type
- Multi-level BOM matches manual BOM within 5%
- Agent-driven seam extension works on test pattern without breaking geometry
- Engineers prefer this tool for BOM generation over Excel
