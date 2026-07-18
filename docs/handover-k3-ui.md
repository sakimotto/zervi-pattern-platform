# Handover — UI/UX Design for Zervi Pattern Platform

**To:** Kimi K3 (UI/UX Designer)  
**From:** Zervi Pattern Platform team  
**Project:** Zervi Pattern Platform  
**Date:** 2024-07-17  
**Status:** Ready for design foundation

---

## 1. Product Vision

Build an AI-first web application where Zervi manufacturing engineers upload car seat cover DXF files, review AI-extracted panels and parts, manage reusable blocks, generate BOMs, and create multimedia work instructions.

The tool must feel like a modern CAD/PLM application, not a generic admin dashboard.

---

## 2. Target Users

### Primary: Manufacturing Engineers
- Use progeCAD / LibreCAD / AutoCAD daily
- Comfortable with technical drawings
- Want speed and precision
- Skeptical of flashy UI that slows them down

### Secondary: Production Planners
- Review BOMs and work instructions
- Need clear data tables and export options

### Tertiary: Management
- View dashboards and cost roll-ups
- Need high-level summaries

---

## 3. Core User Flows

### Flow 1: Upload & Review a Pattern
1. User lands on Pattern Library
2. Clicks “Upload DXF”
3. Selects file
4. Platform runs AI agents (progress indicator)
5. Pattern opens in viewer
6. User reviews panels, labels, validation issues
7. User approves or corrects
8. User exports clean DXF or BOM

### Flow 2: Find Reusable Parts
1. User searches for a panel number or vehicle
2. Platform shows matching patterns
3. User selects a panel
4. Platform shows similar panels across all patterns
5. User groups them into a block
6. Block appears in Block Library

### Flow 3: Generate BOM
1. User opens an approved pattern
2. Clicks “Generate BOM”
3. Platform computes materials and quantities
4. User reviews/edits BOM table
5. User clicks “Sync to Odoo”

### Flow 4: Create Work Instructions
1. User opens approved pattern
2. Clicks “Work Instructions”
3. Platform auto-generates operation sequence
4. User adds images/videos/text to each step
5. User saves instruction set

---

## 4. Key Screens

### 4.1 Pattern Library (Dashboard)

**Purpose:** Browse, search, and manage all imported patterns.

**Layout:**
- Top: Global search bar + primary action “Upload DXF”
- Left sidebar: Filters (vehicle, row, material, status, date)
- Main area: Grid or list of pattern cards
- Each card: thumbnail preview, pattern name, vehicle, status badge, last updated

**Interactions:**
- Hover card: quick actions (view, validate, export)
- Click card: open Pattern Viewer
- Bulk select: delete, archive, re-run agents

**Empty state:** Clear CTA to upload first DXF

### 4.2 Pattern Viewer (Main Workspace)

**Purpose:** Inspect and edit one pattern.

**Layout:**
- Top toolbar: zoom, pan, fit, layer toggles, measure, export
- Left sidebar (collapsible):
  - Layer tree (Z_CUT, Z_NOTCH, Z_STITCH, etc.)
  - Panel list with checkboxes
  - Label list
- Center: large 2D canvas showing the pattern
- Right sidebar (collapsible):
  - Properties of selected entity
  - Validation report
- Bottom panel (tabs):
  - Validation
  - BOM Preview
  - Work Instructions
  - Agent Log

