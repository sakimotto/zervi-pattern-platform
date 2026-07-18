# Zervi Pattern Platform

AI-first pattern intelligence system for Zervi car seat cover manufacturing.

## Vision

Transform thousands of DXF/DWG pattern files into a searchable, reusable, AI-enhanced design database. Engineers keep using progeCAD or any 2D CAD tool. They export DXF using a Zervi template. The platform does the rest:

- Parse and validate patterns
- Extract panels, parts, notches, seams, labels
- Match similar parts across vehicles
- Build reusable blocks
- Generate BOMs and costs
- Create multimedia work instructions
- Sync with Odoo ERP

## Repository Structure

```
zervi-pattern-platform/
├── apps/
│   ├── web/                 # Browser UI (SvelteKit + Canvas)
│   └── api/                 # Python backend / agent runtime
├── packages/
│   ├── dxf-parser/          # DXF/DWG parsing and normalization
│   ├── pattern-engine/      # 2D geometry, panels, validation
│   ├── agent-runtime/       # Multi-agent orchestration
│   └── odoo-bridge/         # Odoo XML-RPC/JSON-RPC integration
├── db/
│   └── migrations/          # PostgreSQL + pgvector schema
├── docs/
│   ├── architecture.md      # System architecture
│   ├── plan.md              # Implementation plan
│   └── handover-k3-ui.md    # UI/UX handover for Kimi K3
├── scripts/                 # Automation scripts
└── tests/                   # Shared fixtures and e2e tests
```

## Key Principles

1. **AI-first:** Specialist agents perform parsing, matching, validation, and documentation tasks.
2. **Local-first:** Runs locally by default; syncs to cloud/Elestio services when configured.
3. **CAD-agnostic:** Engineers keep their existing CAD tools. DXF is the interchange format.
4. **Reusable:** Patterns decompose into blocks, parts, and operations that can be reused across vehicles.
5. **Odoo-integrated:** BOMs, inventory, costing, and manufacturing orders flow into Odoo.

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | SvelteKit, TailwindCSS, TypeScript |
| 2D Canvas | Fabric.js / Paper.js |
| Backend | Python, FastAPI |
| Agents | LangGraph + custom skills |
| LLM | DeepSeek / Kimi / OpenAI |
| Database | PostgreSQL + pgvector |
| Vector search | pgvector |
| DXF | `dxf-parser`, `ezdxf` |
| Odoo | XML-RPC/JSON-RPC client |

## Quick Start (Coming Soon)

```bash
# Clone
git clone https://github.com/sakimotto/zervi-pattern-platform.git
cd zervi-pattern-platform

# Install
npm install
pip install -r requirements.txt

# Run
docker compose up -d db
npm run dev
```

## License

Proprietary — Zervi Group internal use.
