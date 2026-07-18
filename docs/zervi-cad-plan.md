# Zervi CAD — Detailed Implementation Plan

**Foundation:** QCAD (GPLv3, 25 years mature, JavaScript scripting, DXF native)  
**Goal:** Internal 2D CAD for Zervi car seat cover manufacturing  
**Approach:** Fork QCAD, keep its CAD engine, add Zervi-specific features as plugins/scripts

---

## 1. Why QCAD Is the Right Foundation

| Requirement | QCAD Provides |
|-------------|-------------|
| Real 2D CAD | Yes — 25 years of development |
| DXF native | Yes — full DXF read/write |
| Open source | GPLv3 — free for internal use |
| Scripting | ECMAScript/JavaScript — we can add features |
| Entity editing | Lines, arcs, circles, polylines, splines, text, dimensions |
| Snap | Endpoint, midpoint, center, intersection, grid |
| Undo/redo | Built-in |
| Layers/blocks | Full support |
| Cross-platform | Windows, macOS, Linux |

**We do not build a CAD engine. We use QCAD's.**

---

## 2. Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Zervi CAD (QCAD fork)                     │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  QCAD Core (C++/Qt)                                 │    │
│  │  • Entity editing                                   │    │
│  │  • Snap, layers, blocks, dimensions                 │    │
│  │  • Undo/redo                                        │    │
│  │  • DXF I/O                                          │    │
│  └─────────────────────────────────────────────────────┘    │
│                              ↓                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Zervi Plugins (JavaScript)                         │    │
│  │  • Pattern import/validation                        │    │
│  │  • Panel hierarchy (driver/passenger/cushion)       │    │
│  │  • BOM generator                                    │    │
│  │  • Block library (seat cover components)            │    │
│  │  • Odoo sync                                        │    │
│  │  • AI agents                                        │    │
│  └─────────────────────────────────────────────────────┘    │
│                              ↓                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Zervi UI Extensions (Qt widgets)                   │    │
│  │  • Pattern panel                                    │    │
│  │  • BOM panel                                        │    │
│  │  • Block library panel                              │    │
│  │  • Agent chat panel                                 │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Phase 0: Foundation (Week 1–2)

### Goal
Build QCAD from source, set up development environment, create Zervi fork.

### Tasks

1. **Clone and build QCAD**
   ```bash
   git clone https://github.com/qcad/qcad.git zervi-cad
   cd zervi-cad
   # Follow compilation instructions for Windows
   ```

2. **Create Zervi branch**
   - Fork QCAD to `sakimotto/zervi-cad`
   - Create `zervi-main` branch
   - Set up build scripts for Windows

3. **Set up development environment**
   - Qt Creator or Visual Studio
   - QCAD build dependencies
   - Debug build for development

4. **Create Zervi plugin structure**
   ```
   zervi-cad/
   ├── scripts/
   │   └── Zervi/
   │       ├── Zervi.js              # Main plugin entry
   │       ├── PatternImport.js      # DXF import/validation
   │       ├── Hierarchy.js          # Panel grouping
   │       ├── BOM.js                # BOM generation
   │       ├── BlockLibrary.js       # Reusable blocks
   │       ├── OdooSync.js           # Odoo integration
   │       └── Agents/               # AI agents
   │           ├── DXFParserAgent.js
   │           ├── HierarchyAgent.js
   │           ├── BOMAgent.js
   │           └── OdooSyncAgent.js
   ```

### Deliverables
- QCAD builds and runs
- Zervi branch created
- Plugin skeleton loads

---

## 4. Phase 1: Pattern Import & Validation (Week 3–4)

### Goal
Import Zervi-template DXF files, validate layers, extract panels.

### Tasks

1. **PatternImport.js**
   - Read DXF using QCAD's built-in import
   - Validate layers against Zervi template (Z_CUT, Z_NOTCH, Z_TEXT_PANELNO, etc.)
   - Flag missing or wrong layers
   - Extract panels from Z_CUT layer geometry

2. **Panel detection**
   - Use QCAD's entity query to find closed shapes
   - Match labels to panels by proximity
   - Classify holes (notch, grommet, hole)

