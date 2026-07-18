/**
 * Pattern Import - Import and validate Zervi pattern DXF files.
 */

function PatternImport() {
    this.requiredLayers = [
        "Z_CUT",
        "Z_NOTCH",
        "Z_STITCH",
        "Z_TEXT_PARTNO",
        "Z_TEXT_PANELNO",
        "Z_TEXT_ITEMNO",
        "Z_DIM",
        "Z_HOOK",
        "Z_LOOP",
        "Z_JOIN",
        "Z_MARK"
    ];
}

PatternImport.prototype.validate = function(doc) {
    var issues = [];

    // Check for required layers
    var layerNames = doc.queryLayerNames();
    for (var i = 0; i < this.requiredLayers.length; i++) {
        var required = this.requiredLayers[i];
        var found = false;
        for (var j = 0; j < layerNames.length; j++) {
            if (layerNames[j].toUpperCase() === required.toUpperCase()) {
                found = true;
                break;
            }
        }
        if (!found) {
            issues.push("Missing layer: " + required);
        }
    }

    return issues;
};

PatternImport.prototype.analyze = function(doc) {
    var panels = [];
    var labels = [];
    var holes = [];

    // Get all entities from Z_CUT layer
    var cutEntities = doc.queryLayerEntities("Z_CUT", false);
    for (var i = 0; i < cutEntities.length; i++) {
        var entity = cutEntities[i];
        // Process cut entities to find panels
    }

    // Get labels from Z_TEXT_PANELNO layer
    var labelEntities = doc.queryLayerEntities("Z_TEXT_PANELNO", false);
    for (var i = 0; i < labelEntities.length; i++) {
        var entity = labelEntities[i];
        if (isTextEntity(entity) || isMTextEntity(entity)) {
            labels.push({
                text: entity.getText(),
                position: entity.getInsertionPoint(),
                layer: "Z_TEXT_PANELNO"
            });
        }
    }

    // Get holes from Z_NOTCH layer
    var notchEntities = doc.queryLayerEntities("Z_NOTCH", false);
    for (var i = 0; i < notchEntities.length; i++) {
        var entity = notchEntities[i];
        if (isCircleEntity(entity)) {
            var center = entity.getCenter();
            var radius = entity.getRadius();
            holes.push({
                center: [center.x, center.y],
                radius: radius,
                classification: radius < 15 ? "notch" : radius < 50 ? "grommet" : "hole"
            });
        }
    }

    return {
        panels: panels,
        labels: labels,
        holes: holes
    };
};

function isTextEntity(entity) {
    return entity.getType() === RS.EntityText;
}

function isMTextEntity(entity) {
    return entity.getType() === RS.EntityMText;
}

function isCircleEntity(entity) {
    return entity.getType() === RS.EntityCircle;
}

// Entry point
function main() {
    var doc = EAction.getDocument();
    if (!doc) {
        EAction.warnUser("No document open");
        return;
    }

    var importer = new PatternImport();
    var issues = importer.validate(doc);

    if (issues.length > 0) {
        var msg = "Validation issues found:\n\n" + issues.join("\n");
        EAction.warnUser(msg);
        return;
    }

    var analysis = importer.analyze(doc);
    EAction.handleUserMessage("Pattern analysis complete: " +
        analysis.panels.length + " panels, " +
        analysis.labels.length + " labels, " +
        analysis.holes.length + " holes");
}

main();
