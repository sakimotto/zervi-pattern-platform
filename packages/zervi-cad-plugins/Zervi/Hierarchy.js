/**
 * Hierarchy - Manage panel hierarchy (driver/passenger/cushion/seatback).
 */

function Hierarchy() {
    this.assemblies = [];
}

Hierarchy.prototype.suggestGrouping = function(panels) {
    var groups = {
        driver: [],
        passenger: [],
        cushion: [],
        seatback: [],
        headrest: []
    };

    for (var i = 0; i < panels.length; i++) {
        var panel = panels[i];
        var name = panel.name || "";

        if (name.match(/^RB/i)) groups.driver.push(panel);
        else if (name.match(/^RC/i)) groups.passenger.push(panel);
        else if (name.match(/^HR/i)) groups.headrest.push(panel);
        else if (name.match(/^THSBS/i)) groups.seatback.push(panel);
        else if (name.match(/^THSC/i)) groups.cushion.push(panel);
    }

    return groups;
};

Hierarchy.prototype.createAssembly = function(name, panels, type) {
    var assembly = {
        name: name,
        type: type,
        panels: panels,
        children: []
    };
    this.assemblies.push(assembly);
    return assembly;
};

function main() {
    var doc = EAction.getDocument();
    if (!doc) {
        EAction.warnUser("No document open");
        return;
    }

    EAction.handleUserMessage("Hierarchy module loaded");
}

main();
