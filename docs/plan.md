# Zervi Pattern Platform — Implementation Plan

## Phase 0: Foundation (Week 1)

### Goals
- Repository set up with clean structure
- Development environment reproducible
- Core documentation complete
- UI/UX handover ready for Kimi K3

### Tasks
1. [x] Create repo structure
2. [ ] Add root `package.json` with workspace scripts
3. [ ] Add Python `pyproject.toml` / `requirements.txt`
4. [ ] Add `docker-compose.yml` for local PostgreSQL + pgvector
5. [ ] Add `README.md` developer setup
6. [ ] Write `docs/architecture.md`
7. [ ] Write `docs/plan.md`
8. [ ] Write `docs/handover-k3-ui.md`
9. [ ] Initialize Git and push to GitHub
10. [ ] Add GitHub issue templates (bug, feature, agent task)

### Deliverables
- `README.md`
- `docs/architecture.md`
- `docs/plan.md`
- `docs/handover-k3-ui.md`
- `docker-compose.yml`
- `package.json`
- `pyproject.toml`

---

## Phase 1: DXF Ingestion & Pattern Storage (Weeks 2–3)

### Goals
- Import a Zervi-template DXF file
- Extract panels, labels, holes
- Store results in PostgreSQL
- Validate imported data

### Tasks
1. [ ] Build `packages/dxf-parser`
   - Parse DXF into normalized entity list
   - Extract layers, lines, arcs, circles, polylines, text, mtext
   - Handle block explosions (or flag them)
   - Export JSON representation
2. [ ] Build `packages/pattern-engine`
   - Endpoint snapping and closed-loop detection
   - Panel detection from `Z_CUT` + `Z_NOTCH` layers
   - Label-to-panel matching
   - Hole classification (notch/grommet/hole)
   - Validation rules
3. [ ] Build database migrations
   - Tables from `architecture.md`
   - Indexes for embeddings
4. [ ] Build `apps/api` ingestion endpoint
   - `POST /api/v1/patterns/ingest`
   - Store raw DXF
   - Run parser + pattern engine
   - Save to Postgres
5. [ ] Add tests using sample DXFs from `tests/shared-fixtures`

### Deliverables
- Ingestion API working locally
- STARIA file can be imported with panels and labels
- Validation report generated

---

## Phase 2: Web UI — Pattern Viewer (Weeks 3–5)

### Goals
- Engineers can upload a DXF and see the pattern
- Panel list, layer tree, properties panel
- Zoom, pan, toggle layers
- View validation issues

### Tasks
1. [ ] Set up `apps/web` with SvelteKit + TailwindCSS
2. [ ] Implement dark-mode-first design system
3. [ ] Build 2D canvas renderer using Fabric.js or Paper.js
   - Render lines, arcs, circles, text
   - Layer visibility toggles
   - Hover/select entities
4. [ ] Build Pattern Library page
   - Grid/list of imported patterns
   - Search and filters
5. [ ] Build Pattern Viewer page
   - Canvas center
   - Left: layer tree + panel list
   - Right: properties panel
   - Bottom: validation log + BOM preview
6. [ ] Connect to API
7. [ ] Add K3 UI polish

### Deliverables
- Working web UI
- Pattern upload → viewer flow
- Dark mode, responsive layout

---

## Phase 3: Agent Runtime & First Agents (Weeks 5–7)

### Goals
- Multi-agent orchestration works
- DXF Parser Agent and Validator Agent operational
- Human-in-the-loop approval flow

### Tasks
1. [ ] Build `packages/agent-runtime`
   - Task queue / state machine
   - Agent registry
   - Skill registry
   - Approval workflow
   - Logging
2. [ ] Implement DXF Parser Agent
   - Calls dxf-parser + pattern-engine
   - Returns structured pattern
3. [ ] Implement Validator Agent
   - Checks template compliance
   - Checks hole placement
   - Reports issues with severity
4. [ ] Add agent approval UI
   - List pending agent decisions
   - Approve/reject with comment
5. [ ] Add LLM integration (DeepSeek / Kimi)
   - Agent reasoning for ambiguous cases
   - Confidence scoring

### Deliverables
- Agent orchestrator running
- Two specialist agents operational
- Approval UI

