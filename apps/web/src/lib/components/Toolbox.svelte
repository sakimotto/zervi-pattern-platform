<script>
	import { createEventDispatcher } from 'svelte';

	const dispatch = createEventDispatcher();

	const tools = [
		{ icon: '📄', label: 'New', action: 'new' },
		{ icon: '📂', label: 'Open', action: 'open' },
		{ icon: '💾', label: 'Save', action: 'save' },
		{ icon: '📤', label: 'Export', action: 'export' },
		{ icon: '📥', label: 'Import', action: 'import' },
		{ icon: '📚', label: 'Library', action: 'library' },
		{ icon: '🔍', label: 'Search', action: 'search' },
		{ icon: '⚙️', label: 'Settings', action: 'settings' }
	];

	let activeTool = null;

	function handleTool(action) {
		activeTool = action;
		dispatch('action', action);
	}
</script>

<div class="flex flex-col items-center gap-1 w-12 py-2 bg-[var(--bg-secondary)] border-r border-[var(--border-color)]">
	{#each tools as tool}
		<button
			on:click={() => handleTool(tool.action)}
			class="w-10 h-10 rounded flex items-center justify-center text-lg hover:bg-[var(--bg-elevated)] {activeTool === tool.action ? 'bg-[var(--accent)] text-white' : 'text-[var(--text-secondary)]'}"
			title={tool.label}
		>
			{tool.icon}
		</button>
	{/each}
</div>
