<script>
	import { createEventDispatcher } from 'svelte';

	const dispatch = createEventDispatcher();

	let searchQuery = '';
	let selectedCategory = 'all';
	let selectedBlock = null;
	let insertOptions = {
		scale: 1,
		angle: 0,
		mirrorX: false,
		mirrorY: false
	};

	const categories = [
		{ id: 'all', label: 'All Blocks' },
		{ id: 'hooks', label: 'Hooks & Loops' },
		{ id: 'slots', label: 'Slots & Cutouts' },
		{ id: 'notches', label: 'Notches & Holes' },
		{ id: 'grommets', label: 'Grommets' },
		{ id: 'seams', label: 'Seam Guides' },
		{ id: 'panels', label: 'Panel Templates' },
		{ id: 'labels', label: 'Labels & Text' }
	];

	// Placeholder blocks — later these come from the database
	let blocks = [
		{ id: 'hook-std', name: 'Standard Hook', category: 'hooks', preview: 'hook' },
		{ id: 'hook-reinf', name: 'Reinforced Hook', category: 'hooks', preview: 'hook' },
		{ id: 'loop-std', name: 'Standard Loop', category: 'hooks', preview: 'loop' },
		{ id: 'slot-headrest', name: 'Headrest Slot', category: 'slots', preview: 'slot' },
		{ id: 'slot-seatbelt', name: 'Seatbelt Slot', category: 'slots', preview: 'slot' },
		{ id: 'notch-13mm', name: 'Notch 13mm', category: 'notches', preview: 'notch' },
		{ id: 'notch-15mm', name: 'Notch 15mm', category: 'notches', preview: 'notch' },
		{ id: 'grommet-20mm', name: 'Grommet 20mm', category: 'grommets', preview: 'grommet' },
		{ id: 'grommet-25mm', name: 'Grommet 25mm', category: 'grommets', preview: 'grommet' },
		{ id: 'seam-overlock', name: 'Overlock Seam', category: 'seams', preview: 'seam' },
		{ id: 'seam-twin', name: 'Twin Needle', category: 'seams', preview: 'seam' }
	];

	$: filteredBlocks = blocks.filter((b) => {
		const matchesCategory = selectedCategory === 'all' || b.category === selectedCategory;
		const matchesSearch = b.name.toLowerCase().includes(searchQuery.toLowerCase());
		return matchesCategory && matchesSearch;
	});

	function selectBlock(block) {
		selectedBlock = block;
	}

	function insertBlock() {
		if (!selectedBlock) return;
		dispatch('insert', { block: selectedBlock, options: insertOptions });
	}
</script>

<div class="flex flex-col h-full bg-[var(--bg-secondary)] border-r border-[var(--border-color)]">
	<!-- Search -->
	<div class="p-2 border-b border-[var(--border-color)]">
		<input
			type="text"
			bind:value={searchQuery}
			placeholder="Search blocks..."
			class="w-full px-2 py-1 text-sm bg-[var(--bg-elevated)] border border-[var(--border-color)] rounded text-[var(--text-primary)]"
		/>
	</div>

	<!-- Categories -->
	<div class="p-2 border-b border-[var(--border-color)]">
		<select
			bind:value={selectedCategory}
			class="w-full px-2 py-1 text-sm bg-[var(--bg-elevated)] border border-[var(--border-color)] rounded text-[var(--text-primary)]"
		>
			{#each categories as cat}
				<option value={cat.id}>{cat.label}</option>
			{/each}
		</select>
	</div>

	<!-- Block Grid -->
	<div class="flex-1 overflow-y-auto p-2">
		<div class="grid grid-cols-2 gap-2">
			{#each filteredBlocks as block}
				<button
					on:click={() => selectBlock(block)}
					class="flex flex-col items-center gap-1 p-2 rounded border {selectedBlock?.id === block.id ? 'border-[var(--accent)] bg-[var(--bg-elevated)]' : 'border-[var(--border-color)] hover:bg-[var(--bg-elevated)]'}"
				>
					<div class="w-full h-16 bg-[#0a0a0a] rounded flex items-center justify-center text-2xl">
						{#if block.preview === 'hook'}🪝
						{:else if block.preview === 'loop'}🔗
						{:else if block.preview === 'slot'}▭
						{:else if block.preview === 'notch'}◉
						{:else if block.preview === 'grommet'}⭕
						{:else if block.preview === 'seam'}〰️
						{:else}▣{/if}
					</div>
					<span class="text-xs text-[var(--text-primary)]">{block.name}</span>
				</button>
			{/each}
		</div>
	</div>

	<!-- Insert Options -->
	{#if selectedBlock}
		<div class="p-2 border-t border-[var(--border-color)] space-y-2 bg-[var(--bg-elevated)]">
			<div class="text-xs font-semibold text-[var(--text-secondary)] uppercase">Insert: {selectedBlock.name}</div>

			<div class="grid grid-cols-2 gap-2">
				<label class="text-xs text-[var(--text-secondary)]">
					Scale
					<input type="number" bind:value={insertOptions.scale} step="0.1" min="0.1" class="w-full mt-1 px-1 py-0.5 text-sm bg-[var(--bg-primary)] border border-[var(--border-color)] rounded text-[var(--text-primary)]" />
				</label>
				<label class="text-xs text-[var(--text-secondary)]">
					Angle
					<input type="number" bind:value={insertOptions.angle} step="1" class="w-full mt-1 px-1 py-0.5 text-sm bg-[var(--bg-primary)] border border-[var(--border-color)] rounded text-[var(--text-primary)]" />
				</label>
			</div>

			<div class="flex gap-4 text-xs text-[var(--text-secondary)]">
				<label class="flex items-center gap-1">
					<input type="checkbox" bind:checked={insertOptions.mirrorX} /> Mirror X
				</label>
				<label class="flex items-center gap-1">
					<input type="checkbox" bind:checked={insertOptions.mirrorY} /> Mirror Y
				</label>
			</div>

			<button
				on:click={insertBlock}
				class="w-full px-3 py-1.5 text-sm bg-[var(--accent)] text-white rounded hover:opacity-90"
			>
				Insert Block
			</button>
		</div>
	{/if}
</div>
