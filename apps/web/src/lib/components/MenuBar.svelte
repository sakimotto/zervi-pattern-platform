<script>
	import { createEventDispatcher } from 'svelte';

	const dispatch = createEventDispatcher();

	let activeMenu = null;

	const menus = [
		{
			label: 'File',
			items: [
				{ label: 'New Pattern', action: 'new' },
				{ label: 'Open DXF...', action: 'open' },
				{ label: 'Save', action: 'save' },
				{ label: 'Export DXF...', action: 'export-dxf' },
				{ label: 'Export PDF...', action: 'export-pdf' },
				{ label: 'Close Pattern', action: 'close' }
			]
		},
		{
			label: 'Edit',
			items: [
				{ label: 'Undo', action: 'undo', shortcut: 'Ctrl+Z' },
				{ label: 'Redo', action: 'redo', shortcut: 'Ctrl+Y' },
				{ label: 'Preferences', action: 'preferences' }
			]
		},
		{
			label: 'View',
			items: [
				{ label: 'Zoom In', action: 'zoom-in' },
				{ label: 'Zoom Out', action: 'zoom-out' },
				{ label: 'Fit to View', action: 'fit' },
				{ label: 'Toggle Grid', action: 'grid' },
				{ label: 'Layer Manager', action: 'layers' }
			]
		},
		{
			label: 'Tools',
			items: [
				{ label: 'Generate BOM', action: 'bom' },
				{ label: 'Work Instructions', action: 'work-instructions' },
				{ label: 'Agent History', action: 'agent-history' },
				{ label: 'Odoo Sync', action: 'odoo-sync' }
			]
		},
		{
			label: 'Help',
			items: [
				{ label: 'Documentation', action: 'docs' },
				{ label: 'About', action: 'about' }
			]
		}
	];

	function toggleMenu(label) {
		activeMenu = activeMenu === label ? null : label;
	}

	function handleAction(action) {
		dispatch('action', action);
		activeMenu = null;
	}

	function handleClickOutside(e) {
		if (!e.target.closest('.menu-bar')) {
			activeMenu = null;
		}
	}
</script>

<svelte:window on:click={handleClickOutside} />

<div class="menu-bar flex items-center gap-1 px-2 py-1 bg-[var(--bg-secondary)] border-b border-[var(--border-color)] select-none">
	<!-- App Icon / Logo -->
	<div class="flex items-center gap-2 mr-4">
		<div class="w-6 h-6 rounded bg-[var(--accent)] flex items-center justify-center text-white font-bold text-xs">
			Z
		</div>
		<span class="text-sm font-semibold text-[var(--text-primary)]">Zervi Pattern</span>
	</div>

	<!-- Menus -->
	{#each menus as menu}
		<div class="relative">
			<button
				on:click={() => toggleMenu(menu.label)}
				class="px-3 py-1 text-sm rounded hover:bg-[var(--bg-elevated)] {activeMenu === menu.label ? 'bg-[var(--bg-elevated)]' : ''}"
			>
				{menu.label}
			</button>

			{#if activeMenu === menu.label}
				<div class="absolute top-full left-0 mt-1 w-48 bg-[var(--bg-elevated)] border border-[var(--border-color)] rounded shadow-lg z-50">
					{#each menu.items as item}
						<button
							on:click={() => handleAction(item.action)}
							class="w-full text-left px-3 py-1.5 text-sm hover:bg-[var(--border-color)] flex items-center justify-between"
						>
							<span>{item.label}</span>
							{#if item.shortcut}
								<span class="text-xs text-[var(--text-secondary)]">{item.shortcut}</span>
							{/if}
						</button>
					{/each}
				</div>
			{/if}
		</div>
	{/each}

	<!-- Right side -->
	<div class="flex-1"></div>
	<div class="flex items-center gap-2">
		<button class="px-2 py-1 text-sm rounded hover:bg-[var(--bg-elevated)]" title="Settings">⚙️</button>
		<button class="px-2 py-1 text-sm rounded hover:bg-[var(--bg-elevated)]" title="User">👤</button>
	</div>
</div>