---

## Phase 4: Part Matching & Blocks (Weeks 7–9)

### Goals
- Find similar panels across patterns
- Suggest reusable blocks
- Build block library

### Tasks
1. [ ] Implement geometry embedding
   - Convert panel geometry to vector embedding
   - Store in pgvector
2. [ ] Build Part Matching Agent
   - Query similar panels
   - Group duplicates/near-duplicates
   - Suggest block creation
3. [ ] Build Block Library UI
   - Browse blocks
   - View usage across patterns
   - Drag-and-drop into patterns
4. [ ] Add block creation workflow
   - Promote panel to block
   - Name, categorize, tag

### Deliverables
- Similar part detection
- Block library with search

---

## Phase 5: BOM, Costing & Work Instructions (Weeks 9–11)

### Goals
- Auto-generate BOM from pattern
- Link materials and costs
- Generate step-by-step work instructions

### Tasks
1. [ ] Build material catalog
   - Fabrics, threads, hardware
   - Cost per unit
2. [ ] Implement BOM Generator Agent
   - Compute fabric area
   - Count holes/hardware
   - Generate BOM lines
3. [ ] Build BOM editor UI
   - Editable table
   - Cost roll-up
4. [ ] Implement Work Instruction Agent
   - Generate operations from layers
   - Create multimedia steps
5. [ ] Build work instruction editor
   - Add images/videos/text
   - Sequence operations

### Deliverables
- BOM export (CSV/Excel)
- Work instruction builder

---

## Phase 6: Odoo Integration (Weeks 11–13)

### Goals
- Sync products, BOMs, and routings to Odoo
- Two-way sync where possible

### Tasks
1. [ ] Build `packages/odoo-bridge`
   - Auth client
   - Product CRUD
   - BOM CRUD
   - Routing CRUD
2. [ ] Implement Odoo Sync Agent
   - Map platform data to Odoo models
   - Handle conflicts
   - Report sync status
3. [ ] Add Odoo settings UI
   - URL, database, credentials (via Infisical)
   - Sync mappings
4. [ ] Add sync history and logs

### Deliverables
- Push BOM to Odoo
- Pull product list from Odoo
- Sync status dashboard

---

## Phase 7: Polish, Testing & Rollout (Weeks 13–15)

### Goals
- Stable enough for internal pilot
- Engineers can use it daily
- Documentation complete

### Tasks
1. [ ] End-to-end tests
2. [ ] Performance optimization
   - Large DXF handling
   - Canvas rendering
   - Database queries
3. [ ] Error handling and recovery
4. [ ] User documentation
5. [ ] Pilot with 1–2 engineers
6. [ ] Iterate based on feedback

### Deliverables
- Production-ready internal release
- Training docs
- Pilot feedback report

---

## Technology Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Frontend | SvelteKit | Fast, modern, less boilerplate than React |
| 2D Canvas | Fabric.js | Mature, easy selection/layers, good DXF rendering fit |
| Backend | FastAPI + Python | Python ecosystem for geometry and AI |
| Agents | LangGraph | Proven orchestration, state machines, human-in-the-loop |
| LLM | DeepSeek / Kimi | Strong math/geometry reasoning, cost-effective |
| Database | PostgreSQL + pgvector | Already running for Saki AI |
| DXF parsing | dxf-parser + custom | Browser and server-side parsing |
| Geometry engine | custom + shapely | Server-side robust geometry |

---

## Risk Register

| Risk | Impact | Mitigation |
|------|--------|------------|
| DXF files too messy to parse reliably | High | Build flexible parser + validator; accept human correction |
| Engineers resist new export template | High | Keep template minimal; provide clear checklist |
| LLM makes wrong part classifications | Medium | Human approval for low-confidence decisions |
| Large files slow browser | Medium | Server-side preprocessing; lazy loading; viewport culling |
| Odoo schema differences | Medium | Configurable field mappings; sync logs |

---

## Success Metrics

- 90% of new patterns pass validation with no human edits
- BOM generation saves 50% of manual BOM time
- Part matching finds 30%+ reusable blocks across patterns
- Engineers can upload and review a pattern in under 2 minutes
