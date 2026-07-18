/**
 * BOM - Generate and manage bill of materials.
 */

function BOM() {
    this.lines = [];
}

BOM.prototype.addLine = function(panel, material, quantity) {
    this.lines.push({
        part_number: panel.name || panel.id,
        name: panel.name || panel.id,
        material: material,
        quantity: quantity,
        area_mm2: panel.area || 0,
        cut_length_mm: panel.cutLength || 0
    });
};

BOM.prototype.generate = function(assemblies) {
    var bom = [];
    for (var i = 0; i < assemblies.length; i++) {
        var assembly = assemblies[i];
        for (var j = 0; j < assembly.panels.length; j++) {
            var panel = assembly.panels[j];
            this.addLine(panel, "GP6 Premium Neoprene", 1);
        }
    }
    return this.lines;
};

BOM.prototype.toCSV = function() {
    var csv = "part_number,name,material,quantity,area_mm2,cut_length_mm\n";
    for (var i = 0; i < this.lines.length; i++) {
        var line = this.lines[i];
        csv += line.part_number + "," + line.name + "," + line.material + "," + line.quantity + "," + line.area_mm2 + "," + line.cut_length_mm + "\n";
    }
    return csv;
};

function main() {
    var doc = EAction.getDocument();
    if (!doc) {
        EAction.warnUser("No document open");
        return;
    }

    EAction.handleUserMessage("BOM module loaded");
}

main();
