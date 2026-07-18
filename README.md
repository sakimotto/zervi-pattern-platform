# Zervi Pattern Platform

AI-first design intelligence system for Zervi car seat cover manufacturing.

## Current Status (2026-07-18)

**Working:**
- DXF parsing and panel detection
- Web-based CAD viewer with zoom/pan
- Layer filtering and panel selection
- CAD-style UI (menu bar, ribbon, file tabs, status bar, toolbox, block library)
- API ingestion endpoint
- Multi-select and export DXF

**Needs CAD Engine:**
- Undo/redo
- Entity editing (lines, arcs, circles)
- Snap system
- Trim/extend/fillet
- Rotate/scale/mirror
- Dimensioning

**Handover:** See `docs/handover-deepseek.md` for CAD engine development.

## Vision

Engineers continue to draw in their existing 2D CAD tools (progeCAD, LibreCAD, AutoCAD). The platform imports the DXF files they export, structures the data into PostgreSQL + pgvector, and provides a web-based viewer and editor for pattern analysis, hierarchy management, and multi-level BOM generation.

Major geometry changes are performed by AI agents with specialized skills, not by generic CAD editing tools.

## Repository Structure

```
zervi-pattern-platform/
├── apps/
│   ├── web/                 # Browser UI (SvelteKit + Canvas)
│   └── api/                 # Python backend / agent runtime
├── packages/
│   ├── dxf-parser/          # DXF/DWG parsing and normalization
│   ├── pattern-engine/      # 2D geometry, panels, validation
│   ├── agent-runtime/       # Lightweight agent orchestration
│   └── odoo-bridge/         # Odoo XML-RPC/JSON-RPC integration
├── db/
│   └── migrations/          # PostgreSQL + pgvector schema
├── docs/
│   ├── architecture.md      # System architecture
│   ├── plan.md              # Implementation plan
│   ├── handover-k3-ui.md    # UI/UX handover for Kimi K3
│   └── handover-deepseek.md # CAD engine handover for DeepSeek
├── scripts/                 # Automation scripts
└── tests/                   # Shared fixtures and e2e tests
```

## Key Principles

1. **Design intelligence first:** Viewing, structuring, and analyzing patterns is the primary job.
2. **Basic editing, agent-driven major work:** Small edits in UI; big changes via specialist agents.
3. **CAD-agnostic:** Engineers keep their existing CAD tools. DXF is the interchange format.
4. **Multi-level BOM is core:** Break single-level patterns into driver/passenger/cushion/seatback/headrest assemblies.
5. **Odoo-integrated:** BOMs, inventory, costing, and manufacturing orders flow into Odoo.

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | SvelteKit, TailwindCSS, TypeScript |
| 2D Canvas | Fabric.js / Paper.js |
| Backend | Python, FastAPI |
| Agents | Simple Python runtime + custom skills |
| LLM | DeepSeek / Kimi / OpenAI |
| Database | PostgreSQL + pgvector |
| Vector search | pgvector |
| DXF | `dxf-parser`, `ezdxf` |
| Odoo | XML-RPC/JSON-RPC client |

## Quick Start

```bash
# Clone
git clone https://github.com/sakimotto/zervi-pattern-platform.git
cd zervi-pattern-platform

# Install Python deps
python -m venv .venv
.venv/Scripts/pip install fastapi uvicorn[standard] pydantic pydantic-settings ezdxf shapely python-multipart python-dotenv httpx

# Install Node deps
cd apps/web
npm install

# Run API (in one terminal)
cd apps/api
../../.venv/Scripts/python.exe -m uvicorn main:app --reload --host 127.0.0.1 --port 8000

# Run Web (in another terminal)
cd apps/web
npm run dev

# Open browser
# http://localhost:5173/viewer
```

## How to Resume After Crash

1. Read `docs/plan.md` for current status and next steps
2. Read `docs/architecture.md` for system design
3. Check `git log` for latest commits
4. Start API and web servers as above
5. Open `http://localhost:5173/viewer`
6. Upload a DXF from `D:\OneDrive\OneDrive - Zervi Asia Co., Ltd\Documents\LBRECAD-TEST\`

## License

Proprietary — Zervi Group internal use.
