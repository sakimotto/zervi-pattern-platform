# Zervi Pattern Platform — Architecture

## 1. Overview

The Zervi Pattern Platform is an AI-first design intelligence system for car seat cover manufacturing. It is **not** a CAD replacement. Engineers continue to draw in their existing 2D CAD tools (progeCAD, LibreCAD, AutoCAD). The platform imports the DXF files they export, structures the data, and provides a web-based viewer and editor for pattern analysis, hierarchy management, and multi-level BOM generation.

Major geometry changes (e.g., extending seam allowances, splitting assemblies) are performed by AI agents with specialized skills, not by generic CAD editing tools.

## 2. Current Implementation Status

**As of 2026-07-18:**

| Component | Status | Location |
|-----------|--------|----------|
| DXF parser | ✅ Working | `packages/dxf-parser/src/parser.py` |
| Pattern engine | 🚧 Refactoring | `packages/pattern-engine/src/engine.py` — moving to Clipper2 |
| API ingestion | ✅ Working | `apps/api/app/routers/patterns.py` |
| Web viewer | ✅ Working | `apps/web/src/routes/viewer/+page.svelte` |
| CAD-style UI | ✅ Working | `apps/web/src/lib/components/` |
| Block library panel | ✅ Working | `apps/web/src/lib/components/BlockLibrary.svelte` |
| File management | ✅ Working | File tabs, close, dirty state |
| Basic editing | ✅ Working | Rename, move, draw line, add notch |
| Export DXF | ✅ Working | Export selected panels |
| Multi-level BOM | 📋 Planned | Schema exists, UI not built |
| Odoo sync | 📋 Planned | Not yet implemented |

**UI Components:**

- `MenuBar.svelte` — File, Edit, View, Tools, Help menus
- `RibbonTabs.svelte` — Home, View, Panels, BOM, Agents, Output tabs
- `FileTabs.svelte` — Multiple open patterns
- `StatusBar.svelte` — Coordinates, scale, selection info
- `Toolbox.svelte` — Vertical toolbar (New, Open, Save, Export, Library, Settings)
- `BlockLibrary.svelte` — Block categories, thumbnails, insert options

## 3. CAD Library Stack

**Do not build custom geometry code.** Use existing open-source libraries:

| Library | Purpose | Status |
|---------|---------|--------|
| **Clipper2** | 2D booleans, offsets, polygon operations | 🚧 Being integrated |
| **ezdxf** | DXF read/write | ✅ Working |
| **libredwg** | DWG import | 📋 Planned |
| **PlaneGCS / libslvs** | Constraint solving | 📋 Future |
| **LibreCAD source** | CAD operation reference | 📋 Reference only |

**What we removed:** Custom shapely polygonization, custom endpoint snapping, custom point-in-polygon.

**What we keep:** Current UI, canvas rendering, and editing features.

## 4. Core Principles

## 3. High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    progeCAD / LibreCAD / AutoCAD                 │
│                      (Engineers draw here)                       │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                    Export DXF (Zervi template)
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    Zervi Pattern Platform                        │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Web UI (SvelteKit + Canvas)                            │    │
│  │  • 2D pattern viewer (layers, fonts, notes)            │    │
│  │  • Hierarchy editor (group panels into assemblies)      │    │
│  │  • Basic edits (labels, names, minor tweaks)            │    │
│  │  • BOM viewer & editor                                  │    │
│  │  • Agent chat / approval panel                          │    │
│  └─────────────────────────────────────────────────────────┘    │
│                              ↓                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Agent Runtime (Python)                                  │    │
│  │  • DXF Parser Agent                                      │    │
│  │  • Hierarchy Builder Agent                               │    │
│  │  • BOM Generator Agent                                   │    │
│  │  • Seam Extension Agent                                  │    │
│  │  • Odoo Sync Agent                                       │    │
│  └─────────────────────────────────────────────────────────┘    │
│                              ↓                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  PostgreSQL + pgvector                                   │    │
│  │  • Patterns, panels, labels, holes                       │    │
│  │  • Assemblies (multi-level BOM)                          │    │
│  │  • Embeddings for part matching                          │    │
│  │  • Agent memory                                          │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                         Odoo ERP                                 │
│              Products • BOMs • Routings • Costing                │
└─────────────────────────────────────────────────────────────────┘
```

## 4. Data Model

### 4.1 Multi-Level BOM Structure

The most important design decision is the **assembly hierarchy**. A seat cover pattern is decomposed like this:

```
Vehicle Pattern (e.g., Hyundai Staria 3rd Row)
├── DRIVER SIDE
│   ├── CUSHION COVER
│   │   ├── Main Panel (THSBS201)
│   │   ├── Side Panel (THSBS202)
│   │   ├── Hook Tab (THSBS203)
│   │   └── Notches / Grommets
│   ├── SEAT BACK COVER
│   │   ├── Main Panel (THSBS204)
│   │   ├── Side Panel (THSBS205)
│   │   └── Headrest Sleeve (THSBS206)
│   └── HEADREST COVER
│       ├── Main Panel (THSBS207)
│       └── Grommets (x2)
└── PASSENGER SIDE
    └── (mirror of driver side)
