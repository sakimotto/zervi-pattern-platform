/**
 * Block Library - Manage reusable blocks for seat cover components.
 */

function BlockLibrary() {
    this.categories = [
        "hooks",
        "slots",
        "notches",
        "grommets",
        "seams",
        "panels",
        "labels"
    ];
    this.blocks = [];
}

BlockLibrary.prototype.addBlock = function(name, category, entities) {
    this.blocks.push({
        name: name,
        category: category,
        entities: entities,
        usage_count: 0
    });
};

BlockLibrary.prototype.search = function(query) {
    var results = [];
    for (var i = 0; i < this.blocks.length; i++) {
        var block = this.blocks[i];
        if (block.name.toLowerCase().indexOf(query.toLowerCase()) >= 0) {
            results.push(block);
        }
    }
    return results;
};

BlockLibrary.prototype.getByCategory = function(category) {
    var results = [];
    for (var i = 0; i < this.blocks.length; i++) {
        if (this.blocks[i].category === category) {
            results.push(this.blocks[i]);
        }
    }
    return results;
};

function main() {
    var doc = EAction.getDocument();
    if (!doc) {
        EAction.warnUser("No document open");
        return;
    }

    EAction.handleUserMessage("Block Library module loaded");
}

main();
