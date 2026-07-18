/**
 * Zervi CAD Plugin for QCAD
 * Main entry point for Zervi Pattern Platform features.
 */

// Include Zervi modules
include("PatternImport.js");
include("Hierarchy.js");
include("BOM.js");
include("BlockLibrary.js");
include("OdooSync.js");
include("Agents/Agent.js");

/**
 * Initialize Zervi plugin.
 */
function init() {
    // Register menu items
    var menu = EAction.getMenu("Zervi");
    if (!menu) {
        menu = EAction.createMenu("Zervi", "Zervi");
    }

    // Pattern Import
    var importAction = new RGuiAction("&Import Pattern...", menu);
    importAction.setIcon("scripts/Zervi/icons/import.svg");
    importAction.setScriptFile("scripts/Zervi/PatternImport.js");
    importAction.setShortcut("Ctrl+I");
    importAction.setStatusTip("Import and validate a Zervi pattern DXF");
    importAction.setRequiresDocument(true);

    // Hierarchy
    var hierarchyAction = new RGuiAction("&Hierarchy...", menu);
    hierarchyAction.setIcon("scripts/Zervi/icons/hierarchy.svg");
    hierarchyAction.setScriptFile("scripts/Zervi/Hierarchy.js");
    hierarchyAction.setStatusTip("Manage panel hierarchy");
    hierarchyAction.setRequiresDocument(true);

    // BOM
    var bomAction = new RGuiAction("&BOM...", menu);
    bomAction.setIcon("scripts/Zervi/icons/bom.svg");
    bomAction.setScriptFile("scripts/Zervi/BOM.js");
    bomAction.setShortcut("Ctrl+B");
    bomAction.setStatusTip("Generate and manage BOM");
    bomAction.setRequiresDocument(true);

    // Block Library
    var blockAction = new RGuiAction("&Block Library...", menu);
    blockAction.setIcon("scripts/Zervi/icons/block.svg");
    blockAction.setScriptFile("scripts/Zervi/BlockLibrary.js");
    blockAction.setStatusTip("Manage reusable blocks");
    blockAction.setRequiresDocument(true);

    // Odoo Sync
    var odooAction = new RGuiAction("&Odoo Sync...", menu);
    odooAction.setIcon("scripts/Zervi/icons/odoo.svg");
    odooAction.setScriptFile("scripts/Zervi/OdooSync.js");
    odooAction.setStatusTip("Sync to Odoo ERP");
    odooAction.setRequiresDocument(true);

    // Separator
    menu.addSeparator();

    // Agent Chat
    var agentAction = new RGuiAction("&Agent...", menu);
    agentAction.setIcon("scripts/Zervi/icons/agent.svg");
    agentAction.setScriptFile("scripts/Zervi/Agents/Agent.js");
    agentAction.setShortcut("Ctrl+A");
    agentAction.setStatusTip("Zervi AI Agent");
    agentAction.setRequiresDocument(true);

    print("Zervi plugin initialized");
}

// Auto-initialize when QCAD loads
init();