3. **Validation report**
   - Show missing layers
   - Show unmatched labels
   - Show holes outside panels
   - Allow user to fix before proceeding

### Success Criteria
- Import STARIA DXF and see 25 panels
- Import CGA10APH70 DXF and see panels with correct labels
- Validation report shows issues clearly

---

## 5. Phase 2: Panel Hierarchy (Week 5–6)

### Goal
Group panels into driver/passenger/cushion/seatback/headrest assemblies.

### Tasks

1. **Hierarchy.js**
   - Naming convention parser (RB, RC, HR, etc.)
   - Auto-suggest grouping
   - Manual override via UI

2. **Hierarchy panel (Qt widget)**
   - Tree view of assemblies
   - Drag-and-drop panels into groups
   - Rename assemblies
   - Color-code by assembly type

3. **Assembly data model**
   ```
   Vehicle Pattern
   ├── DRIVER SIDE
   │   ├── CUSHION COVER
   │   │   ├── Main Panel
   │   │   ├── Side Panel
   │   │   └── Hook Tab
   │   ├── SEAT BACK COVER
   │   │   ├── Main Panel
   │   │   └── Headrest Sleeve
   │   └── HEADREST COVER
   │       └── Main Panel
   └── PASSENGER SIDE
       └── (mirror)
   ```

### Success Criteria
- Auto-group STARIA 3rd row into driver/passenger/cushion/seatback
- Manual drag-and-drop works
- Hierarchy saved to pattern file

---

## 6. Phase 3: BOM Generation (Week 7–8)

### Goal
Generate multi-level BOM from assemblies.

### Tasks

1. **BOM.js**
   - Compute BOM per assembly
   - Include material, quantity, cut length, area
   - Support different materials per panel

2. **BOM panel (Qt widget)**
   - Tree view of BOM
   - Editable quantities and materials
   - Cost roll-up
   - Export to CSV/Excel

3. **Material catalog**
   - Fabrics, threads, hardware
   - Cost per unit
   - Link to Odoo products

### Success Criteria
- Generate BOM for STARIA 3rd row
- BOM matches manual BOM within 5%
- Export BOM to Excel

---

## 7. Phase 4: Block Library (Week 9–10)

### Goal
Reusable blocks for common seat cover components.

### Tasks

1. **BlockLibrary.js**
   - Store blocks as QCAD blocks
   - Categories: hooks, slots, grommets, notches, seams
   - Insert with scale, angle, mirror

2. **Block library panel (Qt widget)**
   - Category tree
   - Thumbnail previews
   - Search
   - Drag-and-drop into drawing

3. **Block creation workflow**
   - Select entities, create block
   - Name, categorize, tag
   - Usage tracking

### Success Criteria
- Create hook tab block from existing pattern
- Insert block into new pattern
- Block library persists across sessions

---

## 8. Phase 5: Odoo Integration (Week 11–12)

### Goal
Sync BOMs, products, and manufacturing data to Odoo.

### Tasks

1. **OdooSync.js**
   - Odoo XML-RPC/JSON-RPC client
   - Product CRUD
   - BOM CRUD
   - Routing CRUD

2. **Sync panel (Qt widget)**
   - Connection status
   - Sync history
   - Error log
   - Manual sync trigger

3. **Field mapping**
   - Zervi panels → Odoo products
   - Zervi assemblies → Odoo BOMs
   - Zervi operations → Odoo routings

### Success Criteria
- Push BOM to Odoo
- See products and BOMs in Odoo
- Sync status visible

---

## 9. Phase 6: AI Agents (Week 13–14)

### Goal
AI-powered pattern analysis and automation.

### Tasks

1. **Agent framework**
   - Simple JavaScript agent runtime
   - Task queue
   - Approval workflow

2. **Specialist agents**
   - **DXFParserAgent** — Analyze DXF, suggest improvements
   - **HierarchyAgent** — Suggest assembly grouping
   - **BOMAgent** — Generate BOM with material suggestions
   - **OdooSyncAgent** — Map to Odoo with conflict resolution

3. **Agent chat panel (Qt widget)**
   - Chat interface
   - Task list
   - Approval buttons
   - Agent history

