# Zervi Pattern Platform — Architecture

## 1. Overview

The Zervi Pattern Platform is an AI-first, agent-native system that converts car seat cover DXF/DWG drawings into structured, reusable manufacturing intelligence.

Engineers continue to use their preferred 2D CAD application (progeCAD, LibreCAD, AutoCAD). They export drawings using the Zervi DXF Template. The platform ingests these files, runs specialist AI agents to understand them, stores the results in a PostgreSQL + pgvector database, and exposes everything through a web UI and Odoo integration.

## 2. High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           Client Layer                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐  │
│  │ Pattern      │  │ Agent        │  │ BOM &        │  │ Work        │  │
│  │ Library      │  │ Chat /       │  │ Costing      │  │ Instructions│  │
│  │ Viewer       │  │ Approvals    │  │              │  │             │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  └─────────────┘  │
│                              SvelteKit + Canvas                         │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼ HTTP / WebSocket
┌─────────────────────────────────────────────────────────────────────────┐
│                           API / Agent Layer                              │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                      Agent Orchestrator                           │   │
│  │  • Task routing  • Workflow state  • Human approvals  • Logging   │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│       │            │            │            │            │             │
│       ▼            ▼            ▼            ▼            ▼             │
│  ┌────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ DXF    │  │ Pattern  │  │ BOM      │  │ Validator│  │ Work     │   │
│  │ Parser │  │ Matcher  │  │ Generator│  │ Agent    │  │ Instr.   │   │
│  │ Agent  │  │ Agent    │  │ Agent    │  │          │  │ Agent    │   │
│  └────────┘  └──────────┘  └──────────┐  ┌──────────┘  └──────────┘   │
│       │            │            │     │  │     │            │          │
│       └────────────┴────────────┘     │  │     └────────────┘          │
│                                       │  │                               │
│  ┌────────────────────────────────────┘  └──────────────────────────┐   │
│  │                         Shared Tools & Skills                      │   │
│  │  DXF read/write • Geometry ops • Embedding model • Odoo client     │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                              Python + FastAPI                           │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼ SQL
┌─────────────────────────────────────────────────────────────────────────┐
│                         Data Layer                                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐  │
│  │ PostgreSQL   │  │ pgvector     │  │ File Store   │  │ Vector      │  │
│  │ structured   │  │ embeddings   │  │ DXF originals│  │ memory      │  │
│  │ data         │  │ & search     │  │ & exports    │  │ & cache     │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  └─────────────┘  │
│                      Reuses existing Saki AI Postgres on Elest.io         │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼ XML-RPC / JSON-RPC
┌─────────────────────────────────────────────────────────────────────────┐
│                         Odoo ERP                                         │
│  Products • BOMs • Routings • Inventory • Costing • Manufacturing Orders │
└─────────────────────────────────────────────────────────────────────────┘
```

## 3. Data Model

### 3.1 Core Entities

| Entity | Description |
|--------|-------------|
| `Pattern` | One DXF file representing a pattern set for a vehicle/row/position. |
| `Panel` | A single cut piece of fabric (e.g., THSBS204). |
| `Hole` | A notch, grommet, or mounting hole inside a panel. |
| `Label` | Text found in the DXF: part number, panel number, dimension, etc. |
| `Block` | A reusable component (e.g., standard hook tab, headrest slot). |
| `BOMLine` | One line of a bill of materials for a pattern. |
| `Operation` | A manufacturing step: cut, sew, overlock, attach hardware. |
| `WorkInstruction` | Multimedia step-by-step guide linked to operations. |
| `Vehicle` | Car model, year, trim, market. |
| `Material` | Fabric, thread, hardware specification. |
| `AgentRun` | Log of an agent task, input, output, confidence, approval state. |

### 3.2 PostgreSQL Schema (Initial)

```sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE vehicles (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    make TEXT,
    model TEXT,
    year_start INT,
    year_end INT,
    market TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE patterns (
    id SERIAL PRIMARY KEY,
    vehicle_id INT REFERENCES vehicles(id),
    name TEXT NOT NULL,
    row_position TEXT,
    seat_position TEXT,
    file_path TEXT,
    dxf_hash TEXT UNIQUE,
    status TEXT DEFAULT 'draft', -- draft, validated, approved, archived
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE panels (
    id SERIAL PRIMARY KEY,
    pattern_id INT REFERENCES patterns(id) ON DELETE CASCADE,
    panel_number TEXT,
    part_number TEXT,
    material_code TEXT,
    geometry JSONB NOT NULL,
    area_mm2 NUMERIC,
    cut_length_mm NUMERIC,
    bounding_box JSONB,
    centroid JSONB,
    embedding VECTOR(1536),
    status TEXT DEFAULT 'draft',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE labels (
    id SERIAL PRIMARY KEY,
    pattern_id INT REFERENCES patterns(id) ON DELETE CASCADE,
    panel_id INT REFERENCES panels(id) ON DELETE SET NULL,
    text TEXT,
    layer TEXT,
    label_type TEXT,
    position JSONB,
    height NUMERIC,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE holes (
    id SERIAL PRIMARY KEY,
    panel_id INT REFERENCES panels(id) ON DELETE CASCADE,
    center_x NUMERIC,
    center_y NUMERIC,
    radius_mm NUMERIC,
    diameter_mm NUMERIC,
    classification TEXT, -- notch, grommet, hole
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE blocks (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT,
    geometry JSONB NOT NULL,
    embedding VECTOR(1536),
    usage_count INT DEFAULT 0,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE bom_lines (
    id SERIAL PRIMARY KEY,
    pattern_id INT REFERENCES patterns(id) ON DELETE CASCADE,
    panel_id INT REFERENCES panels(id) ON DELETE SET NULL,
    material_code TEXT,
    description TEXT,
    quantity NUMERIC,
    unit TEXT,
    cost_local NUMERIC,
    odoo_product_id INT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE operations (
    id SERIAL PRIMARY KEY,
    pattern_id INT REFERENCES patterns(id) ON DELETE CASCADE,
    panel_id INT REFERENCES panels(id) ON DELETE SET NULL,
    sequence INT,
    operation_type TEXT, -- cut, sew, overlock, attach, mark
    description TEXT,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE work_instructions (
    id SERIAL PRIMARY KEY,
    operation_id INT REFERENCES operations(id) ON DELETE CASCADE,
    step_number INT,
    title TEXT,
    description TEXT,
    media_urls TEXT[],
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE knowledge (
    id SERIAL PRIMARY KEY,
    title TEXT,
    content TEXT,
    embedding VECTOR(1536),
    source TEXT,
    tags TEXT[],
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE agent_runs (
    id SERIAL PRIMARY KEY,
    agent_name TEXT NOT NULL,
    task TEXT NOT NULL,
    input JSONB,
    output JSONB,
    confidence NUMERIC,
    human_approved BOOLEAN DEFAULT NULL,
    approved_by TEXT,
    approved_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_panels_embedding ON panels USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX idx_blocks_embedding ON blocks USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX idx_knowledge_embedding ON knowledge USING ivfflat (embedding vector_cosine_ops);
```

## 4. Agent System

### 4.1 Agent Orchestrator

The orchestrator receives a task, selects the right agent(s), manages state, logs decisions, and requests human approval when confidence is low.

Tasks can be:
- `parse_dxf` — ingest a new file
- `match_parts` — find similar parts across patterns
- `generate_bom` — build BOM for a pattern
- `validate_pattern` — check compliance
- `create_work_instructions` — generate sewing/CNC guides
- `sync_to_odoo` — push to ERP

### 4.2 Specialist Agents

| Agent | Input | Output | Tools |
|-------|-------|--------|-------|
| DXF Parser Agent | Raw DXF bytes | Patterns, Panels, Labels, Holes | dxf-parser, geometry ops |
| Pattern Classifier Agent | Pattern metadata + labels | Vehicle/row/position | knowledge base, regex |
| Part Matching Agent | Panel embeddings | Similarity groups, block candidates | pgvector, geometry comparison |
| BOM Generator Agent | Panels + holes + materials | BOM lines | material catalog, costing rules |
| Validator Agent | Pattern + panels + rules | Validation report | geometry checks, template rules |
| Work Instruction Agent | Operations + pattern | Step-by-step guides | template library, media builder |
| Odoo Sync Agent | BOM + products | Odoo records | Odoo XML-RPC/JSON-RPC |
| Naming Agent | Labels + positions | Standardized names | naming conventions |

### 4.3 Skills

Skills are reusable functions agents can call:

- `extract_closed_panels(entities)`
- `snap_endpoints(segments, tolerance)`
- `classify_hole(radius)`
- `match_label_to_panel(labels, panels)`
- `compute_cut_length(geometry)`
- `embed_geometry(geometry)`
- `compare_panel_shapes(a, b)`
- `validate_hole_inside_boundary(hole, panel)`
- `generate_odoo_product_payload(panel)`

## 5. DXF Template

To import reliably, exported DXF files should follow this layer convention:

| Layer | Contents |
|-------|----------|
| `Z_CUT` | Outer boundaries, slots, any cut path |
| `Z_NOTCH` | Notch / mounting holes (circles) |
| `Z_STITCH` | Stitch / seam lines |
| `Z_TEXT_PARTNO` | Part numbers (e.g., CGA10APH70) |
| `Z_TEXT_PANELNO` | Panel numbers (e.g., RB1, THSBS204) |
| `Z_TEXT_ITEMNO` | Item/hardware labels (e.g., a, b, c) |
| `Z_DIM` | Dimensions |
| `Z_HOOK` | Hook locations |
| `Z_LOOP` | Loop locations |
| `Z_JOIN` | Join / spline paths |
| `Z_MARK` | Marking points |

Rules:
1. Explode all blocks before export.
2. One pattern set per DXF file.
3. Text labels should be near the geometry they describe.
4. Closed shapes must actually close (tiny gaps are OK, agent will snap).

## 6. Security & Privacy

- All files processed locally by default.
- Database credentials stored in Infisical, never in code.
- LLM calls can be routed through local models or approved APIs.
- No customer vehicle data leaves Zervi infrastructure without approval.

## 7. Integration with Zervi AI Toolkit

The platform reuses:
- Skill definitions from `zervi-ai-toolkit`
- Handover note conventions
- Agent identity and auth patterns
- Session-start protocol

## 8. Future Extensions

- 2D constraint solver for parametric patterns
- Nesting optimization integration
- CNC G-code generation
- 3D seat cover preview
- Supplier quote integration
- Customer-facing configurator