```

This hierarchy is stored as a tree in PostgreSQL:

```sql
CREATE TABLE assemblies (
    id SERIAL PRIMARY KEY,
    parent_id INT REFERENCES assemblies(id) ON DELETE CASCADE,
    pattern_id INT REFERENCES patterns(id) ON DELETE CASCADE,
    name TEXT NOT NULL, -- e.g., DRIVER SIDE, CUSHION COVER
    assembly_type TEXT, -- side, component, sub_component
    sort_order INT,
    metadata JSONB
);

CREATE TABLE assembly_panels (
    assembly_id INT REFERENCES assemblies(id) ON DELETE CASCADE,
    panel_id INT REFERENCES panels(id) ON DELETE CASCADE,
    quantity INT DEFAULT 1,
    PRIMARY KEY (assembly_id, panel_id)
);
```

### 4.2 Core Tables

| Table | Purpose |
|-------|---------|
| `patterns` | One DXF file, linked to vehicle |
| `panels` | Cut pieces of fabric with geometry |
| `labels` | Text entities (part numbers, panel numbers, dimensions) |
| `holes` | Notches, grommets, mounting holes |
| `assemblies` | Multi-level BOM tree |
| `bom_lines` | Generated BOM items per assembly |
| `agent_runs` | Log of agent tasks and approvals |

### 4.3 pgvector Usage

- Panel geometry embeddings for similarity search
- Block/component embeddings for reuse suggestions
- Knowledge base embeddings for AI context

## 5. Agent System

### 5.1 Simple Agent Runtime

We do not need LangGraph initially. A lightweight Python agent runtime is enough:

- Task queue (in-memory or Redis)
- Agent registry
- Skill registry
- Approval workflow
- Structured logging

### 5.2 Specialist Agents

| Agent | What It Does | Example Task |
|-------|------------|--------------|
| DXF Parser Agent | Reads DXF, extracts entities | “Parse this file into panels, labels, holes” |
| Hierarchy Builder Agent | Suggests assembly grouping | “Group these panels into driver/passenger/cushion/seatback” |
| BOM Generator Agent | Builds multi-level BOM | “Generate BOM for Hyundai Staria 3rd row” |
| Seam Extension Agent | Modifies geometry | “Extend seam allowance on all cushion covers by 10mm” |
| Odoo Sync Agent | Pushes BOM to ERP | “Create BOM lines in Odoo for this pattern” |

### 5.3 Skills

Reusable functions agents can call:

- `extract_closed_panels(entities)`
- `match_label_to_panel(labels, panels)`
- `classify_hole(radius)`
- `suggest_assembly_grouping(panels, naming_rules)`
- `compute_bom_for_assembly(assembly)`
- `extend_seam_allowance(panel, distance)`
- `generate_odoo_bom_line(assembly)`

## 6. DXF Template

Engineers must export DXF using these layers:

| Layer | Contents |
|-------|----------|
| `Z_CUT` | Outer boundaries, slots |
| `Z_NOTCH` | Notch / mounting holes |
| `Z_STITCH` | Stitch / seam lines |
| `Z_TEXT_PARTNO` | Part numbers (e.g., CGA10APH70) |
| `Z_TEXT_PANELNO` | Panel numbers (e.g., RB1, THSBS204) |
| `Z_TEXT_ITEMNO` | Item labels (e.g., a, b, c) |
| `Z_DIM` | Dimensions |
| `Z_HOOK` | Hook locations |
| `Z_LOOP` | Loop locations |
| `Z_JOIN` | Join paths |
| `Z_MARK` | Marking points |

Rules:
1. Explode blocks before export.
2. One pattern set per DXF.
3. Text labels near the geometry they describe.
4. Closed shapes should close (small gaps OK).

## 7. Editing vs. Agent Work

| Type | Done By | Examples |
|------|---------|----------|
| Basic edits | User in UI | Rename panel, change label, move text, adjust notch size |
| Major geometry | Agent with skills | Extend seam allowance, split cushion cover into sub-panels, mirror driver to passenger |
| Analysis | Agent with skills | Classify holes, match parts, suggest blocks |
| Integration | Agent with skills | Sync BOM to Odoo |

## 8. Security & Privacy

- Local-first by default.
- Database credentials in Infisical.
- LLM calls can be routed to local models or approved APIs.
- No customer data leaves Zervi without approval.

## 9. Integration with Zervi AI Toolkit

Reuses:
- Skill definitions
- Handover note conventions
- Agent identity patterns
- Session-start protocol

## 10. Future Extensions (Not Now)

- 2D constraint solver for parametric patterns
- Nesting optimization
- CNC G-code generation
- 3D seat cover preview
- Supplier quotes
- Customer configurator