### Success Criteria
- Agent suggests hierarchy grouping
- Agent generates BOM with material recommendations
- User approves/rejects agent suggestions

---

## 10. Phase 7: Polish & Rollout (Week 15–16)

### Goal
Production-ready internal release.

### Tasks

1. **Error handling** — Graceful failure everywhere
2. **User documentation** — How to use each feature
3. **Training materials** — Videos, guides
4. **Pilot program** — 2–3 engineers test for 1 week
5. **Feedback iteration** — Fix issues, improve UX

### Success Criteria
- Engineers can use Zervi CAD daily
- BOM generation saves 50% of manual time
- No data loss or corruption

---

## 11. Technical Details

### 11.1 File Structure

```
zervi-cad/
├── src/                          # QCAD core (C++)
├── scripts/
│   └── Zervi/
│       ├── Zervi.js              # Plugin registration
│       ├── PatternImport.js      # DXF import/validation
│       ├── Hierarchy.js          # Panel grouping
│       ├── BOM.js                # BOM generation
│       ├── BlockLibrary.js       # Block management
│       ├── OdooSync.js           # Odoo integration
│       ├── Agents/
│       │   ├── Agent.js          # Base agent class
│       │   ├── DXFParserAgent.js
│       │   ├── HierarchyAgent.js
│       │   ├── BOMAgent.js
│       │   └── OdooSyncAgent.js
│       ├── UI/
│       │   ├── HierarchyPanel.js
│       │   ├── BomPanel.js
│       │   ├── BlockLibraryPanel.js
│       │   └── AgentChatPanel.js
│       └── lib/
│           ├── geometry.js       # Geometry utilities
│           ├── naming.js         # Naming conventions
│           └── odoo.js           # Odoo client
├── docs/
│   ├── architecture.md
│   ├── plan.md
│   └── handover-deepseek.md
└── tests/
    ├── fixtures/                 # Test DXF files
    ├── PatternImport.test.js
    ├── Hierarchy.test.js
    └── BOM.test.js
```

### 11.2 Key Technologies

| Layer | Technology | Why |
|-------|-----------|-----|
| CAD engine | QCAD (C++/Qt) | Mature, proven, scriptable |
| Plugins | JavaScript (ECMAScript) | QCAD's native scripting |
| UI panels | Qt widgets | Native QCAD extension |
| Database | PostgreSQL + pgvector | Pattern memory, part matching |
| Odoo sync | XML-RPC/JSON-RPC | Standard Odoo API |
| AI | DeepSeek / Kimi | Math/geometry reasoning |

### 11.3 License Compliance

- QCAD is GPLv3
- Our plugins are also GPLv3 (derivative work)
- Internal use: no distribution, no requirement to open source
- If we distribute: must open source Zervi CAD

---

## 12. Risk Register

| Risk | Impact | Mitigation |
|------|--------|------------|
| QCAD build fails on Windows | High | Use pre-built QCAD as base, only build plugins |
| JavaScript plugins too slow | Medium | Offload heavy geometry to C++ or Python |
| Odoo schema differences | Medium | Configurable field mappings |
| Engineers resist new tool | High | Keep QCAD UI familiar, add features gradually |
| GPLv3 compliance issues | Medium | Legal review, internal use only |

---

## 13. Success Metrics

- Engineers can import, edit, and export patterns in Zervi CAD
- BOM generation is 50% faster than manual
- 80% of panels correctly grouped by auto-hierarchy
- Odoo sync works without manual fixes
- Zero data loss during 1-week pilot

---

## 14. Next Steps

1. **Confirm QCAD builds** on your Windows machine
2. **Create Zervi fork** on GitHub
3. **Start Phase 0** — build and set up development environment
4. **Assign DeepSeek** to Phase 1–3 (pattern import, hierarchy, BOM)
5. **Bring me back** for UI panels and agent integration (Phase 4–6)

---

## 15. Contact

- **CAD engine (QCAD core, plugins):** DeepSeek
- **UI/UX (panels, agent chat):** Kimi Code CLI
- **Project owner:** Arthur Mitrou
