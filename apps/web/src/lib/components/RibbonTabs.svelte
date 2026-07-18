<script>
	import { createEventDispatcher } from 'svelte';

	const dispatch = createEventDispatcher();

	let activeTab = 'home';

	const tabs = [
		{ id: 'home', label: 'Home' },
		{ id: 'view', label: 'View' },
		{ id: 'panels', label: 'Panels' },
		{ id: 'bom', label: 'BOM' },
		{ id: 'agents', label: 'Agents' },
		{ id: 'output', label: 'Output' }
	];

	const tabContent = {
		home: [
			{ label: 'Select', icon: '⬚', action: 'select' },
			{ label: 'Pan', icon: '✋', action: 'pan' },
			{ label: 'Measure', icon: '📏', action: 'measure' }
		],
		view: [
			{ label: 'Zoom In', icon: '🔍+', action: 'zoom-in' },
			{ label: 'Zoom Out', icon: '🔍-', action: 'zoom-out' },
			{ label: 'Fit View', icon: '⛶', action: 'fit' },
			{ label: 'Grid', icon: '▦', action: 'grid' }
		],
		panels: [
			{ label: 'Group Panels', icon: '🗂️', action: 'group' },
			{ label: 'Rename', icon: '✏️', action: 'rename' },
			{ label: 'Split', icon: '✂️', action: 'split' },
			{ label: 'Mirror', icon: '🔄', action: 'mirror' }
		],
		bom: [
			{ label: 'Generate BOM', icon: '📋', action: 'bom' },
			{ label: 'Edit BOM', icon: '📝', action: 'bom-edit' },
			{ label: 'Export BOM', icon: '📤', action: 'bom-export' }
		],
		agents: [
			{ label: 'Run Agent', icon: '🤖', action: 'agent-run' },
			{ label: 'Approvals', icon: '✅', action: 'agent-approvals' },
			{ label: 'History', icon: '📜', action: 'agent-history' }
		],
		output: [
			{ label: 'Export DXF', icon: '📄', action: 'export-dxf' },
			{ label: 'Export PDF', icon: '📑', action: 'export-pdf' },
			{ label: 'Sync Odoo', icon: '🔗', action: 'odoo-sync' }
		]
	};

	function selectTab(id) {
		activeTab = id;
		dispatch('tabChange', id);
	}

	function handleAction(action) {
		dispatch('action', action);
	}
</script>

<div class="bg-[var(--bg-secondary)] border-b border-[var(--border-color)]">
	<!-- Tab Headers -->
	<div class="flex gap-0 px-2">
		{#each tabs as tab}
			<button
				on:click={() => selectTab(tab.id)}
				class="px-4 py-2 text-sm font-medium border-b-2 transition-colors {activeTab === tab.id ? 'border-[var(--accent)] text-[var(--accent)]' : 'border-transparent text-[var(--text-secondary)] hover:text-[var(--text-primary)]'}"
			>
				{tab.label}
			</button>
		{/each}
	</div>

	<!-- Tab Content -->
	<div class="flex items-center gap-1 px-2 py-1 bg-[var(--bg-elevated)]">
		{#each tabContent[activeTab] as action}
			<button
				on:click={() => handleAction(action.action)}
				class="flex flex-col items-center gap-0.5 px-3 py-1.5 rounded hover:bg-[var(--border-color)] text-[var(--text-primary)]"
				title={action.label}
			>
				<span class="text-lg">{action.icon}</span>
				<span class="text-xs">{action.label}</span>
			</button>
		{/each}
	</div>
</div>