**Canvas behavior:**
- Dark background (#1a1a1a or similar)
- Entities colored by layer or entity type
- Hover highlights entity
- Click selects entity
- Middle-mouse or space+drag to pan
- Scroll wheel to zoom

**Selection state:**
- Selected panel: highlighted with bounding box
- Properties panel shows: panel number, part number, area, cut length, material

### 4.3 Agent Approval Panel

**Purpose:** Review AI agent decisions before they are applied.

**Layout:**
- List of pending agent tasks
- Each item: agent name, task summary, confidence score, proposed change
- Actions: Approve, Reject, Edit
- Filter: pending, approved, rejected, all

### 4.4 Block Library

**Purpose:** Browse and manage reusable pattern components.

**Layout:**
- Search bar
- Category filters (hooks, slots, grommets, reinforcements)
- Grid of block cards
- Each card: preview, name, category, usage count
- Click: block detail + usage across patterns

### 4.5 BOM & Costing

**Purpose:** View and edit bill of materials.

**Layout:**
- Editable data table
- Columns: item, material, quantity, unit, cost, total
- Top: pattern selector, “Generate BOM” button, “Sync to Odoo” button
- Bottom: cost roll-up summary

### 4.6 Work Instructions Builder

**Purpose:** Build step-by-step manufacturing guides.

**Layout:**
- Left: operation sequence list (reorderable)
- Center: selected step editor
  - Title
  - Description
  - Media upload (image/video)
- Right: preview of final instruction card

### 4.7 Settings / Integrations

**Purpose:** Configure Odoo, LLM, templates, users.

**Sections:**
- Odoo connection
- LLM provider and model
- DXF template rules
- User management
- Agent behavior (auto-approve thresholds)

---

## 5. Design System Requirements

### 5.1 Color Palette

**Mode:** Dark mode first. Light mode optional.

**Suggested dark theme:**
- Background: `#0f1115`
- Surface: `#181b21`
- Surface elevated: `#22262d`
- Border: `#2d323c`
- Text primary: `#e8eaed`
- Text secondary: `#9aa0a6`
- Accent primary: `#4f8cff` (Zervi blue)
- Accent secondary: `#34d399` (success / validation pass)
- Warning: `#fbbf24`
- Error: `#f87171`

**CAD canvas:**
- Background: `#0a0a0a`
- Grid: `#1f1f1f`
- Cut lines: `#ff6b6b`
- Notches: `#4ade80`
- Stitch lines: `#fbbf24`
- Text: `#e8eaed`
- Selected highlight: `#4f8cff`

### 5.2 Typography

- Font: Inter or Roboto for UI
- Monospace: JetBrains Mono or Fira Code for technical data
- Scale:
  - XS: 12px
  - SM: 14px
  - Base: 16px
  - LG: 18px
  - XL: 20px
  - 2XL: 24px
  - 3XL: 30px

### 5.3 Spacing

- 4px base grid
- Common values: 4, 8, 12, 16, 24, 32, 48, 64

### 5.4 Components Needed

- Button (primary, secondary, danger, ghost)
- Input / Textarea
- Select / Combobox
- Data table (sortable, filterable, paginated)
- Tabs
- Accordion
- Modal / Dialog
- Toast / Notification
- Progress bar / Spinner
- Badge
- Tooltip
- Split pane / Resizable panels
- Canvas wrapper
- File upload dropzone
- Search bar
- Filter chips

### 5.5 Icons

Use Lucide icons or Heroicons. CAD-specific icons may need custom SVG:
- Zoom in/out
- Pan
- Measure
- Layer visibility
- Block
- BOM
- Work instruction
- Validate

---

## 6. Interaction Patterns

### 6.1 Navigation
- Persistent left rail with icons + labels
- Active state clearly indicated
- Keyboard shortcut `Ctrl+K` for command palette / search

### 6.2 Notifications
- Toast notifications top-right
- Agent completion, validation errors, sync status

### 6.3 Loading States
- Skeleton loaders for lists
- Progress indicator for long agent tasks
- Canvas shows spinner while rendering large patterns

### 6.4 Error States
- Validation issues shown in bottom panel with line/entity references
- Inline form errors
- Full-page error boundary with reload action

### 6.5 Confirmation
- Destructive actions require confirmation
- Bulk actions require confirmation

---

## 7. Accessibility

- WCAG 2.1 AA minimum
- Keyboard navigation for all UI elements
- Focus visible states
- Screen reader labels for canvas regions
- Color not the only indicator of status

---

## 8. Responsive Considerations

Primary use is desktop/large monitor. Tablet support is nice-to-have. Mobile is not a priority.

Minimum recommended viewport: 1280px wide.

---

## 9. Deliverables Expected from K3

1. Figma or equivalent design file with all key screens
2. Design tokens (colors, typography, spacing, shadows)
3. Component library spec
4. Click-through prototype of upload → review → BOM flow
5. Dark mode specification
6. Handoff notes for frontend developer

---

## 10. Open Questions for K3

1. Should the canvas use a dark CAD-style background or match the app surface?
2. Should we use a left-rail navigation or a top bar?
3. How much density vs. whitespace do you prefer for tables?
4. Should agent approvals be a separate page or a slide-over panel?
5. Any existing Zervi brand colors or assets to incorporate?

---

## 11. Reference Files

- `docs/architecture.md` — system architecture and data model
- `docs/plan.md` — implementation phases
- `tests/shared-fixtures/` — sample DXF files for context

---

## 12. Notes

- This is a technical/manufacturing tool. Beauty is welcome, but clarity and speed come first.
- Every pixel should serve the engineer’s workflow.
- When in doubt, imitate modern CAD/PLM tools (Onshape, Fusion 360, Figma’s clean density) rather than admin dashboards.
